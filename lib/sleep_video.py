"""Sleep video assembly engine — long-form horizontal (16:9) for YouTube.

Creates 1-3+ hour sleep story videos from:
- AI-generated script (scenes with narration text + image prompts)
- ElevenLabs voiceover (calm, soothing voice)
- Imagen/Nanobanana generated images
- Ambient background music

Features:
- Slow Ken Burns pan/zoom across images (30-60s per image)
- Smooth crossfade transitions between scenes
- Background music mixed under narration
- 1920x1080 horizontal output optimized for YouTube
- Chunked voiceover generation (ElevenLabs has text limits)
- Automatic scene timing based on narration duration
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path


# YouTube specs
WIDTH = 1920
HEIGHT = 1080
FPS = 24  # 24fps is fine for slow-moving sleep content, saves encoding time
VIDEO_BITRATE = "4M"  # Lower bitrate OK for slow-moving imagery
AUDIO_BITRATE = "192k"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Sleep content defaults
DEFAULT_IMAGE_DURATION = 45.0  # seconds per image if no voiceover timing
CROSSFADE_DURATION = 3.0  # seconds of crossfade between scenes
BG_MUSIC_VOLUME = 0.08  # background music volume (very quiet under narration)
NARRATION_VOLUME = 1.0


def _run_ffmpeg(args, timeout=600):
    """Run an ffmpeg command. Longer timeout for long-form video."""
    cmd = ["ffmpeg", "-y"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr[-800:]}")
    return result


def get_audio_duration(audio_path):
    """Get duration of an audio file in seconds."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", audio_path],
        capture_output=True, text=True, timeout=30,
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def image_to_scene(image_path, output_path, duration=45.0, effect="pan_left"):
    """Convert a single image to a slow Ken Burns scene clip.

    Uses lightweight zoompan from 2200px (not 8000px) for fast rendering.
    Sleep content is slow-moving so subtle effects are all we need.

    Args:
        image_path: Path to source image
        output_path: Path to output mp4
        duration: Scene duration in seconds
        effect: Ken Burns effect type (zoom_in, zoom_out, pan_left, pan_right,
                pan_up, pan_down, still)
    """
    total_frames = int(duration * FPS)
    # Scale to 2200px wide — enough headroom for subtle pan/zoom without
    # the massive CPU cost of 8000px. Renders ~10x faster.
    src_scale = 2200

    if effect == "still":
        vf = (
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={WIDTH}:{HEIGHT},format=yuv420p"
        )
    elif effect == "zoom_in":
        vf = (
            f"scale={src_scale}:-1,"
            f"zoompan=z='1+on/{total_frames}*0.08'"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={total_frames}:s={WIDTH}x{HEIGHT}:fps={FPS},"
            f"format=yuv420p"
        )
    elif effect == "zoom_out":
        vf = (
            f"scale={src_scale}:-1,"
            f"zoompan=z='1.08-on/{total_frames}*0.08'"
            f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={total_frames}:s={WIDTH}x{HEIGHT}:fps={FPS},"
            f"format=yuv420p"
        )
    elif effect == "pan_left":
        vf = (
            f"scale={src_scale}:-1,"
            f"zoompan=z='1.04'"
            f":x='iw/2-(iw/zoom/2)-on/{total_frames}*(iw*0.03)'"
            f":y='ih/2-(ih/zoom/2)'"
            f":d={total_frames}:s={WIDTH}x{HEIGHT}:fps={FPS},"
            f"format=yuv420p"
        )
    elif effect == "pan_right":
        vf = (
            f"scale={src_scale}:-1,"
            f"zoompan=z='1.04'"
            f":x='iw/2-(iw/zoom/2)+on/{total_frames}*(iw*0.03)'"
            f":y='ih/2-(ih/zoom/2)'"
            f":d={total_frames}:s={WIDTH}x{HEIGHT}:fps={FPS},"
            f"format=yuv420p"
        )
    elif effect == "pan_up":
        vf = (
            f"scale={src_scale}:-1,"
            f"zoompan=z='1.04'"
            f":x='iw/2-(iw/zoom/2)'"
            f":y='ih/2-(ih/zoom/2)-on/{total_frames}*(ih*0.02)'"
            f":d={total_frames}:s={WIDTH}x{HEIGHT}:fps={FPS},"
            f"format=yuv420p"
        )
    elif effect == "pan_down":
        vf = (
            f"scale={src_scale}:-1,"
            f"zoompan=z='1.04'"
            f":x='iw/2-(iw/zoom/2)'"
            f":y='ih/2-(ih/zoom/2)+on/{total_frames}*(ih*0.02)'"
            f":d={total_frames}:s={WIDTH}x{HEIGHT}:fps={FPS},"
            f"format=yuv420p"
        )
    else:
        raise ValueError(f"Unknown effect: {effect}")

    args = [
        "-loop", "1", "-i", image_path,
        "-t", str(duration),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "ultrafast",
        "-b:v", VIDEO_BITRATE, "-maxrate", VIDEO_BITRATE, "-bufsize", "8M",
        "-r", str(FPS), "-pix_fmt", "yuv420p",
        output_path,
    ]
    _run_ffmpeg(args, timeout=max(300, int(duration * 3)))
    return output_path


def concatenate_with_crossfade(clip_paths, output_path, fade_duration=CROSSFADE_DURATION):
    """Concatenate video clips with crossfade transitions.

    For long-form content, we process in batches to avoid FFmpeg filter
    complexity limits, then concat the batches.
    """
    if len(clip_paths) == 1:
        import shutil
        shutil.copy2(clip_paths[0], output_path)
        return output_path

    # For many clips, process in batches of 8 then concat batches
    batch_size = 8
    if len(clip_paths) > batch_size:
        tmpdir = tempfile.mkdtemp(prefix="sleep_batch_")
        batches = []
        for b in range(0, len(clip_paths), batch_size):
            batch = clip_paths[b:b + batch_size]
            batch_out = os.path.join(tmpdir, f"batch_{b:04d}.mp4")
            if len(batch) == 1:
                import shutil
                shutil.copy2(batch[0], batch_out)
            else:
                _crossfade_batch(batch, batch_out, fade_duration)
            batches.append(batch_out)

        if len(batches) == 1:
            import shutil
            shutil.copy2(batches[0], output_path)
        else:
            # Simple concat between batches (crossfade already applied within)
            _simple_concat(batches, output_path)
        return output_path

    _crossfade_batch(clip_paths, output_path, fade_duration)
    return output_path


def _crossfade_batch(clip_paths, output_path, fade_duration):
    """Apply crossfade between a small batch of clips (max ~8)."""
    # Get durations for offset calculation
    durations = []
    for clip in clip_paths:
        durations.append(get_audio_duration(clip))

    inputs = []
    for clip in clip_paths:
        inputs += ["-i", clip]

    # Build xfade filter chain
    filter_parts = []
    current = "[0:v]"
    cumulative_offset = 0

    for i in range(1, len(clip_paths)):
        out_label = f"[v{i}]" if i < len(clip_paths) - 1 else "[vout]"
        cumulative_offset += durations[i - 1] - fade_duration
        filter_parts.append(
            f"{current}[{i}:v]xfade=transition=fade:duration={fade_duration}"
            f":offset={cumulative_offset:.2f}{out_label}"
        )
        current = out_label if i < len(clip_paths) - 1 else ""

    filter_str = ";".join(filter_parts)
    args = inputs + [
        "-filter_complex", filter_str,
        "-map", "[vout]",
        "-c:v", "libx264", "-preset", "fast",
        "-b:v", VIDEO_BITRATE, "-maxrate", VIDEO_BITRATE, "-bufsize", "8M",
        "-pix_fmt", "yuv420p",
        output_path,
    ]
    _run_ffmpeg(args, timeout=1200)
    return output_path


def _simple_concat(clip_paths, output_path):
    """Simple concatenation without transitions."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for clip in clip_paths:
            f.write(f"file '{clip}'\n")
        list_file = f.name
    args = [
        "-f", "concat", "-safe", "0", "-i", list_file,
        "-c:v", "libx264", "-preset", "fast",
        "-b:v", VIDEO_BITRATE, "-maxrate", VIDEO_BITRATE, "-bufsize", "8M",
        "-pix_fmt", "yuv420p",
        output_path,
    ]
    _run_ffmpeg(args, timeout=1200)
    os.unlink(list_file)
    return output_path


def concat_audio_files(audio_paths, output_path):
    """Concatenate multiple audio files into one seamless track."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        for audio in audio_paths:
            f.write(f"file '{audio}'\n")
        list_file = f.name
    args = [
        "-f", "concat", "-safe", "0", "-i", list_file,
        "-c:a", "libmp3lame", "-b:a", AUDIO_BITRATE,
        output_path,
    ]
    _run_ffmpeg(args, timeout=300)
    os.unlink(list_file)
    return output_path


def prepend_silence(audio_path, output_path, silence_duration):
    """Prepend silence to an audio file (e.g. to delay narration after title card)."""
    args = [
        "-f", "lavfi", "-t", str(silence_duration),
        "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-i", audio_path,
        "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[out]",
        "-map", "[out]",
        "-c:a", "libmp3lame", "-b:a", AUDIO_BITRATE,
        output_path,
    ]
    _run_ffmpeg(args, timeout=300)
    return output_path


def mix_audio(narration_path, bg_music_path, output_path,
              narration_vol=NARRATION_VOLUME, music_vol=BG_MUSIC_VOLUME,
              title_duration=0.0):
    """Mix narration with background music.

    Background music is looped and starts from second 0 (covering title card).
    Narration is delayed by title_duration so it starts after the title card.
    This ensures there's never dead silence at the beginning.
    """
    narration_dur = get_audio_duration(narration_path)
    total_dur = narration_dur + title_duration
    fade_out_start = max(0, total_dur - 5)

    if title_duration > 0:
        # Narration delayed: pad with silence, bg music plays from 0:00
        args = [
            "-i", narration_path,
            "-stream_loop", "-1", "-i", bg_music_path,
            "-filter_complex",
            # Pad narration with silence at the start so it begins after title card
            f"[0:a]adelay={int(title_duration * 1000)}|{int(title_duration * 1000)},volume={narration_vol}[narr];"
            # Background music starts immediately, loops for full duration
            f"[1:a]volume={music_vol},afade=t=in:st=0:d=5,afade=t=out:st={fade_out_start}:d=5[music];"
            f"[narr][music]amix=inputs=2:duration=longest:dropout_transition=3[out]",
            "-map", "[out]",
            "-c:a", "aac", "-b:a", AUDIO_BITRATE,
            "-t", str(total_dur),
            output_path,
        ]
    else:
        # No title card — original behavior
        args = [
            "-i", narration_path,
            "-stream_loop", "-1", "-i", bg_music_path,
            "-filter_complex",
            f"[0:a]volume={narration_vol}[narr];"
            f"[1:a]volume={music_vol},afade=t=in:st=0:d=5,afade=t=out:st={narration_dur - 5}:d=5[music];"
            f"[narr][music]amix=inputs=2:duration=first:dropout_transition=3[out]",
            "-map", "[out]",
            "-c:a", "aac", "-b:a", AUDIO_BITRATE,
            "-t", str(narration_dur),
            output_path,
        ]
    _run_ffmpeg(args, timeout=600)
    return output_path


def add_audio_to_video(video_path, audio_path, output_path):
    """Mux audio onto video track. Trims to shortest."""
    args = [
        "-i", video_path, "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", AUDIO_BITRATE,
        "-shortest",
        output_path,
    ]
    _run_ffmpeg(args, timeout=600)
    return output_path


def add_title_card(output_path, title_text, subtitle_text="", duration=8.0,
                    background_image=None):
    """Generate a title card with text overlay.

    If background_image is provided, uses it with a dark overlay + Ken Burns zoom.
    Otherwise falls back to a solid dark background.

    Args:
        output_path: Path to output mp4
        title_text: Main title text
        subtitle_text: Optional subtitle
        duration: Duration in seconds
        background_image: Optional path to background image
    """
    def _escape(text):
        return text.replace("'", "'\\''").replace(":", "\\:")

    # Split long titles into two lines at a sensible break point
    def _split_title(text, max_chars=28):
        if len(text) <= max_chars:
            return [text]
        # Try splitting at colon, dash, or midpoint word boundary
        for sep in [":", " - ", " — "]:
            if sep in text:
                parts = text.split(sep, 1)
                return [parts[0].strip(), parts[1].strip()]
        # Fall back to splitting at the word closest to midpoint
        words = text.split()
        mid = len(text) // 2
        best_i, best_dist = 0, len(text)
        pos = 0
        for i, w in enumerate(words):
            pos += len(w) + 1
            if abs(pos - mid) < best_dist:
                best_dist = abs(pos - mid)
                best_i = i + 1
        return [" ".join(words[:best_i]), " ".join(words[best_i:])]

    title_lines = _split_title(title_text)
    sub_escaped = _escape(subtitle_text)

    if background_image and os.path.exists(background_image):
        # Use image background with dark overlay + still (no zoompan for speed)
        vf = (
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
            f"crop={WIDTH}:{HEIGHT},"
            f"colorlevels=rimax=0.25:gimax=0.25:bimax=0.25"
        )
        # Draw each title line centered, stacked vertically
        # Line 1 positioned above center, line 2 at center
        n_lines = len(title_lines)
        for li, line in enumerate(title_lines):
            line_esc = _escape(line)
            if n_lines == 1:
                y_expr = "(h-text_h)/2-40"
            else:
                # Two lines: first at center-70, second at center-10
                y_expr = f"(h-text_h)/2-{70 - li * 60}"
            vf += (
                f",drawtext=text='{line_esc}'"
                f":fontfile={FONT}:fontsize=64:fontcolor=white"
                f":alpha='if(lt(t,0.5),0,if(lt(t,2),(t-0.5)/1.5,if(gt(t,{duration-1.5}),({duration}-t)/1.5,1)))'"
                f":x=(w-text_w)/2:y={y_expr}"
            )
        if subtitle_text:
            sub_y = "(h-text_h)/2+50" if n_lines == 1 else "(h-text_h)/2+60"
            vf += (
                f",drawtext=text='{sub_escaped}'"
                f":fontfile={FONT}:fontsize=32:fontcolor=white"
                f":alpha='if(lt(t,1.5),0,if(lt(t,3),(t-1.5)/1.5,if(gt(t,{duration-1.5}),({duration}-t)/1.5,1)))'"
                f":x=(w-text_w)/2:y={sub_y}"
            )
        vf += ",format=yuv420p"

        args = [
            "-loop", "1", "-i", background_image,
            "-t", str(duration),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "ultrafast",
            "-b:v", VIDEO_BITRATE, "-pix_fmt", "yuv420p",
            "-r", str(FPS),
            output_path,
        ]
    else:
        # Fallback: solid dark background
        vf = ""
        for li, line in enumerate(title_lines):
            line_esc = _escape(line)
            if li > 0:
                vf += ","
            n_lines = len(title_lines)
            if n_lines == 1:
                y_expr = "(h-text_h)/2-40"
            else:
                y_expr = f"(h-text_h)/2-{70 - li * 60}"
            vf += (
                f"drawtext=text='{line_esc}'"
                f":fontfile={FONT}:fontsize=64:fontcolor=white@0.9"
                f":x=(w-text_w)/2:y={y_expr}"
            )
        if subtitle_text:
            vf += (
                f",drawtext=text='{sub_escaped}'"
                f":fontfile={FONT}:fontsize=32:fontcolor=white@0.6"
                f":x=(w-text_w)/2:y=(h-text_h)/2+50"
            )

        args = [
            "-f", "lavfi",
            "-i", f"color=c=0x0a0a14:s={WIDTH}x{HEIGHT}:d={duration}:r={FPS}",
            "-vf", vf,
            "-c:v", "libx264", "-preset", "fast",
            "-b:v", VIDEO_BITRATE, "-pix_fmt", "yuv420p",
            output_path,
        ]

    _run_ffmpeg(args)
    return output_path


def generate_srt(scenes_narration, scene_durations, output_path, title_duration=8.0,
                  words_per_line=6, max_lines=2):
    """Generate an SRT subtitle file from scene narrations and timing."""
    def _format_srt_time(seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    srt_blocks = []
    block_idx = 1
    current_time = title_duration

    for scene_idx, (narration, scene_dur) in enumerate(zip(scenes_narration, scene_durations)):
        words = narration.replace("...", " ... ").split()
        total_words = len(words)
        if total_words == 0:
            current_time += scene_dur
            continue

        time_per_word = scene_dur / total_words
        max_words_per_block = words_per_line * max_lines
        i = 0
        while i < total_words:
            chunk_words = words[i:i + max_words_per_block]
            chunk_word_count = len(chunk_words)

            start = current_time + i * time_per_word
            end = current_time + (i + chunk_word_count) * time_per_word
            end = max(end, start + 1.5)
            end = min(end, current_time + scene_dur)

            text_words = chunk_words
            if len(text_words) > words_per_line:
                mid = len(text_words) // 2
                line1 = " ".join(text_words[:mid])
                line2 = " ".join(text_words[mid:])
                text = f"{line1}\n{line2}"
            else:
                text = " ".join(text_words)

            srt_blocks.append(
                f"{block_idx}\n"
                f"{_format_srt_time(start)} --> {_format_srt_time(end)}\n"
                f"{text}\n"
            )
            block_idx += 1
            i += chunk_word_count

        current_time += scene_dur

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_blocks))

    print(f"SRT generated: {block_idx - 1} subtitle blocks -> {output_path}")
    return output_path


def burn_subtitles(video_path, srt_path, output_path):
    """Burn SRT subtitles into video with styled text."""
    style = (
        "FontName=DejaVu Sans Bold,"
        "FontSize=22,"
        "PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,"
        "BackColour=&H80000000,"
        "Outline=2,"
        "Shadow=1,"
        "MarginV=50,"
        "Alignment=2,"
        "BorderStyle=3"
    )

    srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")

    args = [
        "-i", video_path,
        "-vf", f"subtitles='{srt_escaped}':force_style='{style}'",
        "-c:v", "libx264", "-preset", "fast",
        "-b:v", VIDEO_BITRATE, "-maxrate", VIDEO_BITRATE, "-bufsize", "8M",
        "-c:a", "copy",
        "-pix_fmt", "yuv420p",
        output_path,
    ]
    _run_ffmpeg(args, timeout=1200)
    print(f"Subtitles burned in -> {output_path}")
    return output_path


# Ken Burns effect rotation
EFFECTS_CYCLE = [
    # All "still" — crossfades between scenes provide visual movement.
    # zoompan effects took 40-60s per scene on this 2-core server.
    "still", "still", "still", "still",
    "still", "still", "still", "still",
]


def assemble_sleep_video(scenes, narration_path, output_path,
                         bg_music_path=None, title=None, subtitle=None,
                         title_image=None, srt_path=None,
                         audio_pre_mixed=False):
    """Assemble a full sleep video from scenes, narration, and optional music.

    Args:
        scenes: List of dicts with keys:
            - image: path to image file
            - duration: duration in seconds (optional — auto-calculated from narration)
            - effect: Ken Burns effect (optional — auto-cycled)
        narration_path: Path to full narration audio (single file or will be concat'd)
        output_path: Final output video path
        bg_music_path: Optional ambient background music to mix under narration
        title: Optional title card text
        subtitle: Optional subtitle for title card
        title_image: Optional background image for title card
        srt_path: Optional SRT file path — burns subtitles into the final video
        audio_pre_mixed: If True, audio is already padded/mixed. Skip audio
            processing and subtract title duration for scene calculation.

    Returns:
        output_path
    """
    # Guard: assembly takes 5-20 min and blocks the Claude session if called inline.
    # This function must only be called via sleep_interactive.py, which runs as a
    # detached background worker and delivers the result to Telegram automatically.
    if not os.environ.get('__SLP_WORKER_ACTIVE'):
        raise RuntimeError(
            'assemble_sleep_video() cannot be called inline — it blocks the session. '
            'Use: python3 /root/.openclaw/workspace/lib/sleep_interactive.py assemble <project_dir>'
        )

    tmpdir = tempfile.mkdtemp(prefix="sleep_video_")
    print(f"Working directory: {tmpdir}")

    # Get total narration duration to split evenly across scenes
    total_duration = get_audio_duration(narration_path)
    n_scenes = len(scenes)

    # If audio is pre-mixed (already padded with title silence + bg music),
    # subtract title duration so scenes are sized to narration only.
    if audio_pre_mixed and title:
        title_padding = 8.0
        total_duration = total_duration - title_padding
        print(f"Audio pre-mixed: subtracting {title_padding}s title padding -> {total_duration:.1f}s for scenes")

    # Calculate per-scene duration (evenly split if not specified)
    scene_durations = []
    specified_total = 0
    unspecified_count = 0
    for scene in scenes:
        if "duration" in scene and scene["duration"]:
            scene_durations.append(scene["duration"])
            specified_total += scene["duration"]
        else:
            scene_durations.append(None)
            unspecified_count += 1

    # Distribute remaining time to unspecified scenes
    if unspecified_count > 0:
        remaining = total_duration - specified_total
        per_scene = max(15.0, remaining / unspecified_count)  # min 15s per scene
        scene_durations = [d if d else per_scene for d in scene_durations]

    # Account for crossfade time loss and title card when calculating durations.
    # Each crossfade eats CROSSFADE_DURATION seconds from the total video length.
    # With a title card, total clips = n_scenes + 1, so crossfades = n_scenes.
    # Without title card, crossfades = n_scenes - 1.
    title_dur = 8.0 if title else 0.0
    n_crossfades = n_scenes if title else max(0, n_scenes - 1)
    crossfade_loss = n_crossfades * CROSSFADE_DURATION

    # Target: video duration after crossfade = title_dur + narration_dur
    # So raw scene time needed = (title_dur + narration_dur) - title_dur + crossfade_loss
    #                          = narration_dur + crossfade_loss
    target_scene_time = total_duration + crossfade_loss

    total_scene_dur = sum(scene_durations)
    if abs(total_scene_dur - target_scene_time) > 1.0:
        ratio = target_scene_time / total_scene_dur
        scene_durations = [d * ratio for d in scene_durations]

    print(f"Total narration: {total_duration:.1f}s across {n_scenes} scenes")
    print(f"Title card: {title_dur:.0f}s | Crossfade loss: {crossfade_loss:.0f}s | Target video: {title_dur + total_duration:.0f}s")

    # Generate scene clips
    clips = []
    title_clip = None

    if title:
        title_path = os.path.join(tmpdir, "title_card.mp4")
        add_title_card(title_path, title, subtitle or "",
                       background_image=title_image)
        title_clip = title_path
        print("Title card generated")

    for i, scene in enumerate(scenes):
        image = scene["image"]
        duration = scene_durations[i]
        effect = scene.get("effect", EFFECTS_CYCLE[i % len(EFFECTS_CYCLE)])

        clip_path = os.path.join(tmpdir, f"scene_{i:03d}.mp4")
        print(f"Scene {i + 1}/{n_scenes}: {effect} for {duration:.1f}s — {os.path.basename(image)}")

        image_to_scene(image, clip_path, duration=duration, effect=effect)
        clips.append(clip_path)

    # Prepend title card if present
    if title_clip:
        clips.insert(0, title_clip)

    # Concatenate all clips with crossfade
    print("Concatenating scenes with crossfade...")
    video_path = os.path.join(tmpdir, "video_no_audio.mp4")
    concatenate_with_crossfade(clips, video_path)

    # Calculate title card duration for audio delay
    title_dur = 8.0 if title else 0.0

    # If audio is already mixed/padded by the caller, use it directly
    if audio_pre_mixed:
        print("Audio pre-mixed by caller -- skipping padding/mixing")
        final_audio = narration_path
    elif bg_music_path and os.path.exists(bg_music_path):
        print("Mixing narration with background music...")
        mixed_audio = os.path.join(tmpdir, "mixed_audio.aac")
        mix_audio(narration_path, bg_music_path, mixed_audio,
                  title_duration=title_dur)
        final_audio = mixed_audio
    elif title_dur > 0:
        # No bg music but title card exists — prepend silence so narration
        # doesn't play over the title card
        print(f"Padding narration with {title_dur}s silence for title card...")
        padded_audio = os.path.join(tmpdir, "padded_narration.mp3")
        prepend_silence(narration_path, padded_audio, title_dur)
        final_audio = padded_audio
    else:
        final_audio = narration_path

    # Mux audio onto video
    print("Adding audio to video...")
    if srt_path and os.path.exists(srt_path):
        # Mux audio first to a temp file, then burn subtitles
        pre_sub_path = os.path.join(tmpdir, "pre_subtitles.mp4")
        add_audio_to_video(video_path, final_audio, pre_sub_path)
        print("Burning subtitles...")
        burn_subtitles(pre_sub_path, srt_path, output_path)
    else:
        add_audio_to_video(video_path, final_audio, output_path)

    # Get final file size
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    final_dur = get_audio_duration(output_path)
    print(f"\nDone! {output_path}")
    print(f"Duration: {final_dur / 60:.1f} minutes | Size: {size_mb:.0f} MB")

    return output_path


if __name__ == "__main__":
    import sys
    print("Sleep video assembly engine loaded.")
    ffmpeg_ver = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    print(f"FFmpeg: {ffmpeg_ver.stdout.split(chr(10))[0]}")
    print(f"Output format: {WIDTH}x{HEIGHT} @ {FPS}fps")
    print(f"Ken Burns effects: {', '.join(set(EFFECTS_CYCLE))}")
    print(f"Crossfade duration: {CROSSFADE_DURATION}s")
    print(f"\nUsage: Import and call assemble_sleep_video()")

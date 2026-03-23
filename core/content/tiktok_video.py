"""TikTok video assembly using FFmpeg — v6 with Retell patterns.

Creates vertical (1080x1920) videos from images, video clips, voiceovers,
and text overlays. Uses blurred background compositing, hook text with
fade alpha, and TikTok-optimized bitrate encoding.
"""

import json
import os
import subprocess
import tempfile


# TikTok specs (from Retell platform presets)
WIDTH = 1080
HEIGHT = 1920
FPS = 30
VIDEO_BITRATE = "8M"
AUDIO_BITRATE = "192k"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
BLUR_SIGMA = 50


def _run_ffmpeg(args, timeout=300):
    """Run an ffmpeg command and return the result."""
    cmd = ["ffmpeg", "-y"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error: {result.stderr[-500:]}")
    return result


def get_audio_duration(audio_path):
    """Get duration of an audio file in seconds."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", audio_path],
        capture_output=True, text=True, timeout=30,
    )
    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


def _blurred_bg_filter():
    """Retell-style blurred background: scale up to cover, crop, blur, overlay sharp center."""
    return (
        f"split[bg][fg];"
        f"[bg]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,"
        f"crop={WIDTH}:{HEIGHT},gblur=sigma={BLUR_SIGMA}[blurred];"
        f"[fg]scale={WIDTH}:-1:force_original_aspect_ratio=decrease[sharp];"
        f"[blurred][sharp]overlay=(W-w)/2:(H-h)/2,format=yuv420p"
    )


def image_to_clip(image_path, output_path, duration=5.0, zoom=False, blurred_bg=True):
    """Convert a single image to a video clip.

    Args:
        blurred_bg: Use Retell-style blurred background instead of black bars.
        zoom: Ken Burns zoom effect.
    """
    args = ["-loop", "1", "-i", image_path, "-t", str(duration)]

    if zoom:
        filter_str = (
            f"scale=8000:-1,"
            f"zoompan=z='min(zoom+0.0005,1.05)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
            f":d={int(duration * FPS)}:s={WIDTH}x{HEIGHT}:fps={FPS},"
            f"format=yuv420p"
        )
    elif blurred_bg:
        filter_str = _blurred_bg_filter()
    else:
        filter_str = (
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2,format=yuv420p"
        )

    args += ["-vf", filter_str, "-c:v", "libx264", "-preset", "fast",
             "-b:v", VIDEO_BITRATE, "-maxrate", VIDEO_BITRATE, "-bufsize", "16M",
             "-r", str(FPS), "-pix_fmt", "yuv420p", output_path]
    _run_ffmpeg(args)
    return output_path


def scale_video_clip(input_path, output_path, blurred_bg=True):
    """Scale a video clip to TikTok dimensions with blurred background."""
    if blurred_bg:
        vf = _blurred_bg_filter()
    else:
        vf = (
            f"scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease,"
            f"pad={WIDTH}:{HEIGHT}:(ow-iw)/2:(oh-ih)/2,setsar=1,format=yuv420p"
        )
    args = [
        "-i", input_path,
        "-vf", vf,
        "-c:v", "libx264", "-preset", "fast",
        "-b:v", VIDEO_BITRATE, "-maxrate", VIDEO_BITRATE, "-bufsize", "16M",
        "-r", str(FPS), "-an", "-pix_fmt", "yuv420p", output_path,
    ]
    _run_ffmpeg(args)
    return output_path


def _escape_drawtext(text):
    """Escape text for ffmpeg drawtext filter."""
    return text.replace("'", "'\\''").replace(":", "\\:").replace("\\", "\\\\\\\\")


def add_text_overlay(input_path, output_path, text, position="center",
                     fontsize=56, fontcolor="white", style="border",
                     box_opacity=0.6, start_time=0, end_time=None):
    """Add text overlay to a video clip.

    Args:
        position: "top", "center", "bottom", or (x, y) tuple
        style: "border" (Retell-style black outline) or "box" (semi-transparent box)
    """
    text_escaped = _escape_drawtext(text)

    if position == "top":
        x, y = "(w-text_w)/2", f"{int(HEIGHT * 0.08)}"
    elif position == "bottom":
        x, y = "(w-text_w)/2", f"{int(HEIGHT * 0.82)}"
    elif position == "center":
        x, y = "(w-text_w)/2", "(h-text_h)/2"
    elif isinstance(position, tuple):
        x, y = str(position[0]), str(position[1])
    else:
        x, y = "(w-text_w)/2", "(h-text_h)/2"

    drawtext = (
        f"drawtext=text='{text_escaped}':fontfile={FONT}"
        f":fontsize={fontsize}:fontcolor={fontcolor}:x={x}:y={y}"
    )

    if style == "border":
        drawtext += ":borderw=3:bordercolor=black"
    else:
        drawtext += f":box=1:boxcolor=black@{box_opacity}:boxborderw=12"

    if end_time is not None:
        drawtext += f":enable='between(t,{start_time},{end_time})'"
    elif start_time > 0:
        drawtext += f":enable='gte(t,{start_time})'"

    args = ["-i", input_path, "-vf", drawtext,
            "-c:v", "libx264", "-preset", "fast",
            "-b:v", VIDEO_BITRATE, "-maxrate", VIDEO_BITRATE, "-bufsize", "16M",
            "-c:a", "copy", "-pix_fmt", "yuv420p", output_path]
    _run_ffmpeg(args)
    return output_path


def add_hook_text(input_path, output_path, text, fade_in=0.5, hold_start=1.0,
                  hold_end=3.0, fade_out=3.5, fontsize=52, fontcolor="white"):
    """Add Retell-style hook text with fade-in/fade-out alpha.

    Text fades in, holds, then fades out. Positioned at 15% from top, centered.
    """
    text_escaped = _escape_drawtext(text)
    alpha = (
        f"if(lt(t\\,{hold_start})\\,t-{fade_in}\\,"
        f"if(lt(t\\,{hold_end})\\,1\\,{fade_out}-t))"
    )
    drawtext = (
        f"drawtext=text='{text_escaped}':fontfile={FONT}"
        f":fontsize={fontsize}:fontcolor={fontcolor}"
        f":borderw=3:bordercolor=black"
        f":x=(w-text_w)/2:y=h*0.15"
        f":enable='between(t,{fade_in},{fade_out})'"
        f":alpha='{alpha}'"
    )
    args = ["-i", input_path, "-vf", drawtext,
            "-c:v", "libx264", "-preset", "fast",
            "-b:v", VIDEO_BITRATE, "-maxrate", VIDEO_BITRATE, "-bufsize", "16M",
            "-c:a", "copy", "-pix_fmt", "yuv420p", output_path]
    _run_ffmpeg(args)
    return output_path


def concatenate_clips(clip_paths, output_path, transition="fade", fade_duration=0.3):
    """Concatenate multiple video clips into one video.

    Args:
        clip_paths: List of video file paths
        output_path: Output video path
        transition: "none" or "fade"
        fade_duration: Duration of crossfade in seconds
    """
    if transition == "none" or len(clip_paths) == 1:
        # Simple concat
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            for clip in clip_paths:
                f.write(f"file '{clip}'\n")
            list_file = f.name
        args = ["-f", "concat", "-safe", "0", "-i", list_file,
                "-c:v", "libx264", "-preset", "fast",
                "-b:v", VIDEO_BITRATE, "-maxrate", VIDEO_BITRATE, "-bufsize", "16M",
                "-pix_fmt", "yuv420p", output_path]
        _run_ffmpeg(args)
        os.unlink(list_file)
    else:
        # Crossfade between clips
        inputs = []
        for clip in clip_paths:
            inputs += ["-i", clip]

        # Build xfade filter chain
        filter_parts = []
        current = "[0:v]"
        for i in range(1, len(clip_paths)):
            next_label = f"[v{i}]" if i < len(clip_paths) - 1 else "[vout]"
            offset = i * 4 - fade_duration * i  # Approximate offset based on ~4s clips
            filter_parts.append(
                f"{current}[{i}:v]xfade=transition=fade:duration={fade_duration}:offset={offset:.1f}{next_label}"
            )
            current = next_label if i < len(clip_paths) - 1 else ""

        # Fallback to simple concat if xfade gets too complex
        if len(clip_paths) > 6:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                for clip in clip_paths:
                    f.write(f"file '{clip}'\n")
                list_file = f.name
            args = ["-f", "concat", "-safe", "0", "-i", list_file,
                    "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                    "-pix_fmt", "yuv420p", output_path]
            _run_ffmpeg(args)
            os.unlink(list_file)
        else:
            filter_str = ";".join(filter_parts)
            args = inputs + ["-filter_complex", filter_str, "-map", "[vout]",
                            "-c:v", "libx264", "-preset", "fast", "-crf", "23",
                            "-pix_fmt", "yuv420p", output_path]
            _run_ffmpeg(args)

    return output_path


def add_audio(video_path, audio_path, output_path, audio_volume=1.0):
    """Add audio track to a video. Trims audio or video to match the shorter one."""
    args = [
        "-i", video_path, "-i", audio_path,
        "-c:v", "copy",
        "-filter:a", f"volume={audio_volume}",
        "-c:a", "aac", "-b:a", AUDIO_BITRATE,
        "-shortest",
        output_path,
    ]
    _run_ffmpeg(args)
    return output_path


def assemble_tiktok(scenes, voiceover_path, output_path, add_captions=True,
                    hook_text=None, blurred_bg=True):
    """Assemble a full TikTok video from scenes — v6 with Retell patterns.

    Args:
        scenes: List of dicts with keys:
            - media: path to image or video file
            - type: "image" or "video"
            - duration: duration in seconds (for images, ignored for video)
            - text: optional text overlay
            - text_position: "top", "center", "bottom" (default "bottom")
            - text_style: "border" or "box" (default "border")
            - zoom: bool, Ken Burns effect for images (default False)
        voiceover_path: Path to voiceover audio file
        output_path: Final output video path
        add_captions: Whether to add text overlays from scene data
        hook_text: Optional hook text that fades in/out at the start
        blurred_bg: Use Retell blurred background compositing
    """
    tmpdir = tempfile.mkdtemp(prefix="tiktok_")
    clips = []

    # If we have voiceover, calculate per-scene duration
    if voiceover_path and os.path.exists(voiceover_path):
        total_audio = get_audio_duration(voiceover_path)
        n_scenes = len(scenes)
        default_duration = total_audio / n_scenes
    else:
        default_duration = 4.0

    for i, scene in enumerate(scenes):
        media = scene["media"]
        media_type = scene.get("type", "image")
        duration = scene.get("duration", default_duration)
        text = scene.get("text", "")
        text_pos = scene.get("text_position", "bottom")
        text_style = scene.get("text_style", "border")
        zoom = scene.get("zoom", False)

        clip_path = os.path.join(tmpdir, f"clip_{i:03d}.mp4")

        if media_type == "image":
            image_to_clip(media, clip_path, duration=duration, zoom=zoom,
                          blurred_bg=blurred_bg)
        else:
            scale_video_clip(media, clip_path, blurred_bg=blurred_bg)

        # Add text overlay if provided
        if text and add_captions:
            text_clip = os.path.join(tmpdir, f"clip_{i:03d}_text.mp4")
            add_text_overlay(clip_path, text_clip, text, position=text_pos,
                             fontsize=48, style=text_style)
            clips.append(text_clip)
        else:
            clips.append(clip_path)

    # Concatenate all clips
    concat_path = os.path.join(tmpdir, "concat.mp4")
    concatenate_clips(clips, concat_path, transition="none")

    # Add hook text with fade alpha to the first few seconds
    if hook_text:
        hook_path = os.path.join(tmpdir, "hooked.mp4")
        add_hook_text(concat_path, hook_path, hook_text)
        concat_path = hook_path

    # Add voiceover
    if voiceover_path and os.path.exists(voiceover_path):
        add_audio(concat_path, voiceover_path, output_path)
    else:
        import shutil
        shutil.copy2(concat_path, output_path)

    return output_path


if __name__ == "__main__":
    print("TikTok video assembly library loaded.")
    print(f"FFmpeg: {subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True).stdout.split(chr(10))[0]}")
    print(f"Output format: {WIDTH}x{HEIGHT} @ {FPS}fps")

"""Interactive sleep video pipeline — step-by-step with approval gates.

Instead of running everything at once, this breaks the pipeline into
discrete steps that save state to a project directory. Between steps,
outputs are sent to Telegram for review/approval.

Workflow:
    1. generate_script() → saves script.json, sends to Telegram for review
    2. generate_voice() → generates narration, sends audio to Telegram
    3. generate_images() → generates images, sends gallery to Telegram
    4. select_music() → picks royalty-free bg music based on genre (replaces generate_ambient)
    5. assemble() → builds final video with proper audio mixing (voice > music)

Each step reads/writes to a project directory, so you can:
- Edit the script JSON manually before generating voice
- Regenerate a single scene's image without redoing everything
- Swap the voice without regenerating images
- Resume from any step if something fails

Usage (from Cortana/Claude Code):
    from lib.sleep_interactive import SleepProject

    # Step 1: Create project + generate script
    project = SleepProject.create("A moonlit forest walk", duration=3, style="nature")
    # → sends script to Telegram for review

    # Step 2: After Ben approves/edits script
    project.generate_voice(voice="cortana")
    # → sends narration audio to Telegram

    # Step 3: After Ben approves voice
    project.generate_images()
    # → sends images to Telegram

    # Step 3b: Redo a specific scene's image
    project.regenerate_image(scene_index=3, custom_prompt="A misty lake at dawn...")

    # Step 4: Select background music (auto-picks based on style)
    project.select_music()  # or project.select_music("choir") to override

    # Step 5: After all approved, assemble (proper audio mixing built in)
    project.assemble()
    # → sends final video to Telegram
"""

import json
import os
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

from elevenlabs import text_to_speech, VOICES
from sleep_video import (
    assemble_sleep_video, concat_audio_files, get_audio_duration,
    mix_audio, prepend_silence, EFFECTS_CYCLE, BG_MUSIC_VOLUME,
)
from imagegen import generate_image_gemini

OUTPUT_DIR = "/root/.openclaw/workspace/output/sleep-videos"
ASSETS_DIR = "/root/.openclaw/workspace/assets/ambient"
MUSIC_DIR = "/root/.openclaw/workspace/assets/music"
DEFAULT_VOICE = "cortana"
DEFAULT_IMAGE_MODEL = "imagen-4.0-generate-001"
ELEVENLABS_CHUNK_SIZE = 4500
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Background music tracks — royalty-free, genre-matched
# Attribution required for Scott Buckley tracks (CC-BY 4.0)
MUSIC_TRACKS = {
    "piano": {
        "file": "piano-ambient-pads.mp3",
        "name": "Sleep by Scott Buckley",
        "attribution": '"Sleep" by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au',
        "styles": ["calm_narrative", "meditation", "nature"],
    },
    "choir": {
        "file": "choir-harp-ethereal.mp3",
        "name": "Frozen Star by Kevin MacLeod",
        "attribution": '"Frozen Star" by Kevin MacLeod (incompetech.com) - released under CC-BY 3.0.',
        "styles": ["stoic"],
    },
    "strings": {
        "file": "strings-drone-hiraeth.mp3",
        "name": "Hiraeth by Scott Buckley",
        "attribution": '"Hiraeth" by Scott Buckley - released under CC-BY 4.0. www.scottbuckley.com.au',
        "styles": ["dramatic", "epic"],
    },
}

# Music volume: low enough to sit under narration without overpowering.
# 0.08 = roughly -22dB below full scale. Combined with loudnorm on the
# narration track, this keeps the voice clearly dominant.
MUSIC_VOLUME_DEFAULT = 0.08


def _select_music(style):
    """Select the best background music track for a given video style.

    Returns (file_path, track_info) or (None, None) if no match.
    """
    # Direct style match
    for key, info in MUSIC_TRACKS.items():
        if style in info["styles"]:
            path = os.path.join(MUSIC_DIR, info["file"])
            if os.path.exists(path):
                return path, info
    # Fallback to piano (default)
    piano = MUSIC_TRACKS["piano"]
    path = os.path.join(MUSIC_DIR, piano["file"])
    if os.path.exists(path):
        return path, piano
    return None, None


def _load_env():
    env = {}
    with open("/root/.openclaw/.env") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                if line.startswith("export "):
                    line = line[7:]
                key, val = line.split("=", 1)
                env[key.strip()] = val.strip().strip('"').strip("'")
    return env


def _send_telegram(text, topic=22):
    """Send a text message to Telegram."""
    env = _load_env()
    payload = json.dumps({
        "chat_id": env.get("TELEGRAM_CHAT_ID", ""),
        "text": text,
        "message_thread_id": topic,
        "disable_web_page_preview": True,
        "parse_mode": "HTML",
    }).encode()
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{env['TELEGRAM_BOT_TOKEN']}/sendMessage",
        data=payload, headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read()).get("ok", False)
    except Exception as e:
        print(f"Telegram send failed: {e}")
        return False


def _send_telegram_audio(file_path, caption="", topic=22):
    """Send an audio file to Telegram."""
    import requests
    env = _load_env()
    with open(file_path, "rb") as f:
        resp = requests.post(
            f"https://api.telegram.org/bot{env['TELEGRAM_BOT_TOKEN']}/sendAudio",
            data={"chat_id": env["TELEGRAM_CHAT_ID"], "message_thread_id": topic, "caption": caption},
            files={"audio": (os.path.basename(file_path), f, "audio/mpeg")},
            timeout=120,
        )
    return resp.json().get("ok", False)


def _send_telegram_photo(file_path, caption="", topic=22):
    """Send a photo to Telegram."""
    import requests
    env = _load_env()
    with open(file_path, "rb") as f:
        resp = requests.post(
            f"https://api.telegram.org/bot{env['TELEGRAM_BOT_TOKEN']}/sendPhoto",
            data={"chat_id": env["TELEGRAM_CHAT_ID"], "message_thread_id": topic, "caption": caption},
            files={"photo": (os.path.basename(file_path), f, "image/png")},
            timeout=60,
        )
    return resp.json().get("ok", False)


def _send_telegram_video(file_path, caption="", topic=22):
    """Send a video file to Telegram."""
    import requests
    env = _load_env()
    with open(file_path, "rb") as f:
        resp = requests.post(
            f"https://api.telegram.org/bot{env['TELEGRAM_BOT_TOKEN']}/sendVideo",
            data={
                "chat_id": env["TELEGRAM_CHAT_ID"],
                "message_thread_id": topic,
                "caption": caption,
                "supports_streaming": "true",
            },
            files={"video": (os.path.basename(file_path), f, "video/mp4")},
            timeout=180,
        )
    return resp.json().get("ok", False)


def _get_gemini_key():
    env = _load_env()
    return env.get("GEMINI_API_KEY", os.environ.get("GEMINI_API_KEY", ""))


def _split_text(text, max_chars):
    """Split text at sentence boundaries."""
    sentences = text.replace("...", "\u2026").split(". ")
    sentences = [s.replace("\u2026", "...") for s in sentences]
    chunks, current = [], ""
    for sentence in sentences:
        candidate = current + sentence + ". " if current else sentence + ". "
        if len(candidate) > max_chars and current:
            chunks.append(current.strip())
            current = sentence + ". "
        else:
            current = candidate
    if current.strip():
        chunks.append(current.strip())
    return chunks


class SleepProject:
    """Manages a sleep video project with step-by-step approval gates."""

    def __init__(self, project_dir):
        self.project_dir = Path(project_dir)
        self.state_file = self.project_dir / "project_state.json"
        self.state = self._load_state()

    def _load_state(self):
        if self.state_file.exists():
            with open(self.state_file) as f:
                return json.load(f)
        return {"status": "new", "steps_completed": []}

    def _save_state(self):
        with open(self.state_file, "w") as f:
            json.dump(self.state, f, indent=2)

    @classmethod
    def create(cls, topic, duration=3, style="calm_narrative", num_scenes=None):
        """Create a new project and generate the script (Step 1).

        Args:
            topic: Story theme/topic
            duration: Target duration in minutes
            style: calm_narrative, meditation, stoic, nature
            num_scenes: Override scene count (default: auto)

        Returns:
            SleepProject instance with script generated
        """
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        project_dir = Path(OUTPUT_DIR) / f"sleep-{timestamp}"
        project_dir.mkdir(parents=True, exist_ok=True)

        project = cls(project_dir)
        project.state = {
            "status": "script_generated",
            "steps_completed": ["create"],
            "topic": topic,
            "duration": duration,
            "style": style,
            "created": timestamp,
        }

        # Generate script
        script = _generate_script(topic, duration, style, num_scenes)
        script_path = str(project_dir / "script.json")
        with open(script_path, "w") as f:
            json.dump(script, f, indent=2)

        project.state["script_path"] = script_path
        project.state["title"] = script["title"]
        project.state["num_scenes"] = len(script["scenes"])
        project._save_state()

        # Send script to Telegram for review
        _send_script_to_telegram(script, project_dir)

        print(f"Project created: {project_dir}")
        print(f"Script: {script['title']} — {len(script['scenes'])} scenes")
        print("Script sent to Telegram for review.")
        return project

    @classmethod
    def load(cls, project_dir):
        """Load an existing project."""
        project = cls(project_dir)
        if project.state["status"] == "new":
            raise ValueError(f"No project found at {project_dir}")
        return project

    @classmethod
    def latest(cls):
        """Load the most recent project."""
        projects = sorted(Path(OUTPUT_DIR).glob("sleep-*"))
        if not projects:
            raise ValueError("No projects found")
        return cls.load(projects[-1])

    def get_script(self):
        """Return the current script."""
        with open(self.state["script_path"]) as f:
            return json.load(f)

    def update_script(self, script):
        """Save an updated script (after manual edits)."""
        with open(self.state["script_path"], "w") as f:
            json.dump(script, f, indent=2)
        print("Script updated.")

    def update_scene(self, scene_index, narration=None, image_prompt=None, effect=None):
        """Update a specific scene's narration, image prompt, or effect."""
        script = self.get_script()
        scene = script["scenes"][scene_index]
        if narration is not None:
            scene["narration"] = narration
        if image_prompt is not None:
            scene["image_prompt"] = image_prompt
        if effect is not None:
            scene["effect"] = effect
        self.update_script(script)
        print(f"Scene {scene_index + 1} updated.")

    def generate_voice(self, voice=DEFAULT_VOICE, stability=0.7, similarity=0.8):
        """Step 2: Generate narration audio and send to Telegram for review."""
        script = self.get_script()
        audio_dir = self.project_dir / "audio"
        audio_dir.mkdir(exist_ok=True)

        audio_files = []
        for i, scene in enumerate(script["scenes"]):
            narration = scene["narration"]
            audio_path = str(audio_dir / f"narration_{i:03d}.mp3")

            if len(narration) > ELEVENLABS_CHUNK_SIZE:
                chunks = _split_text(narration, ELEVENLABS_CHUNK_SIZE)
                chunk_files = []
                for j, chunk in enumerate(chunks):
                    chunk_path = str(audio_dir / f"narration_{i:03d}_chunk_{j:02d}.mp3")
                    print(f"  Scene {i + 1} chunk {j + 1}/{len(chunks)}: {len(chunk)} chars")
                    text_to_speech(chunk, chunk_path, voice=voice,
                                   stability=stability, similarity_boost=similarity)
                    chunk_files.append(chunk_path)
                concat_audio_files(chunk_files, audio_path)
            else:
                print(f"Scene {i + 1}/{len(script['scenes'])}: {len(narration)} chars")
                text_to_speech(narration, audio_path, voice=voice,
                               stability=stability, similarity_boost=similarity)

            dur = get_audio_duration(audio_path)
            print(f"  Audio: {dur:.1f}s")
            audio_files.append(audio_path)

        # Concat all into full narration
        full_narration = str(self.project_dir / "full_narration.mp3")
        concat_audio_files(audio_files, full_narration)
        total_dur = get_audio_duration(full_narration)

        self.state["voice"] = voice
        self.state["narration_path"] = full_narration
        self.state["narration_duration"] = total_dur
        self.state["steps_completed"].append("voice")
        self.state["status"] = "voice_generated"
        self._save_state()

        # Send to Telegram
        _send_telegram(
            f"🎙 Narration generated — {total_dur:.0f}s ({total_dur/60:.1f} min)\n"
            f"Voice: {voice}\n\n"
            f"Sending full narration audio for review...",
        )
        _send_telegram_audio(full_narration, caption=f"Full narration — {total_dur:.0f}s | Voice: {voice}")

        print(f"Narration: {total_dur:.0f}s ({total_dur/60:.1f} min)")
        print("Audio sent to Telegram for review.")
        return full_narration

    def generate_images(self, model=DEFAULT_IMAGE_MODEL):
        """Step 3: Generate scene images one at a time, sending each to Telegram immediately.

        Auto-backgrounds itself — safe to call inline, will never block the session.
        """
        # Auto-background: spawn ourselves and return immediately
        if not os.environ.get('_SLEEP_IMGGEN_BG'):
            import time as _t
            log_path = f'/tmp/imggen-{os.path.basename(str(self.project_dir))}-{int(_t.time())}.log'
            cmd = ['python3', __file__, 'generate_images', str(self.project_dir), '--model', model]
            env = dict(os.environ)
            env['_SLEEP_IMGGEN_BG'] = '1'
            with open(log_path, 'w') as _log:
                proc = subprocess.Popen(
                    cmd, stdout=_log, stderr=_log,
                    env=env, start_new_session=True,
                )
            script = self.get_script()
            num_scenes = len(script["scenes"])
            _send_telegram(
                f'\U0001f5bc Generating {num_scenes} images in background (PID {proc.pid})\n'
                f'Sending each image to Telegram as it renders...',
            )
            print(f'Image gen backgrounded PID={proc.pid} log={log_path}')
            return log_path

        script = self.get_script()
        image_dir = self.project_dir / "images"
        image_dir.mkdir(exist_ok=True)

        num_scenes = len(script["scenes"])
        _send_telegram(f"\U0001f5bc Generating {num_scenes} scene images \u2014 sending each as it's ready...")

        image_files = []
        for i, scene in enumerate(script["scenes"]):
            prompt = scene["image_prompt"]
            image_path = str(image_dir / f"scene_{i:03d}.png")

            full_prompt = (
                f"{prompt}. "
                f"Cinematic 16:9 composition, soft warm lighting, "
                f"serene and peaceful atmosphere, high quality, photorealistic. "
                f"No people, no faces, no text."
            )

            print(f"Image {i + 1}/{num_scenes}: {prompt[:80]}...")

            try:
                generate_image_gemini(full_prompt, image_path, model=model, aspect_ratio="16:9")
            except Exception as e:
                print(f"  Failed ({e}), trying fallback...")
                try:
                    generate_image_gemini(full_prompt, image_path,
                                          model="gemini-2.5-flash-image", aspect_ratio="16:9")
                except Exception as e2:
                    print(f"  Fallback failed ({e2}), placeholder created")
                    _create_placeholder(image_path, f"Scene {i + 1}")

            image_files.append(image_path)

            # Send immediately after generating -- don't wait for all images
            caption = f"Scene {i + 1}/{num_scenes}: {scene['image_prompt'][:150]}"
            _send_telegram_photo(image_path, caption=caption)

        self.state["image_files"] = image_files
        self.state["image_model"] = model
        self.state["steps_completed"].append("images")
        self.state["status"] = "images_generated"
        self._save_state()

        _send_telegram(
            f"\u2705 All {num_scenes} images generated!\n\n"
            f"To redo any image, tell me the scene number and what to change.\n"
            f"When you're happy with all images, say 'approved' to continue!"
        )

        print(f"All {num_scenes} images generated and sent to Telegram.")
        return image_files

    def regenerate_image(self, scene_index, custom_prompt=None, model=DEFAULT_IMAGE_MODEL):
        """Redo a specific scene's image (after feedback)."""
        script = self.get_script()
        scene = script["scenes"][scene_index]

        prompt = custom_prompt or scene["image_prompt"]
        full_prompt = (
            f"{prompt}. "
            f"Cinematic 16:9 composition, soft warm lighting, "
            f"serene and peaceful atmosphere, high quality, photorealistic. "
            f"No people, no faces, no text."
        )

        image_path = str(self.project_dir / "images" / f"scene_{scene_index:03d}.png")
        print(f"Regenerating scene {scene_index + 1}...")

        generate_image_gemini(full_prompt, image_path, model=model, aspect_ratio="16:9")

        # If custom prompt was provided, save it to the script
        if custom_prompt:
            scene["image_prompt"] = custom_prompt
            self.update_script(script)

        # Send to Telegram
        _send_telegram_photo(image_path, caption=f"🔄 Scene {scene_index + 1} regenerated")

        print(f"Scene {scene_index + 1} regenerated and sent to Telegram.")
        return image_path

    def select_music(self, override_track=None):
        """Step 4: Select background music from royalty-free library.

        Automatically picks the best track based on video style, or
        accepts a manual override ("piano", "choir", or "strings").

        No ElevenLabs API calls needed — uses pre-downloaded tracks.
        """
        style = self.state.get("style", "calm_narrative")

        if override_track and override_track in MUSIC_TRACKS:
            info = MUSIC_TRACKS[override_track]
            music_path = os.path.join(MUSIC_DIR, info["file"])
        else:
            music_path, info = _select_music(style)

        if not music_path or not os.path.exists(music_path):
            print("ERROR: No music track found! Check assets/music/ directory.")
            return None

        self.state["music_path"] = music_path
        self.state["music_track"] = info["name"]
        self.state["music_attribution"] = info["attribution"]
        if "ambient" not in self.state["steps_completed"]:
            self.state["steps_completed"].append("ambient")
        self._save_state()

        _send_telegram(
            f"🎵 Background music selected: <b>{info['name']}</b>\n"
            f"Style: {style} → {os.path.basename(music_path)}\n\n"
            f"Attribution: {info['attribution']}\n\n"
            f"Ready to assemble! Say 'go' when ready."
        )

        print(f"Music selected: {info['name']} ({music_path})")
        return music_path

    def generate_ambient(self, prompt_text, duration_seconds=30, num_clips=4):
        """Step 4 (legacy): Generate ambient audio using ElevenLabs sound generation.

        DEPRECATED — use select_music() instead for royalty-free background music.
        Kept for backward compatibility.

        Args:
            prompt_text: Description of desired ambient sound
            duration_seconds: Duration per clip (max 22 for ElevenLabs)
            num_clips: Number of clips to generate and crossfade
        """
        import subprocess

        env = _load_env()
        el_key = env.get("ELEVENLABS_API_KEY", "")

        ambient_dir = self.project_dir / "ambient"
        ambient_dir.mkdir(exist_ok=True)

        # Generate clips
        clip_paths = []
        for i in range(num_clips):
            clip_path = str(ambient_dir / f"ambient_{i:02d}.mp3")
            print(f"Generating ambient clip {i + 1}/{num_clips}...")

            data = json.dumps({
                "text": prompt_text,
                "duration_seconds": min(duration_seconds, 22),
                "prompt_influence": 0.5,
            }).encode()

            req = urllib.request.Request(
                "https://api.elevenlabs.io/v1/sound-generation",
                data=data,
                headers={"xi-api-key": el_key, "Content-Type": "application/json"},
            )
            resp = urllib.request.urlopen(req, timeout=60)
            with open(clip_path, "wb") as f:
                while True:
                    chunk = resp.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
            clip_paths.append(clip_path)

        # Crossfade clips together + normalize volume
        ambient_loop = str(ambient_dir / "ambient_loop.mp3")
        if len(clip_paths) == 1:
            # Just normalize the single clip
            subprocess.run([
                "ffmpeg", "-y", "-i", clip_paths[0],
                "-af", "loudnorm=I=-20:TP=-3:LRA=7,afade=t=in:st=0:d=3,afade=t=out:st=19:d=3",
                "-c:a", "libmp3lame", "-b:a", "192k", ambient_loop,
            ], capture_output=True, timeout=60)
        else:
            # Build crossfade filter
            inputs = []
            for p in clip_paths:
                inputs += ["-i", p]

            filter_parts = []
            current = "[0:a]"
            for i in range(1, len(clip_paths)):
                out = f"[a{i}]" if i < len(clip_paths) - 1 else "[aout]"
                filter_parts.append(f"{current}[{i}:a]acrossfade=d=3:c1=tri:c2=tri{out}")
                current = out if i < len(clip_paths) - 1 else ""

            fade_dur = duration_seconds * num_clips - 3 * (num_clips - 1) - 5
            filter_str = ";".join(filter_parts)
            filter_str += f",[aout]loudnorm=I=-20:TP=-3:LRA=7,afade=t=in:st=0:d=3,afade=t=out:st={max(1, fade_dur)}:d=5[out]"

            cmd = ["ffmpeg", "-y"] + inputs + [
                "-filter_complex", filter_str,
                "-map", "[out]", "-c:a", "libmp3lame", "-b:a", "192k", ambient_loop,
            ]
            subprocess.run(cmd, capture_output=True, timeout=120)

        self.state["ambient_path"] = ambient_loop
        self.state["steps_completed"].append("ambient")
        self._save_state()

        # Send to Telegram
        _send_telegram_audio(ambient_loop, caption=f"🌙 Ambient audio generated: {prompt_text[:100]}")

        print(f"Ambient audio saved: {ambient_loop}")
        return ambient_loop

    def assemble(self, music_volume=None):
        """Step 5: Assemble the final video from all approved assets.

        Audio mixing strategy:
        - Narration is loudness-normalized to -16 LUFS (broadcast standard)
        - Music volume is set to 0.08 (~-22dB) so it sits well underneath
        - Music fades in over 5s at video start, fades out over 5s at end
        - Music loops seamlessly if shorter than the video
        - Result: voice is always clearly dominant, music adds atmosphere

        Args:
            music_volume: Background music volume (0-1). Default uses MUSIC_VOLUME_DEFAULT (0.08).
        """
        import subprocess

        if music_volume is None:
            music_volume = MUSIC_VOLUME_DEFAULT

        # Auto-background: spawn ourselves and return immediately
        if not os.environ.get('_SLEEP_ASSEMBLY_BG'):
            import time as _t
            log_path = f'/tmp/assembly-{os.path.basename(str(self.project_dir))}-{int(_t.time())}.log'
            cmd = [
                'python3', __file__, 'assemble', str(self.project_dir),
                '--music-volume', str(music_volume),
            ]
            env = dict(os.environ)
            env['_SLEEP_ASSEMBLY_BG'] = '1'
            with open(log_path, 'w') as _log:
                proc = subprocess.Popen(
                    cmd, stdout=_log, stderr=_log,
                    env=env, start_new_session=True,
                )
            _send_telegram(
                f'\U0001f3ac Assembly started in background (PID {proc.pid})\n'
                f'Log: {log_path}\n'
                f"I'll send the video here when it's done — usually ~10 min.",
            )
            print(f'Assembly backgrounded PID={proc.pid} log={log_path}')
            return log_path

        script = self.get_script()
        narration_path = self.state["narration_path"]
        image_files = self.state.get("image_files", [])
        # Prefer music_path (from select_music), fall back to ambient_path (legacy)
        music_path = self.state.get("music_path") or self.state.get("ambient_path")

        if not image_files:
            # Auto-detect from images dir
            image_dir = self.project_dir / "images"
            image_files = sorted(str(p) for p in image_dir.glob("scene_*.png"))

        # Title card is 8 seconds — audio must account for this
        title_duration = 8.0

        # Mix narration with background music if available
        if music_path and os.path.exists(music_path):
            track_name = self.state.get("music_track", os.path.basename(music_path))
            print(f"Mixing narration with background music: {track_name}")
            print(f"  Music volume: {music_volume} (voice stays dominant)")
            mixed_audio = str(self.project_dir / "mixed_audio.aac")
            nar_dur = get_audio_duration(narration_path)
            total_dur = nar_dur + title_duration
            fade_out_start = max(1, total_dur - 5)

            # Audio mixing filter:
            # 1. Narration: normalize loudness to -16 LUFS, then delay by title_duration
            # 2. Music: loop, set to low volume, fade in/out at start/end
            # 3. Mix with amix, narration always on top
            cmd = [
                "ffmpeg", "-y",
                "-i", narration_path,
                "-stream_loop", "-1", "-i", music_path,
                "-filter_complex",
                # Normalize narration loudness, then delay for title card
                f"[0:a]loudnorm=I=-16:TP=-1.5:LRA=11,"
                f"adelay={int(title_duration * 1000)}|{int(title_duration * 1000)},"
                f"volume=1.0[narr];"
                # Music: low volume + gentle fade in/out
                f"[1:a]volume={music_volume},"
                f"afade=t=in:st=0:d=5,"
                f"afade=t=out:st={fade_out_start}:d=5[music];"
                # Mix: voice dominant, music underneath
                f"[narr][music]amix=inputs=2:duration=longest:dropout_transition=3,"
                f"alimiter=limit=0.95[out]",
                "-map", "[out]", "-c:a", "aac", "-b:a", "192k",
                "-t", str(total_dur), mixed_audio,
            ]
            subprocess.run(cmd, capture_output=True, timeout=600)
            final_audio = mixed_audio
        else:
            # No music — still need to pad narration for title card
            print(f"Padding narration with {title_duration}s silence for title card...")
            padded_audio = str(self.project_dir / "padded_narration.mp3")
            prepend_silence(narration_path, padded_audio, title_duration)
            final_audio = padded_audio

        # Build scene list for assembly
        scenes_for_assembly = []
        for i, scene in enumerate(script["scenes"]):
            scenes_for_assembly.append({
                "image": image_files[i],
                "effect": scene.get("effect", EFFECTS_CYCLE[i % len(EFFECTS_CYCLE)]),
            })


        # Generate a separate dark title card image
        title_image = str(self.project_dir / "images" / "title_card.png")
        title_prompt = (
            f"Dark cinematic background for a sleep story titled '{script['title']}'. "
            f"Very dark, muted tones. Deep navy, charcoal, dark forest green. "
            f"Subtle ambient details like faint stars, soft moonlight, or gentle mist. "
            f"No bright colors, no warm tones, no orange, no candlelight. "
            f"Ultra dark and calming. No text, no people, no faces."
        )
        try:
            print("Generating title card image...")
            generate_image_gemini(title_prompt, title_image, model=DEFAULT_IMAGE_MODEL, aspect_ratio="16:9")
        except Exception as e:
            print(f"Title card image failed ({e}), using dark background")
            title_image = None

        # Assemble video (no bg_music_path — we already mixed the audio)
        output_path = str(self.project_dir / "final.mp4")
        print("Assembling video...")
        assemble_sleep_video(
            scenes=scenes_for_assembly,
            narration_path=final_audio,
            output_path=output_path,
            title=script["title"],
            subtitle="Close your eyes... and drift away",
            title_image=title_image,
        )

        self.state["output_path"] = output_path
        self.state["steps_completed"].append("assemble")
        self.state["status"] = "complete"
        self._save_state()

        # Compress for Telegram if needed
        file_size = os.path.getsize(output_path) / (1024 * 1024)
        if file_size > 48:
            print("Compressing for Telegram...")
            compressed = str(self.project_dir / "final_compressed.mp4")
            subprocess.run([
                "ffmpeg", "-y", "-i", output_path,
                "-c:v", "libx264", "-crf", "26", "-preset", "fast",
                "-c:a", "aac", "-b:a", "160k", compressed,
            ], capture_output=True, timeout=600)
            send_path = compressed
        else:
            send_path = output_path

        # Send to Telegram
        dur = get_audio_duration(output_path)
        attribution = self.state.get("music_attribution", "")
        music_info = f"\n🎵 {self.state.get('music_track', 'N/A')}" if self.state.get("music_track") else ""
        _send_telegram_video(
            send_path,
            caption=(
                f"🎬 {script['title']}\n⏱ {dur:.0f}s | 1080p{music_info}\n\n"
                f"Final video ready for review!"
            ),
        )

        # Remind about attribution for YouTube description
        if attribution:
            _send_telegram(
                f"📋 <b>YouTube description attribution (required):</b>\n\n"
                f"{attribution}\n\n"
                f"Add this to the video description when uploading."
            )

        print(f"Video assembled: {output_path}")
        print(f"Duration: {dur:.0f}s | Size: {file_size:.0f} MB")
        if attribution:
            print(f"Music attribution: {attribution}")
        print("Sent to Telegram!")
        return output_path

    def status(self):
        """Print current project status."""
        print(f"Project: {self.project_dir}")
        print(f"Status: {self.state['status']}")
        print(f"Steps completed: {', '.join(self.state['steps_completed'])}")
        if "title" in self.state:
            print(f"Title: {self.state['title']}")
        if "narration_duration" in self.state:
            print(f"Narration: {self.state['narration_duration']:.0f}s")
        if "output_path" in self.state:
            print(f"Output: {self.state['output_path']}")
        return self.state


def _generate_script(topic, duration_minutes, style, num_scenes=None):
    """Generate script via Gemini."""
    key = _get_gemini_key()
    if not key:
        raise RuntimeError("GEMINI_API_KEY not found")

    if not num_scenes:
        num_scenes = max(8, duration_minutes)

    style_instructions = {
        "calm_narrative": (
            "Write in a calm, soothing narrative voice. Use gentle, flowing language. "
            "Describe sensory details — sounds, textures, warmth, light. "
            "Pace should be slow and meditative. Use pauses (indicated by '...'). "
            "The listener should feel like they're drifting through a peaceful dream."
        ),
        "meditation": (
            "Write as a guided meditation. Address the listener directly with 'you'. "
            "Include breathing cues ('take a deep breath...'), body scan elements, "
            "and visualization prompts. Pace should be very slow with many pauses."
        ),
        "stoic": (
            "Write as a philosophical bedtime reflection drawing on Stoic wisdom. "
            "Weave in ideas from Marcus Aurelius, Seneca, Epictetus naturally — "
            "don't name-drop, just embody the philosophy. Tone should be wise, "
            "warm, and reassuring. Help the listener release the day's worries."
        ),
        "nature": (
            "Write a vivid nature journey — a walk through forests, along streams, "
            "through meadows. Rich sensory detail — the sound of water, rustling leaves, "
            "distant birdsong. No plot needed, just gentle movement through a landscape. "
            "The listener should feel enveloped in nature."
        ),
    }

    prompt = f"""You are writing a sleep story script for a YouTube video. The video will be {duration_minutes} minutes long.

Topic: {topic}

Style: {style_instructions.get(style, style_instructions['calm_narrative'])}

Generate a script with exactly {num_scenes} scenes. Each scene will be displayed as a single image with slow Ken Burns camera movement while the narration plays.

IMPORTANT RULES:
- The narration should take approximately {duration_minutes} minutes to read aloud at a slow, calm pace (~100 words per minute for sleep content)
- That means roughly {duration_minutes * 100} words total across all scenes
- Distribute words roughly evenly across scenes
- Each scene's narration should flow naturally into the next
- Use ellipses (...) for natural pauses
- No loud or exciting moments — this is for falling asleep
- Start gently, build a peaceful atmosphere, and gradually become softer and more repetitive toward the end
- The final 2-3 scenes should be especially quiet and dreamlike

For each scene's image_prompt, describe a photorealistic, serene landscape or setting. The images should:
- Be cinematic, 16:9 aspect ratio compositions
- Use soft, warm lighting (golden hour, moonlight, candlelight, dawn)
- Feature calming colors (deep blues, soft purples, warm ambers, forest greens)
- NO people or faces
- NO text in the image
- Each image should be distinctly different but thematically connected

Return valid JSON in this exact format:
{{
    "title": "YouTube video title (include 'Sleep Story' or 'Bedtime Story')",
    "description": "YouTube description (2-3 sentences, include keywords for sleep content)",
    "tags": ["sleep story", "bedtime story", "relaxation", ...up to 10 relevant tags],
    "scenes": [
        {{
            "narration": "The full narration text for this scene...",
            "image_prompt": "Detailed image generation prompt for this scene's visual...",
            "effect": "one of: zoom_in, zoom_out, pan_left, pan_right, pan_up, pan_down"
        }}
    ]
}}

Return ONLY the JSON, no other text."""

    print(f"Generating script: {topic} ({duration_minutes} min, {num_scenes} scenes)...")

    from google import genai
    from google.genai import types

    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.8,
            max_output_tokens=16000,
        ),
    )

    text = response.text
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    script = json.loads(text.strip())
    print(f"Script generated: '{script['title']}' — {len(script['scenes'])} scenes")
    return script


def _send_script_to_telegram(script, project_dir):
    """Format and send script to Telegram for review."""
    # Count total words
    total_words = sum(len(s["narration"].split()) for s in script["scenes"])

    header = (
        f"📝 <b>SCRIPT FOR REVIEW</b>\n\n"
        f"<b>Title:</b> {script['title']}\n"
        f"<b>Scenes:</b> {len(script['scenes'])}\n"
        f"<b>Total words:</b> {total_words} (~{total_words // 100} min at sleep pace)\n"
        f"<b>Project:</b> {project_dir}\n\n"
        f"<b>Description:</b> {script['description']}\n\n"
        f"---\n\n"
    )
    _send_telegram(header)

    # Send each scene as a separate message
    for i, scene in enumerate(script["scenes"]):
        word_count = len(scene["narration"].split())
        msg = (
            f"<b>Scene {i + 1}/{len(script['scenes'])}</b> ({word_count} words, ~{word_count // 100} min)\n"
            f"<b>Effect:</b> {scene.get('effect', 'auto')}\n"
            f"<b>Image:</b> <i>{scene['image_prompt'][:200]}</i>\n\n"
            f"{scene['narration'][:800]}"
        )
        if len(scene['narration']) > 800:
            msg += f"\n\n<i>...({len(scene['narration']) - 800} more chars)</i>"
        _send_telegram(msg)

    _send_telegram(
        "👆 Full script above.\n\n"
        "You can:\n"
        "• Edit any scene's narration or image prompt\n"
        "• Ask me to rewrite specific scenes\n"
        "• Change the title/description\n"
        "• Say 'approved' to proceed to voice generation\n\n"
        "Cost so far: ~$0.004 (just script gen)"
    )


def _create_placeholder(output_path, label=""):
    """Create a dark placeholder image."""
    import subprocess
    escaped = label.replace("'", "'\\''")
    subprocess.run([
        "ffmpeg", "-y", "-f", "lavfi",
        "-i", f"color=c=0x0a0a14:s=1920x1080:d=1:r=1",
        "-frames:v", "1",
        "-vf", f"drawtext=text='{escaped}':fontcolor=white@0.3:fontsize=32:x=(w-text_w)/2:y=(h-text_h)/2:fontfile={FONT}",
        output_path,
    ], capture_output=True, timeout=30)

# ─── CLI entry point (for backgrounding heavy steps) ──────────────────────────
# Cortana: background heavy steps with nohup so your session stays responsive:
#   nohup python3 /root/.openclaw/workspace/lib/sleep_interactive.py generate_images /path/to/project > /tmp/job.log 2>&1 &
#   nohup python3 /root/.openclaw/workspace/lib/sleep_interactive.py assemble /path/to/project > /tmp/job.log 2>&1 &
#   nohup python3 /root/.openclaw/workspace/lib/sleep_interactive.py generate_voice /path/to/project [voice] > /tmp/job.log 2>&1 &
#   nohup python3 /root/.openclaw/workspace/lib/sleep_interactive.py generate_ambient /path/to/project "ambient description" > /tmp/job.log 2>&1 &

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SleepProject CLI — for backgrounding heavy steps")
    parser.add_argument("command", choices=["generate_images", "generate_voice", "assemble", "generate_ambient", "select_music", "status"])
    parser.add_argument("project_dir", help="Path to project directory")
    parser.add_argument("arg", nargs="?", help="Extra arg (voice name, ambient prompt, etc.)")
    parser.add_argument("--model", default=DEFAULT_IMAGE_MODEL)
    parser.add_argument("--music-volume", type=float, default=0.6)
    args = parser.parse_args()

    project = SleepProject.load(args.project_dir)

    if args.command == "generate_images":
        project.generate_images(model=args.model)
    elif args.command == "generate_voice":
        voice = args.arg or DEFAULT_VOICE
        project.generate_voice(voice=voice)
    elif args.command == "assemble":
        project.assemble(music_volume=args.music_volume)
    elif args.command == "select_music":
        project.select_music(override_track=args.arg)
    elif args.command == "generate_ambient":
        if not args.arg:
            print("ERROR: ambient prompt required as third argument")
            sys.exit(1)
        project.generate_ambient(args.arg)
    elif args.command == "status":
        project.status()

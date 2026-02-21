#!/usr/bin/env python3
"""
sleep_pipeline.py — Sleep video production pipeline. Single entry point for all steps.

Usage:
    python3 sleep_pipeline.py create --topic "..." [--duration 3] [--style stoic] [--scenes 8]
    python3 sleep_pipeline.py voice   <project_dir> [--voice VOICE_ID]
    python3 sleep_pipeline.py images  <project_dir> [--model MODEL]
    python3 sleep_pipeline.py assemble <project_dir> [--music-volume 0.08]
    python3 sleep_pipeline.py music   <project_dir> [--track choir|piano|strings]
    python3 sleep_pipeline.py status  <project_dir>
    python3 sleep_pipeline.py status  --latest

Heavy steps (voice, images, assemble) always detach into a background worker.
Calling this script is always safe — it returns immediately for heavy steps,
then delivers the result to Telegram when done.
"""

import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

WORKSPACE   = Path('/root/.openclaw/workspace')
OUTPUT_DIR  = WORKSPACE / 'output' / 'sleep-videos'
MUSIC_DIR   = WORKSPACE / 'assets' / 'music'

# ── Defaults ──────────────────────────────────────────────────────────────────

DEFAULT_VOICE     = 'V2bPluzT7MuirpucVAKH'  # Frank
DEFAULT_IMG_MODEL = 'imagen-4.0-generate-001'
DEFAULT_DURATION  = 3    # minutes
DEFAULT_SCENES    = 8
DEFAULT_STYLE     = 'stoic'
DEFAULT_MUSIC_VOL = 0.08
TITLE_DURATION    = 8.0  # seconds of silence before narration (for title card)
TG_TOPIC          = 22   # Telegram thread for sleep videos

MUSIC_TRACKS = {
    'piano': {
        'file': 'piano-ambient-pads.mp3',
        'name': 'Sleep by Scott Buckley',
        'attribution': '"Sleep" by Scott Buckley — CC-BY 4.0. www.scottbuckley.com.au',
        'styles': ['calm_narrative', 'meditation', 'nature'],
    },
    'choir': {
        'file': 'choir-harp-ethereal.mp3',
        'name': 'Frozen Star by Kevin MacLeod',
        'attribution': '"Frozen Star" by Kevin MacLeod (incompetech.com) — CC-BY 3.0.',
        'styles': ['stoic'],
    },
    'strings': {
        'file': 'strings-drone-hiraeth.mp3',
        'name': 'Hiraeth by Scott Buckley',
        'attribution': '"Hiraeth" by Scott Buckley — CC-BY 4.0. www.scottbuckley.com.au',
        'styles': ['dramatic', 'epic'],
    },
}

# Steps that always background themselves — never run inline.
HEAVY_STEPS = {'voice', 'images', 'assemble'}

# ── Environment ───────────────────────────────────────────────────────────────

def _load_env():
    """Parse /root/.openclaw/.env into os.environ (idempotent)."""
    env_path = Path('/root/.openclaw/.env')
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        line = line.removeprefix('export').strip()
        if '=' not in line:
            continue
        k, _, v = line.partition('=')
        os.environ.setdefault(k.strip(), v.strip().strip('"\''))

_load_env()

# ── Telegram ──────────────────────────────────────────────────────────────────

def _tg(text, topic=TG_TOPIC):
    """Send a text message to Telegram (HTML mode)."""
    import urllib.request
    token   = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
    if not token or not chat_id:
        print(f'[telegram] not configured, skipping: {text[:80]}')
        return
    # Split messages over 4096 chars
    for chunk in _split_tg(text, 4096):
        payload = json.dumps({
            'chat_id': chat_id,
            'text': chunk,
            'message_thread_id': topic,
            'disable_web_page_preview': True,
            'parse_mode': 'HTML',
        }).encode()
        req = urllib.request.Request(
            f'https://api.telegram.org/bot{token}/sendMessage',
            data=payload, headers={'Content-Type': 'application/json'},
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                r.read()
        except Exception as e:
            print(f'[telegram] sendMessage failed: {e}', file=sys.stderr)


def _tg_file(path, method, caption='', topic=TG_TOPIC):
    """Upload a file to Telegram (photo/audio/video)."""
    import requests
    token   = os.environ.get('TELEGRAM_BOT_TOKEN', '')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID', '')
    if not token or not chat_id:
        print(f'[telegram] not configured, skipping file upload: {path}')
        return
    field_map = {'sendPhoto': 'photo', 'sendAudio': 'audio', 'sendVideo': 'video'}
    field = field_map.get(method, 'document')
    mime_map = {'sendPhoto': 'image/png', 'sendAudio': 'audio/mpeg', 'sendVideo': 'video/mp4'}
    mime = mime_map.get(method, 'application/octet-stream')
    path = Path(path)
    try:
        with open(path, 'rb') as f:
            resp = requests.post(
                f'https://api.telegram.org/bot{token}/{method}',
                data={'chat_id': chat_id, 'message_thread_id': topic, 'caption': caption,
                      'supports_streaming': 'true'},
                files={field: (path.name, f, mime)},
                timeout=180,
            )
        if not resp.json().get('ok'):
            print(f'[telegram] {method} failed: {resp.text[:200]}', file=sys.stderr)
    except Exception as e:
        print(f'[telegram] {method} error: {e}', file=sys.stderr)


def _split_tg(text, max_len):
    if len(text) <= max_len:
        return [text]
    chunks, buf = [], ''
    for line in text.splitlines(keepends=True):
        if len(buf) + len(line) > max_len:
            chunks.append(buf)
            buf = ''
        buf += line
    if buf:
        chunks.append(buf)
    return chunks


# ── ffmpeg wrapper ────────────────────────────────────────────────────────────

def _ffmpeg(args, timeout=600):
    """Run ffmpeg -y <args>. Raises RuntimeError on failure."""
    cmd = ['ffmpeg', '-y'] + [str(a) for a in args]
    result = subprocess.run(cmd, capture_output=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(
            f'ffmpeg failed (rc={result.returncode}):\n'
            + result.stderr.decode(errors='replace')[-1500:]
        )
    return result


# ── Project state ─────────────────────────────────────────────────────────────

class SleepProject:
    """Lightweight project state wrapper. No heavy ops — those are module functions."""

    def __init__(self, project_dir):
        self.dir = Path(project_dir)
        self.state_path = self.dir / 'project_state.json'
        self.state = self._load()

    def _load(self):
        if self.state_path.exists():
            return json.loads(self.state_path.read_text())
        return {'status': 'new', 'steps_completed': []}

    def save(self):
        self.state_path.write_text(json.dumps(self.state, indent=2))

    def mark(self, step):
        self.state.setdefault('steps_completed', []).append(step)
        self.save()

    # ── Class methods ──────────────────────────────────────────────────────────

    @classmethod
    def load(cls, project_dir):
        p = cls(project_dir)
        if not p.state_path.exists():
            raise FileNotFoundError(f'No project at {project_dir}')
        return p

    @classmethod
    def latest(cls):
        dirs = sorted(OUTPUT_DIR.glob('sleep-*'), key=lambda d: d.stat().st_mtime, reverse=True)
        if not dirs:
            raise RuntimeError('No projects found in ' + str(OUTPUT_DIR))
        return cls.load(dirs[0])

    @classmethod
    def create(cls, topic, duration=DEFAULT_DURATION, style=DEFAULT_STYLE, num_scenes=DEFAULT_SCENES):
        """Generate script, save project, send to Telegram. Lightweight — runs inline."""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        project_dir = OUTPUT_DIR / f'sleep-{timestamp}'
        project_dir.mkdir(parents=True)

        project = cls(project_dir)
        project.state = {
            'status': 'in_progress',
            'steps_completed': [],
            'topic': topic,
            'duration': duration,
            'style': style,
            'num_scenes': num_scenes,
            'created': timestamp,
        }

        print(f'Generating script for: {topic}')
        script = _generate_script(topic, duration, style, num_scenes)

        script_path = project_dir / 'script.json'
        script_path.write_text(json.dumps(script, indent=2))

        project.state['script_path'] = str(script_path)
        project.state['title'] = script.get('title', topic[:60])
        project.mark('create')

        _send_script_to_telegram(script, project_dir)
        return project

    # ── Lightweight operations ─────────────────────────────────────────────────

    def get_script(self):
        return json.loads(Path(self.state['script_path']).read_text())

    def update_script(self, script):
        Path(self.state['script_path']).write_text(json.dumps(script, indent=2))

    def update_scene(self, index, narration=None, image_prompt=None, effect=None):
        script = self.get_script()
        scene = script['scenes'][index]
        if narration:
            scene['narration'] = narration
        if image_prompt:
            scene['image_prompt'] = image_prompt
        if effect:
            scene['effect'] = effect
        self.update_script(script)
        print(f'Scene {index} updated.')

    def select_music(self, override_track=None):
        style = self.state.get('style', DEFAULT_STYLE)
        track_key = override_track or _pick_music_track(style)
        track = MUSIC_TRACKS[track_key]
        music_path = MUSIC_DIR / track['file']
        if not music_path.exists():
            raise FileNotFoundError(f'Music file not found: {music_path}')
        self.state['music_path'] = str(music_path)
        self.state['music_track'] = track['name']
        self.state['music_attribution'] = track['attribution']
        self.save()
        print(f'Music: {track["name"]}')
        return str(music_path)

    def status(self):
        print(f'Project : {self.dir.name}')
        print(f'Status  : {self.state.get("status")}')
        print(f'Steps   : {", ".join(self.state.get("steps_completed", []))}')
        for k in ('title', 'topic', 'duration', 'style', 'num_scenes'):
            if k in self.state:
                print(f'{k.capitalize():8}: {self.state[k]}')
        if 'narration_duration' in self.state:
            d = self.state['narration_duration']
            print(f'Narration: {d:.0f}s ({d/60:.1f} min)')
        if 'output_path' in self.state:
            print(f'Output  : {self.state["output_path"]}')


# ── Music selection ───────────────────────────────────────────────────────────

def _pick_music_track(style):
    for key, track in MUSIC_TRACKS.items():
        if style in track['styles']:
            return key
    return 'piano'


# ── Script generation ─────────────────────────────────────────────────────────

def _generate_script(topic, duration_minutes, style, num_scenes):
    key = os.environ.get('GEMINI_API_KEY', '')
    if not key:
        raise RuntimeError('GEMINI_API_KEY not set')

    style_guides = {
        'stoic': (
            'Write as a philosophical bedtime reflection drawing on Stoic wisdom. '
            'Weave in ideas from Marcus Aurelius, Seneca, Epictetus naturally — '
            "don't name-drop, just embody the philosophy. Tone: wise, warm, reassuring. "
            'Help the listener release the day\'s worries and find peace.'
        ),
        'calm_narrative': (
            'Write in a calm, soothing narrative voice. Gentle, flowing language. '
            'Describe sensory details — sounds, textures, warmth, light. '
            "Slow and meditative pace. Use pauses ('...'). "
            'The listener should feel like they\'re drifting through a peaceful dream.'
        ),
        'meditation': (
            "Write as a guided meditation. Address the listener directly with 'you'. "
            "Include breathing cues, body scan elements, visualization prompts. "
            'Very slow pace with many pauses.'
        ),
        'nature': (
            'Write a vivid nature journey — forest walk, stream, meadow. '
            'Rich sensory detail: water sounds, rustling leaves, distant birdsong. '
            'No plot needed, just gentle movement through a landscape.'
        ),
    }

    guide = style_guides.get(style, style_guides['calm_narrative'])
    target_words = duration_minutes * 100  # ~100 wpm for sleep content
    words_per_scene = target_words // num_scenes

    prompt = f"""You are writing a sleep story script for a YouTube video.

Topic: {topic}
Duration: {duration_minutes} minutes (~{target_words} words total at sleep pace)
Style: {guide}
Scenes: exactly {num_scenes} scenes, ~{words_per_scene} words each

Rules:
- Second person ("you", "your") — speak directly to the listener
- Use ellipses (...) for natural pauses
- No loud moments — this is for falling asleep
- Final 2-3 scenes: especially quiet and dreamlike
- Images: cinematic 16:9, soft lighting, no people, no faces, no text

Return ONLY valid JSON:
{{
    "title": "YouTube title including 'Sleep Story'",
    "subtitle": "Short tagline for title card (one sentence)",
    "description": "YouTube description (2-3 sentences, SEO keywords)",
    "tags": ["sleep story", "bedtime story", ...up to 10 tags],
    "scenes": [
        {{
            "narration": "Narration text for this scene (~{words_per_scene} words)...",
            "image_prompt": "Detailed cinematic image description for this scene..."
        }}
    ]
}}"""

    print(f'Generating script ({duration_minutes} min, {num_scenes} scenes)...')
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(temperature=0.8, max_output_tokens=16000),
    )

    text = response.text
    if '```json' in text:
        text = text.split('```json')[1].split('```')[0]
    elif '```' in text:
        text = text.split('```')[1].split('```')[0]

    script = json.loads(text.strip())
    print(f"Script: '{script['title']}' — {len(script['scenes'])} scenes")
    return script


def _send_script_to_telegram(script, project_dir):
    total_words = sum(len(s['narration'].split()) for s in script['scenes'])
    _tg(
        f"<b>SCRIPT READY FOR REVIEW</b>\n\n"
        f"<b>Title:</b> {script['title']}\n"
        f"<b>Scenes:</b> {len(script['scenes'])}\n"
        f"<b>Words:</b> {total_words} (~{total_words // 100} min)\n"
        f"<b>Project:</b> {project_dir}\n\n"
        f"<b>Description:</b> {script.get('description', '')}"
    )
    for i, scene in enumerate(script['scenes']):
        msg = (
            f"<b>Scene {i + 1}</b>\n"
            f"{scene['narration']}\n\n"
            f"<i>Image: {scene.get('image_prompt', '')[:200]}</i>"
        )
        _tg(msg)
        time.sleep(0.3)


# ── Heavy step: voice ─────────────────────────────────────────────────────────

def _step_voice(project, voice=DEFAULT_VOICE):
    """Generate narration for all scenes via ElevenLabs, concat, send to Telegram."""
    sys.path.insert(0, str(WORKSPACE / 'lib'))
    from elevenlabs import text_to_speech
    from sleep_video import concat_audio_files, get_audio_duration

    script = project.get_script()
    scenes = script['scenes']
    audio_dir = project.dir / 'audio'
    audio_dir.mkdir(exist_ok=True)

    scene_files = []
    for i, scene in enumerate(scenes):
        out = audio_dir / f'narration_{i:03d}.mp3'
        narration = scene['narration']
        print(f'Voice {i + 1}/{len(scenes)}: {len(narration)} chars')

        # Chunk if over ElevenLabs limit
        if len(narration) > 4500:
            chunks = _split_text(narration, 4500)
            chunk_files = []
            for j, chunk in enumerate(chunks):
                cp = audio_dir / f'narration_{i:03d}_chunk_{j:02d}.mp3'
                text_to_speech(chunk, str(cp), voice=voice, stability=0.7, similarity_boost=0.8)
                chunk_files.append(str(cp))
            concat_audio_files(chunk_files, str(out))
        else:
            text_to_speech(narration, str(out), voice=voice, stability=0.7, similarity_boost=0.8)

        dur = get_audio_duration(str(out))
        print(f'  {out.name}: {dur:.1f}s')
        scene_files.append(str(out))

    narration_path = project.dir / 'full_narration.mp3'
    concat_audio_files(scene_files, str(narration_path))
    total_dur = get_audio_duration(str(narration_path))

    project.state['voice'] = voice
    project.state['narration_path'] = str(narration_path)
    project.state['narration_duration'] = total_dur
    project.mark('voice')

    _tg(f'<b>Narration ready</b> — {total_dur:.0f}s ({total_dur / 60:.1f} min)\nVoice: {voice}')
    _tg_file(narration_path, 'sendAudio', caption=f'Full narration — {total_dur:.0f}s')
    print(f'Voice done: {total_dur:.0f}s')


def _split_text(text, max_chars):
    sentences = text.replace('...', '\u2026').split('. ')
    sentences = [s.replace('\u2026', '...') for s in sentences]
    chunks, buf = [], ''
    for s in sentences:
        candidate = buf + ('. ' if buf else '') + s
        if len(candidate) <= max_chars:
            buf = candidate
        else:
            if buf:
                chunks.append(buf + '.')
            buf = s
    if buf:
        chunks.append(buf)
    return chunks or [text]


# ── Heavy step: images ────────────────────────────────────────────────────────

def _step_images(project, model=DEFAULT_IMG_MODEL):
    """Generate scene images via Gemini Imagen, send each to Telegram immediately."""
    sys.path.insert(0, str(WORKSPACE / 'lib'))
    from imagegen import generate_image_gemini

    script = project.get_script()
    scenes = script['scenes']
    img_dir = project.dir / 'images'
    img_dir.mkdir(exist_ok=True)

    _tg(f'<b>Generating {len(scenes)} images</b> — sending each as it\'s ready...')

    image_files = []
    for i, scene in enumerate(scenes):
        out = img_dir / f'scene_{i:03d}.png'
        prompt = scene.get('image_prompt', scene['narration'][:300])
        full_prompt = (
            f'{prompt}. '
            'Cinematic 16:9 composition, soft warm lighting, serene and peaceful atmosphere, '
            'high quality, photorealistic. No people, no faces, no text.'
        )
        print(f'Image {i + 1}/{len(scenes)}: {prompt[:80]}...')

        try:
            generate_image_gemini(full_prompt, str(out), model=model, aspect_ratio='16:9')
        except Exception as e:
            print(f'  Primary model failed ({e}), trying fallback...')
            try:
                generate_image_gemini(full_prompt, str(out),
                                      model='gemini-2.5-flash-image', aspect_ratio='16:9')
            except Exception as e2:
                print(f'  Fallback failed ({e2}), using placeholder')
                _make_placeholder(out, f'Scene {i + 1}')

        image_files.append(str(out))
        caption = f'Scene {i + 1}/{len(scenes)}: {prompt[:150]}'
        _tg_file(out, 'sendPhoto', caption=caption)

    project.state['image_files'] = image_files
    project.state['image_model'] = model
    project.mark('images')

    _tg(f'<b>All {len(image_files)} images ready.</b>\nApprove and say "assemble" when ready.')
    print(f'Images done: {len(image_files)}')


def _make_placeholder(path, label):
    _ffmpeg([
        '-f', 'lavfi', '-i', 'color=c=0x1a1a2e:s=1920x1080:d=1',
        '-vf', f"drawtext=text='{label}':fontsize=72:fontcolor=white"
                ":x=(w-text_w)/2:y=(h-text_h)/2",
        '-frames:v', '1', str(path),
    ])


# ── Heavy step: assemble ──────────────────────────────────────────────────────

def _step_assemble(project, music_volume=DEFAULT_MUSIC_VOL):
    """Full video assembly: audio mixing → scene clips → concat → mux → deliver."""
    sys.path.insert(0, str(WORKSPACE / 'lib'))
    from sleep_video import (
        image_to_scene, concatenate_with_crossfade, add_title_card,
        add_audio_to_video, get_audio_duration,
    )
    from imagegen import generate_image_gemini

    # Ensure music is selected
    if 'music_path' not in project.state:
        project.select_music()

    script       = project.get_script()
    narration    = Path(project.state['narration_path'])
    music        = Path(project.state['music_path'])
    image_files  = project.state.get('image_files', [])
    title        = project.state.get('title', '')
    subtitle     = script.get('subtitle', 'Close your eyes... and drift away')

    if not image_files:
        image_files = sorted(str(p) for p in (project.dir / 'images').glob('scene_*.png'))

    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix='sleep_assemble_'))
    print(f'Working dir: {tmp}')
    _tg('<b>Assembly started</b> — mixing audio and rendering scenes...')

    # ── Step 1: Normalize narration loudness ──────────────────────────────────
    print('Step 1: Normalizing narration...')
    normed = tmp / 'narration_normed.m4a'
    _ffmpeg([
        '-i', narration,
        '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
        '-ar', '44100', '-c:a', 'aac', '-b:a', '192k',
        normed,
    ])
    narration_dur = get_audio_duration(str(normed))
    print(f'  Narration: {narration_dur:.1f}s')

    # ── Step 2: Prepend title card silence ────────────────────────────────────
    print(f'Step 2: Padding {TITLE_DURATION:.0f}s silence for title card...')
    padded = tmp / 'narration_padded.m4a'
    _ffmpeg([
        '-f', 'lavfi', '-t', str(TITLE_DURATION),
        '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
        '-i', normed,
        '-filter_complex', '[0:a][1:a]concat=n=2:v=0:a=1[out]',
        '-map', '[out]', '-c:a', 'aac', '-b:a', '192k',
        padded,
    ])
    padded_dur = get_audio_duration(str(padded))
    print(f'  Padded: {padded_dur:.1f}s')

    # ── Step 3: Mix with background music ─────────────────────────────────────
    print(f'Step 3: Mixing with music (vol={music_volume})...')
    mixed = tmp / 'mixed_audio.m4a'
    fade_out_start = max(1, padded_dur - 5)
    _ffmpeg([
        '-i', padded,
        '-stream_loop', '-1', '-i', music,
        '-filter_complex',
        f'[1:a]atrim=0:{padded_dur},asetpts=PTS-STARTPTS,'
        f'volume={music_volume},'
        f'afade=t=in:st=0:d=5,'
        f'afade=t=out:st={fade_out_start}:d=5[music];'
        f'[0:a][music]amix=inputs=2:duration=first:dropout_transition=3,'
        f'alimiter=limit=0.95[out]',
        '-map', '[out]', '-c:a', 'aac', '-b:a', '192k',
        '-t', str(padded_dur),
        mixed,
    ])
    mixed_dur = get_audio_duration(str(mixed))
    if abs(mixed_dur - padded_dur) > 3.0:
        raise RuntimeError(
            f'Audio duration mismatch: expected ~{padded_dur:.1f}s, got {mixed_dur:.1f}s'
        )
    print(f'  Mixed: {mixed_dur:.1f}s')

    # ── Step 4: Calculate scene durations ─────────────────────────────────────
    n_scenes     = len(image_files)
    n_crossfades = n_scenes  # title card + n_scenes clips = n_scenes crossfades
    crossfade_s  = 3.0
    crossfade_loss = n_crossfades * crossfade_s
    per_scene    = (narration_dur + crossfade_loss) / n_scenes
    print(f'Step 4: {n_scenes} scenes × {per_scene:.1f}s each (crossfade loss: {crossfade_loss:.0f}s)')

    # ── Step 5: Generate title card image (dark background) ───────────────────
    print('Step 5: Generating title card image...')
    title_img_path = project.dir / 'images' / 'title_card.png'
    title_prompt = (
        f"Dark cinematic background for a sleep story titled '{title}'. "
        'Very dark muted tones: deep navy, charcoal, soft moonlight. '
        'No bright colors, no warm tones, no text, no people.'
    )
    try:
        generate_image_gemini(title_prompt, str(title_img_path),
                              model=DEFAULT_IMG_MODEL, aspect_ratio='16:9')
    except Exception as e:
        print(f'  Title card image failed ({e}), using dark placeholder')
        _make_placeholder(title_img_path, title[:40])

    # ── Step 6: Generate title card clip ─────────────────────────────────────
    print('Step 6: Rendering title card clip...')
    title_clip = tmp / 'title_card.mp4'
    add_title_card(str(title_clip), title, subtitle,
                   background_image=str(title_img_path))

    # ── Step 7: Render scene clips ────────────────────────────────────────────
    clips = [str(title_clip)]
    for i, img in enumerate(image_files):
        clip = tmp / f'scene_{i:03d}.mp4'
        print(f'Step 7.{i+1}: Rendering scene {i+1}/{n_scenes}...')
        image_to_scene(img, str(clip), duration=per_scene, effect='still')
        clips.append(str(clip))

    # ── Step 8: Concatenate with crossfades ───────────────────────────────────
    print(f'Step 8: Concatenating {len(clips)} clips with crossfades...')
    video_only = tmp / 'video_no_audio.mp4'
    concatenate_with_crossfade(clips, str(video_only))

    # ── Step 9: Mux audio ─────────────────────────────────────────────────────
    print('Step 9: Muxing audio...')
    final = project.dir / 'final.mp4'
    add_audio_to_video(str(video_only), str(mixed), str(final))

    # ── Step 10: Compress if over Telegram's 50MB limit ──────────────────────
    size_mb = final.stat().st_size / (1024 * 1024)
    print(f'Final: {size_mb:.0f}MB')
    send_path = final
    if size_mb > 48:
        print('Step 10: Compressing for Telegram...')
        compressed = project.dir / 'final_compressed.mp4'
        _ffmpeg(['-i', final, '-c:v', 'libx264', '-crf', '26', '-preset', 'fast',
                 '-c:a', 'aac', '-b:a', '160k', compressed])
        send_path = compressed
        size_mb = send_path.stat().st_size / (1024 * 1024)

    # ── Step 11: Save state ───────────────────────────────────────────────────
    final_dur = get_audio_duration(str(send_path))
    project.state['output_path'] = str(send_path)
    project.state['status'] = 'complete'
    project.mark('assemble')

    # ── Step 12: Deliver to Telegram ─────────────────────────────────────────
    print(f'Step 12: Sending to Telegram ({size_mb:.0f}MB)...')
    music_track = project.state.get('music_track', '')
    caption = (
        f'<b>{title}</b>\n'
        f'{final_dur / 60:.1f} min | {size_mb:.0f}MB\n'
        + (f'<i>{music_track}</i>' if music_track else '')
    )
    _tg_file(send_path, 'sendVideo', caption=caption)

    attribution = project.state.get('music_attribution', '')
    if attribution:
        _tg(f'<b>YouTube attribution (required):</b>\n\n{attribution}')

    print(f'Done: {send_path} ({final_dur:.0f}s, {size_mb:.0f}MB)')


# ── CLI entry point ───────────────────────────────────────────────────────────

def _background_self(raw_argv, step):
    """Detach this process as a background worker. Caller should sys.exit(0) after."""
    ts = int(time.time())
    log = f'/tmp/sleep-{step}-{ts}.log'
    env = {**os.environ, '__SLP_WORKER': '1'}
    with open(log, 'w') as lf:
        proc = subprocess.Popen(
            [sys.executable, __file__] + raw_argv,
            env=env, start_new_session=True,
            stdout=lf, stderr=subprocess.STDOUT,
        )
    _tg(
        f'<b>{step}</b> started in background\n'
        f'PID: {proc.pid} | Log: <code>{log}</code>'
    )
    print(f'Backgrounded: PID={proc.pid} log={log}')


if __name__ == '__main__':
    import argparse

    p = argparse.ArgumentParser(
        description='Sleep video pipeline — heavy steps always background themselves.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = p.add_subparsers(dest='cmd', required=True)

    # create
    p_create = sub.add_parser('create', help='Generate script and create project')
    p_create.add_argument('--topic',    required=True)
    p_create.add_argument('--duration', type=int,   default=DEFAULT_DURATION)
    p_create.add_argument('--style',                default=DEFAULT_STYLE)
    p_create.add_argument('--scenes',   type=int,   default=DEFAULT_SCENES)

    # voice
    p_voice = sub.add_parser('voice', help='Generate narration audio')
    p_voice.add_argument('project_dir')
    p_voice.add_argument('--voice', default=DEFAULT_VOICE)

    # images
    p_images = sub.add_parser('images', help='Generate scene images')
    p_images.add_argument('project_dir')
    p_images.add_argument('--model', default=DEFAULT_IMG_MODEL)

    # assemble
    p_assemble = sub.add_parser('assemble', help='Assemble final video')
    p_assemble.add_argument('project_dir')
    p_assemble.add_argument('--music-volume', type=float, default=DEFAULT_MUSIC_VOL)

    # music
    p_music = sub.add_parser('music', help='Select background music track')
    p_music.add_argument('project_dir')
    p_music.add_argument('--track', choices=list(MUSIC_TRACKS.keys()), default=None)

    # status
    p_status = sub.add_parser('status', help='Show project status')
    p_status.add_argument('project_dir', nargs='?', default=None)
    p_status.add_argument('--latest', action='store_true')

    args = p.parse_args()

    # ── Background heavy steps before doing any real work ─────────────────────
    if args.cmd in HEAVY_STEPS and not os.environ.get('__SLP_WORKER'):
        _background_self(sys.argv[1:], args.cmd)
        sys.exit(0)

    # We're the worker (or a lightweight step) — mark and run.
    os.environ['__SLP_WORKER'] = '1'

    try:
        if args.cmd == 'create':
            project = SleepProject.create(
                topic=args.topic,
                duration=args.duration,
                style=args.style,
                num_scenes=args.scenes,
            )
            print(f'Project created: {project.dir}')

        elif args.cmd == 'voice':
            project = SleepProject.load(args.project_dir)
            _step_voice(project, voice=args.voice)

        elif args.cmd == 'images':
            project = SleepProject.load(args.project_dir)
            _step_images(project, model=args.model)

        elif args.cmd == 'assemble':
            project = SleepProject.load(args.project_dir)
            _step_assemble(project, music_volume=args.music_volume)

        elif args.cmd == 'music':
            project = SleepProject.load(args.project_dir)
            project.select_music(override_track=args.track)

        elif args.cmd == 'status':
            if args.latest or not args.project_dir:
                project = SleepProject.latest()
            else:
                project = SleepProject.load(args.project_dir)
            project.status()

    except KeyboardInterrupt:
        print('\nInterrupted.')
        sys.exit(1)
    except Exception as e:
        msg = f'<b>Pipeline error ({args.cmd})</b>\n<code>{e}</code>'
        _tg(msg)
        print(f'ERROR: {e}', file=sys.stderr)
        raise

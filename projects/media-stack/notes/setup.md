# Setup Notes

## Hyperframes

Run via:

```bash
projects/media-stack/bin/hyperframes init demo --non-interactive --example blank
projects/media-stack/bin/hyperframes preview
projects/media-stack/bin/hyperframes render --output output/demo.mp4
```

## MMX

Authenticate first:

```bash
projects/media-stack/bin/mmx auth login --api-key <MINIMAX_API_KEY>
```

Then use:

```bash
projects/media-stack/bin/mmx image "A futuristic city skyline"
projects/media-stack/bin/mmx speech synthesize --text "Hello" --out output/mmx/hello.mp3
projects/media-stack/bin/mmx music generate --prompt "Cinematic ambient" --instrumental --out output/mmx/ambient.mp3
projects/media-stack/bin/mmx video generate --prompt "Neon rain in a city alley" --async
```

## Integration plan

- MMX generates assets into `output/mmx/`
- Hyperframes composes final videos in `hyperframes/`
- OpenClaw orchestrates scripts, prompts, approvals, and delivery

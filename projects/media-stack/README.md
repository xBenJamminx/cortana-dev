# Media Stack

This folder is the local integration point for:
- OpenClaw orchestration
- Hyperframes for deterministic video composition/rendering
- MMX CLI for generative media (image/video/music/speech)

## Structure

- `hyperframes/` - Hyperframes project workspace
- `bin/` - local wrapper scripts
- `output/` - rendered/generated artifacts
- `notes/` - setup notes and usage docs

## Philosophy

- OpenClaw is the brain
- Hyperframes is the compositor
- MMX is the media generator

## Intended workflows

1. Research/script -> Hyperframes explainer video
2. Prompt -> MMX generated assets -> Hyperframes final assembly
3. Wiki synthesis -> narrated short -> Telegram delivery

#!/bin/bash
# Cortana scheduled posts - DEPRECATED
# bird CLI is discontinued. Use X OAuth or Composio for posting.
# Old tokens removed for security.

for _env in "$HOME/.hermes/.env" "$HOME/.openclaw/.env"; do
  [ -f "$_env" ] && { set -a; . "$_env"; set +a; break; }
done

echo "[$(date)] This script is deprecated. Use scheduled-composio-post.py or X OAuth instead."

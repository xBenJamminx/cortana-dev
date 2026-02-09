# X API Reference (via Composio)

## Authentication

Uses Composio's `TWITTER_RECENT_SEARCH` action with a connected account.
No bearer token needed. Set `COMPOSIO_API_KEY` in env or `/root/.openclaw/.env`.

## Available Composio Actions

| Action | Description |
|--------|-------------|
| `TWITTER_RECENT_SEARCH` | Search tweets from last 7 days |
| `TWITTER_USER_LOOKUP_ME` | Get authenticated user info |
| `TWITTER_CREATION_OF_A_POST` | Post a tweet |
| `TWITTER_BOOKMARKS_BY_USER` | Get bookmarked tweets |
| `TWITTER_FOLLOW_USER` | Follow a user |
| `TWITTER_UNFOLLOW_USER` | Unfollow a user |

## Search Operators

| Operator | Example | Notes |
|----------|---------|-------|
| keyword | `bun 2.0` | Implicit AND |
| `OR` | `bun OR deno` | Must be uppercase |
| `-` | `-is:retweet` | Negation |
| `()` | `(fast OR perf)` | Grouping |
| `from:` | `from:elonmusk` | Posts by user |
| `to:` | `to:elonmusk` | Replies to user |
| `#` | `#buildinpublic` | Hashtag |
| `$` | `$AAPL` | Cashtag |
| `lang:` | `lang:en` | BCP-47 language code |
| `is:retweet` | `-is:retweet` | Filter retweets |
| `is:reply` | `-is:reply` | Filter replies |
| `is:quote` | `is:quote` | Quote tweets |
| `has:media` | `has:media` | Contains media |
| `has:links` | `has:links` | Contains links |
| `url:` | `url:github.com` | Links to domain |
| `conversation_id:` | `conversation_id:123` | Thread by root tweet ID |

**Note:** `min_likes`, `min_retweets` not available via API. Filter post-hoc from `public_metrics`.

## Response Fields

Tweets include: id, text, author_id, created_at, conversation_id, public_metrics (like_count, retweet_count, reply_count, quote_count, bookmark_count, impression_count), entities (urls, mentions, hashtags).

User expansions include: username, name, public_metrics (followers_count, tweet_count), description.

## Constructing Tweet URLs

```
https://x.com/{username}/status/{tweet_id}
```

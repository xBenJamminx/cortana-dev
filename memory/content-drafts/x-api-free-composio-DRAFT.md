# How to Use the X API for $0

## Twitter Thread

**1/**
The X API just went pay-per-use. Here's how to use it for $0.

**2/**
The new pricing:
$0.005 per tweet read
$0.01 per user lookup
$0.01 per post

20,000 reads = $100. No more free reads. Write-only if you don't pay.

Better than the old $200/month fixed plan, but still adds up fast.

**3/**
Composio has a Twitter integration on their free tier.

20,000 tool calls/month. No credit card. Same X API endpoints underneath.

TWITTER_RECENT_SEARCH gives you the same search, same data, same operators X is now charging for.

**4/**
What you get:
- Tweet search (last 7 days)
- All search operators (from:, to:, has:links, is:reply)
- Full public metrics (likes, RT, impressions, bookmarks)
- Author data with follower counts
- 100 results per request + pagination

Full X API v2 search. For $0.

**5/**
I built a research CLI on top of it. Reply monitoring, profile lookups, topic research, account watchlists.

Caught replies I was completely missing in my notifications. High-value accounts buried under noise.

All free. All real-time.

**6/**
The math:

X API direct: 20K reads/month = $100
Composio free: 20K calls/month = $0

Need more? $29/month gets 200K calls on Composio.
Same volume on X would run you $1,000+.

**7/**
The X API just went pay-per-use. You don't have to.

---

## Article Version

### The X API just went pay-per-use. Here's how to use it for $0.

I almost paid $100/month to read my own replies.

Last week I built a tool to monitor who's replying to my posts on X. Sort by engagement, surface the high-value accounts, stop missing people buried in my notifications. Pretty standard stuff for anyone building in public.

Then I hit the pricing page.

X killed their fixed API plans on February 7th. Everything is pay-per-use now. $0.005 per tweet read. $0.01 per user lookup. My little reply monitor would burn through 20,000 reads in a month easy. That's $100. For reading tweets.

I almost signed up. Then I found the workaround.

### The free path nobody's talking about

Composio is a tool integration platform for AI agents. They connect to 100+ services: Slack, GitHub, Notion, Gmail. Standard integration stuff.

But they also have a Twitter integration. And their free tier gives you 20,000 tool calls per month. No credit card.

One of those tools is TWITTER_RECENT_SEARCH. Same X API v2 search endpoint. Same data. Same query operators. Same response format.

I swapped one API layer and my $100/month problem became $0.

### Same data, zero cost

This isn't some scraped or limited version. Through Composio you get:

Full tweet search across the last 7 days. All X search operators: from:, to:, has:links, is:reply, conversation_id:, hashtags, cashtags. Public metrics including likes, retweets, replies, quotes, impressions, bookmarks. Author expansion with username, display name, follower count, bio. 100 results per request with pagination.

That's the full search API. The same one X just started charging for.

### What I actually built

The reply monitor was just the start. Once you have free API access, you start building things you wouldn't bother paying for.

I pulled 100 replies to one of my posts and ran engagement analysis. Turns out 87 unique accounts replied, but only 10 had real traction. The rest were noise. I was spending time scrolling through all of them trying not to miss anyone. Now the tool surfaces the ones that matter.

Then I added profile lookups. Someone replies with a smart take, I check their account. 50K followers and they build developer tools? That's a relationship worth investing in. 12 followers and no bio? Maybe not right now.

Topic research came next. "What are people saying about Claude Code today?" with real numbers attached. Not vibes, not trending tab guesswork. Actual engagement data on actual posts.

Thread following. Watchlists for accounts I care about. A caching layer so I'm not burning API calls on the same query twice in 15 minutes.

None of this would have been worth $100+/month. All of it is worth $0.

### The setup

Five minutes:

1. Sign up at composio.dev (free, no credit card)
2. Connect your X account through OAuth
3. Copy your API key
4. One POST request to TWITTER_RECENT_SEARCH with your query

That's it. Every reply, every mention, every search result. Full metrics. Free.

### The math

X API direct: 20,000 tweet reads/month = $100, plus 5,000 user lookups = $50. Total around $150/month.

Composio free tier: 20,000 tool calls/month = $0.

If you need more, $29/month on Composio gets you 200,000 calls. That same volume on X would cost over $1,000.

### The catch

20,000 calls/month is plenty for bots, research, monitoring, and engagement analysis. If you're building a product that needs millions of calls, you'll outgrow it. At that scale X's pay-per-use pricing might actually make more sense.

But for indie developers, bot builders, and anyone who wants to stop paying to read tweets? This is the move.

### Bottom line

The X API just went pay-per-use. That's better than the old fixed tiers for most people.

But free is better than pay-per-use.

20,000 API calls. Full search. Full metrics. $0.

The X API just went pay-per-use. You don't have to.

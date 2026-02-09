# Everyday AI -- Community Platform MVP Scope

**Date:** 2026-02-09
**Status:** DRAFT -- Needs Ben's review
**Goal:** Build a community platform that replaces Skool/Whop for Everyday AI, with future white-label potential.

---

## The Pitch

"The community platform that doesn't tax your growth."

Every other platform takes 5-10% of creator revenue on top of monthly fees. We take 1-1.5% to cover infrastructure costs. Creators keep what they earn.

---

## V1: What We Need to Run Everyday AI On It

### Core Features (Must Have for Launch)

**1. Auth + Member Management**
- Email/password + Google OAuth sign-up
- Member profiles (name, avatar, bio)
- Membership tiers (Founding $29/mo, Standard $49/mo, Free)
- Member directory with tier badges
- Admin panel to manage/ban/invite members
- Tech: Clerk or Auth.js + custom role system

**2. Payments + Subscriptions**
- Stripe Checkout for subscriptions (monthly/annual)
- Stripe Customer Portal (members manage their own billing)
- Free trials (7-day)
- Cancellation flow with optional discount offer
- Tier-based access gating (content locked behind tiers)
- Stock limits (50 founding spots)
- One-time digital product purchases (templates, toolkits)
- Webhook handler for payment events (new sub, cancellation, failed payment)
- Tech: Stripe Billing + Webhooks

**3. Community Feed (Forum-style)**
- Threaded posts with rich text (markdown)
- Categories/channels (general, wins, resources, etc.)
- Likes, comments, replies
- Pin posts, admin-only channels
- Image/file attachments on posts
- Sort by: newest, most liked, trending
- Tech: Custom built, stored in Postgres

**4. Real-time Chat**
- Channel-based chat rooms (like Discord/Slack)
- Tier-gated channels (founding-only, premium, etc.)
- Message reactions, replies, mentions
- Online presence indicators
- Tech: WebSockets via Socket.io or Ably/Pusher for managed infrastructure

**5. Course/Content System**
- Module > Lesson structure
- Video embedding (YouTube/Vimeo to start, native hosting later)
- Rich text lessons with embedded media
- Progress tracking (completion %)
- Drip content (unlock after X days)
- Tier-gated courses
- Tech: Custom built, video embeds initially (native hosting is a V2 feature)

**6. Digital Product Storefront**
- Sell one-time downloads (PDFs, templates, starter kits)
- Stripe Checkout for one-time purchases
- Download delivery after purchase
- Product listing page
- Tech: Stripe + file storage (S3/R2)

**7. Custom Domains + Multi-tenancy**
- Default subdomain: yourname.platform.com
- BYOD (bring your own domain) via CNAME + auto-SSL
- Multi-tenant architecture: one app, many communities
- Tenant-specific theming (logo, colors, cover image)
- Tech: Vercel Edge Middleware for hostname routing, Let's Encrypt

**8. Admin Dashboard**
- Member count, growth over time
- Revenue: MRR, new subs, churn, failed payments
- Active members, engagement metrics
- Content performance (which posts/courses get traction)
- Tech: Custom dashboard pulling from Stripe API + app analytics

---

### V1 Nice-to-Haves (Build During Beta)

**9. Gamification**
- Points system (earn points from posts, comments, likes received)
- Levels (configurable thresholds)
- Leaderboard (7-day, 30-day, all-time)
- Level-locked content (unlock a course at level 5)
- This is Skool's moat -- having it from day one is a differentiator

**10. Email Notifications**
- Welcome email on join
- Weekly digest of popular posts
- New course/content alerts
- Payment receipts (Stripe handles these)
- Tech: Resend or Postmark for transactional email

**11. Affiliate System**
- Referral links for members
- Configurable commission % per tier
- Tracking dashboard for affiliates
- Automated payouts via Stripe Connect
- Tech: Custom tracking + Stripe Connect

**12. Discord Bot Integration**
- Stripe webhook fires on payment
- Bot assigns Discord role based on tier
- Auto-removes role on cancellation
- Bridging until chat is fully built out

---

### V2 (Post-Launch, White-Label Features)

- Native video hosting (Cloudflare Stream or Mux)
- Quizzes/assessments on courses
- White-label mobile app (React Native or Capacitor)
- Full API for third-party integrations
- Zapier/webhook triggers for all events
- Advanced analytics (cohort analysis, engagement heatmaps)
- Template marketplace (creators share/sell templates to each other)
- AI features (auto-summarize discussions, content recommendations)
- Embeddable widgets (embed community feed on external site)
- SSO (SAML/OIDC for enterprise customers)

---

## Tech Stack

### Frontend
- **SvelteKit** -- already using it for the landing page, fast, lightweight, SSR/SSG capable
- **Tailwind CSS** -- already using it
- **Socket.io client** or **Ably** -- for real-time chat

### Backend
- **SvelteKit API routes** for most endpoints (keeps it one codebase)
- **Postgres** (Neon or Supabase) -- primary database
- **Drizzle ORM** -- type-safe, lightweight, works great with SvelteKit
- **Redis** (Upstash) -- session cache, rate limiting, real-time presence
- **Stripe** -- all payments
- **Clerk** -- auth (or Auth.js if we want fully self-hosted auth)
- **Cloudflare R2** -- file storage (S3-compatible, no egress fees)
- **Resend** -- transactional email

### Infrastructure
- **Vercel** -- hosting, edge middleware for multi-tenant routing, auto-SSL for custom domains
- **Neon Postgres** -- serverless Postgres, scales to zero, branching for dev/staging
- **Upstash Redis** -- serverless Redis for caching and rate limiting
- **Cloudflare R2** -- file/video storage

### Why This Stack
- SvelteKit is fast, the bundle sizes are tiny, and we already know it
- Everything is serverless -- no servers to manage, scales automatically, pay for what you use
- Vercel handles custom domains and SSL automatically
- Total infrastructure cost at launch: ~$0-50/mo (Vercel free tier, Neon free tier, Upstash free tier, R2 free tier)
- At 1,000 members: ~$50-150/mo
- At 10,000 members: ~$200-500/mo

---

## Architecture: Multi-Tenant

```
Request comes in:
  community.everydayai.com
  OR
  coolcommunity.platform.com

  -> Vercel Edge Middleware
  -> Reads hostname
  -> Looks up tenant in DB (cached in Redis)
  -> Sets tenant context for the request
  -> SvelteKit app renders with tenant's data, theme, content
```

Every community shares the same codebase and infrastructure. Data is isolated by tenant ID in Postgres. Theming (logo, colors, fonts) is stored per-tenant and applied at render time.

This means:
- One deployment serves all communities
- New community = new row in the database, not a new deployment
- Custom domains just need a CNAME record + one API call to register with Vercel

---

## Database Schema (Simplified)

```
tenants
  id, name, slug, custom_domain, logo_url, theme_colors, plan, stripe_account_id

users
  id, email, name, avatar_url, created_at

memberships
  id, user_id, tenant_id, tier, stripe_subscription_id, status, started_at, expires_at

posts
  id, tenant_id, author_id, channel_id, title, body, likes_count, created_at

comments
  id, post_id, author_id, body, created_at

channels
  id, tenant_id, name, type (forum|chat), min_tier, position

messages (chat)
  id, channel_id, author_id, body, created_at

courses
  id, tenant_id, title, description, min_tier, published

lessons
  id, course_id, title, content, video_url, position, drip_days

progress
  id, user_id, lesson_id, completed_at

products (digital downloads)
  id, tenant_id, name, price, stripe_price_id, file_url, description

purchases
  id, user_id, product_id, stripe_payment_id, purchased_at

points
  id, user_id, tenant_id, amount, reason, created_at

levels (config)
  id, tenant_id, level_number, name, points_required, unlocks (JSON)
```

---

## Revenue Model

**For Everyday AI (our community):**
- Founding Member: $29/mo (50 spots)
- Standard Member: $49/mo
- Digital products: $19-49 one-time
- Revenue goes directly to our Stripe, minus Stripe's 2.9% + $0.30

**For white-label customers (future):**
- Platform fee: 1-1.5% of transactions (covers infrastructure scaling costs)
- OR tiered flat fee: $29/mo (up to 100 members), $79/mo (up to 1,000), $199/mo (unlimited)
- Stripe's 2.9% + $0.30 is always the creator's cost (pass-through)
- Premium add-ons: native video hosting ($X/mo), custom mobile app ($X/mo)

---

## Build Phases

### Phase 1: Foundation (Weeks 1-2)
- [ ] Project setup: SvelteKit + Tailwind + Postgres + Drizzle
- [ ] Auth with Clerk (sign up, sign in, profiles)
- [ ] Stripe integration (subscriptions, checkout, webhooks, customer portal)
- [ ] Membership tiers with access gating
- [ ] Basic admin dashboard (members, revenue)
- [ ] Multi-tenant routing (subdomain + custom domain support)
- **Result:** People can sign up, pay, and access tier-gated areas

### Phase 2: Community (Weeks 3-4)
- [ ] Forum/feed system (posts, comments, likes, channels)
- [ ] Real-time chat (channels, messages, presence)
- [ ] Member directory
- [ ] Notification system (in-app)
- [ ] Email notifications (welcome, digest)
- **Result:** A functional community with async + real-time discussion

### Phase 3: Content + Commerce (Weeks 5-6)
- [ ] Course builder (modules, lessons, video embeds, progress tracking)
- [ ] Drip content system
- [ ] Digital product storefront
- [ ] File storage and delivery (R2)
- **Result:** Can sell courses and digital products

### Phase 4: Engagement + Polish (Weeks 7-8)
- [ ] Gamification (points, levels, leaderboards)
- [ ] Level-locked content
- [ ] Affiliate/referral system
- [ ] Admin analytics dashboard (MRR, churn, engagement)
- [ ] Mobile-responsive polish pass
- [ ] Landing page integration (update Everyday AI site to point at platform)
- **Result:** Feature-complete MVP ready for founding members

### Phase 5: White-Label Prep (Post-Launch)
- [ ] Tenant onboarding flow (sign up, configure, launch)
- [ ] Theme customization UI (logo, colors, fonts)
- [ ] Billing for platform customers (Stripe Connect)
- [ ] Documentation / setup guides
- [ ] Marketing site for the platform itself

---

## Competitive Positioning Summary

| Feature | Skool | Whop | Us |
|---------|-------|------|----|
| Monthly fee | $9-99 | $0 | $0 (own use) / $29-199 (white-label) |
| Transaction fee | 2.9-10% | ~6.7% | 1-1.5% (+ Stripe 2.9%) |
| Custom domain | No | Yes | Yes |
| Real-time chat | No | Yes | Yes |
| Forum/posts | Yes | Yes | Yes |
| Gamification | Yes (best) | Barely | Yes |
| Courses | Basic | Good | Good |
| Digital products | No | Yes | Yes |
| Native video | No | Yes | V2 |
| API | Barely | Yes | Yes (V2) |
| White-label | No | Partial | Full |
| Data ownership | Their platform | Their platform | Yours |

---

## Open Questions

1. **Platform name?** This needs its own brand separate from Everyday AI. Everyday AI is the first community on it, not the platform itself.
2. **Build solo or hire?** 8 weeks is aggressive for one person. Real-time chat alone is a week.
3. **Build in public cadence?** Weekly updates? Stream the builds? This becomes Everyday AI content.
4. **Launch on Skool first while building?** Run Everyday AI on Skool $9/mo for 1-2 months, migrate to own platform when ready?
5. **Pricing model decision:** flat tiered fee vs small percentage? Need to decide before building billing.

---

## Next Steps

1. Ben reviews this scope
2. Decide on tech stack confirmations
3. Decide whether to launch Everyday AI on Skool now while building
4. Start Phase 1

# Whop.com -- Paid Community Setup Guide

Last updated: 2026-02-07

---

## 1. How Whop Works

Whop is a social commerce platform for selling digital products, memberships, and communities. No monthly fee to use -- you only pay when you make money.

### Core Concept
- A "whop" is your storefront/hub. It contains **products** (pricing tiers) and **apps** (features/modules).
- Products define what people pay. Apps define what they get access to.
- You toggle specific apps on/off per product tier, creating differentiated access.

### Setup Process
1. Go to whop.com and sign up (email or Google)
2. Click "Create your whop" -- name it (max 30 chars), set custom URL
3. Install apps from the App Store (all free to add)
4. Configure pricing (products/tiers)
5. Set up store page (logo, banner, description, gallery, FAQs)
6. Publish -- your whop is live

### Built-in Apps (20+ available, all free to add)

**Community & Communication:**
| App | What It Does |
|-----|-------------|
| **Chat** | Real-time chat rooms. Moderation controls, reactions, replies, pins, webhook support. |
| **Forums** | Threaded posts with comments. Discord webhook relay available. |
| **Announcements** | One-way broadcast channel. Team publishes, members read. |
| **Suggestions** | Members submit ideas and vote on each other's. |

**Content & Courses:**
| App | What It Does |
|-----|-------------|
| **Courses** | Video courses with quizzes (4 types), PDFs, module structure, drip feeding. Basic analytics. |
| **Content** | Rich text pages (like wiki/knowledge base). Tutorials, guides. |
| **Files** | File directory for sharing downloads with members. |

**Live & Events:**
| App | What It Does |
|-----|-------------|
| **Livestreaming** | Go live in 2 clicks (no OBS required). Unlimited duration. |
| **Video Calls** | Host video calls with members. |
| **Events** | Schedule and paywall events. Virtual or in-person. |
| **Calendar Bookings** | Members book time slots with you. Optional payment per booking. |

**Commerce & Tools:**
| App | What It Does |
|-----|-------------|
| **DigiSell** | Sell digital products inside your whop. No external checkout. |
| **Links** | Curated link directory for members. |
| **Website Embed** | Embed external websites/tools. |
| **Webhooks** | Relay from GitHub, RSS, ecommerce platforms. |
| **Affiliate Links** | Manage and share affiliate links with members. |
| **Discord** | Connect external Discord server with role-gating. |
| **Telegram** | Connect Telegram groups. |

### Payment Processing
- Whop is its own payments platform (multi-PSP orchestration, not just a Stripe wrapper)
- Routes each checkout to the provider most likely to accept it (lifts success by 6-11%)
- Supports: 195 countries, 135+ currencies, 100+ payment methods
- Accepts: cards, digital wallets, ACH, crypto, BNPL (Klarna, Zip, Splitit)
- Payout options: Next-day ACH, instant bank, crypto, Venmo, wire

### Storefront
- Hosted storefront with branding (logo, banner, colors, gallery)
- Custom domain support (free domain + hosting + business email for 1 year)
- Templated pages -- limited CSS/deep layout customization (no white-label)
- Optionally listed on Whop Discover marketplace (4M+ monthly visitors)

---

## 2. Whop + Discord Integration

### How It Works
1. Add the **Discord app** to your whop
2. Authorize the **Whop Bot** in your Discord server
3. Map products to Discord roles in the Roles tab
4. When someone purchases, they click "Claim Access" on their Whop membership page
5. Whop Bot automatically assigns the mapped Discord role(s)

### Channel Gating Setup
1. Create Discord roles for each tier (e.g., @Founding-Member, @Standard-Member)
2. Make Discord categories/channels **private** by default
3. Assign visibility permissions to specific roles per channel
4. In Whop, map each product to its corresponding Discord role(s)
5. Different products = different roles = different channel access

**Example for $29/$49 tiers:**
- @Founding-Member role: sees #general, #introductions, #resources, #founders-only
- @Standard-Member role: sees #general, #introductions, #resources, #premium-content, #live-sessions
- Both tiers share common channels; each has exclusive channels

### On Cancellation (configurable per product)
| Action | What Happens |
|--------|-------------|
| **Remove given roles** (default) | Removes only the roles Whop assigned |
| **Remove all roles** | Strips every role the user has |
| **Kick from server** | Removes user entirely |
| **No action** | Does nothing (user keeps access) |

### Critical Requirements
- Whop Bot role must be at the **top** of your server's role hierarchy (or it can't assign roles)
- Members must link their Discord account to Whop first
- Members click "Claim Access" after purchase -- **not fully automatic** (requires one manual click)
- If members miss this step, they'll think they didn't get access (common support ticket)

### Best Practice: Add instructions
- In your post-purchase flow, prominently tell members to click "Claim Access"
- Add a #how-to-join channel in Discord that's visible to @everyone explaining the process
- Include this in your welcome email/DM

---

## 3. Fees (What Whop Takes)

### Platform Commission
| Source | Fee |
|--------|-----|
| **Direct sales (your traffic)** | 3% commission (only on sales with automations: Discord, Telegram, TradingView) |
| **Whop Discover marketplace** | **30% commission** |
| **No automations** | 0% platform fee (just processing) |

### Payment Processing (always applies)
| Type | Fee |
|------|-----|
| Domestic cards | 2.7% + $0.30 per transaction |
| International cards | +1.5% additional |
| Currency conversion | +1% additional |
| ACH (US) | 1.5% (max $5 per transaction) |
| Financing (Klarna/Afterpay) | 15% per transaction |

### Payout Fees
| Method | Fee |
|--------|-----|
| Next Day ACH | $2.50 per payout |
| Instant Bank Deposit (RTP) | 4% + $1.00 |
| Cryptocurrency | 5% + $1.00 |
| Venmo | 5% + $1.00 |
| Bank Wire | $23.00 per payout |
| International Local Banks | Varies by country |

### Other/Hidden Fees
| Type | Fee |
|------|-----|
| 3DS Authentication | $0.03 per transaction |
| Radar (ML fraud detection) | $0.07 per transaction |
| Chargeback/dispute | $15.00 per dispute |
| Early dispute alert | $29.00 per alert |
| Orchestration (optional) | 0.8% per transaction |
| Billing automation | 0.5% per transaction |
| Tax collection/remittance | 0.5% per transaction |
| Affiliate processing | 1.25% per transaction |

### Effective Total Rate (Direct Sales, Domestic, With Discord)
- **~5.7% + $0.30** per transaction (2.7% processing + 3% platform)
- On a $29/mo membership: ~$1.95 in fees (~6.7% effective rate)
- On a $49/mo membership: ~$3.09 in fees (~6.3% effective rate)

### Revenue Projections at Scale
| Monthly Revenue | Total Fees (~6%) | Net You Keep |
|-----------------|-------------------|-------------|
| $500 | ~$30 | ~$470 |
| $2,000 | ~$120 | ~$1,880 |
| $5,000 | ~$300 | ~$4,700 |
| $10,000 | ~$600 | ~$9,400 |

### Key: Non-refundable fees
If you refund a customer, Whop does NOT refund the processing fees or platform commission back to you. You eat that cost.

### Comparison to Competitors
| Platform | Fee Structure |
|----------|---------------|
| **Whop** | $0/mo + ~5.7% per sale (own traffic) or 30% (marketplace) |
| Skool | $99/mo flat, $0 transaction fees |
| Patreon | 10% + processing |
| Gumroad | 10% + processing (30% on Discover) |
| Podia | $39-89/mo + 0-5% fee |
| SchoolMaker | $29/mo, 0% transaction fees |

**Breakeven vs Skool:** At ~$1,750/mo revenue, Whop's percentage fees equal Skool's flat $99/mo. Above that, Skool becomes cheaper per dollar earned.

---

## 4. Best Practices for $29/$49 Community Setup

### Recommended Product Structure

**Product 1: Founding Member -- $29/month**
- Position as limited, early-adopter pricing
- Set **stock limit** (e.g., 50 spots) for scarcity
- Apps: Chat, Forums, Content, Files, Discord access, Announcements
- Founding members keep their rate as long as they stay subscribed
- Once 50 sell, this tier is gone forever

**Product 2: Standard Member -- $49/month**
- Full access to everything
- Apps: All of Founding + Courses, premium content areas, live sessions, Calendar Bookings
- Position as the "complete experience"
- This is your main revenue product long-term

**Product 3: Free Tier (optional but recommended)**
- Apps: Limited Chat access only (one or two channels)
- Serves as top-of-funnel conversion path
- People taste the community, then upgrade

**Product 4+: Digital Products (one-time purchases)**
- Prompt Pack: $19 one-time (Files app with download)
- AI Workflow Templates: $29 one-time
- Standalone products anyone can buy, no subscription required

### Pricing Features to Enable
- **Free trial:** 7-day on the $29 tier (drives conversions, low risk)
- **Cancellation discount:** Auto-offer 20-30% off when someone tries to cancel (retention)
- **Annual pricing:** $290/year for Founding ($48 savings) or $490/year for Standard ($98 savings)
- **Initial fee:** Optional one-time setup fee on first payment (e.g., $10 onboarding fee)

### Launch Strategy
1. **Drive your own traffic only** -- use direct whop URLs, NOT Discover (3% vs 30%)
2. Start with your existing audience (X followers, email list)
3. Enable affiliate program at 20-30% for member referrals
4. Use waitlist mode before launch to build anticipation
5. Announce founding member scarcity ("only 50 spots")
6. Add pre-checkout questions to filter quality members

### Discord Channel Structure for Tiers

**Shared channels (both tiers):**
- #welcome-start-here
- #introductions
- #general-chat
- #wins-and-progress
- #resources

**Founding-only channels:**
- #founders-lounge (networking)

**Standard-only (or Standard + Founding) channels:**
- #premium-content
- #live-session-replays
- #advanced-resources
- #1-on-1-support

**Admin channels:**
- #announcements (read-only)
- #feedback-and-suggestions

---

## 5. Successful AI Education Communities on Whop

### AI Automation Academy (by Hamza Ramic / EstaFlow)
- **URL:** whop.com/discover/argus-ai-automation-academy/
- **Pricing:** $97/month (academy) + $7/week (community tier)
- **Includes:** 5-hour course, live weekly Q&A, group chat, case studies, blueprints
- **Rating:** 5.0 stars
- **Background:** 200+ AI workflows built, 100+ students coached
- **Positioning:** "Build & Sell AI Automation. Find First Client in 30 Days"

### AI Launchpad (by Ralph)
- **Focus:** AI agency building
- **Includes:** 5-hour course, group chat, weekly Q&A
- **Model:** Comprehensive course + community combo

### Other Notable AI Communities on Whop
- **AI Wealth Academy** -- monetizing AI skills broadly
- **AI Clipper Academy** -- AI video clipping + automation (niche focus)
- **AI Automation Content Creator** -- automating content workflows for creators/coaches
- **AI & Automation Mini-Course** -- 30-min micro-courses for busy professionals
- **Apatero Hub** -- AI education for beginners becoming AI creators

### Common Patterns in Successful AI Communities
1. **Course + community combo** (not community alone -- people need structured learning)
2. **Weekly live Q&A or coaching calls** (retention driver)
3. **Creator actively present in chat** (not just a content dump)
4. **Clear outcome promise** ("find first client in 30 days", "automate your workflow")
5. **Multiple tiers:** cheap community entry ($7-30/week) + premium academy ($50-100/month)
6. **Niche focus** beats broad AI education (automation agencies, content creation, specific tools)
7. **Revenue example:** $63K in 60 days documented by one Whop creator (EntreResource.com review)

---

## 6. Product Structuring on Whop

### Four Pricing Types
1. **Free** -- no payment, open access
2. **One-time payment** -- single charge, lifetime or auto-expiring access
3. **Recurring subscription** -- weekly, monthly, quarterly, yearly, or custom
4. **Limited sales** -- set stock count, auto-closes when sold out

### Structuring Memberships + Digital Products Together

**Memberships (recurring):**
- Founding Member: $29/month recurring, stock-limited
- Standard Member: $49/month recurring
- Both include Discord access + community apps

**Digital Products (one-time):**
- Prompt Pack v1: $19 one-time
- AI Workflow Templates: $29 one-time
- Full Automation Toolkit: $49 one-time
- Each is a separate product granting access to a specific Files/Content app

**Bundles:**
- Create a product that includes community + digital download
- Example: "Starter Bundle" = 1 month Standard + Prompt Pack for $59

### How Apps Connect to Products
- Each product has a toggle list of all your installed apps
- Turn on only the apps that product should unlock
- "Prompt Pack" product: toggle on only the Files app containing those prompts
- "Full Membership" product: toggle on Chat, Forums, Courses, Discord, Files, Content, etc.

### Subscription-Specific Features
- **Free trials:** 3-7 days (or custom) before first charge
- **Initial fee:** One-time charge on top of first subscription payment
- **Split payments/installments:** Let customers pay in parts
- **Cancellation discounts:** Auto-offer discount when someone cancels
- **Billing periods:** Weekly, monthly, quarterly, custom intervals

### Access Control Options
- **Stock limits:** Cap purchases per tier
- **Waitlists:** Require admin approval before access
- **Auto-expiring access:** Revoke after X days
- **Hidden pricing:** Only via direct/secret link (not on store page)
- **Pre-checkout questions:** Qualify members before purchase
- **Post-purchase redirect:** Send to specific URL after checkout

---

## 7. Gotchas & Limitations

### Financial Gotchas

1. **Discover Marketplace = 30% fee.** If Whop's marketplace drives the sale, they take 30%. Always use your own links to keep fees at 3%. The marketplace has 4M visitors but 30% is brutal.

2. **Fees are non-refundable.** Issue a refund to a customer? Whop keeps the processing fee AND platform commission. You eat the full cost.

3. **Fees compound at scale.** Processing (2.7%) + platform (3%) + small line items (fraud detection, billing, 3DS) = closer to 6-7% total effective rate. At $5K+/month, flat-fee platforms like Skool ($99/mo) become significantly cheaper.

4. **International fees are steep.** 2.7% + 1.5% + 1% (conversion) = 5.2% + $0.30 for an international customer. Plus the 3% platform fee = 8.2%.

5. **Chargeback fee: $15 per dispute** regardless of outcome. Factor this in.

6. **Payout fees vary wildly.** ACH ($2.50) is fine. Instant/crypto/Venmo (4-5% + $1) eats margins. Bank wire is $23. Batch your payouts.

### Feature Limitations

7. **Course app is basic.** No certificates, no advanced learning analytics, no gamification, no completion tracking beyond basics. If courses are primary, use Teachable/Kajabi instead.

8. **Limited customization.** Store pages are templated. No custom CSS, no deep layout control, no full white-label. If brand presentation matters, use an external landing page that links to Whop checkout.

9. **Limited analytics.** Basic revenue/churn/growth. No content performance analytics, no engagement heatmaps, no advanced cohort analysis.

10. **No built-in email marketing.** No drip sequences, no automations, no funnel builder. Need separate tool (ConvertKit, etc.) connected via webhooks.

11. **No native gamification.** Unlike Skool (leaderboards, levels, points), Whop has nothing built-in for gamifying engagement.

### Platform Concerns

12. **Marketplace reputation.** Whop Discover is flooded with get-rich-quick and low-quality communities. Being associated with the platform could hurt brand perception for discerning audiences. "Hustler/crypto culture" vibes.

13. **Platform dependency.** Your community, content, and customer data live on Whop. Limited data export. If Whop changes terms or goes down, you're affected.

14. **Support is inconsistent.** Multiple reviewers report slow replies. During disputes, users report being bounced around with no resolution. No live support.

15. **Discord claim step is manual.** Members must click "Claim Access" after purchase. It's not automatic. Some will miss it and think they didn't get access. Plan for this in onboarding flow.

16. **Mobile app has bugs.** Reports of glitchy video playback, freezing during courses, and progress tracking inconsistencies.

17. **Dashboard complexity.** New users find the admin interface overwhelming. Settings are scattered across different areas.

### What IS Good

- Zero upfront cost ($0/month to start)
- Built-in affiliate system with automatic payouts
- Flexible pricing (mix one-time + recurring in one store)
- Discord integration is solid once configured
- Competitive processing rates (2.7% + $0.30)
- Global reach (195 countries, crypto, BNPL)
- 20+ free apps to install
- Mobile app rated 4.8 stars (23K+ reviews)
- Custom domain support included free

---

## 8. Affiliate Program Setup

### How It Works
- Whop has built-in affiliate program (Dashboard > Marketing > Affiliates)
- Default commission: 30% of referred sales
- Customizable: set different rates for global affiliates vs member affiliates
- Can set individual deals per affiliate (email, custom percentage, one-time or recurring)
- **30-day payout delay** between purchase and affiliate commission (protects against refund gaming)
- Whop handles all affiliate payments automatically

### Types of Affiliates
1. **Global affiliates:** Anyone with a referral link (default 30%)
2. **Member affiliates:** Existing members who refer others (can set higher rate, e.g., 50%)
3. **Individual affiliates:** Custom deals for specific people

### How Members Get Links
- Members click "Copy link to store page" or "Copy direct checkout link"
- Links are automatically affiliated with their account
- Affiliates have a dashboard to track performance

---

## 9. Recommended Setup for Ben's Community

### Product Configuration
1. **Founding Member** -- $29/month, stock limit 50, includes Discord + Chat + Forums + Content + Files + Announcements
2. **Standard Member** -- $49/month, unlimited, includes all of above + Courses + Calendar Bookings + premium content
3. **Prompt Pack** -- $19 one-time, includes Files app with download
4. **AI Workflow Templates** -- $29 one-time, includes Files app with download
5. **Free Community** -- $0, includes Chat (limited channels only)

### Discord Mapping
- Founding Member product -> @Founding-Member Discord role
- Standard Member product -> @Standard-Member Discord role
- On cancellation: "Remove given roles" (keeps them in server but removes access)

### Affiliate Setup
- Member affiliate rate: 30% recurring
- Global affiliate rate: 20%
- Encourage founding members to refer others

### Migration Path
- Start on Whop (free to launch, low risk)
- If revenue exceeds $3-5K/month, evaluate Skool ($99/mo flat) or self-hosted
- Keep email list independently (ConvertKit/Beehiiv) from day one for portability

---

## Sources

- Whop Docs -- Fees: https://docs.whop.com/fees
- Whop Docs -- Set Up Pricing: https://docs.whop.com/set-up-products-pricing
- Whop Docs -- Affiliate Program: https://docs.whop.com/manage-your-business/growth-marketing/affiliate-program
- Whop Docs -- Discord Intro: https://docs.whop.com/discord-intro
- Whop Blog -- Link Whop to Discord: https://whop.com/blog/link-whop-to-discord/
- Whop Blog -- Paid Discord Server: https://whop.com/blog/paid-discord-server/
- Whop Blog -- Discord Roles: https://whop.com/blog/adding-discord-roles/
- Whop Blog -- Membership Tiers Discord: https://whop.com/blog/membership-tiers-discord/
- Whop Blog -- Pricing Options: https://whop.com/blog/whop-pricing-options/
- Whop Blog -- How to Sell Digital Products: https://whop.com/blog/how-to-sell-digital-products/
- Whop Blog -- What Is a Whop: https://whop.com/blog/what-is-a-whop/
- Whop Blog -- Consumer Affiliates: https://whop.com/blog/consumer-affiliates/
- Whop Blog -- AI Online Courses: https://whop.com/blog/ai-online-courses/
- Whop Help -- Discord Access: https://help.whop.com/en/articles/10415357-how-to-get-access-to-a-discord-server
- SchoolMaker -- Whop Pricing 2026: https://www.schoolmaker.com/blog/whop-pricing
- SchoolMaker -- Whop Review 2026: https://www.schoolmaker.com/blog/whop-review
- BloggingX -- Whop Review 2026: https://bloggingx.com/whop-review/
- Dodo Payments -- Whop Review 2026: https://dodopayments.com/blogs/whop-review
- EntreResource -- $63K in 60 Days Review: https://entreresource.com/whop-review/
- CourseplatformsReview -- Whop: https://www.courseplatformsreview.com/blog/whop/
- Zumvu -- Whop Review 2026: https://blog.zumvu.com/whop-review
- CommunityPlaybooks -- Skool vs Circle vs Whop: https://www.communityplaybooks.com/articles/how-to-find-your-perfect-community-hosting-platform-skool-vs-circle-vs-whop/
- Whop Discover -- AI Automation Academy: https://whop.com/discover/argus-ai-automation-academy/
- Wikipedia -- Whop: https://en.wikipedia.org/wiki/Whop.com
- CanvasBusinessModel -- How Whop Works: https://canvasbusinessmodel.com/blogs/how-it-works/whop-how-it-works

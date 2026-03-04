# Business Execution: Online Review Monitoring + AI Response Drafting

## Objective
Build and launch an autonomous service that monitors business reviews across Google, Yelp, and Facebook, and drafts on-brand AI responses for the owner to approve and post.

## Phase 1: Infrastructure Setup
- [ ] **Data Scraper (Cron-driven):** Python script to pull reviews from Google Places API and Yelp Fusion API.
- [ ] **Response Engine:** GPT-4o powered drafting logic using the business's "Brand Voice" guide.
- [ ] **Deliver Channel (AgentMail):** Outbound email service to send drafts to the client (e.g., `reviews@cortana-ops.com`).
- [ ] **Payment Bridge:** Stripe Checkout link generation.

## Phase 2: The "Cortana-Ops" Landing Page
- [ ] One-page site built in the workspace.
- [ ] Simple "Enter your Business Name" onboarding.
- [ ] Tiered pricing ($149 / $297 / $497).

## Phase 3: Live Test
- [ ] Select a local test business (Ben's choice or a random local plumber).
- [ ] Run the first 24-hour monitoring cycle.
- [ ] Show Ben the first drafted response in Telegram topic 31.

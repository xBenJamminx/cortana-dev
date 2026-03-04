#!/usr/bin/env python3
"""Generate Client Acquisition Execution Plan PDF"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)

# Colors
DARK = HexColor("#1a1a2e")
ACCENT = HexColor("#6c63ff")
ACCENT_LIGHT = HexColor("#e8e6ff")
TEXT = HexColor("#2d2d2d")
MUTED = HexColor("#666666")
WHITE = HexColor("#ffffff")
SUCCESS = HexColor("#10b981")
WARNING = HexColor("#f59e0b")
BG_LIGHT = HexColor("#f8f9fa")

def build_pdf():
    output_path = "/root/.openclaw/workspace/output/Client-Acquisition-Plan.pdf"
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        topMargin=0.6*inch,
        bottomMargin=0.6*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle', parent=styles['Title'],
        fontSize=28, leading=34, textColor=DARK,
        spaceAfter=4, fontName='Helvetica-Bold'
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Normal'],
        fontSize=13, leading=18, textColor=ACCENT,
        spaceAfter=20, fontName='Helvetica-Bold'
    )
    h1_style = ParagraphStyle(
        'H1', parent=styles['Heading1'],
        fontSize=20, leading=26, textColor=DARK,
        spaceBefore=24, spaceAfter=10, fontName='Helvetica-Bold'
    )
    h2_style = ParagraphStyle(
        'H2', parent=styles['Heading2'],
        fontSize=15, leading=20, textColor=ACCENT,
        spaceBefore=16, spaceAfter=8, fontName='Helvetica-Bold'
    )
    h3_style = ParagraphStyle(
        'H3', parent=styles['Heading3'],
        fontSize=12, leading=16, textColor=DARK,
        spaceBefore=12, spaceAfter=6, fontName='Helvetica-Bold'
    )
    body_style = ParagraphStyle(
        'Body', parent=styles['Normal'],
        fontSize=10, leading=15, textColor=TEXT,
        spaceAfter=6
    )
    bullet_style = ParagraphStyle(
        'Bullet', parent=body_style,
        leftIndent=20, bulletIndent=8,
        spaceAfter=4
    )
    email_style = ParagraphStyle(
        'Email', parent=styles['Normal'],
        fontSize=9.5, leading=14, textColor=HexColor("#333333"),
        leftIndent=16, rightIndent=16, spaceAfter=4,
        fontName='Courier', backColor=BG_LIGHT
    )
    callout_style = ParagraphStyle(
        'Callout', parent=body_style,
        fontSize=11, leading=16, textColor=DARK,
        leftIndent=12, borderPadding=8,
        fontName='Helvetica-BoldOblique'
    )
    check_style = ParagraphStyle(
        'Check', parent=body_style,
        leftIndent=24, bulletIndent=10,
        spaceAfter=3, fontSize=10
    )

    content = []

    def hr():
        content.append(Spacer(1, 6))
        content.append(HRFlowable(width="100%", thickness=1, color=HexColor("#e0e0e0")))
        content.append(Spacer(1, 6))

    def add_table(headers, rows, col_widths=None):
        data = [headers] + rows
        if not col_widths:
            col_widths = [doc.width / len(headers)] * len(headers)
        t = Table(data, colWidths=col_widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), ACCENT),
            ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('TEXTCOLOR', (0, 1), (-1, -1), TEXT),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, HexColor("#e0e0e0")),
            ('BACKGROUND', (0, 1), (-1, -1), WHITE),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [WHITE, BG_LIGHT]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ]))
        content.append(t)
        content.append(Spacer(1, 12))

    # ========== TITLE PAGE ==========
    content.append(Spacer(1, 120))
    content.append(Paragraph("Client Acquisition", title_style))
    content.append(Paragraph("Execution Plan", title_style))
    content.append(Spacer(1, 8))
    content.append(Paragraph("Land first Parker &amp; Taylor clients. Pipeline from zero to revenue in 30 days.", subtitle_style))
    content.append(Spacer(1, 30))
    content.append(HRFlowable(width="40%", thickness=2, color=ACCENT))
    content.append(Spacer(1, 20))
    content.append(Paragraph("Parker & Taylor  |  February 2026", ParagraphStyle(
        'DateLine', parent=body_style, fontSize=11, textColor=MUTED, alignment=TA_LEFT
    )))
    content.append(Spacer(1, 40))

    # Problem box
    problem_data = [
        ['THE SITUATION'],
        ['Pipeline: EMPTY  |  X: Suspended  |  Strategy docs: Great  |  Execution: Zero']
    ]
    t = Table(problem_data, colWidths=[doc.width])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), HexColor("#dc2626")),
        ('TEXTCOLOR', (0, 0), (0, 0), WHITE),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 11),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('BACKGROUND', (0, 1), (0, 1), HexColor("#fef2f2")),
        ('TEXTCOLOR', (0, 1), (0, 1), HexColor("#991b1b")),
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (0, 1), 10),
        ('ALIGN', (0, 1), (0, 1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 1, HexColor("#dc2626")),
    ]))
    content.append(t)

    content.append(PageBreak())

    # ========== CHANNEL 1: COLD EMAIL ==========
    content.append(Paragraph("CHANNEL 1", subtitle_style))
    content.append(Paragraph("Cold Email via Apollo", h1_style))
    content.append(Paragraph(
        "Highest volume, lowest time per touch. Runs on autopilot once set up. "
        "Apollo does everything: lead sourcing, contact data, email sequences, AND domain warmup. "
        "Setup: 2-3 hours one-time, then 30 min/week to review replies.", body_style))
    hr()

    content.append(Paragraph("Setup Checklist", h2_style))
    for item in [
        "Sign up for Apollo Basic ($49/mo) or start the 14-day free trial",
        "Buy a sending domain (NOT your main domain, use parkerandtaylor.co or similar)",
        "Connect sending domain to Apollo and START WARMUP immediately (2-week bottleneck)",
        "Build your 3 target lists (see below)",
        "Load email sequences into Apollo"
    ]:
        content.append(Paragraph(f"\u2610  {item}", check_style))

    content.append(Spacer(1, 8))
    content.append(Paragraph("Target Lists to Build in Apollo", h2_style))
    content.append(Paragraph("Build 3 separate lists (200-300 contacts each to start):", body_style))

    content.append(Paragraph("List 1: Hiring Signal", h3_style))
    for b in [
        "Filter: Companies hiring for Ops Manager, RevOps, Implementation, EA",
        "Company size: 5-50 employees",
        "Industry: Professional services, real estate, financial services, agencies",
        "Why: If they're hiring ops, they have ops pain. Your automation is cheaper than a hire."
    ]:
        content.append(Paragraph(f"\u2022  {b}", bullet_style))

    content.append(Paragraph("List 2: Founder-Led Services", h3_style))
    for b in [
        "Filter: CEO/Founder titles at companies with 5-30 employees",
        "Industry: Consulting, real estate, law, financial advisory, agencies",
        "Revenue: $1M-$20M",
        "Why: These people personally feel the ops burden. They're your buyer."
    ]:
        content.append(Paragraph(f"\u2022  {b}", bullet_style))

    content.append(Paragraph("List 3: Growth Signal", h3_style))
    for b in [
        "Filter: Recent funding, acquisitions, or headcount growth",
        "Company size: 10-50 employees",
        "Why: Growth = new operational complexity. Perfect timing for your offer."
    ]:
        content.append(Paragraph(f"\u2022  {b}", bullet_style))

    content.append(Spacer(1, 8))
    content.append(Paragraph("Email Sequences", h2_style))

    content.append(Paragraph("Sequence 1: Hiring Intercept", h3_style))
    content.append(Paragraph("<b>Subject:</b> Quick thought on your [Role] hire", email_style))
    content.append(Spacer(1, 4))
    for line in [
        "Hey {firstName},",
        "",
        "Saw you're looking for a {jobTitle}. Before you commit to the full-time cost,",
        "worth knowing: most of the manual ops work that role would handle can be",
        "automated in about 30 days.",
        "",
        "I recently did this for an investment firm. Cut 10+ hours/week of manual",
        "reporting and deal flow processing. No new hire needed.",
        "",
        "Not saying skip the hire entirely. Just might change the scope (and salary)",
        "you need.",
        "",
        "Worth a 15-minute call to see if any of that applies?",
        "",
        "Ben"
    ]:
        content.append(Paragraph(line if line else "&nbsp;", email_style))

    content.append(Spacer(1, 8))
    content.append(Paragraph("<b>Follow-up (Day 3):</b> Just bumping this up. Happy to share a quick example of what 'automating the ops bottleneck' actually looks like. No pitch, just context. 15 minutes?", email_style))
    content.append(Spacer(1, 4))
    content.append(Paragraph("<b>Final (Day 7):</b> I'll keep it short. If operational overhead ever becomes a priority, I help lean teams automate the manual stuff instead of adding headcount. Standing offer for a diagnostic chat whenever timing works.", email_style))

    content.append(Spacer(1, 10))
    content.append(Paragraph("Sequence 2: Founder Outreach", h3_style))
    content.append(Paragraph("<b>Subject:</b> Saving {companyName} 10+ hrs/week", email_style))
    content.append(Spacer(1, 4))
    for line in [
        "Hey {firstName},",
        "",
        "Running a {employeeCount}-person team means you're probably doing a lot of",
        "operational work yourself. Reporting, CRM updates, client onboarding, follow-ups.",
        "",
        "I help founder-led companies automate those workflows. Not the 'AI will change",
        "everything' pitch. Practical stuff: I identify your biggest time sink and build",
        "the automation in 30 days.",
        "",
        "Recently did this for an investment firm. They went from 15+ hours/week of",
        "manual ops to under 3.",
        "",
        "Would a 15-min diagnostic call be useful? I'll tell you exactly what's",
        "automatable and what's not.",
        "",
        "Ben"
    ]:
        content.append(Paragraph(line if line else "&nbsp;", email_style))

    content.append(Spacer(1, 10))
    content.append(Paragraph("Volume Targets", h2_style))
    add_table(
        ['Timeframe', 'Daily Volume', 'Expected Results'],
        [
            ['Week 1-2', 'Domain warming (no sends)', 'Patience'],
            ['Week 3', '25 emails/day', '4-6 replies/week'],
            ['Week 4+', '50 emails/day', '8-12 replies/week, 2-4 calls/week'],
        ],
        [doc.width*0.3, doc.width*0.35, doc.width*0.35]
    )

    content.append(PageBreak())

    # ========== CHANNEL 2: LINKEDIN ==========
    content.append(Paragraph("CHANNEL 2", subtitle_style))
    content.append(Paragraph("LinkedIn Outbound", h1_style))
    content.append(Paragraph(
        "Warmer than email. People see your face, your content, your profile. "
        "Higher conversion per touch. Time: 30-45 min/day.", body_style))
    hr()

    content.append(Paragraph("Daily Routine (Non-Negotiable)", h2_style))
    for time, task in [
        ("15 min", "Comment on 5-10 posts from target accounts. Thoughtful comments, not 'great post!' This gets you on their radar BEFORE you DM them."),
        ("15 min", "Send 5-10 connection requests with a personalized note."),
        ("15 min", "Follow up with existing connections who accepted but haven't replied.")
    ]:
        content.append(Paragraph(f"<b>{time}:</b> {task}", bullet_style))

    content.append(Spacer(1, 8))
    content.append(Paragraph("Weekly Targets", h2_style))
    add_table(
        ['Activity', 'Weekly Target', 'Goal'],
        [
            ['Connection requests', '50', 'Build pipeline'],
            ['Follow-up messages', '25', 'Convert connections'],
            ['Comments/day', '10', 'Visibility'],
            ['Conversations', '3-5', 'Qualify leads'],
            ['Calls booked', '1-2', 'Close deals'],
        ],
        [doc.width*0.35, doc.width*0.3, doc.width*0.35]
    )

    content.append(Paragraph("Profile Optimization (Do This First)", h2_style))
    for item in [
        'Headline: "I help lean teams automate ops instead of hiring. Founder @ Parker &amp; Taylor."',
        'Banner: Simple, clean. "AI automation for operators."',
        "About section: Problem > solution > proof > CTA. Reference Five Points results.",
        "Featured section: Pin best post + case study or proposal framework",
        "Turn on Creator Mode"
    ]:
        content.append(Paragraph(f"\u2610  {item}", check_style))

    content.append(Spacer(1, 12))

    # ========== CHANNEL 3: PARTNERSHIPS ==========
    content.append(Paragraph("CHANNEL 3", subtitle_style))
    content.append(Paragraph("Agency Partnerships + Local Meetup", h1_style))
    content.append(Paragraph(
        "Other people sell for you. One relationship = multiple referrals. "
        "Time: 2-3 hours this week, then 30 min/week maintenance.", body_style))
    hr()

    content.append(Paragraph("Agency Partnership Targets", h2_style))
    content.append(Paragraph("Identify 10 people across these categories:", body_style))
    for cat in ["Marketing agency owners", "Business coaches / fractional COOs",
                "Accountants / bookkeepers serving SMBs", "Web development agencies", "HR consultants"]:
        content.append(Paragraph(f"\u2022  {cat}", bullet_style))

    content.append(Spacer(1, 8))
    content.append(Paragraph("Partnership Message Template", h3_style))
    for line in [
        "Hey {Name},",
        "",
        "I specialize in AI automation for small businesses. The kind of stuff your",
        "clients probably ask you about but isn't your core offering.",
        "",
        "If any of your clients ever need help automating their ops (reporting, CRM",
        "workflows, onboarding, follow-ups), I'd love to be your go-to referral.",
        "Happy to kick back 10-15% on anything that comes through.",
        "",
        "No commitment, just putting it out there. Want to hop on a quick call so",
        "I can explain what I do?",
        "",
        "Ben"
    ]:
        content.append(Paragraph(line if line else "&nbsp;", email_style))

    content.append(Spacer(1, 10))
    content.append(Paragraph("Local AI Meetup", h2_style))
    content.append(Paragraph('Title: "AI for Operators: Cut 10+ Hours/Week Without Hiring"', callout_style))
    content.append(Spacer(1, 6))
    for item in [
        "Find venue: coworking space, library, or coffee shop (15-20 people)",
        "Create Lu.ma or Eventbrite page",
        "Post on LinkedIn, local Facebook groups, Meetup.com",
        "Format: 20-min presentation + Q&amp;A + collect emails",
        "Follow up with every attendee within 24 hours"
    ]:
        content.append(Paragraph(f"\u2610  {item}", check_style))

    content.append(PageBreak())

    # ========== WEEKLY SCHEDULE ==========
    content.append(Paragraph("Weekly Execution Schedule", h1_style))
    content.append(Paragraph("Mapped to your existing schedule. No new time blocks needed.", body_style))
    hr()

    content.append(Paragraph("Wednesday (Full Side Business Day)", h2_style))
    content.append(Paragraph("<b>AM Block (9am-12pm): OUTBOUND</b>", body_style))
    for b in [
        "30 min: LinkedIn commenting + DMs",
        "60 min: Review Apollo replies, adjust sequences",
        "60 min: Follow-ups on all channels"
    ]:
        content.append(Paragraph(f"\u2022  {b}", bullet_style))
    content.append(Paragraph("<b>PM Block (1pm-5pm): DELIVERY</b>", body_style))
    for b in ["Work on Five Points or new client delivery", "Mimoo improvements (only if no client work)"]:
        content.append(Paragraph(f"\u2022  {b}", bullet_style))

    content.append(Spacer(1, 8))
    content.append(Paragraph("Thursday PM (Side Business Light)", h2_style))
    content.append(Paragraph("<b>Content Block (1pm-4pm):</b>", body_style))
    for b in ["Batch write 3 LinkedIn posts for next week", "Record 1-2 short-form videos", "Review outbound metrics"]:
        content.append(Paragraph(f"\u2022  {b}", bullet_style))
    content.append(Paragraph("<b>Outbound (4pm-5pm):</b>", body_style))
    for b in ["30 min: LinkedIn DMs + connection requests", "Quick follow-ups"]:
        content.append(Paragraph(f"\u2022  {b}", bullet_style))

    content.append(Spacer(1, 8))
    content.append(Paragraph("Friday (Full Side Business Day)", h2_style))
    content.append(Paragraph("<b>AM (9am-12pm): OUTBOUND</b>", body_style))
    for b in ["30 min: LinkedIn commenting + DMs", "60 min: Apollo list building / sequence tweaks",
              "60 min: Agency partnership outreach + follow-ups"]:
        content.append(Paragraph(f"\u2022  {b}", bullet_style))
    content.append(Paragraph("<b>Midday (12pm-2pm): DELIVERY</b>", body_style))
    content.append(Paragraph("\u2022  Client work or Mimoo build", bullet_style))
    content.append(Paragraph("<b>PM (2pm-5pm): CALLS + CLOSE</b>", body_style))
    for b in ["Diagnostic calls", "Proposals within 24 hours of any call", "Weekly review: what worked, what didn't"]:
        content.append(Paragraph(f"\u2022  {b}", bullet_style))

    content.append(PageBreak())

    # ========== 30-DAY MILESTONES ==========
    content.append(Paragraph("30-Day Milestones", h1_style))
    hr()

    content.append(Paragraph("Week 1 (Feb 26 - Mar 4)", h2_style))
    for item in [
        "Apollo account set up (trial or Basic plan)",
        "Sending domain purchased + warmup started in Apollo",
        "LinkedIn profile optimized",
        "First 50 LinkedIn connection requests sent",
        "10 agency partnership messages sent",
        "Meetup venue identified"
    ]:
        content.append(Paragraph(f"\u2610  {item}", check_style))

    content.append(Paragraph("Week 2 (Mar 5-11)", h2_style))
    for item in [
        "100 cumulative LinkedIn touches",
        "Domain still warming in Apollo (patience)",
        "5+ LinkedIn conversations active",
        "1 diagnostic call booked",
        "Meetup date set and event page live"
    ]:
        content.append(Paragraph(f"\u2610  {item}", check_style))

    content.append(Paragraph("Week 3 (Mar 12-18)", h2_style))
    for item in [
        "Cold email sequences GO LIVE in Apollo (domain warmed)",
        "25-50 cold emails/day sending via Apollo",
        "150+ cumulative LinkedIn touches",
        "2+ diagnostic calls booked",
        "1 proposal sent"
    ]:
        content.append(Paragraph(f"\u2610  {item}", check_style))

    content.append(Paragraph("Week 4 (Mar 19-25)", h2_style))
    for item in [
        "50 cold emails/day steady state",
        "200+ cumulative LinkedIn touches",
        "Meetup hosted",
        "3+ proposals sent",
        "TARGET: 1 deal closed ($6-8k build or $4-6k/mo partnership)"
    ]:
        content.append(Paragraph(f"\u2610  {item}", check_style))

    content.append(Spacer(1, 16))

    # ========== METRICS TABLE ==========
    content.append(Paragraph("Success Metrics (Track Weekly)", h1_style))
    hr()
    add_table(
        ['Metric', 'Weekly Target'],
        [
            ['LinkedIn connection requests', '50'],
            ['LinkedIn DM conversations', '5-10'],
            ['Cold emails sent', '125-250 (once live)'],
            ['Email replies', '5-10'],
            ['Diagnostic calls booked', '2-4'],
            ['Proposals sent', '1-2'],
            ['Deals closed', '1/month minimum'],
        ],
        [doc.width*0.6, doc.width*0.4]
    )

    # ========== TOOLS TABLE ==========
    content.append(Paragraph("Tools Needed", h2_style))
    add_table(
        ['Tool', 'Cost', 'Purpose'],
        [
            ['Apollo Basic', '$49/mo', 'Lead sourcing + email sequences + domain warmup. All-in-one.'],
            ['Sending domain', '$10/yr', 'Protect your main domain reputation'],
            ['Lu.ma', 'Free', 'Meetup event page'],
            ['LinkedIn', 'Free', 'Outbound + content'],
        ],
        [doc.width*0.2, doc.width*0.3, doc.width*0.5]
    )

    # Final callout
    content.append(Spacer(1, 16))
    final_data = [
        ['THE BOTTOM LINE'],
        ['Total monthly cost: ~$50. Target: 1 deal/month ($6-8k build or $4-6k/mo partnership).\nDomain warmup takes 2 weeks. Buy the domain and start warmup in Apollo TODAY.\nLinkedIn works now. No setup delay. Start DMs today.\nDon\'t optimize, execute.']
    ]
    t = Table(final_data, colWidths=[doc.width])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 0), SUCCESS),
        ('TEXTCOLOR', (0, 0), (0, 0), WHITE),
        ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (0, 0), 12),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('BACKGROUND', (0, 1), (0, 1), HexColor("#ecfdf5")),
        ('TEXTCOLOR', (0, 1), (0, 1), HexColor("#065f46")),
        ('FONTNAME', (0, 1), (0, 1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (0, 1), 10),
        ('ALIGN', (0, 1), (0, 1), 'LEFT'),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 16),
        ('BOX', (0, 0), (-1, -1), 1.5, SUCCESS),
    ]))
    content.append(t)

    doc.build(content)
    print(f"PDF generated: {output_path}")

if __name__ == "__main__":
    build_pdf()

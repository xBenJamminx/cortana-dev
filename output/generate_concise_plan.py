#!/usr/bin/env python3
"""Generate concise 2-page Client Acquisition Plan PDF"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)

DARK = HexColor("#1a1a2e")
ACCENT = HexColor("#6c63ff")
TEXT = HexColor("#2d2d2d")
MUTED = HexColor("#666666")
WHITE = HexColor("#ffffff")
BG = HexColor("#f8f9fa")
GREEN = HexColor("#10b981")
RED = HexColor("#dc2626")

def build():
    path = "/root/.openclaw/workspace/output/Client-Acquisition-Plan-Concise.pdf"
    doc = SimpleDocTemplate(path, pagesize=letter,
        topMargin=0.5*inch, bottomMargin=0.5*inch,
        leftMargin=0.65*inch, rightMargin=0.65*inch)

    styles = getSampleStyleSheet()
    title = ParagraphStyle('T', parent=styles['Title'], fontSize=22, leading=26,
        textColor=DARK, spaceAfter=2, fontName='Helvetica-Bold')
    sub = ParagraphStyle('Sub', parent=styles['Normal'], fontSize=11, leading=14,
        textColor=ACCENT, spaceAfter=10, fontName='Helvetica-Bold')
    h1 = ParagraphStyle('H1', parent=styles['Heading1'], fontSize=14, leading=18,
        textColor=DARK, spaceBefore=14, spaceAfter=6, fontName='Helvetica-Bold')
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=11, leading=14,
        textColor=ACCENT, spaceBefore=10, spaceAfter=4, fontName='Helvetica-Bold')
    body = ParagraphStyle('B', parent=styles['Normal'], fontSize=9.5, leading=13,
        textColor=TEXT, spaceAfter=3)
    bullet = ParagraphStyle('Bu', parent=body, leftIndent=16, bulletIndent=6, spaceAfter=2)
    small = ParagraphStyle('Sm', parent=body, fontSize=8.5, leading=11, textColor=MUTED)
    email_style = ParagraphStyle('Em', parent=body, fontSize=8.5, leading=11,
        leftIndent=12, fontName='Courier', backColor=BG, textColor=HexColor("#333"))
    check = ParagraphStyle('Ch', parent=body, leftIndent=18, bulletIndent=6, spaceAfter=2, fontSize=9)

    c = []

    def hr():
        c.append(HRFlowable(width="100%", thickness=0.5, color=HexColor("#ddd")))
        c.append(Spacer(1, 4))

    def tbl(headers, rows, widths=None):
        data = [headers] + rows
        if not widths: widths = [doc.width/len(headers)] * len(headers)
        t = Table(data, colWidths=widths)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), ACCENT),
            ('TEXTCOLOR', (0,0), (-1,0), WHITE),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 8.5),
            ('FONTSIZE', (0,1), (-1,-1), 8.5),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('TEXTCOLOR', (0,1), (-1,-1), TEXT),
            ('GRID', (0,0), (-1,-1), 0.5, HexColor("#e0e0e0")),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, BG]),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
        ]))
        c.append(t)
        c.append(Spacer(1, 6))

    # ===== HEADER =====
    c.append(Paragraph("Client Acquisition Plan", title))
    c.append(Paragraph("3 channels. 30 days. Close the $3.5k/mo gap.", sub))
    hr()

    # ===== CHANNEL 1 =====
    c.append(Paragraph("1. Cold Email (Apollo + Instantly)", h1))
    c.append(Paragraph("Highest volume, runs on autopilot. Setup: 2-3hrs, then 30 min/week.", body))

    c.append(Paragraph("Setup (Do This Week)", h2))
    for item in [
        "Buy sending domain (parkerandtaylor.co or similar, NOT your main domain)",
        "Sign up for Instantly ($30/mo) and START DOMAIN WARMUP immediately (2-week bottleneck)",
        "Sign up for Apollo (free, 10K credits/mo)",
        "Build 3 lists: (1) Hiring ops roles, (2) Founder-led 5-30 person companies, (3) Recently funded/growing",
        "Connect Apollo to Instantly, load sequences"
    ]:
        c.append(Paragraph(f"\u2610  {item}", check))

    c.append(Paragraph("Sequence 1: Hiring Intercept", h2))
    c.append(Paragraph("<b>Subject: Quick thought on your [Role] hire</b>", email_style))
    c.append(Paragraph(
        "Saw you're looking for a {jobTitle}. Before you commit to full-time cost: most of that manual ops work "
        "can be automated in 30 days. I did this for an investment firm, cut 10+ hrs/week. Not saying skip the hire, "
        "just might change the scope you need. Worth a 15-min call?", email_style))
    c.append(Paragraph("<b>Day 3:</b> Bump. Happy to share a quick example. 15 min? | <b>Day 7:</b> Last note. Standing offer for a diagnostic chat.", small))

    c.append(Paragraph("Sequence 2: Founder Outreach", h2))
    c.append(Paragraph("<b>Subject: Saving {companyName} 10+ hrs/week</b>", email_style))
    c.append(Paragraph(
        "Running a {employeeCount}-person team means you're probably doing ops yourself. Reporting, CRM, onboarding, follow-ups. "
        "I help founders automate those in 30 days. Did this for an investment firm, 15+ hrs/week manual ops down to under 3. "
        "Would a 15-min diagnostic call be useful?", email_style))

    c.append(Paragraph("Volume: Weeks 1-2 warmup, Week 3 = 25/day, Week 4+ = 50/day (expect 8-12 replies/week, 2-4 calls)", small))

    # ===== CHANNEL 2 =====
    c.append(Paragraph("2. LinkedIn Outbound", h1))
    c.append(Paragraph("Works TODAY. No setup delay. 30-45 min/day.", body))

    c.append(Paragraph("Daily Routine", h2))
    for item in [
        "<b>15 min:</b> Comment on 5-10 target accounts' posts (get on radar before DMing)",
        "<b>15 min:</b> Send 5-10 connection requests with personalized notes",
        "<b>15 min:</b> Follow up with connections who accepted but haven't replied"
    ]:
        c.append(Paragraph(f"\u2022  {item}", bullet))

    c.append(Paragraph("Targets: 50 connections/week, 25 follow-ups/week, 3-5 real convos, 1-2 calls booked", small))

    c.append(Paragraph("Profile (One-Time)", h2))
    for item in [
        'Headline: "I help lean teams automate ops instead of hiring. Founder @ Parker &amp; Taylor."',
        "About: Problem > solution > proof (Five Points) > CTA",
        "Featured: Pin best post + case study. Turn on Creator Mode."
    ]:
        c.append(Paragraph(f"\u2610  {item}", check))

    # ===== CHANNEL 3 =====
    c.append(Paragraph("3. Agency Partnerships + Local Meetup", h1))
    c.append(Paragraph("Other people sell for you. 2-3 hrs this week, then 30 min/week.", body))

    c.append(Paragraph("Partnerships", h2))
    c.append(Paragraph(
        "Message 10 people (agency owners, business coaches, accountants, web devs): "
        '"I specialize in AI automation for small businesses. If your clients ever ask about AI, '
        "I'd love to be your go-to referral. Happy to kick back 10-15%.\"", body))

    c.append(Paragraph("Meetup", h2))
    c.append(Paragraph(
        '<b>"AI for Operators: Cut 10+ Hours/Week Without Hiring"</b> at a coworking space or library. '
        "20-min talk + Q&amp;A. Collect emails. Follow up within 24hrs. Plan this week, host in 2-3 weeks.", body))

    hr()

    # ===== WEEKLY SCHEDULE =====
    c.append(Paragraph("Weekly Schedule", h1))
    tbl(
        ['Day', 'AM', 'PM'],
        [
            ['Wed (full)', 'OUTBOUND: LinkedIn + Apollo replies + follow-ups', 'DELIVERY: Client work or Mimoo'],
            ['Thu', 'Particle', 'CONTENT: Batch 3 LinkedIn posts + OUTBOUND: 30 min DMs'],
            ['Fri (full)', 'OUTBOUND: LinkedIn + Apollo lists + agency outreach', 'CALLS + CLOSE: Diagnostics, proposals, weekly review'],
        ],
        [doc.width*0.12, doc.width*0.44, doc.width*0.44]
    )

    # ===== 30-DAY MILESTONES =====
    c.append(Paragraph("30-Day Milestones", h1))
    tbl(
        ['Week', 'Milestones', 'Target'],
        [
            ['1', 'Apollo + Instantly set up, warmup started, 50 LinkedIn touches, 10 agency msgs', 'Infrastructure live'],
            ['2', '100 LinkedIn touches, 5+ convos, meetup page live', '1 call booked'],
            ['3', 'Cold email GO LIVE (25-50/day), 150+ LinkedIn touches', '2+ calls, 1 proposal'],
            ['4', '50 emails/day steady, meetup hosted, 200+ LinkedIn touches', '3+ proposals, 1 DEAL CLOSED'],
        ],
        [doc.width*0.08, doc.width*0.62, doc.width*0.30]
    )

    # ===== METRICS =====
    c.append(Paragraph("Weekly Scorecard", h1))
    tbl(
        ['Metric', 'Target'],
        [
            ['LinkedIn connections sent', '50/week'],
            ['LinkedIn conversations', '5-10/week'],
            ['Cold emails sent', '125-250/week (once live)'],
            ['Replies (all channels)', '10-15/week'],
            ['Diagnostic calls', '2-4/week'],
            ['Proposals sent', '1-2/week'],
            ['Deals closed', '1/month minimum'],
        ],
        [doc.width*0.55, doc.width*0.45]
    )

    # ===== BOTTOM LINE =====
    box = [
        ['DO TODAY'],
        ['1. Buy sending domain + start Instantly warmup (2-week bottleneck)\n'
         '2. Optimize LinkedIn profile\n'
         '3. Send first 10 LinkedIn connection requests\n'
         '4. Sign up for Apollo\n\n'
         'Total cost: ~$35/mo. One deal at $6-8k eliminates burn for 2 months.']
    ]
    t = Table(box, colWidths=[doc.width])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (0,0), GREEN),
        ('TEXTCOLOR', (0,0), (0,0), WHITE),
        ('FONTNAME', (0,0), (0,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (0,0), 10),
        ('ALIGN', (0,0), (0,0), 'CENTER'),
        ('BACKGROUND', (0,1), (0,1), HexColor("#ecfdf5")),
        ('TEXTCOLOR', (0,1), (0,1), HexColor("#065f46")),
        ('FONTNAME', (0,1), (0,1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,1), (0,1), 9.5),
        ('LEADING', (0,1), (0,1), 14),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 1.5, GREEN),
    ]))
    c.append(t)

    doc.build(c)
    print(f"PDF: {path}")

if __name__ == "__main__":
    build()

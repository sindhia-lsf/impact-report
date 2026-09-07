#!/usr/bin/env python3
"""Generate Black Tech Week 2026 impact report artifacts from aggregate JSON."""

from __future__ import annotations

import html
import json
import math
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "impact-summary.json"
ARTIFACTS = ROOT / "artifacts"
ARTIFACTS.mkdir(parents=True, exist_ok=True)


def money(value: float | int | None) -> str:
    if value is None:
        return "n/a"
    value = float(value)
    if abs(value) >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    if abs(value) >= 1_000:
        return f"${value / 1_000:.0f}K"
    return f"${value:,.0f}"


def num(value: float | int | None, digits: int = 0) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float) and not value.is_integer():
        return f"{value:,.{digits}f}"
    return f"{int(value):,}"


def pct(value: float | int | None) -> str:
    return "n/a" if value is None else f"{float(value):.1f}%"


def text_escape(value: object) -> str:
    return escape(str(value), {'"': "&quot;"})


def load_summary() -> dict:
    return json.loads(DATA.read_text())


def report_model(summary: dict) -> dict:
    reach = summary["reach"]
    geo = summary["geography"]
    fb = summary["foundersAndBusiness"]
    equity = summary["equityAndInclusion"]
    econ = summary["economicImpact"]
    actual = next(s for s in econ["scenarios"] if s["scenario_key"] == "actual_badged")
    registered = next(s for s in econ["scenarios"] if s["scenario_key"] == "registered_offline")
    virtual = summary["virtualPerformance"]["totals"]
    top_markets = ", ".join(m["label"] for m in geo["topMarkets"][:6])
    top_states = ", ".join(f"{s['label']} ({num(s['count'])})" for s in geo["topStates"][:5])
    race = summary["equityAndInclusion"]["raceEthnicity"]
    gender = summary["equityAndInclusion"]["gender"]

    headlines = [
        f"Black Tech Week 2026 reached an estimated {num(reach['estimatedGrossFootprint'])} people across verified onsite attendance, community partner events, meetup attendance, and YouTube unique viewers.",
        f"The broader demand signal was {num(reach['registrationAndDigitalDemandSignals'])}: BTW registrations, meetup RSVPs, and YouTube unique viewers.",
        f"The registered audience represented {num(geo['statesRepresented'])} states and {num(geo['zipCodesRepresented'])} ZIP codes, with top non-local markets including {top_markets}.",
        f"Founder and business density was a core strength: {num(fb['founders'])} founders, {num(fb['executives'])} executives, and {num(fb['uniqueOrganizations'])} unique organizations appeared in the aggregate dataset.",
        f"The modeled actual-attendee economic impact is {money(actual['total_impact'])}, including {money(actual['visitor_spending'])} in visitor spending and {num(actual['room_nights'])} modeled room nights.",
        f"Virtual distribution added {num(virtual['uniqueViewers'])} unique viewers, {num(virtual['views'])} views, {num(virtual['watchHours'], 1)} watch hours, and {num(virtual['subscribersGained'])} subscribers gained.",
        f"{num(equity['distressedZipcodeRegistrations'])} BTW registrations, or {pct(equity['distressedZipcodeRegistrationsPct'])}, came from distressed ZIP-code areas; Bootcamp attendees showed {pct(equity['bootcampDistressedAttendeesPct'])} distressed-area representation.",
    ]

    executive_summary = (
        "Black Tech Week 2026 created a multi-channel impact footprint that combined a flagship in-person convening, "
        "virtual distribution, year-round meetup engagement, founder pipeline development, and community partner activity. "
        f"Using aggregate dashboard data, the event reached an estimated {num(reach['estimatedGrossFootprint'])} people across actual in-person badge-printed attendees, community partner events, confirmed meetup attendance, and YouTube unique viewers. "
        f"The broader demand signal was {num(reach['registrationAndDigitalDemandSignals'])} when active Black Tech Week registrations, meetup RSVPs, and YouTube unique viewers are combined. "
        f"The audience was geographically distributed across {num(geo['statesRepresented'])} states and {num(geo['zipCodesRepresented'])} ZIP codes, demonstrating that the Cincinnati-based program reaches well beyond the host city while still building dense local and regional engagement.\n\n"
        f"For sponsors and civic partners, the strongest story is the combination of economic activity and founder concentration. The actual-attendee economic impact model estimates {money(actual['total_impact'])} in total impact, including {money(actual['visitor_spending'])} in visitor spending, {money(actual['lodging_revenue'])} in lodging revenue, and {num(actual['room_nights'])} room nights. "
        f"The registered-onsite scenario shows the upper demand-based opportunity at {money(registered['total_impact'])}. These figures should be presented as modeled estimates using stated assumptions, not audited financial results.\n\n"
        f"Black Tech Week also attracted the audience sponsors care about: {num(fb['founders'])} founders, {num(fb['executives'])} executives, {num(fb['uniqueOrganizations'])} unique organizations, {num(fb['sessions'])} sessions, and {num(fb['speakerCount'])} speakers. "
        f"Programming depth was visible in session engagement, with {num(fb['sessionUniqueAttendees'])} unique scanned session attendees, {num(fb['sessionScans'])} total session scans, and {pct(fb['twoPlusSessionPct'])} of engaged attendees scanning into two or more sessions. "
        f"The inclusion story is similarly strong: {num(equity['distressedZipcodeRegistrations'])} registrations came from distressed ZIP-code areas, and the aggregate demographic data shows a predominantly Black audience with majority women representation among disclosed responses."
    )

    sections = [
        ("Purpose and Audience", [
            "Position Black Tech Week 2026 as a sponsor-ready platform for founder access, inclusive economic development, and regional visibility.",
            "Use modeled economic impact carefully and distinguish verified attendance, registrations, digital reach, and demand signals.",
        ]),
        ("Total Footprint Reached", [
            f"Verified and modeled impact footprint: {num(reach['estimatedGrossFootprint'])}.",
            f"Demand and digital signal: {num(reach['registrationAndDigitalDemandSignals'])}.",
            f"Channels: {num(reach['btwActualInPersonBadgePrinted'])} actual in-person badge prints, {num(reach['communityPartnerEventAttendees'])} community partner event attendees, {num(reach['meetupActualAttended'])} confirmed meetup attendees, and {num(virtual['uniqueViewers'])} YouTube unique viewers.",
        ]),
        ("Geographic Reach", [
            f"Audience origin spans {num(geo['statesRepresented'])} states and {num(geo['zipCodesRepresented'])} ZIP codes.",
            f"Mapped visitor mix: {num(geo['localVisitors'])} local, {num(geo['regionalVisitors'])} regional, {num(geo['overnightVisitors'])} overnight, and {num(geo['outOfStateVisitors'])} out-of-state visitors.",
            f"Top states by registration volume: {top_states}.",
        ]),
        ("Economic Impact", [
            f"Actual attendee scenario: {money(actual['total_impact'])} total modeled impact, {money(actual['direct_impact'])} direct impact, and {money(actual['indirect_induced_impact'])} indirect/induced impact.",
            f"Registered onsite scenario: {money(registered['total_impact'])} total modeled impact based on registered onsite mix.",
            f"Community partner nightlife/event impact adds {money(econ['communityPartnerEconomicImpactWithMultiplier'])} with multiplier assumptions.",
        ]),
        ("Founder and Business Empowerment", [
            f"{num(fb['founders'])} founders, {num(fb['executives'])} executives, and {num(fb['uniqueOrganizations'])} unique organizations are visible in the registration dataset.",
            f"Session activity produced {num(fb['sessionScans'])} scans across tracked programming, with {pct(fb['twoPlusSessionPct'])} of engaged attendees attending two or more sessions.",
            f"The Bootcamp pipeline adds {num(fb['bootcampInterest'])} interest records, {num(fb['bootcampApplications'])} applications, and {num(fb['bootcampAttendees'])} attendees across {num(fb['bootcampCities'])} cities.",
        ]),
        ("Equity and Inclusion", [
            f"{num(equity['distressedZipcodeRegistrations'])} registrations came from distressed ZIP-code areas ({pct(equity['distressedZipcodeRegistrationsPct'])}).",
            f"Bootcamp distressed-area representation: {pct(equity['bootcampDistressedInterestPct'])} of interest, {pct(equity['bootcampDistressedApplicationsPct'])} of applications, and {pct(equity['bootcampDistressedAttendeesPct'])} of attendees.",
            f"Race/ethnicity top disclosed aggregate: {race[0]['label']} at {num(race[0]['count'])}. Gender top disclosed aggregate: {gender[0]['label']} at {num(gender[0]['count'])}.",
        ]),
        ("Sponsor Pitch Implications", [
            "Lead with founder density, national distribution, and measurable programming depth.",
            "Use the economic model to show why the host region benefits from sponsor investment.",
            "Offer sponsors category-specific ways to activate: founder services, hiring, capital access, civic innovation, hospitality, and content distribution.",
        ]),
        ("Data Notes", [
            "All figures are aggregate-only and generated from local dashboard APIs, Postgres aggregate queries, and command-center virtual performance snapshots.",
            "Economic impact figures are modeled estimates based on local assumptions; they are suitable for sponsor/executive pitch materials but should be labeled accordingly.",
            "No personal identifiers are included in this report package.",
        ]),
    ]

    slides = [
        ("Black Tech Week 2026 Impact", "Sponsor Outreach + Executive Pitch Report", [
            f"{num(reach['estimatedGrossFootprint'])} estimated gross footprint",
            f"{num(geo['statesRepresented'])} states | {num(geo['zipCodesRepresented'])} ZIP codes",
            f"{money(actual['total_impact'])} modeled actual-attendee economic impact",
        ]),
        ("Impact At A Glance", "A cross-channel platform, not a single event", [
            f"{num(reach['btwActualInPersonBadgePrinted'])} actual in-person badge prints",
            f"{num(reach['communityPartnerEventAttendees'])} community partner event attendees",
            f"{num(reach['meetupActualAttended'])} confirmed meetup attendees",
            f"{num(virtual['uniqueViewers'])} YouTube unique viewers",
        ]),
        ("National + Regional Footprint", "Reach radiates from Cincinnati into national markets", [
            f"{num(geo['statesRepresented'])} states represented",
            f"{num(geo['zipCodesRepresented'])} ZIP codes represented",
            f"{num(geo['outOfStateVisitors'])} out-of-state visitors",
            f"Top markets: {top_markets}",
        ]),
        ("Economic Impact", "Modeled value for the host city and region", [
            f"{money(actual['total_impact'])} actual-attendee modeled impact",
            f"{money(actual['visitor_spending'])} visitor spending",
            f"{num(actual['room_nights'])} modeled room nights",
            f"{money(registered['total_impact'])} registered-onsite demand scenario",
        ]),
        ("Founder + Business Density", "Sponsors get access to the audience they want", [
            f"{num(fb['founders'])} founders",
            f"{num(fb['executives'])} executives",
            f"{num(fb['uniqueOrganizations'])} unique organizations",
            f"{num(fb['speakerCount'])} speakers across {num(fb['sessions'])} sessions",
        ]),
        ("Programming Depth", "Engagement extended beyond attendance", [
            f"{num(fb['sessionUniqueAttendees'])} unique scanned session attendees",
            f"{num(fb['sessionScans'])} total session scans",
            f"{pct(fb['twoPlusSessionPct'])} attended two or more sessions",
            f"{num(fb['avgSessionsPerEngagedAttendee'], 1)} avg sessions per engaged attendee",
        ]),
        ("Inclusive Reach", "Aggregate demographics and distressed-area participation", [
            f"{num(equity['distressedZipcodeRegistrations'])} distressed-ZIP registrations",
            f"{pct(equity['distressedZipcodeRegistrationsPct'])} of BTW registrations",
            f"{pct(equity['bootcampDistressedAttendeesPct'])} of Bootcamp attendees from distressed areas",
            f"{num(race[0]['count'])} {race[0]['label']} aggregate responses",
        ]),
        ("Virtual Distribution", "YouTube Live extended BTW beyond the venue", [
            f"{num(virtual['views'])} views",
            f"{num(virtual['uniqueViewers'])} unique viewers",
            f"{num(virtual['watchHours'], 1)} watch hours",
            f"{num(virtual['subscribersGained'])} subscribers gained",
        ]),
        ("Sponsor Storyline", "Why this matters", [
            "Black Tech Week concentrates founders, operators, executives, and community audiences in one measurable platform.",
            "The host region benefits through visitor spend, lodging, local mobility, nightlife, and partner activity.",
            "Sponsors can align with capital access, talent, founder services, civic innovation, and national content distribution.",
        ]),
    ]

    return {
        "headlines": headlines,
        "executive_summary": executive_summary,
        "sections": sections,
        "slides": slides,
        "actual": actual,
        "registered": registered,
    }


def w_p(text: str, style: str | None = None) -> str:
    style_xml = f'<w:pPr><w:pStyle w:val="{style}"/></w:pPr>' if style else ""
    lines = str(text).split("\n")
    runs = []
    for i, line in enumerate(lines):
        if i:
            runs.append("<w:r><w:br/></w:r>")
        runs.append(f"<w:r><w:t>{text_escape(line)}</w:t></w:r>")
    return f"<w:p>{style_xml}{''.join(runs)}</w:p>"


def w_table(rows: list[list[str]]) -> str:
    cells = []
    for row in rows:
        tds = "".join(f"<w:tc><w:p><w:r><w:t>{text_escape(cell)}</w:t></w:r></w:p></w:tc>" for cell in row)
        cells.append(f"<w:tr>{tds}</w:tr>")
    return f"<w:tbl><w:tblPr><w:tblW w:w=\"5000\" w:type=\"pct\"/></w:tblPr>{''.join(cells)}</w:tbl>"


def make_docx(summary: dict, model: dict) -> Path:
    reach = summary["reach"]
    geo = summary["geography"]
    fb = summary["foundersAndBusiness"]
    equity = summary["equityAndInclusion"]
    actual = model["actual"]
    registered = model["registered"]

    body = [
        w_p("Black Tech Week 2026 Impact Report", "Title"),
        w_p("Sponsor Outreach + Executive Pitch Narrative", "Subtitle"),
        w_p(f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} from aggregate-only local dashboard data."),
        w_p("Executive Summary", "Heading1"),
        w_p(model["executive_summary"]),
        w_p("Headline Claims", "Heading1"),
    ]
    body.extend(w_p(item, "ListParagraph") for item in model["headlines"])
    body.append(w_p("Core Metrics", "Heading1"))
    body.append(w_table([
        ["Metric", "Value"],
        ["Estimated gross impact footprint", num(reach["estimatedGrossFootprint"])],
        ["Broader registration/digital demand signal", num(reach["registrationAndDigitalDemandSignals"])],
        ["Active BTW registrations", num(reach["btwActiveRegistrations"])],
        ["Actual in-person badge prints", num(reach["btwActualInPersonBadgePrinted"])],
        ["YouTube unique viewers", num(reach["youtubeUniqueViewers"])],
        ["Confirmed meetup attendance", num(reach["meetupActualAttended"])],
        ["States represented", num(geo["statesRepresented"])],
        ["ZIP codes represented", num(geo["zipCodesRepresented"])],
        ["Founders", num(fb["founders"])],
        ["Unique organizations", num(fb["uniqueOrganizations"])],
        ["Distressed ZIP registrations", f"{num(equity['distressedZipcodeRegistrations'])} ({pct(equity['distressedZipcodeRegistrationsPct'])})"],
        ["Actual-attendee modeled economic impact", money(actual["total_impact"])],
        ["Registered-onsite modeled economic opportunity", money(registered["total_impact"])],
    ]))
    body.append(w_p("Detailed Impact Findings", "Heading1"))
    body.append(w_p(
        f"Black Tech Week 2026 should be presented as a multi-channel platform anchored in Cincinnati, not only as a three-day event. "
        f"The verified event-attendance layer includes {num(reach['btwActualInPersonBadgePrinted'])} in-person badge prints, while the larger demand layer includes {num(reach['btwActiveRegistrations'])} active registrations. "
        f"This distinction matters for executive and sponsor conversations: badge prints show actual onsite participation, registrations show market demand and intent, and digital/meetup/community measures show the reach that extends beyond the core venue."
    ))
    body.append(w_p(
        f"The footprint story is strongest when framed through complementary channels. The estimated gross footprint of {num(reach['estimatedGrossFootprint'])} combines actual in-person badge prints, community partner event attendance, confirmed meetup attendance, and YouTube unique viewers. "
        f"The broader registration and digital demand signal of {num(reach['registrationAndDigitalDemandSignals'])} combines active BTW registrations, meetup RSVPs, and YouTube unique viewers. "
        f"Neither number should be described as fully deduplicated unique reach across all channels, but both are useful sponsor-facing measures of scale."
    ))
    body.append(w_p(
        f"Geographic reach is a major proof point. The registration base spans {num(geo['statesRepresented'])} states and {num(geo['zipCodesRepresented'])} ZIP codes, with {num(geo['outOfStateVisitors'])} out-of-state visitors and {num(geo['hundredMileTravelers'])} attendees traveling more than 100 miles. "
        f"The top non-local or regional markets include {', '.join(m['label'] for m in geo['topMarkets'][:6])}. "
        f"For Cincinnati and regional stakeholders, this supports a clear destination-event narrative: Black Tech Week concentrates local audiences while drawing business and founder participation from outside the immediate market."
    ))
    body.append(w_p(
        f"The economic model should be used as an assumptions-based estimate. Under the actual attendee onsite mix, the model estimates {money(actual['total_impact'])} in total impact, including {money(actual['direct_impact'])} in direct impact, {money(actual['visitor_spending'])} in visitor spending, {money(actual['lodging_revenue'])} in lodging revenue, and {num(actual['room_nights'])} room nights. "
        f"The registered onsite mix estimates {money(registered['total_impact'])}, which is better interpreted as demand-based economic potential rather than verified realized impact. "
        f"These two scenarios should never be added together; they answer different questions."
    ))
    body.append(w_p(
        f"The founder and business audience is the clearest sponsorship asset. The aggregate dataset identifies {num(fb['founders'])} founders, {num(fb['executives'])} executives, and {num(fb['uniqueOrganizations'])} unique organizations. "
        f"That makes the event useful for sponsors seeking founder discovery, customer development, capital access, hiring, procurement, and brand visibility among Black innovation communities. "
        f"The session data strengthens the claim: {num(fb['sessionUniqueAttendees'])} unique scanned session attendees generated {num(fb['sessionScans'])} scans, with {pct(fb['twoPlusSessionPct'])} of engaged attendees scanning into two or more sessions."
    ))
    body.append(w_p(
        f"The year-round pipeline is also sponsor-relevant. Meetup activity generated {num(reach['meetupRsvps'])} RSVPs, {num(reach['meetupActualAttended'])} confirmed attendees, {num(reach['meetupLocations'])} locations, and {num(reach['meetupPageViews'])} page views. "
        f"Bootcamp programming added {num(fb['bootcampInterest'])} interest records, {num(fb['bootcampApplications'])} applications, and {num(fb['bootcampAttendees'])} attendees across {num(fb['bootcampCities'])} cities. "
        f"This shows Black Tech Week as an ecosystem-building platform that can maintain founder and community relationships beyond the main event week."
    ))
    body.append(w_p(
        f"The inclusion story should be reported with care and confidence. The dashboard identifies {num(equity['distressedZipcodeRegistrations'])} registrations from distressed ZIP-code areas, representing {pct(equity['distressedZipcodeRegistrationsPct'])} of registrations with the available ZIP mapping. "
        f"Bootcamp data shows distressed-area participation at {pct(equity['bootcampDistressedInterestPct'])} of interest records, {pct(equity['bootcampDistressedApplicationsPct'])} of applications, and {pct(equity['bootcampDistressedAttendeesPct'])} of attendees. "
        f"Aggregate demographic fields show strong representation from Black or African American respondents and women respondents, but unknown/prefer-not-to-say categories should remain visible in detailed reporting."
    ))
    for title, bullets in model["sections"]:
        body.append(w_p(title, "Heading1"))
        body.extend(w_p(b, "ListParagraph") for b in bullets)
    body.append(w_p("Recommended Sponsor Activation Angles", "Heading1"))
    body.extend(w_p(item, "ListParagraph") for item in [
        "Founder services and capital access: sponsor investor/founder programming, office hours, or grant pools.",
        "Talent and workforce: activate recruiting, mentorship, and emerging talent pathways.",
        "Civic and regional growth: tie sponsorship to measurable visitor spend, local business support, and national visibility for Cincinnati.",
        "Content distribution: underwrite livestream, post-event content clips, or national founder storytelling.",
        "Inclusive innovation: align with distressed-area reach and founder pipeline programming across Ohio and national meetup markets.",
    ])
    body.append(w_p("Data Governance", "Heading1"))
    body.append(w_p("This report intentionally uses aggregate dashboard outputs only. It excludes names, phone numbers, email addresses, and row-level attendee data. Modeled economic-impact values should be presented as estimates based on stated assumptions."))

    document_xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {''.join(body)}
    <w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="900" w:right="900" w:bottom="900" w:left="900"/></w:sectPr>
  </w:body>
</w:document>'''
    styles_xml = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:b/><w:sz w:val="48"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:rPr><w:color w:val="666666"/><w:sz w:val="26"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:rPr><w:b/><w:sz w:val="30"/></w:rPr></w:style>
  <w:style w:type="paragraph" w:styleId="ListParagraph"><w:name w:val="List Paragraph"/><w:pPr><w:ind w:left="360"/></w:pPr></w:style>
</w:styles>'''
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
</Types>'''
    rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''
    doc_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>'''
    path = ARTIFACTS / "Black-Tech-Week-2026-Impact-Report.docx"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/document.xml", document_xml)
        z.writestr("word/styles.xml", styles_xml)
        z.writestr("word/_rels/document.xml.rels", doc_rels)
    return path


def ppt_text_box(idx: int, x: int, y: int, w: int, h: int, text: str, size: int = 2400, bold: bool = False, color: str = "202124") -> str:
    bold_xml = ' b="1"' if bold else ""
    return f'''
<p:sp>
  <p:nvSpPr><p:cNvPr id="{idx}" name="Text {idx}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>
  <p:txBody><a:bodyPr wrap="square"/><a:lstStyle/><a:p><a:r><a:rPr lang="en-US" sz="{size}"{bold_xml}><a:solidFill><a:srgbClr val="{color}"/></a:solidFill></a:rPr><a:t>{text_escape(text)}</a:t></a:r></a:p></p:txBody>
</p:sp>'''


def ppt_rect(idx: int, x: int, y: int, w: int, h: int, fill: str) -> str:
    return f'''
<p:sp>
  <p:nvSpPr><p:cNvPr id="{idx}" name="Rect {idx}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
  <p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{w}" cy="{h}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{fill}"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr>
</p:sp>'''


def make_slide_xml(title: str, subtitle: str, bullets: list[str], slide_no: int) -> str:
    colors = ["00A676", "0A6EBD", "F5A623", "B64FC8"]
    shapes = [ppt_rect(2, 0, 0, 12192000, 6858000, "F7F8F4")]
    shapes.append(ppt_rect(3, 0, 0, 380000, 6858000, colors[(slide_no - 1) % len(colors)]))
    shapes.append(ppt_text_box(4, 700000, 520000, 10300000, 700000, title, 3600, True))
    shapes.append(ppt_text_box(5, 720000, 1180000, 10000000, 420000, subtitle, 1800, False, "5F6368"))
    y = 1900000
    idx = 6
    for i, bullet in enumerate(bullets):
        shapes.append(ppt_rect(idx, 780000, y + 70000, 180000, 180000, colors[i % len(colors)]))
        idx += 1
        shapes.append(ppt_text_box(idx, 1120000, y, 9400000, 480000, bullet, 2200))
        idx += 1
        y += 620000
    shapes.append(ppt_text_box(idx, 10700000, 6400000, 900000, 300000, str(slide_no), 1400, False, "777777"))
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:spTree>
    <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    {''.join(shapes)}
  </p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''


def make_pptx(model: dict) -> Path:
    slides = model["slides"]
    slide_overrides = "\n".join(
        f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, len(slides) + 1)
    )
    content_types = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  {slide_overrides}
</Types>'''
    rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>'''
    slide_ids = "\n".join(f'<p:sldId id="{255+i}" r:id="rId{i}"/>' for i in range(1, len(slides) + 1))
    presentation = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldSz cx="12192000" cy="6858000" type="screen16x9"/><p:notesSz cx="6858000" cy="9144000"/><p:sldIdLst>{slide_ids}</p:sldIdLst>
</p:presentation>'''
    pres_rels = "\n".join(
        f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{i}.xml"/>'
        for i in range(1, len(slides) + 1)
    )
    path = ARTIFACTS / "Black-Tech-Week-2026-Impact-Deck.pptx"
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("ppt/presentation.xml", presentation)
        z.writestr("ppt/_rels/presentation.xml.rels", f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{pres_rels}</Relationships>''')
        for i, (title, subtitle, bullets) in enumerate(slides, start=1):
            z.writestr(f"ppt/slides/slide{i}.xml", make_slide_xml(title, subtitle, bullets, i))
    return path


def bar(label: str, value: float, max_value: float, color: str = "#00a676") -> str:
    width = 0 if not max_value else max(4, min(100, value / max_value * 100))
    return f'<div class="barRow"><span>{html.escape(label)}</span><div class="barTrack"><i style="width:{width:.1f}%;background:{color}"></i></div><b>{html.escape(num(value))}</b></div>'


def make_html(summary: dict, model: dict) -> Path:
    reach = summary["reach"]
    geo = summary["geography"]
    fb = summary["foundersAndBusiness"]
    equity = summary["equityAndInclusion"]
    econ = summary["economicImpact"]
    actual = model["actual"]
    virtual = summary["virtualPerformance"]["totals"]
    channels = [
        ("In-person badge prints", reach["btwActualInPersonBadgePrinted"], "#00a676"),
        ("Community partner events", reach["communityPartnerEventAttendees"], "#0a6ebd"),
        ("Meetup attendance", reach["meetupActualAttended"], "#f5a623"),
        ("YouTube unique viewers", reach["youtubeUniqueViewers"], "#b64fc8"),
    ]
    channel_bars = "\n".join(bar(label, value, max(v for _, v, _ in channels), color) for label, value, color in channels)
    state_bars = "\n".join(bar(s["label"], s["count"], summary["geography"]["topStates"][0]["count"], "#0a6ebd") for s in summary["geography"]["topStates"][:8])
    title_bars = "\n".join(bar(t["label"], t["count"], summary["selectedCharts"]["titleLevels"][0]["count"], "#00a676") for t in summary["selectedCharts"]["titleLevels"][:8])
    html_doc = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Black Tech Week 2026 Impact Dashboard</title>
  <style>
    :root {{ --ink:#17211b; --muted:#5e6a62; --paper:#fbfbf7; --line:#dfe5dc; --green:#00a676; --blue:#0a6ebd; --gold:#f5a623; --coral:#ef5d45; }}
    body {{ margin:0; font-family: Inter, Arial, sans-serif; color:var(--ink); background:var(--paper); }}
    header {{ padding:44px 48px 28px; background:#111814; color:white; }}
    h1 {{ margin:0; font-size:42px; letter-spacing:0; }}
    h2 {{ margin:0 0 14px; font-size:24px; }}
    h3 {{ margin:0 0 10px; font-size:17px; }}
    p {{ line-height:1.55; color:var(--muted); }}
    header p {{ color:#d6ded8; max-width:900px; }}
    .grid {{ display:grid; gap:16px; grid-template-columns:repeat(4,minmax(0,1fr)); padding:24px 48px; }}
    .card {{ border:1px solid var(--line); border-radius:8px; padding:18px; background:white; }}
    .stat b {{ display:block; font-size:30px; margin-bottom:6px; }}
    .span2 {{ grid-column:span 2; }}
    .span4 {{ grid-column:span 4; }}
    .barRow {{ display:grid; grid-template-columns:180px 1fr 82px; gap:12px; align-items:center; margin:10px 0; font-size:14px; }}
    .barTrack {{ height:14px; background:#edf1ec; border-radius:999px; overflow:hidden; }}
    .barTrack i {{ display:block; height:100%; }}
    .note {{ font-size:13px; color:#69736c; }}
    .claims {{ columns:2; column-gap:28px; }}
    .claims li {{ break-inside:avoid; margin:0 0 10px; }}
    @media (max-width: 900px) {{ .grid {{ grid-template-columns:1fr; padding:18px; }} .span2,.span4 {{ grid-column:auto; }} header {{ padding:32px 20px; }} h1 {{ font-size:32px; }} .claims {{ columns:1; }} .barRow {{ grid-template-columns:1fr; }} }}
  </style>
</head>
<body>
  <header>
    <h1>Black Tech Week 2026 Impact Dashboard</h1>
    <p>Sponsor outreach and executive pitching view generated from aggregate-only local Lightship dashboard data. No personal identifiers or row-level records are included.</p>
  </header>
  <section class="grid">
    <article class="card stat"><b>{num(reach['estimatedGrossFootprint'])}</b><span>Estimated gross footprint</span></article>
    <article class="card stat"><b>{num(reach['registrationAndDigitalDemandSignals'])}</b><span>Broader demand signal</span></article>
    <article class="card stat"><b>{money(actual['total_impact'])}</b><span>Modeled actual-attendee economic impact</span></article>
    <article class="card stat"><b>{num(geo['statesRepresented'])}</b><span>States represented</span></article>
    <article class="card span2"><h2>Reach Channels</h2>{channel_bars}</article>
    <article class="card span2"><h2>Geographic Distribution</h2><p>{num(geo['zipCodesRepresented'])} ZIP codes, {num(geo['outOfStateVisitors'])} out-of-state visitors, and {num(geo['hundredMileTravelers'])} travelers from 100+ miles.</p>{state_bars}</article>
    <article class="card span2"><h2>Founder + Business Audience</h2><div class="grid" style="padding:0;grid-template-columns:repeat(2,1fr)"><div class="stat"><b>{num(fb['founders'])}</b><span>Founders</span></div><div class="stat"><b>{num(fb['uniqueOrganizations'])}</b><span>Organizations</span></div><div class="stat"><b>{num(fb['sessionScans'])}</b><span>Session scans</span></div><div class="stat"><b>{pct(fb['twoPlusSessionPct'])}</b><span>2+ sessions</span></div></div>{title_bars}</article>
    <article class="card span2"><h2>Economic Impact Model</h2><p>{money(actual['visitor_spending'])} visitor spending, {money(actual['lodging_revenue'])} lodging revenue, {num(actual['room_nights'])} modeled room nights, and {money(actual['indirect_induced_impact'])} indirect/induced impact.</p><p class="note">Modeled estimates should be labeled as assumptions-based, not audited results.</p></article>
    <article class="card span2"><h2>Virtual Distribution</h2><p>{num(virtual['views'])} views, {num(virtual['uniqueViewers'])} unique viewers, {num(virtual['watchHours'], 1)} watch hours, {num(virtual['subscribersGained'])} subscribers gained.</p></article>
    <article class="card span2"><h2>Inclusive Reach</h2><p>{num(equity['distressedZipcodeRegistrations'])} registrations from distressed ZIP-code areas ({pct(equity['distressedZipcodeRegistrationsPct'])}). Bootcamp attendee distressed-area representation: {pct(equity['bootcampDistressedAttendeesPct'])}.</p></article>
    <article class="card span4"><h2>Headline Claims</h2><ol class="claims">{''.join(f'<li>{html.escape(c)}</li>' for c in model['headlines'])}</ol></article>
  </section>
</body>
</html>'''
    path = ARTIFACTS / "Black-Tech-Week-2026-Impact-Dashboard.html"
    path.write_text(html_doc)
    return path


def main() -> None:
    summary = load_summary()
    model = report_model(summary)
    (ROOT / "data" / "report-model.json").write_text(json.dumps(model, indent=2))
    docx = make_docx(summary, model)
    pptx = make_pptx(model)
    html_path = make_html(summary, model)
    print(docx)
    print(pptx)
    print(html_path)


if __name__ == "__main__":
    main()

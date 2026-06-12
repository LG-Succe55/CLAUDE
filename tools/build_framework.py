#!/usr/bin/env python3
"""
Global Design AI Intake & Integration Framework — Stellantis Product Design Office.
Builds a professional .docx implementing the user's requirements, integrated with
the Stellantis AI Transformation Office operating model (kick-off + onboarding).
"""
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

TEAL = RGBColor(0x0E, 0x7C, 0x7B)
NAVY = RGBColor(0x1B, 0x2A, 0x4A)
GRAY = RGBColor(0x6B, 0x72, 0x80)
AMBER = RGBColor(0xB4, 0x53, 0x09)
LIGHT_HEX = 'EDF3F3'
TEAL_HEX = '0E7C7B'
BORDER_HEX = 'C9D6D6'

doc = Document()

# ---- page + base styles ----
for sec in doc.sections:
    sec.left_margin = Inches(0.85); sec.right_margin = Inches(0.85)
    sec.top_margin = Inches(0.8); sec.bottom_margin = Inches(0.8)

st = doc.styles['Normal']
st.font.name = 'Calibri'; st.font.size = Pt(10)
st.paragraph_format.space_after = Pt(6); st.paragraph_format.line_spacing = 1.12

def style_heading(name, size, color, bold=True, space_before=14, space_after=6, caps=False):
    s = doc.styles[name]
    s.font.name = 'Calibri'; s.font.size = Pt(size); s.font.bold = bold
    s.font.color.rgb = color
    s.paragraph_format.space_before = Pt(space_before)
    s.paragraph_format.space_after = Pt(space_after)
    s.font.all_caps = caps
    return s

style_heading('Heading 1', 16, NAVY, space_before=18, space_after=8)
style_heading('Heading 2', 12.5, TEAL, space_before=12, space_after=4)
style_heading('Heading 3', 11, NAVY, space_before=10, space_after=3)

def body(text, italic=False, color=None, size=10, space_after=6, bold=False):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.italic = italic; r.bold = bold
    r.font.size = Pt(size)
    if color: r.font.color.rgb = color
    p.paragraph_format.space_after = Pt(space_after)
    return p

def bullets(items, bold_lead=True, space_after=2):
    for it in items:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(space_after)
        if bold_lead and isinstance(it, tuple):
            r = p.add_run(it[0] + ' — '); r.bold = True
            p.add_run(it[1])
        else:
            p.add_run(it if isinstance(it, str) else ' — '.join(it))

def shade(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear'); shd.set(qn('w:fill'), hex_color)
    tcPr.append(shd)

def set_borders(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    borders = OxmlElement('w:tblBorders')
    for edge in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        e = OxmlElement(f'w:{edge}')
        e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), '4')
        e.set(qn('w:space'), '0'); e.set(qn('w:color'), BORDER_HEX)
        borders.append(e)
    tblPr.append(borders)

def add_table(headers, rows, widths=None, header_hex=TEAL_HEX, font_size=9,
              zebra=True, header_color='FFFFFF'):
    t = doc.add_table(rows=1, cols=len(headers))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_borders(t)
    t.autofit = False
    hdr = t.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ''
        p = hdr[i].paragraphs[0]
        r = p.add_run(h); r.bold = True; r.font.size = Pt(font_size)
        r.font.color.rgb = RGBColor.from_string(header_color)
        shade(hdr[i], header_hex)
        p.paragraph_format.space_after = Pt(2); p.paragraph_format.space_before = Pt(2)
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for ci, val in enumerate(row):
            cells[ci].text = ''
            p = cells[ci].paragraphs[0]
            parts = val if isinstance(val, list) else [(val, False)]
            for txt, bold in parts:
                r = p.add_run(txt); r.bold = bold; r.font.size = Pt(font_size)
            p.paragraph_format.space_after = Pt(2); p.paragraph_format.space_before = Pt(2)
            if zebra and ri % 2 == 1:
                shade(cells[ci], 'F4F8F8')
    if widths:
        for ci, w in enumerate(widths):
            for row in t.rows:
                row.cells[ci].width = Inches(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t

def page_number_footer():
    sec = doc.sections[0]
    p = sec.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run('Stellantis · Product Design Office — Global Design AI Intake & Integration Framework · Page ')
    r.font.size = Pt(7.5); r.font.color.rgb = GRAY
    fld = OxmlElement('w:fldSimple'); fld.set(qn('w:instr'), 'PAGE')
    rn = OxmlElement('w:r'); rPr = OxmlElement('w:rPr')
    sz = OxmlElement('w:sz'); sz.set(qn('w:val'), '15'); rPr.append(sz)
    col = OxmlElement('w:color'); col.set(qn('w:val'), '6B7280'); rPr.append(col)
    rn.append(rPr)
    t = OxmlElement('w:t'); t.text = '1'; rn.append(t); fld.append(rn)
    p._p.append(fld)

page_number_footer()

# =============================== COVER =====================================
p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(60)
r = p.add_run('STELLANTIS · PRODUCT DESIGN OFFICE'); r.font.size = Pt(11)
r.font.color.rgb = TEAL; r.bold = True
p = doc.add_paragraph()
r = p.add_run('Global Design AI\nIntake & Integration Framework')
r.font.size = Pt(30); r.bold = True; r.font.color.rgb = NAVY
p = doc.add_paragraph()
r = p.add_run('A repeatable process for proposing, validating, piloting, and scaling AI initiatives '
              'across the global Design organization — with visibility, governance, and alignment built in.')
r.font.size = Pt(12); r.font.color.rgb = GRAY; r.italic = True
p = doc.add_paragraph(); p.paragraph_format.space_before = Pt(16)
r = p.add_run('Version 1.0 · June 2026 · Owner: Global AI Design Lead (Design Functional AI Hub)')
r.font.size = Pt(9); r.font.color.rgb = GRAY
p = doc.add_paragraph()
r = p.add_run('Operating principle: the Global AI Design Lead orchestrates the process. '
              'The teams closest to the problem own the work.')
r.font.size = Pt(10); r.bold = True; r.font.color.rgb = TEAL
doc.add_page_break()

# =========================== 1. PURPOSE ====================================
doc.add_heading('1. Purpose & Operating Principles', level=1)
body('Design teams across North America, Europe, South America, and Asia-Pacific are already '
     'experimenting with AI. The risk is not too little initiative — it is fragmentation: duplicate '
     'pilots, invisible work, unscaled wins, and lessons that evaporate when a pilot ends. This '
     'framework provides one repeatable pipeline that lets any Design team move from idea to scaled '
     'capability quickly, while the organization keeps visibility, governance, and a compounding '
     'knowledge base.')
body('This framework deliberately does not create a central team that tests every tool. It creates a '
     'lightweight operating system around the teams who already want to test, so their work is '
     'visible, comparable, governed, and reusable.', italic=True, color=NAVY)

doc.add_heading('Eight operating principles', level=2)
bullets([
    ('One front door', 'every AI opportunity enters through the same global intake, regardless of region or seniority. No side doors.'),
    ('Orchestrate, don’t operate', 'the Global AI Design Lead runs the process — triage, portfolio, connections, reporting. Testing, piloting, and administering solutions stays with the originating teams.'),
    ('No ownership, no initiative', 'nothing proceeds without a named Business Sponsor, Process Owner, and Pilot Owner.'),
    ('Business problem first', 'every initiative is anchored to a real workflow and a measurable benefit before any tool is discussed.'),
    ('Search before you build', 'the Design AI repository, AI Garage, and the enterprise use-case portfolio are checked at intake. Duplicates are merged, not multiplied.'),
    ('Evidence over enthusiasm', 'one scorecard, one pilot charter, one assessment standard — so a pilot in Turin is comparable to a pilot in Auburn Hills.'),
    ('Right-sized governance', 'review effort scales with risk (data sensitivity, new vendors, spend), not with organizational distance. Fast lane for low-risk work.'),
    ('Every initiative leaves knowledge', 'pilots that do not scale still produce a documented lesson. Retired is a result, not a failure.'),
])

# =========================== 2. SCOPE ======================================
doc.add_heading('2. Scope & Position in the Stellantis AI Operating Model', level=1)
doc.add_heading('In scope', level=2)
bullets([
    'AI tools, agents, workflows, and data products proposed by or for Design teams in NA, EE, SA, and AP/China.',
    'Initiatives spanning creative work (sketching, visualization, animation, CMF), design operations (reviews, research, benchmarking, program memory), and Design’s interfaces to engineering, manufacturing, and marketing.',
    'Both new technology requests and new uses of already-approved platforms.',
], bold_lead=False)
doc.add_heading('Out of scope', level=2)
bullets([
    'Enterprise platform selection and operation (owned by GDPA / ICT).',
    'AI features of the vehicle product itself (owned by PDT).',
    'Personal productivity use of already-approved tools within approved environments — just use them; no intake required.',
], bold_lead=False)

doc.add_heading('Position in the enterprise model', level=2)
body('Design operates as one of the Global Functional AI Hubs in the Stellantis AI Transformation '
     'Office. This framework is how the Design hub executes its leadership directive — Connect, '
     'Build, Adopt, Signal, Represent — at studio level. It does not duplicate enterprise '
     'mechanisms; it plugs into them:')
add_table(
    ['Enterprise mechanism', 'How this framework uses it'],
    [
        ['AI Garage / AI Intake Agent', 'Checked at intake for existing solutions; Design submissions with enterprise relevance are mirrored into the enterprise idea backlog.'],
        ['GDPA platforms (Foundry, Databricks, Snowflake) & AI & Data Talent Pool', 'Default build path for Tier 2–3 pilots; Talent Pool engaged for build-heavy initiatives instead of hiring or shadow IT.'],
        ['Data&AI Marketplace / Collibra', 'Design Data Products produced by initiatives are certified and published for reuse.'],
        ['Stellantis AI Risk Assessment (regulatory & operational)', 'Triggered automatically by tier at the pilot and scale gates.'],
        ['VCP / Wave', 'Initiatives with material recurring value are flagged in Wave under the relevant workstream (e.g., Product Cost, ER&D, Commercial & Quality).'],
        ['AI & Data Ambassador network / Global AI Academy', 'Design’s Regional AI Champions and training plans operate as part of the enterprise network (255 → 2,000 ambassadors).'],
    ],
    widths=[2.6, 4.9])

# =========================== 3. ROLES ======================================
doc.add_heading('3. Roles & Ownership', level=1)
body('Every initiative must name three owners at intake. The framework stalls by design when '
     'ownership is missing — an initiative nobody owns is an initiative nobody needs.', bold=True)
add_table(
    ['Role', 'Accountable for', 'Notes'],
    [
        [[('Business Sponsor', True)], 'The business outcome: approves the value claim, unblocks resources, accepts or rejects the result.', 'Acts as the "AI Business Owner" for the Stellantis regulatory AI risk assessment when one is required.'],
        [[('Process Owner', True)], 'The workflow being improved: validates the current process, the proposed future process, and owns adoption after scaling.', 'May be the same person as the sponsor in small teams — but the role must be explicitly accepted.'],
        [[('Pilot Owner / Champion', True)], 'Executing the pilot: running the test, collecting measurements, reporting at checkpoints, writing the final assessment.', 'Owns the operational AI risk assessment with the ICT use-case lead when required. Remains in the originating team.'],
        [[('Global AI Design Lead', True)], 'The process: intake triage, portfolio, evaluation standards, enterprise brokering, knowledge base, executive reporting.', 'Explicit non-responsibilities: does not test tools, does not run or administer pilots, does not own pilot results.'],
        [[('Regional AI Champions (NA · EE · SA · AP)', True)], 'First contact for their region: help requesters complete intake, sense-check duplicates, approve Tier 1 fast-lane starts, drive local adoption.', 'Part of the enterprise AI & Data Ambassador network.'],
        [[('Design Data Managers / Knowledge Stewards', True)], 'Curating the repository and certifying Design Data Products per the enterprise call-to-action.', 'Nominated per the AI Hub onboarding requirements.'],
        [[('Design ICT AI Lead & Security partners', True)], 'Feasibility, platform path, integration, security and compliance review at the tiers that require it.', 'Engaged through defined interaction points (Section 9) — not on every initiative.'],
    ],
    widths=[1.7, 3.2, 2.6])

doc.add_heading('RACI summary', level=2)
add_table(
    ['Activity', 'Lead', 'Sponsor', 'Process Owner', 'Pilot Owner', 'Reg. Champion', 'ICT / Security'],
    [
        ['Submit intake', 'I', 'A', 'C', 'R', 'C', '—'],
        ['Duplicate & repository check', 'A/R', 'I', '—', 'C', 'R', '—'],
        ['Evaluation & prioritization (G1)', 'A/R', 'C', 'C', 'C', 'C', 'C (Tier 2+)'],
        ['Pilot execution & checkpoints', 'I', 'A', 'C', 'R', 'C', 'C (per tier)'],
        ['Security / AI risk review', 'I', 'A (regulatory)', '—', 'R', '—', 'A (operational)'],
        ['Scale decision (G4)', 'R (business case)', 'A', 'C', 'C', 'C', 'C'],
        ['Knowledge capture', 'A', 'I', 'C', 'R', 'C', '—'],
        ['Executive reporting', 'A/R', 'I', 'I', 'I', 'C', 'I'],
    ],
    widths=[2.05, 0.95, 0.95, 1.0, 0.95, 0.95, 1.0], font_size=8)
body('R = Responsible · A = Accountable · C = Consulted · I = Informed. Scale decisions are accountable '
     'to Design leadership with the sponsor; the Lead assembles the case.', size=8, color=GRAY)

# =========================== 4. PIPELINE ===================================
doc.add_heading('4. The Pipeline: Stages & Gates', level=1)
body('Every initiative lives in exactly one stage. Stage status is visible to the whole Design '
     'organization through the portfolio board (Section 11).')
doc.add_picture('/home/user/CLAUDE/work/framework_pipeline.png', width=Inches(6.9))
add_table(
    ['Stage', 'Definition', 'Entry requires', 'Exit requires'],
    [
        [[('Explore', True)], 'Ideas under consideration.', 'Complete intake with named owners.',
         'Gate 1: scorecard disposition — proceed, redirect, merge, park, or decline.'],
        [[('Pilot', True)], 'Active testing and validation.', 'Gate 2: approved pilot charter; tier-appropriate security/feasibility pre-checks done.',
         'Gate 3: final assessment vs success criteria within 2 weeks of pilot end.'],
        [[('Accelerate', True)], 'Initiatives demonstrating measurable value.', 'Pilot met success criteria; sponsor confirms value; expansion plan (more users / programs / studios).',
         'Gate 4: scale business case — value, cost, platform path, change plan.'],
        [[('Scale', True)], 'Approved for broader deployment.', 'Design leadership approval; enterprise alignment (platform, licensing, security) confirmed.',
         'Handover to Process Owner as standard practice; adoption tracked; initiative closed into knowledge base.'],
        [[('Retire', True)], 'Did not demonstrate sufficient value — from any stage.', 'Disposition decision at any gate or checkpoint.',
         'Lessons-learned entry published; knowledge asset created. Mandatory — no silent failures.'],
    ],
    widths=[0.95, 1.75, 2.4, 2.4], font_size=8.5)

# =========================== 5. INTAKE =====================================
doc.add_heading('5. Intake', level=1)
body('One global form, designed to be completed in 15 minutes without assistance. Requesters who '
     'prefer a conversation start with their Regional AI Champion, who completes the form with them. '
     'Intake is acknowledged within 5 business days and triaged at the next monthly Design AI '
     'Council — no submission waits more than 30 days for a disposition and a named next step.')
doc.add_heading('Required intake fields', level=2)
add_table(
    ['Field', 'What good looks like'],
    [
        ['Initiative name', 'Short, plain language. "Benchmark image search for interiors," not "AI transformation phase 2."'],
        ['Requesting organization', 'Studio / department submitting.'],
        ['Region', 'NA · EE · SA · AP — or Global if inherently cross-regional.'],
        ['Business problem', 'The pain in one paragraph, in workflow terms. No technology words required.'],
        ['Current process', 'How the work happens today: steps, tools, time, people.'],
        ['Proposed future process', 'How the work would happen with the solution. A sketch beats an essay.'],
        ['Expected benefits', 'What improves — time, cost, quality, experience — and roughly how much.'],
        ['Users impacted', 'Who and how many, at pilot and at scale.'],
        ['Estimated value', 'Order-of-magnitude is fine at intake (hours/week, € range). Refined at evaluation.'],
        ['Requested technology or platform', 'If known. "Unknown — need guidance" is a valid answer; the Lead brokers options.'],
        ['Pilot Owner / Champion', 'Named individual in the requesting team.'],
        ['Business Sponsor', 'Named individual accountable for the outcome.'],
        ['Process Owner', 'Named individual who owns the workflow.'],
        ['Data classification', 'Public · internal · confidential / unreleased-program · personal data. Drives the governance tier.'],
        ['Existing-solution check', 'Confirmation the repository and AI Garage were searched; list near-matches found.'],
        ['Desired timeline & reach', 'When the team wants to start; single studio, region, or global ambition.'],
    ],
    widths=[2.0, 5.5], font_size=8.5)
body('The first twelve fields satisfy the framework’s mandatory requirements; the final four '
     'exist to route the initiative correctly (tier, duplicates, sequencing) without a second '
     'round-trip to the requester.', size=8.5, color=GRAY)

# =========================== 6. EVALUATION =================================
doc.add_heading('6. Evaluation & Prioritization (Gate 1)', level=1)
body('Every initiative is scored on the same ten criteria, 1–5 each, weighted as below. Scoring is '
     'done at the monthly Design AI Council by the Lead and Regional Champions, with ICT/Security '
     'consulted where flagged. The scorecard creates comparability — it does not replace judgment; '
     'the Council can override with a recorded rationale.')
add_table(
    ['Criterion', 'Weight', 'What it measures'],
    [
        ['Strategic alignment', '15', 'Advances Design Intelligence priorities and the enterprise AI strategy (data products, semantic layer, agents).'],
        ['Global applicability', '15', 'Useful beyond the originating studio; potential to become a shared capability.'],
        ['Time savings', '12', 'Hours returned to designers and studio teams.'],
        ['Cost savings', '10', 'Direct cost reduction or avoidance.'],
        ['Quality improvement', '10', 'Better design outcomes: earlier issue detection, fewer reworks, stronger reviews.'],
        ['Technical feasibility', '10', 'Achievable with available platforms and skills in a 30–90 day pilot.'],
        ['User experience improvement', '8', 'Reduces friction in daily design work; desirability to users.'],
        ['Security considerations', '8', 'Exposure of unreleased-program material, IP, vendor risk. Gating: a score of 1 pauses the initiative regardless of total.'],
        ['Data considerations', '6', 'Data availability, quality, classification, and rights. Gating: a score of 1 pauses the initiative.'],
        ['Change management impact', '6', 'Training burden, workflow disruption, adoption risk.'],
    ],
    widths=[1.9, 0.7, 4.9], font_size=8.5)
doc.add_heading('Dispositions', level=2)
bullets([
    ('Proceed to Pilot', 'score ≥ 70, owners confirmed, tier checks passed. Enters pilot queue.'),
    ('Redirect', 'an existing solution already covers the need — requester is connected to it. Logged as a win for reuse.'),
    ('Merge', 'duplicates an active initiative — teams are connected; one initiative continues with both regions.'),
    ('Park', 'promising but not now (score 50–69, missing prerequisite, or pilot capacity full). Given a revisit date — parked is not a polite no.'),
    ('Decline', 'score < 50 or gating issue with no path. Reason recorded in the repository; requester gets the rationale.'),
])
body('Pilot capacity is protected: as a guideline, each region runs no more than three concurrent '
     'pilots, so pilots get real attention and finish. Prioritization favors high value + low effort '
     'first; high value + high effort initiatives are sequenced with enterprise (GDPA/Talent Pool) support.',
     size=9)

# =========================== 7. PILOTS =====================================
doc.add_heading('7. Pilot Standards (Gates 2–3)', level=1)
body('Pilots are executed and owned by the originating team. The framework standardizes how pilots '
     'are framed and judged — not who runs them.')
doc.add_heading('Pilot charter (required at Gate 2)', level=2)
bullets([
    ('Objectives & hypothesis', 'what we expect to improve, and why.'),
    ('Success criteria', 'quantified, agreed with the sponsor before starting; baseline measured first ("review prep takes 6 h today; target ≤ 3 h").'),
    ('Duration', '30–90 days; 60 is the default. Longer means the scope is too big — split it.'),
    ('Participating users', 'named participants; minimum group size agreed for the evidence to mean something.'),
    ('Measurement approach', 'how data is collected (time logs, output counts, user ratings) and by whom.'),
    ('Checkpoint reviews', 'a 15-minute mid-point report at the Design AI Council: on track / at risk / stop.'),
    ('Final assessment', 'due within two weeks of pilot end (template, Appendix D): results vs criteria, value estimate, user feedback, security/data observations, recommendation — accelerate, iterate once, or retire.'),
])
body('An honest "this did not work, here is why" assessment is treated as a first-class contribution '
     'to the knowledge base — it saves the next three teams from the same dead end.', italic=True,
     color=TEAL)

# =========================== 8. TIERS ======================================
doc.add_heading('8. Right-Sized Governance: Three Tiers', level=1)
body('Governance effort scales with risk. The tier is set at intake from data classification, '
     'technology novelty, and spend — and determines which reviews are required. This is how the '
     'framework ensures appropriate review without bureaucracy.')
add_table(
    ['Tier', 'Triggers', 'Required path', 'Target speed'],
    [
        [[('Tier 1 · Fast lane', True)],
         'Approved tools and environments; no new data exposure; no new vendor; no incremental spend.',
         'Regional Champion approval → log in portfolio → start. Outcome reported like any pilot.',
         '< 1 week from intake'],
        [[('Tier 2 · Standard', True)],
         'New tool or vendor; internal (non-confidential) data; limited users; modest spend.',
         'Full intake → scorecard → ICT feasibility check + security pre-check → pilot charter.',
         '≤ 30 days to pilot start'],
        [[('Tier 3 · Elevated', True)],
         'Confidential / unreleased-program or personal data; new platform; integration with enterprise systems; spend above the Design-leadership threshold.',
         'Tier 2 path + Stellantis AI Risk Assessment (regulatory before pilot where required; operational before scale) + GDPA/ICT architecture engagement + procurement.',
         'Per enterprise review cycles — started early by the Lead'],
    ],
    widths=[1.25, 2.3, 2.85, 1.1], font_size=8.5)
body('Design-specific note: sketches, models, and renders of unreleased programs are '
     'program-confidential. Any initiative moving such material outside approved environments is '
     'Tier 3 by definition — no exceptions.', bold=True, size=9)

# =========================== 9. GOVERNANCE =================================
doc.add_heading('9. Governance Interaction Points', level=1)
add_table(
    ['Partner', 'Engaged when', 'For'],
    [
        ['ICT / Design ICT AI Lead', 'Tier 2+ at evaluation; all scale decisions.', 'Feasibility, architecture, platform path, integration, licensing.'],
        ['Enterprise AI teams / GDPA', 'Build-heavy pilots; any initiative producing a data product; scale gate.', 'Platform capabilities, AI & Data Talent Pool capacity, data product publication to the Marketplace.'],
        ['AI Garage', 'At intake (search) and after successful pilots (publish).', 'Discovery of existing solutions; making Design agents and use cases visible to the enterprise.'],
        ['Security teams', 'Tier 2 pre-check; Tier 3 full review.', 'Vendor risk, data handling, environment approval, IP protection.'],
        ['AI Governance organization', 'Tier 3 before pilot (regulatory) and before scale (operational).', 'Stellantis AI Risk Assessments; EU AI Act and regional regulatory obligations.'],
        ['Regional Design leadership', 'Pilots affecting studio operations; all scale decisions in their region.', 'Resourcing, prioritization, adoption sponsorship.'],
        ['VCP / Wave (with Finance)', 'When recurring value is material.', 'Flagging the initiative under the relevant VCP workstream so Design’s AI value is counted.'],
    ],
    widths=[1.7, 2.45, 3.35], font_size=8.5)
body('The Lead owns these relationships and brokers every connection, so requesting teams never need '
     'to navigate the enterprise organization alone — and partner organizations get one coherent '
     'Design interlocutor instead of fifty.', size=9)

# =========================== 10. KNOWLEDGE =================================
doc.add_heading('10. Knowledge Management', level=1)
body('The repository is the compounding asset of this framework: a single, searchable record of '
     'everything Design has tried, learned, and standardized. Every initiative writes to it at every '
     'gate — by the time an initiative closes, its knowledge entry already exists.')
doc.add_heading('What is captured', level=2)
add_table(
    ['Asset', 'Created at', 'Curated by'],
    [
        ['Use case description & intake record', 'Intake', 'Pilot Owner'],
        ['Evaluation & disposition (incl. declines and redirects)', 'Gate 1', 'Lead'],
        ['Pilot charter, checkpoint notes, final assessment & outcomes', 'Gates 2–3', 'Pilot Owner'],
        ['Lessons learned (success and failure)', 'Gate 3 / Retire', 'Pilot Owner + Knowledge Steward'],
        ['Adoption metrics for scaled solutions', 'Scale, ongoing', 'Process Owner'],
        ['Training materials & recommended practices', 'Accelerate / Scale', 'Knowledge Steward + Academy'],
        ['Contacts & subject-matter experts directory', 'Continuous', 'Knowledge Steward'],
    ],
    widths=[3.4, 1.6, 2.5], font_size=8.5)
bullets([
    ('Searchable and reusable', 'organized by workflow, region, technology, and outcome; readable by all Design teams globally.'),
    ('Quarterly digest', '"What Design Learned This Quarter" — distributed to all studios; the network’s shared memory in practice.'),
    ('Enterprise alignment', 'the repository is itself managed as a Design Data Product — certified and registered per the enterprise data-product call-to-action, so Design’s knowledge becomes a reusable enterprise asset.'),
])

# =========================== 11. PORTFOLIO =================================
doc.add_heading('11. Portfolio Management & Operating Cadence', level=1)
add_table(
    ['Forum', 'Cadence', 'Participants', 'Decisions'],
    [
        ['Design AI Council', 'Monthly', 'Lead (chair), 4 Regional Champions, Design ICT AI Lead, rotating sponsors', 'Intake triage (G1), pilot starts (G2), checkpoint reviews, pilot assessments (G3), Tier escalations'],
        ['Design AI Portfolio Review', 'Quarterly', 'Design leadership, Lead, Champions', 'Scale approvals (G4), retire decisions, investment asks, tier thresholds'],
        ['Enterprise rhythms', 'Per AI Transformation Office calendar', 'Lead represents Design', 'Functional AI Community reporting, Steer Co inputs, VCP/Wave updates'],
    ],
    widths=[1.55, 1.0, 2.55, 2.4], font_size=8.5)
body('The portfolio board shows every initiative by stage (Explore / Pilot / Accelerate / Scale / '
     'Retired), region, tier, and owner — visible to the entire Design organization. Visibility is '
     'the duplicate-prevention mechanism: teams can see what exists before they propose.', size=9.5)

# =========================== 12. REPORTING =================================
doc.add_heading('12. Executive Reporting', level=1)
body('A monthly one-pager from the Council, and a quarterly executive pack aligned to the enterprise '
     'KPI framework (product usage/adoption · health & quality · incremental value · time to market).')
add_table(
    ['Framework metric', 'Enterprise KPI category'],
    [
        ['Number of active initiatives by stage and region', 'Health & quality'],
        ['Regional participation (initiatives and pilot owners per region)', 'Usage / adoption'],
        ['Adoption rates of scaled solutions', 'Usage / adoption'],
        ['Time savings achieved (validated by pilots, projected at scale)', 'Incremental value'],
        ['Estimated business value (€ + hours), incl. Wave-flagged VCP value', 'Incremental value'],
        ['Successful pilots (met success criteria) and pilot cycle time', 'Time to market'],
        ['Scaled solutions in production use', 'Time to market / value'],
        ['Knowledge assets created (use cases, lessons, training materials)', 'Health & quality'],
    ],
    widths=[4.6, 2.9], font_size=8.5)

# =========================== 13. ROADMAP ===================================
doc.add_heading('13. Implementation Roadmap', level=1)
add_table(
    ['First 30 days', 'Days 31–60', 'Days 61–90'],
    [
        ['Publish framework + intake form. Name Regional Champions and Data Managers. Backfill all current initiatives (Vizcom, Runway, active explorations) into the portfolio — the framework launches populated, not empty. Hold Council #1: first triage.',
         'First checkpoint reviews. Repository v1 live with backfilled lessons. Tier thresholds ratified by Design leadership. First monthly one-pager issued.',
         'First quarterly Portfolio Review: first scale/retire decisions. First executive report into the AI Hub reporting rhythm. Publish digest #1. Confirm first Wave/VCP flags.'],
    ],
    widths=[2.5, 2.5, 2.5], font_size=8.5)

# =========================== APPENDICES ====================================
doc.add_page_break()
doc.add_heading('Appendix A — Intake Form Template', level=1)
add_table(
    ['#', 'Field', 'Answer'],
    [[str(i + 1), f, ''] for i, f in enumerate([
        'Initiative name', 'Requesting organization', 'Region (NA / EE / SA / AP / Global)',
        'Business problem (one paragraph)', 'Current process (steps, tools, time, people)',
        'Proposed future process', 'Expected benefits', 'Users impacted (pilot / at scale)',
        'Estimated value (hours, €, order of magnitude)', 'Requested technology or platform (or "need guidance")',
        'Pilot Owner / Champion (name)', 'Business Sponsor (name)', 'Process Owner (name)',
        'Data classification (public / internal / confidential-unreleased / personal)',
        'Existing-solution check (repository + AI Garage searched; near-matches found)',
        'Desired timeline & reach (studio / region / global)'])],
    widths=[0.4, 3.6, 3.5], font_size=8.5)

doc.add_heading('Appendix B — Evaluation Scorecard', level=1)
add_table(
    ['Criterion (weight)', 'Score 1', 'Score 3', 'Score 5'],
    [
        ['Strategic alignment (15)', 'Unrelated to Design/enterprise AI priorities', 'Supports a priority indirectly', 'Directly advances a stated priority'],
        ['Global applicability (15)', 'Single-team niche', 'Useful to one region', 'Every studio would use it'],
        ['Time savings (12)', '< 1 h/week/user', '2–5 h/week/user', '> 5 h/week/user or removes a bottleneck'],
        ['Cost savings (10)', 'None identifiable', 'Moderate, indirect', 'Material, direct, recurring'],
        ['Quality improvement (10)', 'No effect on outcomes', 'Fewer errors/reworks likely', 'Demonstrably better design outcomes'],
        ['Technical feasibility (10)', 'Needs unavailable tech/skills', 'Feasible with help (Talent Pool)', 'Ready on approved platforms now'],
        ['User experience (8)', 'Adds friction', 'Neutral to mildly better', 'Users actively want it'],
        ['Security (8) — gating', 'Unresolvable exposure (score 1 = pause)', 'Manageable with controls', 'No new exposure'],
        ['Data (6) — gating', 'Data unavailable/unusable (score 1 = pause)', 'Available with preparation', 'Available, clean, rights cleared'],
        ['Change management (6)', 'Major retraining/disruption', 'Moderate training need', 'Near-zero adoption burden'],
    ],
    widths=[1.9, 1.85, 1.85, 1.9], font_size=8)
body('Total = Σ(score × weight) / 5, max 100. Guidance: ≥ 70 proceed · 50–69 park with revisit date · '
     '< 50 decline/merge/redirect. Council may override with recorded rationale.', size=8.5, color=GRAY)

doc.add_heading('Appendix C — Pilot Charter Template', level=1)
add_table(
    ['Section', 'Content'],
    [['Initiative & owners', 'Name · Pilot Owner · Business Sponsor · Process Owner · Region · Tier'],
     ['Objectives & hypothesis', 'What we expect to improve and why'],
     ['Success criteria', 'Quantified targets with baseline values, agreed with sponsor'],
     ['Duration', 'Start / end (30–90 days; default 60)'],
     ['Participants', 'Named users, minimum group size'],
     ['Measurement approach', 'Data collected, method, by whom, how often'],
     ['Checkpoints', 'Mid-point Council review date; on-track / at-risk / stop'],
     ['Security & data notes', 'Classification, environment, tier-required reviews completed'],
     ['Exit', 'Final assessment due date (≤ 2 weeks after end); rollback plan']],
    widths=[1.9, 5.6], font_size=8.5)

doc.add_heading('Appendix D — Final Assessment Template', level=1)
add_table(
    ['Section', 'Content'],
    [['Results vs success criteria', 'Each criterion: baseline → target → achieved'],
     ['Value estimate', 'Validated hours/€ at pilot scope; projection at scale with assumptions'],
     ['User feedback', 'Participant ratings and representative quotes'],
     ['Security / data observations', 'Issues encountered; controls that worked'],
     ['Recommendation', 'Accelerate · Iterate once (with changes) · Retire'],
     ['Lessons learned', 'What the next team should know — mandatory, success or failure'],
     ['Knowledge assets', 'Links: charter, data, training drafts, SME contacts']],
    widths=[1.9, 5.6], font_size=8.5)

doc.add_heading('Appendix E — Enterprise Alignment Glossary', level=1)
add_table(
    ['Framework term', 'Enterprise counterpart'],
    [['Design AI repository', 'Design Data Product, registered via Collibra / Data&AI Marketplace'],
     ['Regional AI Champions', 'AI & Data Ambassadors (Design seats in the 255 → 2,000 network)'],
     ['Design Data Managers / Knowledge Stewards', '"Nominate Data Managers within your domain" (hub-leader call-to-action)'],
     ['Pipeline stages (Explore→Scale)', 'Compatible with Wave stage gates (L0 Idea → L3 Approved) for VCP-flagged initiatives'],
     ['Estimated business value', 'VCP value-creation levers, tracked in Wave where material'],
     ['Reporting metrics', 'Enterprise Data&AI product KPIs: usage/adoption · health & quality · incremental value · time to market'],
     ['Build support for pilots', 'GDPA Global Platform (standardized foundations) + AI & Data Talent Pool (capacity on request)']],
    widths=[3.0, 4.5], font_size=8.5)

doc.save('/home/user/CLAUDE/work/Global_Design_AI_Intake_Integration_Framework.docx')
print('saved docx')

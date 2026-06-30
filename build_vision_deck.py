#!/usr/bin/env python3
"""
Chrysler Brand Design Vision — executive scaffold generator.

18-slide premium automotive executive deck (16:9). Placeholder slides only:
titles, subtitles, callout boxes, labeled image frames, icon placeholders,
minimal placeholder text, and speaker-note placeholders on every slide.

Design language: Apple-keynote / McKinsey simplicity. White backgrounds,
large hero imagery, minimal text, generous whitespace, subtle
Chrysler-inspired accents.
"""

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# ----------------------------------------------------------------------------
# Design system
# ----------------------------------------------------------------------------
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

INK      = RGBColor(0x1A, 0x1A, 0x1C)   # primary text
GRAPHITE = RGBColor(0x4A, 0x4E, 0x57)   # secondary text
SLATE    = RGBColor(0x86, 0x8B, 0x94)   # tertiary / captions
PLATINUM = RGBColor(0xC8, 0xCC, 0xD2)   # hairlines
MIST     = RGBColor(0xEF, 0xF1, 0xF3)   # placeholder fill
CLOUD    = RGBColor(0xF7, 0xF8, 0xF9)   # subtle panel
WHITE    = RGBColor(0xFF, 0xFF, 0xFF)
CHRYSLER = RGBColor(0x1B, 0x2A, 0x4A)   # deep Chrysler-inspired navy accent
SILVER   = RGBColor(0xA9, 0xAE, 0xB5)   # wing / badge silver

FONT_DISPLAY = "Arial"   # substitute for licensed Chrysler display face
FONT_BODY    = "Arial"

prs = Presentation()
prs.slide_width = SLIDE_W
prs.slide_height = SLIDE_H
BLANK = prs.slide_layouts[6]


# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def add_slide():
    return prs.slides.add_slide(BLANK)


def set_bg(slide, color=WHITE):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = color


def _set_font(run, size, color, bold, name, spacing, italic=False):
    f = run.font
    f.size = Pt(size); f.bold = bold; f.italic = italic
    f.name = name; f.color.rgb = color
    if spacing is not None:
        run._r.get_or_add_rPr().set("spc", str(int(spacing * 100)))


def textbox(slide, x, y, w, h, lines, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    for m in ("margin_left", "margin_right", "margin_top", "margin_bottom"):
        setattr(tf, m, 0)
    for i, ln in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = ln.get("align", align)
        if ln.get("space_after") is not None:
            p.space_after = Pt(ln["space_after"])
        if ln.get("space_before") is not None:
            p.space_before = Pt(ln["space_before"])
        if ln.get("line_spacing") is not None:
            p.line_spacing = ln["line_spacing"]
        r = p.add_run()
        r.text = ln["text"]
        _set_font(r, ln.get("size", 18), ln.get("color", INK),
                  ln.get("bold", False), ln.get("name", FONT_BODY),
                  ln.get("spacing"), ln.get("italic", False))
    return tb


def rect(slide, x, y, w, h, fill=None, line=None, line_w=None,
         shape=MSO_SHAPE.RECTANGLE):
    sp = slide.shapes.add_shape(shape, x, y, w, h)
    sp.shadow.inherit = False
    if fill is None:
        sp.fill.background()
    else:
        sp.fill.solid(); sp.fill.fore_color.rgb = fill
    if line is None:
        sp.line.fill.background()
    else:
        sp.line.color.rgb = line
        sp.line.width = line_w or Pt(0.75)
    return sp


def hairline(slide, x, y, w, color=PLATINUM, weight=Pt(1.0)):
    ln = slide.shapes.add_connector(2, x, y, x + w, y)
    ln.line.color.rgb = color
    ln.line.width = weight
    return ln


def kicker(slide, x, y, text, color=CHRYSLER, w=Inches(8)):
    return textbox(slide, x, y, w, Inches(0.3),
                   [{"text": text.upper(), "size": 11, "color": color,
                     "bold": True, "name": FONT_DISPLAY, "spacing": 3.0}])


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = (
        "SPEAKER NOTES (placeholder) — " + text)


def footer(slide, number):
    textbox(slide, Inches(0.7), Inches(7.04), Inches(8), Inches(0.3),
            [{"text": "CHRYSLER  ·  BRAND DESIGN VISION", "size": 8,
              "color": SLATE, "spacing": 1.5}])
    textbox(slide, Inches(11.6), Inches(7.04), Inches(1.0), Inches(0.3),
            [{"text": f"{number:02d}", "size": 8, "color": SLATE, "spacing": 1.5}],
            align=PP_ALIGN.RIGHT)
    textbox(slide, Inches(11.4), Inches(0.34), Inches(1.2), Inches(0.3),
            [{"text": "CONFIDENTIAL", "size": 7.5, "color": PLATINUM,
              "spacing": 2.0}], align=PP_ALIGN.RIGHT)


def image_frame(slide, x, y, w, h, label="IMAGE PLACEHOLDER", fill=MIST,
                note="Replace · 16:9 · 300dpi", icon=True):
    rect(slide, x, y, w, h, fill=fill)
    tick = Inches(0.26); tw = Pt(1.25)
    for cx, cy, pos in [(x, y, "tl"), (x + w, y, "tr"),
                        (x, y + h, "bl"), (x + w, y + h, "br")]:
        dx = tick if "l" in pos else -tick
        dy = tick if "t" in pos else -tick
        a = slide.shapes.add_connector(2, cx, cy, cx + dx, cy)
        a.line.color.rgb = SILVER; a.line.width = tw
        b = slide.shapes.add_connector(2, cx, cy, cx, cy + dy)
        b.line.color.rgb = SILVER; b.line.width = tw
    cy0 = y + h / 2
    if icon and h > Inches(1.3):
        ic = Inches(0.56)
        icx = x + (w - ic) / 2
        icy = y + (h - ic) / 2 - Inches(0.24)
        rect(slide, icx, icy, ic, ic, fill=None, line=SILVER, line_w=Pt(1.5),
             shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        rect(slide, icx + ic * 0.22, icy + ic * 0.2, Inches(0.11), Inches(0.11),
             fill=SILVER, shape=MSO_SHAPE.OVAL)
        tri = slide.shapes.add_shape(MSO_SHAPE.ISOSCELES_TRIANGLE,
                                     icx + ic * 0.30, icy + ic * 0.44,
                                     Inches(0.30), Inches(0.18))
        tri.fill.solid(); tri.fill.fore_color.rgb = SILVER
        tri.line.fill.background(); tri.shadow.inherit = False
        ly = icy + ic + Inches(0.10)
    else:
        ly = cy0 - Inches(0.22)
    textbox(slide, x, ly, w, Inches(0.4),
            [{"text": label, "size": 10.5, "color": SLATE, "bold": True,
              "spacing": 2.0, "align": PP_ALIGN.CENTER}], align=PP_ALIGN.CENTER)
    if note:
        textbox(slide, x, ly + Inches(0.30), w, Inches(0.3),
                [{"text": note, "size": 8, "color": PLATINUM, "spacing": 0.8,
                  "align": PP_ALIGN.CENTER}], align=PP_ALIGN.CENTER)


def icon_chip(slide, x, y, size=Inches(0.62)):
    rect(slide, x, y, size, size, fill=None, line=CHRYSLER, line_w=Pt(1.25),
         shape=MSO_SHAPE.OVAL)
    inner = Inches(0.18)
    rect(slide, x + (size - inner) / 2, y + (size - inner) / 2, inner, inner,
         fill=CHRYSLER, shape=MSO_SHAPE.OVAL)


def wing_mark(slide, x, y, w=Inches(2.0)):
    hairline(slide, x, y, w, color=SILVER, weight=Pt(1.5))
    d = Inches(0.14)
    rect(slide, x + w / 2 - d / 2, y - d / 2, d, d, fill=CHRYSLER,
         shape=MSO_SHAPE.DIAMOND)


def callout(slide, x, y, w, h, head, sub):
    """Subtle callout box."""
    rect(slide, x, y, w, h, fill=CLOUD, line=PLATINUM, line_w=Pt(0.5))
    rect(slide, x, y, Inches(0.06), h, fill=CHRYSLER)
    textbox(slide, x + Inches(0.3), y + Inches(0.22), w - Inches(0.5),
            h - Inches(0.4),
            [{"text": head, "size": 13, "color": INK, "bold": True,
              "space_after": 4},
             {"text": sub, "size": 10.5, "color": SLATE, "line_spacing": 1.2}])


def col_x(i, n, x0=Inches(0.75), total=Inches(11.83), gap=Inches(0.4)):
    w = Emu(int((total - gap * (n - 1)) / n))
    return Emu(int(x0 + (w + gap) * i)), w


# ----------------------------------------------------------------------------
# Slide templates
# ----------------------------------------------------------------------------
def s_title():
    s = add_slide(); set_bg(s)
    image_frame(s, Inches(0), Inches(0), SLIDE_W, SLIDE_H,
                label="FULL-WIDTH HERO VEHICLE IMAGE", fill=CLOUD,
                note="Replace · cinematic full-bleed key visual")
    # lower-left editorial lockup on a soft scrim
    rect(s, Inches(0), Inches(4.7), Inches(8.2), Inches(2.8), fill=WHITE)
    wing_mark(s, Inches(0.85), Inches(5.15), Inches(2.0))
    kicker(s, Inches(0.85), Inches(5.35), "Stellantis · Chrysler")
    textbox(s, Inches(0.82), Inches(5.7), Inches(7.0), Inches(1.0),
            [{"text": "Chrysler Design Vision", "size": 44, "color": INK,
              "bold": True, "name": FONT_DISPLAY}])
    textbox(s, Inches(0.85), Inches(6.65), Inches(7.0), Inches(0.5),
            [{"text": "The Future of Chrysler Design", "size": 16,
              "color": GRAPHITE}])
    notes(s, "Open with the brand ambition. One sentence on why this vision "
              "matters now. Set the tone — design-led, premium, confident.")
    return s


def s_pillars():
    s = add_slide(); set_bg(s)
    kicker(s, Inches(0.75), Inches(0.7), "Executive Story")
    textbox(s, Inches(0.72), Inches(1.05), Inches(11.0), Inches(0.9),
            [{"text": "Why Chrysler?", "size": 32, "color": INK, "bold": True,
              "name": FONT_DISPLAY}])
    # executive summary statement
    rect(s, Inches(0.75), Inches(2.1), Inches(11.83), Inches(1.2), fill=CLOUD)
    textbox(s, Inches(1.1), Inches(2.1), Inches(11.1), Inches(1.2),
            [{"text": "Chrysler makes everyday life effortless — design that "
                      "removes friction and puts people first.", "size": 17,
              "color": GRAPHITE, "italic": True, "line_spacing": 1.25}],
            anchor=MSO_ANCHOR.MIDDLE)
    pillars = [
        ("Modern American Design", "Optimistic, human, unmistakably Chrysler."),
        ("Technology With Purpose", "Intelligence that disappears into the experience."),
        ("Beautiful Simplicity", "Luxury as the absence of friction."),
    ]
    for i, (h, sub) in enumerate(pillars):
        x, w = col_x(i, 3)
        icon_chip(s, x, Inches(3.95))
        hairline(s, x, Inches(4.85), Emu(int(w)))
        textbox(s, x, Inches(5.0), w, Inches(1.5),
                [{"text": f"0{i+1}", "size": 12, "color": SILVER, "bold": True,
                  "spacing": 2.0, "space_after": 6},
                 {"text": h, "size": 16, "color": INK, "bold": True,
                  "space_after": 5},
                 {"text": sub, "size": 11, "color": SLATE, "line_spacing": 1.2}])
    footer(s, 2)
    notes(s, "Three pillars frame the whole story. Keep to one line each. "
              "These recur as the spine of the narrative.")
    return s


def s_vision():
    s = add_slide(); set_bg(s)
    kicker(s, Inches(0.75), Inches(0.7), "The Vision")
    textbox(s, Inches(0.72), Inches(1.05), Inches(11.5), Inches(0.9),
            [{"text": "What is the Vision of Chrysler Design?", "size": 28,
              "color": INK, "bold": True, "name": FONT_DISPLAY}])
    # large quote placeholder (left)
    textbox(s, Inches(0.75), Inches(2.3), Inches(6.4), Inches(2.6),
            [{"text": "“", "size": 60, "color": PLATINUM, "bold": True,
              "space_after": 0},
             {"text": "Luxury is no longer ornament. It is the removal of "
                      "friction from everyday life.", "size": 22,
              "color": INK, "line_spacing": 1.2}])
    # three strategic pillars (left, compact)
    vpillars = [
        ("Innovative Practicality", "design that solves real life"),
        ("Human-Centered Technology", "built around people, not features"),
        ("Beautiful Simplicity", "calm, considered, effortless"),
    ]
    for i, (h, d) in enumerate(vpillars):
        y = Inches(5.05) + Inches(0.6) * i
        rect(s, Inches(0.78), y + Inches(0.04), Inches(0.16), Inches(0.16),
             fill=CHRYSLER, shape=MSO_SHAPE.DIAMOND)
        textbox(s, Inches(1.15), y, Inches(5.8), Inches(0.5),
                [{"text": f"{h}  —  {d}",
                  "size": 13, "color": GRAPHITE}])
    # supporting visual (right)
    image_frame(s, Inches(7.5), Inches(2.2), Inches(5.08), Inches(4.4),
                label="SUPPORTING VISUAL")
    footer(s, 3)
    notes(s, "Land the vision in one quote. The three pillars echo slide 2. "
              "Let the supporting visual carry the emotion.")
    return s


def s_left_right_brain():
    s = add_slide(); set_bg(s)
    kicker(s, Inches(0.75), Inches(0.7), "Strategic Framework")
    textbox(s, Inches(0.72), Inches(1.05), Inches(11.5), Inches(0.9),
            [{"text": "Left Brain / Right Brain", "size": 28, "color": INK,
              "bold": True, "name": FONT_DISPLAY}])
    textbox(s, Inches(0.75), Inches(1.75), Inches(11.5), Inches(0.4),
            [{"text": "Updated Chrysler Board", "size": 14, "color": GRAPHITE}])
    # large board placeholder split into two halves
    image_frame(s, Inches(0.75), Inches(2.35), Inches(5.83), Inches(4.15),
                label="LEFT BRAIN  ·  RATIONAL", note="Replace · board imagery")
    image_frame(s, Inches(6.75), Inches(2.35), Inches(5.83), Inches(4.15),
                label="RIGHT BRAIN  ·  EMOTIONAL", note="Replace · board imagery")
    # center divider mark
    wing_mark(s, Inches(6.18), Inches(4.4), Inches(0.95))
    footer(s, 4)
    notes(s, "Position the dual nature of the brand — rational engineering "
              "credibility meeting emotional design. Walk the board left to right.")
    return s


def s_design_dna():
    s = add_slide(); set_bg(s)
    kicker(s, Inches(0.75), Inches(0.7), "Brand Foundation")
    textbox(s, Inches(0.72), Inches(1.05), Inches(11.5), Inches(0.9),
            [{"text": "Chrysler Design DNA", "size": 28, "color": INK,
              "bold": True, "name": FONT_DISPLAY}])
    # large graphic placeholder (left)
    image_frame(s, Inches(0.75), Inches(2.1), Inches(6.3), Inches(4.4),
                label="LARGE DESIGN-DNA GRAPHIC")
    # three labeled columns (right)
    cols = [
        ("Design Principles", "Thoughtful · Logical · Precise · Purposeful"),
        ("Brand Attributes", "Confident · Approachable · Effortless · Calm"),
        ("Visual Language", "Calm architecture · Warm materials · Human scale"),
    ]
    for i, (h, sub) in enumerate(cols):
        y = Inches(2.2) + Inches(1.45) * i
        callout(s, Inches(7.35), y, Inches(5.23), Inches(1.2), h, sub)
    footer(s, 5)
    notes(s, "Define the DNA that every Chrysler shares. Keep principles tight "
              "and ownable. The graphic should make the language tangible.")
    return s


def s_portfolio():
    s = add_slide(); set_bg(s)
    kicker(s, Inches(0.75), Inches(0.7), "The Lineup")
    textbox(s, Inches(0.72), Inches(1.05), Inches(11.5), Inches(0.9),
            [{"text": "Future Chrysler Portfolio", "size": 28, "color": INK,
              "bold": True, "name": FONT_DISPLAY}])
    tiles = ["Future Pacifica", "Airflow", "Arrow", "Arrow Cross", "300 Concept"]
    for i, name in enumerate(tiles):
        x, w = col_x(i, 5, gap=Inches(0.3))
        image_frame(s, x, Inches(2.3), w, Inches(3.3),
                    label=f"VEHICLE {i+1}", note="Replace")
        textbox(s, x, Inches(5.75), w, Inches(0.4),
                [{"text": name, "size": 12, "color": INK, "bold": True,
                  "align": PP_ALIGN.CENTER}], align=PP_ALIGN.CENTER)
    footer(s, 6)
    notes(s, "Reveal the full family at once — the scale of the vision. "
              "Image placeholders only; no specs.")
    return s


def s_exterior(number, kick, title, summary, bullets):
    """Exec summary + large exterior + three bullets (head, sub)."""
    s = add_slide(); set_bg(s)
    kicker(s, Inches(0.75), Inches(0.7), kick)
    textbox(s, Inches(0.72), Inches(1.05), Inches(6.0), Inches(0.9),
            [{"text": title, "size": 30, "color": INK, "bold": True,
              "name": FONT_DISPLAY}])
    textbox(s, Inches(0.75), Inches(2.0), Inches(5.6), Inches(1.2),
            [{"text": summary, "size": 15,
              "color": GRAPHITE, "italic": True, "line_spacing": 1.3}])
    by = Inches(3.5)
    for i, (head, sub) in enumerate(bullets):
        y = by + Inches(0.95) * i
        icon_chip(s, Inches(0.78), y, Inches(0.5))
        textbox(s, Inches(1.5), y - Inches(0.02), Inches(5.0), Inches(0.8),
                [{"text": head, "size": 14, "color": INK, "bold": True,
                  "space_after": 2},
                 {"text": sub, "size": 11, "color": SLATE}])
    image_frame(s, Inches(7.1), Inches(1.05), Inches(5.48), Inches(5.45),
                label="LARGE EXTERIOR IMAGE")
    footer(s, number)
    notes(s, f"{title}: lead with emotion, then the three strategic bullets. "
              "Let the exterior image dominate.")
    return s


def s_interior(number, kick, title, caption):
    """Large interior rendering + minimal caption."""
    s = add_slide(); set_bg(s)
    kicker(s, Inches(0.75), Inches(0.6), kick)
    textbox(s, Inches(0.72), Inches(0.95), Inches(11.0), Inches(0.7),
            [{"text": title, "size": 26, "color": INK, "bold": True,
              "name": FONT_DISPLAY}])
    image_frame(s, Inches(0.75), Inches(1.8), Inches(11.83), Inches(4.65),
                label="LARGE INTERIOR RENDERING")
    textbox(s, Inches(0.75), Inches(6.55), Inches(11.0), Inches(0.4),
            [{"text": caption, "size": 12,
              "color": SLATE, "spacing": 0.5}])
    footer(s, number)
    notes(s, f"{title}: one immersive rendering, one short caption. "
              "Speak to the experience, not the features.")
    return s


def s_stellantis_fit():
    s = add_slide(); set_bg(s)
    kicker(s, Inches(0.75), Inches(0.7), "Portfolio Positioning")
    textbox(s, Inches(0.72), Inches(1.05), Inches(11.5), Inches(0.9),
            [{"text": "How Chrysler Fits Within Stellantis", "size": 26,
              "color": INK, "bold": True, "name": FONT_DISPLAY}])
    textbox(s, Inches(0.75), Inches(1.75), Inches(11.5), Inches(0.4),
            [{"text": "Differentiation, not overlap — the distinct, "
                      "human-centered space Chrysler owns.", "size": 13,
              "color": GRAPHITE}])
    # Chrysler hero box centered, sibling brand placeholders around
    rect(s, Inches(4.9), Inches(2.5), Inches(3.5), Inches(1.6),
         fill=CHRYSLER)
    textbox(s, Inches(4.9), Inches(2.5), Inches(3.5), Inches(1.6),
            [{"text": "CHRYSLER", "size": 18, "color": WHITE, "bold": True,
              "spacing": 2.0, "align": PP_ALIGN.CENTER, "space_after": 4},
             {"text": "Innovative practicality\nfor everyday life", "size": 11,
              "color": PLATINUM, "align": PP_ALIGN.CENTER,
              "line_spacing": 1.1}], anchor=MSO_ANCHOR.MIDDLE)
    sibs = ["BRAND A", "BRAND B", "BRAND C", "BRAND D"]
    for i, name in enumerate(sibs):
        x, w = col_x(i, 4)
        rect(s, x, Inches(4.7), w, Inches(1.5), fill=CLOUD, line=PLATINUM,
             line_w=Pt(0.5))
        textbox(s, x, Inches(4.7), w, Inches(1.5),
                [{"text": name, "size": 12, "color": SLATE, "bold": True,
                  "spacing": 1.5, "align": PP_ALIGN.CENTER, "space_after": 4},
                 {"text": "Distinct role", "size": 9.5,
                  "color": PLATINUM, "align": PP_ALIGN.CENTER,
                  "line_spacing": 1.1}], anchor=MSO_ANCHOR.MIDDLE)
    footer(s, 17)
    notes(s, "Show where Chrysler sits and how it stays distinct. Replace "
              "BRAND A–D with the relevant Stellantis siblings. Emphasize "
              "white space Chrysler owns.")
    return s


def s_customer_experience():
    s = add_slide(); set_bg(s)
    kicker(s, Inches(0.75), Inches(0.7), "Looking Forward")
    textbox(s, Inches(0.72), Inches(1.05), Inches(11.5), Inches(0.9),
            [{"text": "Future Customer Experience", "size": 28, "color": INK,
              "bold": True, "name": FONT_DISPLAY}])
    items = [
        ("Digital Ecosystem", "Seamless, connected, personal."),
        ("Technology", "Purposeful and invisible."),
        ("Sustainability", "Warm, recycled, responsible materials."),
        ("Luxury", "Friction removed from daily life."),
        ("AI", "Adaptive, predictive, human-centered."),
        ("Connected Mobility", "Effortless, door to destination."),
    ]
    # 3 x 2 grid of icon + label cards
    gx, gw = Inches(0.75), Inches(11.83)
    cols, rows = 3, 2
    gap = Inches(0.4)
    cw = Emu(int((gw - gap * (cols - 1)) / cols))
    ch = Inches(2.0)
    for idx, (name, note_txt) in enumerate(items):
        r, c = divmod(idx, cols)
        x = Emu(int(gx + (cw + gap) * c))
        y = Inches(2.25) + (ch + Inches(0.35)) * r
        rect(s, x, y, cw, ch, fill=CLOUD, line=PLATINUM, line_w=Pt(0.5))
        # icon placeholder
        isz = Inches(0.7)
        rect(s, Emu(int(x + Inches(0.35))), Emu(int(y + Inches(0.35))),
             isz, isz, fill=None, line=CHRYSLER, line_w=Pt(1.25),
             shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        textbox(s, Emu(int(x + Inches(0.35))), Emu(int(y + Inches(0.42))),
                isz, isz, [{"text": "ICON", "size": 7.5, "color": SILVER,
                            "spacing": 1.0, "align": PP_ALIGN.CENTER}],
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
        textbox(s, Emu(int(x + Inches(0.35))), Emu(int(y + Inches(1.25))),
                Emu(int(cw - Inches(0.7))), Inches(0.6),
                [{"text": name, "size": 14, "color": INK, "bold": True,
                  "space_after": 3},
                 {"text": note_txt, "size": 10, "color": SLATE,
                  "line_spacing": 1.15}])
    footer(s, 18)
    notes(s, "Paint the experience Chrysler will deliver. Six themes — swap "
              "ICON boxes for final iconography. Keep words minimal.")
    return s


def s_design_innovation():
    s = add_slide(); set_bg(s)
    kicker(s, Inches(0.75), Inches(0.7), "Capability")
    textbox(s, Inches(0.72), Inches(1.05), Inches(11.5), Inches(0.9),
            [{"text": "Design Innovation", "size": 28, "color": INK,
              "bold": True, "name": FONT_DISPLAY}])
    # large infographic placeholder spanning, with 6 labeled nodes below
    image_frame(s, Inches(0.75), Inches(2.0), Inches(11.83), Inches(2.7),
                label="LARGE INFOGRAPHIC PLACEHOLDER",
                note="Replace · innovation framework graphic")
    areas = ["Exterior Design", "Interior Design", "CMF",
             "Lighting", "Digital Experience", "AI-enabled Design"]
    for i, name in enumerate(areas):
        x, w = col_x(i, 6, gap=Inches(0.25))
        rect(s, x, Inches(4.95), w, Inches(1.4), fill=CLOUD, line=PLATINUM,
             line_w=Pt(0.5))
        rect(s, x, Inches(4.95), w, Inches(0.07), fill=CHRYSLER)
        textbox(s, Emu(int(x + Inches(0.18))), Inches(5.2),
                Emu(int(w - Inches(0.36))), Inches(1.1),
                [{"text": f"0{i+1}", "size": 11, "color": SILVER, "bold": True,
                  "space_after": 4},
                 {"text": name, "size": 11.5, "color": INK, "bold": True,
                  "line_spacing": 1.1}])
    footer(s, 19)
    notes(s, "Show breadth of design capability across six domains. The "
              "infographic ties them into one system. Replace nodes as needed.")
    return s


def s_takeaways():
    s = add_slide(); set_bg(s)
    image_frame(s, Inches(0), Inches(0), SLIDE_W, Inches(3.3),
                label="CLOSING HERO IMAGE", fill=CLOUD,
                note="Replace · aspirational closing visual", icon=False)
    kicker(s, Inches(0.75), Inches(3.6), "In Summary")
    textbox(s, Inches(0.72), Inches(3.95), Inches(11.0), Inches(0.8),
            [{"text": "Executive Takeaways", "size": 30, "color": INK,
              "bold": True, "name": FONT_DISPLAY}])
    msgs = [
        ("Designed Around People", "Luxury is the removal of everyday friction."),
        ("Distinct Within Stellantis", "Modern American design — human and confident."),
        ("Ready to Lead", "A clear, design-led vision for Chrysler's future."),
    ]
    for i, (h, sub) in enumerate(msgs):
        x, w = col_x(i, 3)
        textbox(s, x, Inches(5.0), w, Inches(0.7),
                [{"text": f"0{i+1}", "size": 30, "color": SILVER, "bold": True,
                  "name": FONT_DISPLAY}])
        hairline(s, x, Inches(5.7), Emu(int(w)))
        textbox(s, x, Inches(5.85), w, Inches(1.2),
                [{"text": h, "size": 16, "color": INK, "bold": True,
                  "space_after": 5},
                 {"text": sub, "size": 11.5, "color": GRAPHITE,
                  "line_spacing": 1.25}])
    footer(s, 20)
    notes(s, "Close on three memorable messages that map to the three pillars. "
              "End on the hero image and the ask.")
    return s


# ----------------------------------------------------------------------------
# Build
# ----------------------------------------------------------------------------
s_title()                                                          # 1
s_pillars()                                                        # 2
s_vision()                                                         # 3
s_left_right_brain()                                               # 4
s_design_dna()                                                     # 5
s_portfolio()                                                      # 6
s_exterior(7, "The Modern Family Vehicle", "Pacifica",
           "The evolution of the modern family vehicle — flexible, "
           "sophisticated, and designed around people.",
           [("Flexible by Design", "Space that adapts to every journey."),
            ("Sophisticated Comfort", "Refined, calm, effortlessly livable."),
            ("Technology Around People", "Intelligence that serves the family.")])
s_interior(8, "Pacifica", "Pacifica Interior",
           "A family sanctuary — flexible, comfortable, designed around people.")  # 8
s_exterior(9, "The Emotional Halo", "300 Concept",
           "The flagship expression of Chrysler design — composed, "
           "commanding, never excessive.",
           [("Commanding Presence", "Architectural proportion, balanced and tailored."),
            ("Quiet Power", "Confidence expressed through restraint."),
            ("Timeless Craftsmanship", "Authentic American design, refined.")])
s_interior(10, "300 Concept", "300 Interior",
           "An interior sanctuary — crafted, composed, human in scale.")  # 10
s_exterior(11, "The Philosophy", "Airflow",
           "Airflow introduces Chrysler's philosophy: innovative "
           "practicality, designed around people.",
           [("Spacious & Adaptive", "Versatile space for everyday life."),
            ("Technology With Purpose", "Intelligence that serves, then disappears."),
            ("Confident Simplicity", "Clean, logical, human-centered form.")])
s_interior(12, "Airflow", "Airflow Interior",
           "Designed around people — flexible, calm, effortlessly useful.")  # 12
s_exterior(13, "Clever Accessibility", "Arrow",
           "Chrysler's accessible entry — clever, design-led, and "
           "attainable from around $24K.",
           [("Smart & Simple", "Approachable design for the city."),
            ("Attainable", "Thoughtful style within reach."),
            ("Youthful & Modern", "Efficient, urban, design-led.")])
s_interior(14, "Arrow", "Arrow Interior",
           "Smart, simple, and useful — accessible design done thoughtfully.")  # 14
s_exterior(15, "Purposeful Versatility", "Arrow Cross",
           "An accessible crossover with purposeful versatility — "
           "designed around everyday life.",
           [("Flexible & Versatile", "Thoughtful packaging for families."),
            ("Urban & Useful", "Confident, modern, accessible."),
            ("Everyday Ready", "Simple design that adapts.")])
s_interior(16, "Arrow Cross", "Arrow Cross Interior",
           "Versatile and family-friendly — space designed for real life.")  # 16
s_stellantis_fit()                                                 # 17
s_customer_experience()                                            # 18
s_design_innovation()                                              # 19
s_takeaways()                                                      # 20

OUT = "/home/user/CLAUDE/Chrysler_Brand_Design_Vision.pptx"
prs.save(OUT)
print(f"Saved {OUT} with {len(prs.slides._sldIdLst)} slides.")

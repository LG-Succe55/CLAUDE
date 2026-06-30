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
from pptx.oxml.ns import qn

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
    notes(s, "Open with the through-line of the whole deck: Chrysler removes "
              "friction from everyday life through thoughtful, people-first "
              "design. Set a calm, confident, design-led tone — and signal the "
              "audience will never lose sight of that idea.")
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
            [{"text": "Chrysler removes friction from everyday life through "
                      "thoughtful, people-first design.", "size": 17,
              "color": GRAPHITE, "italic": True, "line_spacing": 1.25}],
            anchor=MSO_ANCHOR.MIDDLE)
    pillars = [
        ("Designed Around People", "Every decision begins with the people who use it."),
        ("Removing Everyday Friction", "Thoughtful design that makes daily life easier."),
        ("Modern American Design", "Confident, optimistic, unmistakably Chrysler."),
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
    notes(s, "Open the story: this is why Chrysler exists. State the central "
              "philosophy plainly, then the three ideas it rests on — we return "
              "to exactly these three at the close. Transition: 'This belief is "
              "not abstract. It begins with how we think.'")
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
    # the four brand pillars — the principles behind every decision
    vpillars = [
        ("People First", "every decision begins with people"),
        ("Everyday Ingenuity", "solutions that make daily life easier"),
        ("Human-Centered Intelligence", "technology that quietly supports"),
        ("Modern American Design", "confident, optimistic, unmistakably Chrysler"),
    ]
    for i, (h, d) in enumerate(vpillars):
        y = Inches(4.95) + Inches(0.5) * i
        rect(s, Inches(0.78), y + Inches(0.04), Inches(0.16), Inches(0.16),
             fill=CHRYSLER, shape=MSO_SHAPE.DIAMOND)
        textbox(s, Inches(1.15), y, Inches(6.1), Inches(0.5),
                [{"text": f"{h}  —  {d}",
                  "size": 13, "color": GRAPHITE}])
    # supporting visual (right)
    image_frame(s, Inches(7.5), Inches(2.2), Inches(5.08), Inches(4.4),
                label="SUPPORTING VISUAL")
    footer(s, 3)
    notes(s, "How Chrysler thinks differently. The quote reframes luxury as the "
              "removal of friction. Introduce the four pillars that guide every "
              "design decision — People First, Everyday Ingenuity, Human-Centered "
              "Intelligence, Modern American Design. Transition: 'These principles "
              "are not abstract. They become tangible in every vehicle.'")
    return s


def s_left_right_brain():
    s = add_slide(); set_bg(s)
    kicker(s, Inches(0.75), Inches(0.7), "Strategic Framework")
    textbox(s, Inches(0.72), Inches(1.05), Inches(11.5), Inches(0.9),
            [{"text": "Left Brain / Right Brain", "size": 28, "color": INK,
              "bold": True, "name": FONT_DISPLAY}])
    textbox(s, Inches(0.75), Inches(1.75), Inches(11.5), Inches(0.4),
            [{"text": "How Chrysler thinks — logic and feeling, held together.",
              "size": 14, "color": GRAPHITE}])
    # large board placeholder split into two halves
    image_frame(s, Inches(0.75), Inches(2.35), Inches(5.83), Inches(4.15),
                label="LEFT BRAIN  ·  ENGINEERED FOR LIFE",
                note="Replace · board imagery")
    image_frame(s, Inches(6.75), Inches(2.35), Inches(5.83), Inches(4.15),
                label="RIGHT BRAIN  ·  DESIGNED FOR PEOPLE",
                note="Replace · board imagery")
    # center divider mark
    wing_mark(s, Inches(6.18), Inches(4.4), Inches(0.95))
    footer(s, 4)
    notes(s, "Chrysler thinks differently: rational rigor and human emotion are "
              "not opposites — together they remove friction. Transition: 'This "
              "way of thinking resolves into a clear design DNA.'")
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
        ("The Four Pillars", "People First · Everyday Ingenuity · Human-Centered "
                             "Intelligence · Modern American Design"),
        ("Brand Attributes", "Confident · Approachable · Effortless · Calm"),
        ("Visual Language", "Calm architecture · Warm materials · Human scale"),
    ]
    for i, (h, sub) in enumerate(cols):
        y = Inches(2.2) + Inches(1.45) * i
        callout(s, Inches(7.35), y, Inches(5.23), Inches(1.2), h, sub)
    footer(s, 5)
    notes(s, "The shared DNA every Chrysler carries — the four pillars made "
              "tangible. Transition: 'These principles are not abstract ideas. "
              "They come to life in every vehicle.'")
    return s


def s_portfolio():
    s = add_slide(); set_bg(s)
    kicker(s, Inches(0.75), Inches(0.7), "The Lineup")
    textbox(s, Inches(0.72), Inches(1.05), Inches(11.5), Inches(0.9),
            [{"text": "Future Chrysler Portfolio", "size": 28, "color": INK,
              "bold": True, "name": FONT_DISPLAY}])
    textbox(s, Inches(0.75), Inches(1.72), Inches(11.5), Inches(0.4),
            [{"text": "One philosophy, serving different lives — and "
                      "unmistakably Chrysler in every one.", "size": 14,
              "color": GRAPHITE}])
    tiles = ["Future Pacifica", "Airflow", "Arrow", "Arrow Cross", "300 Concept"]
    for i, name in enumerate(tiles):
        x, w = col_x(i, 5, gap=Inches(0.3))
        image_frame(s, x, Inches(2.3), w, Inches(3.3),
                    label=f"VEHICLE {i+1}", note="Replace")
        textbox(s, x, Inches(5.75), w, Inches(0.4),
                [{"text": name, "size": 12, "color": INK, "bold": True,
                  "align": PP_ALIGN.CENTER}], align=PP_ALIGN.CENTER)
    footer(s, 6)
    notes(s, "Reveal the full family at once. Frame it as evidence: 'Together, "
              "the portfolio shows how one philosophy serves different lifestyles "
              "while remaining unmistakably Chrysler.' Each vehicle that follows "
              "expresses one primary pillar. Image placeholders only; no specs.")
    return s


def s_exterior(number, kick, title, summary, bullets):
    """Large full-width exterior image; summary subtitle + three bullets below."""
    s = add_slide(); set_bg(s)
    kicker(s, Inches(0.75), Inches(0.6), kick)
    textbox(s, Inches(0.72), Inches(0.95), Inches(11.0), Inches(0.7),
            [{"text": title, "size": 26, "color": INK, "bold": True,
              "name": FONT_DISPLAY}])
    # executive summary as a single subtitle line
    textbox(s, Inches(0.75), Inches(1.62), Inches(11.83), Inches(0.45),
            [{"text": summary, "size": 13, "color": GRAPHITE, "italic": True,
              "line_spacing": 1.2}])
    # large full-width image (matches interior format)
    image_frame(s, Inches(0.75), Inches(2.2), Inches(11.83), Inches(3.7),
                label="LARGE EXTERIOR IMAGE")
    # three strategic bullets in a row beneath the image
    for i, (head, sub) in enumerate(bullets):
        x, w = col_x(i, 3)
        icon_chip(s, x, Inches(6.05), Inches(0.42))
        textbox(s, Emu(int(x + Inches(0.6))), Inches(6.0),
                Emu(int(w - Inches(0.6))), Inches(0.85),
                [{"text": head, "size": 12.5, "color": INK, "bold": True,
                  "space_after": 1},
                 {"text": sub, "size": 10, "color": SLATE, "line_spacing": 1.1}])
    footer(s, number)
    notes(s, f"{title} — primary principle: {kick}. Let the image carry the "
              "emotion; the summary states the role this vehicle plays in the "
              "philosophy, and the bullets reinforce that one principle while "
              "quietly supporting the others. Tie every point back to removing "
              "friction for the people who use it.")
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
    notes(s, f"{title} — primary principle: {kick}. One immersive rendering, "
              "one short caption. Speak to the lived experience and the calm of "
              "everyday use, not the features.")
    return s


def _set_dash(shape, val="dash"):
    ln = shape.line._get_or_add_ln()
    d = ln.find(qn('a:prstDash'))
    if d is None:
        d = ln.makeelement(qn('a:prstDash'), {})
        ln.append(d)
    d.set('val', val)


def s_stellantis_fit():
    s = add_slide(); set_bg(s)
    kicker(s, Inches(0.75), Inches(0.55), "Portfolio Positioning")
    textbox(s, Inches(0.72), Inches(0.9), Inches(11.5), Inches(0.6),
            [{"text": "Customer Segmentation and Brand Placement", "size": 23,
              "color": INK, "bold": True, "name": FONT_DISPLAY}])
    # insight banner (from reference)
    rect(s, Inches(0.75), Inches(1.55), Inches(11.83), Inches(0.5), fill=CLOUD)
    textbox(s, Inches(0.95), Inches(1.55), Inches(11.4), Inches(0.5),
            [{"text": "Chrysler customers align with Hyundai, Kia, and imports "
                      "on the perception map.", "size": 14, "color": CHRYSLER,
              "align": PP_ALIGN.CENTER}], anchor=MSO_ANCHOR.MIDDLE,
            align=PP_ALIGN.CENTER)

    # ---- perception map plot ----
    px, py, pw, ph = Inches(1.85), Inches(2.35), Inches(9.5), Inches(3.25)
    cx = Emu(int(px + pw / 2)); cy = Emu(int(py + ph / 2))

    def C(fx, fy):
        return Emu(int(px + pw * fx)), Emu(int(py + ph * fy))

    # axes
    hairline(s, px, cy, pw, color=SLATE, weight=Pt(1.0))
    ax = s.shapes.add_connector(2, cx, py, cx, Emu(int(py + ph)))
    ax.line.color.rgb = SLATE; ax.line.width = Pt(1.0)
    # axis labels
    textbox(s, Emu(int(cx - Inches(1.3))), Emu(int(py - Inches(0.30))),
            Inches(2.6), Inches(0.3),
            [{"text": "Forward-Thinking", "size": 11, "color": GRAPHITE,
              "align": PP_ALIGN.CENTER}], align=PP_ALIGN.CENTER)
    textbox(s, Emu(int(cx - Inches(1.3))), Emu(int(py + ph + Inches(0.02))),
            Inches(2.6), Inches(0.3),
            [{"text": "Conventional", "size": 11, "color": GRAPHITE,
              "align": PP_ALIGN.CENTER}], align=PP_ALIGN.CENTER)
    textbox(s, Emu(int(cx - Inches(2.0))), Emu(int(cy - Inches(0.34))),
            Inches(1.5), Inches(0.3),
            [{"text": "Practical", "size": 11, "color": GRAPHITE,
              "align": PP_ALIGN.RIGHT}], align=PP_ALIGN.RIGHT)
    textbox(s, Emu(int(cx + Inches(0.5))), Emu(int(cy - Inches(0.34))),
            Inches(1.5), Inches(0.3),
            [{"text": "Emotional", "size": 11, "color": GRAPHITE}])
    # 56% / 44% split numbers flanking the map
    textbox(s, Inches(0.15), Emu(int(cy - Inches(0.45))), Inches(1.55), Inches(0.9),
            [{"text": "56%", "size": 34, "color": INK, "bold": True,
              "name": FONT_DISPLAY, "align": PP_ALIGN.CENTER}],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    textbox(s, Inches(11.6), Emu(int(cy - Inches(0.45))), Inches(1.6), Inches(0.9),
            [{"text": "44%", "size": 34, "color": INK, "bold": True,
              "name": FONT_DISPLAY, "align": PP_ALIGN.CENTER}],
            align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # ---- grouping ellipses (behind bubbles) ----
    def ellipse(fx0, fy0, fx1, fy1, color, dash=False, weight=Pt(1.25)):
        x0, y0 = C(fx0, fy0); x1, y1 = C(fx1, fy1)
        e = rect(s, x0, y0, Emu(int(x1 - x0)), Emu(int(y1 - y0)),
                 fill=None, line=color, line_w=weight, shape=MSO_SHAPE.OVAL)
        if dash:
            _set_dash(e, "dash")
        return e
    # import cluster (dashed) around Hyundai / Chrysler / Kia
    ellipse(0.14, 0.16, 0.50, 0.56, CHRYSLER, dash=True, weight=Pt(1.5))
    # sibling groupings (solid, dark)
    ellipse(0.60, 0.30, 0.82, 0.46, INK)     # Ford + Jeep
    ellipse(0.66, 0.44, 0.86, 0.60, INK)     # Chevrolet + Dodge
    ellipse(0.52, 0.62, 0.68, 0.80, INK)     # Ram

    # ---- segment bubbles (name + %) ----
    PURPLE = RGBColor(0x6E, 0x4A, 0x9E); REDS = RGBColor(0xC0, 0x39, 0x3C)
    LBLUE = RGBColor(0x4F, 0xA3, 0xD1);  ORANGE = RGBColor(0xE2, 0x7D, 0x2E)
    MAUVE = RGBColor(0x8E, 0x4B, 0x5E);  YELLO = RGBColor(0xE7, 0xC8, 0x4A)
    TEAL = RGBColor(0x4C, 0xB1, 0x8E);   LIME = RGBColor(0x9E, 0xC1, 0x3B)
    PINKM = RGBColor(0xC9, 0x6E, 0x8E);  BLUEB = RGBColor(0x2E, 0x52, 0xA0)
    segs = [
        ("Eco-Conscious Utilitarians", 7, 0.18, 0.27, PURPLE, WHITE),
        ("Sensible Progressives", 13, 0.42, 0.22, REDS, WHITE),
        ("Successful Stewards", 7, 0.66, 0.14, LBLUE, WHITE),
        ("Affluent Achievers", 11, 0.67, 0.27, ORANGE, WHITE),
        ("Functional Doers", 8, 0.56, 0.34, MAUVE, WHITE),
        ("Cautious Commuters", 8, 0.46, 0.45, YELLO, INK),
        ("Basic Drivers", 15, 0.29, 0.63, TEAL, WHITE),
        ("Proud Workhorses", 14, 0.45, 0.71, LIME, INK),
        ("Upscale Traditionalists", 9, 0.61, 0.57, PINKM, WHITE),
        ("Empowered Enthusiasts", 9, 0.73, 0.62, BLUEB, WHITE),
    ]
    for name, pct, fx, fy, col, tc in segs:
        d = Inches(0.52 + pct * 0.028)
        cxp, cyp = C(fx, fy)
        bx = Emu(int(cxp - d / 2)); by = Emu(int(cyp - d / 2))
        rect(s, bx, by, d, d, fill=col, shape=MSO_SHAPE.OVAL)
        textbox(s, bx, Emu(int(by + Inches(0.04))), d, Emu(int(d - Inches(0.08))),
                [{"text": name, "size": 6.5, "color": tc, "bold": True,
                  "align": PP_ALIGN.CENTER, "line_spacing": 0.95,
                  "space_after": 1},
                 {"text": f"{pct}%", "size": 8, "color": tc, "bold": True,
                  "align": PP_ALIGN.CENTER}],
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

    # ---- brand markers (chips) ----
    def chip(fx, fy, name, hero=False):
        w = Inches(1.05) if hero else Inches(0.78)
        h = Inches(0.42) if hero else Inches(0.28)
        cxp, cyp = C(fx, fy)
        bx = Emu(int(cxp - w / 2)); by = Emu(int(cyp - h / 2))
        fill = RGBColor(0xFB, 0xF2, 0xC4) if hero else WHITE
        line = CHRYSLER if hero else SLATE
        rect(s, bx, by, w, h, fill=fill, line=line,
             line_w=Pt(1.25) if hero else Pt(0.5),
             shape=MSO_SHAPE.ROUNDED_RECTANGLE)
        textbox(s, bx, by, w, h,
                [{"text": name, "size": 11 if hero else 8.5,
                  "color": CHRYSLER if hero else INK, "bold": True,
                  "spacing": 1.5 if hero else 0.5, "align": PP_ALIGN.CENTER}],
                align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)
    chip(0.40, 0.11, "Honda")
    chip(0.27, 0.31, "Hyundai")
    chip(0.45, 0.31, "CHRYSLER", hero=True)
    chip(0.33, 0.44, "Kia")
    chip(0.15, 0.55, "Toyota")
    chip(0.62, 0.38, "Ford")
    chip(0.74, 0.38, "Jeep")
    chip(0.69, 0.52, "Chevrolet")
    chip(0.80, 0.52, "Dodge")
    chip(0.58, 0.70, "Ram")

    # ---- bottom bars: Hyundai / Kia practical vs emotional ----
    bx0, btot = Inches(2.55), Inches(5.2)
    pw_ratio = 0.72
    p_w = Emu(int(btot * pw_ratio)); e_w = Emu(int(btot * (1 - pw_ratio)))
    textbox(s, bx0, Inches(5.92), p_w, Inches(0.25),
            [{"text": "Practical", "size": 9, "color": SLATE,
              "align": PP_ALIGN.CENTER}], align=PP_ALIGN.CENTER)
    textbox(s, Emu(int(bx0 + p_w)), Inches(5.92), e_w, Inches(0.25),
            [{"text": "Emotional", "size": 9, "color": SLATE,
              "align": PP_ALIGN.CENTER}], align=PP_ALIGN.CENTER)
    for i, brand in enumerate(["Hyundai", "Kia"]):
        y = Emu(int(Inches(6.22) + Inches(0.34) * i))
        textbox(s, Inches(1.2), Emu(int(y - Inches(0.02))), Inches(1.25),
                Inches(0.28),
                [{"text": brand, "size": 10, "color": INK,
                  "align": PP_ALIGN.RIGHT}], align=PP_ALIGN.RIGHT)
        rect(s, bx0, y, p_w, Inches(0.24), fill=CHRYSLER)
        rect(s, Emu(int(bx0 + p_w)), y, e_w, Inches(0.24), fill=None,
             line=PLATINUM, line_w=Pt(0.75))
        textbox(s, bx0, y, Emu(int(p_w - Inches(0.12))), Inches(0.24),
                [{"text": "72%", "size": 9, "color": WHITE, "bold": True,
                  "align": PP_ALIGN.RIGHT}], align=PP_ALIGN.RIGHT,
                anchor=MSO_ANCHOR.MIDDLE)
        textbox(s, Emu(int(bx0 + p_w + Inches(0.1))), y, e_w, Inches(0.24),
                [{"text": "28%", "size": 9, "color": SLATE}],
                anchor=MSO_ANCHOR.MIDDLE)

    textbox(s, Inches(0.75), Inches(7.02), Inches(9), Inches(0.3),
            [{"text": "Sources: Segmentation Survey 2024; Hyundai/Kia: NVCS "
                      "Oct ’23–Mar ’25", "size": 7.5,
              "color": PLATINUM, "spacing": 0.3}])
    footer(s, 17)
    notes(s, "The segmentation evidence: Chrysler buyers sit in the practical, "
              "forward-thinking quadrant beside Honda, Hyundai, Kia and Toyota — "
              "the imports they cross-shop. Stellantis siblings sit on the "
              "emotional side: Ford/Jeep, Chevrolet/Dodge, and Ram. The market "
              "splits 56% practical / 44% emotional, and Hyundai and Kia index "
              "72% practical. Chrysler owns this human-centered space; its "
              "siblings own emotion, adventure, and capability. Transition: "
              "'Together, these vehicles define Chrysler's future.'")
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
    notes(s, "Human-Centered Intelligence in practice: technology that quietly "
              "supports and removes friction. AI is an enabler, never the brand. "
              "Six themes — swap ICON boxes for final iconography. Keep words "
              "minimal.")
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
    notes(s, "Breadth of design capability across six domains, unified by one "
              "philosophy. Replace nodes as needed. Transition into the close: "
              "'When every decision begins with people, this is what design "
              "becomes.'")
    return s


def s_takeaways():
    s = add_slide(); set_bg(s)
    image_frame(s, Inches(0), Inches(0), SLIDE_W, Inches(3.3),
                label="CLOSING HERO IMAGE", fill=CLOUD,
                note="Replace · aspirational closing visual", icon=False)
    kicker(s, Inches(0.75), Inches(3.6), "In Closing")
    textbox(s, Inches(0.72), Inches(3.95), Inches(11.0), Inches(0.6),
            [{"text": "The Future of Chrysler", "size": 30, "color": INK,
              "bold": True, "name": FONT_DISPLAY}])
    # closing statement — mirrors the philosophy stated on slide 2
    textbox(s, Inches(0.75), Inches(4.5), Inches(11.83), Inches(0.5),
            [{"text": "When every decision begins with people, thoughtful design "
                      "becomes effortless living — that is the future of Chrysler.",
              "size": 13, "color": GRAPHITE, "italic": True, "line_spacing": 1.2}])
    msgs = [
        ("Designed Around People", "Every decision begins with the people who use it."),
        ("Removing Everyday Friction", "Thoughtful design that makes life effortless."),
        ("Modern American Design", "Confident, optimistic, unmistakably Chrysler."),
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
    notes(s, "Come full circle: these are the same three ideas opened on slide 2 "
              "— Designed Around People, Removing Everyday Friction, Modern "
              "American Design. Deliver the closing statement as the final word; "
              "it should feel like a vision, not a summary.")
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
# Pacifica — primary pillar: People First
s_exterior(7, "People First", "Pacifica",
           "Pacifica is the proof that Chrysler has always designed around "
           "people.",
           [("Family Mobility", "Built around the people who live in it."),
            ("Flexible Living", "Space that adapts to every journey."),
            ("Thoughtful Innovation", "Technology designed around people.")])
s_interior(8, "People First", "Pacifica Interior",
           "A family sanctuary — comfort, space, and calm, designed around people.")
# 300 Concept — primary pillar: Modern American Design
s_exterior(9, "Modern American Design", "300 Concept",
           "The flagship expression of Chrysler design — presence through "
           "confidence and craftsmanship, never excess.",
           [("Commanding Presence", "Architectural proportion, calm and assured."),
            ("Crafted Composure", "Confidence expressed through restraint."),
            ("Authentically American", "Timeless design, unmistakably Chrysler.")])
s_interior(10, "Modern American Design", "300 Interior",
           "Crafted, composed, human in scale — presence without excess.")
# Airflow — primary pillar: Everyday Ingenuity
s_exterior(11, "Everyday Ingenuity", "Airflow",
           "Chrysler's design manifesto — intelligent design that simplifies "
           "everyday life rather than complicating it.",
           [("Everyday Ingenuity", "Thoughtful solutions for daily life."),
            ("Intelligence That Recedes", "Technology that quietly supports."),
            ("Confident Simplicity", "Clean, modern, human-centered form.")])
s_interior(12, "Everyday Ingenuity", "Airflow Interior",
           "Designed around people — calm, intelligent, effortlessly useful.")
# Arrow — primary theme: Accessible Design
s_exterior(13, "Accessible Design", "Arrow",
           "Thoughtful Chrysler design, made attainable — approachable, smart, "
           "and easy to live with.",
           [("Approachable Design", "An inviting introduction to Chrysler."),
            ("Smart Packaging", "Everyday usability, thoughtfully resolved."),
            ("Attainable by Design", "Accessible without compromise.")])
s_interior(14, "Accessible Design", "Arrow Interior",
           "Approachable and intuitive — thoughtful design, made attainable.")
# Arrow Cross — primary theme: Purposeful Versatility
s_exterior(15, "Purposeful Versatility", "Arrow Cross",
           "Thoughtful design that adapts to modern family life — flexible, "
           "confident, and quietly intelligent.",
           [("Purposeful Versatility", "Flexibility for how families really live."),
            ("Practical Intelligence", "Smart packaging, calmly resolved."),
            ("Confident & Capable", "Modern, accessible, ready for the everyday.")])
s_interior(16, "Purposeful Versatility", "Arrow Cross Interior",
           "Flexible and family-ready — design that adapts to everyday life.")
s_stellantis_fit()                                                 # 17
s_customer_experience()                                            # 18
s_design_innovation()                                              # 19
s_takeaways()                                                      # 20

OUT = "/home/user/CLAUDE/Chrysler_Brand_Design_Vision.pptx"
prs.save(OUT)
print(f"Saved {OUT} with {len(prs.slides._sldIdLst)} slides.")

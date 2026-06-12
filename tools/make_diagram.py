#!/usr/bin/env python3
"""Process pipeline diagram for the Global Design AI Intake & Integration Framework."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.patches as mpatches

TEAL   = '#0E7C7B'
NAVY   = '#1B2A4A'
GRAY   = '#6B7280'
LIGHT  = '#EDF3F3'
AMBER  = '#B45309'
BG     = '#FFFFFF'

fig, ax = plt.subplots(figsize=(13.4, 4.6), dpi=200)
ax.set_xlim(0, 13.4); ax.set_ylim(0, 4.6)
ax.axis('off'); fig.patch.set_facecolor(BG)

stages = [
    ('EXPLORE',    'Intake & evaluation', 'Ideas under consideration', 0.45),
    ('PILOT',      '30–90 day validation', 'Active testing with charter', 3.65),
    ('ACCELERATE', 'Expand & verify value', 'Measurable value, larger scope', 6.85),
    ('SCALE',      'Global deployment', 'Approved standard practice', 10.05),
]
BW, BH, BY = 2.9, 1.5, 2.35

gates = [
    ('G1', 'Prioritization\nscorecard · duplicate check', 3.375),
    ('G2', 'Pilot readiness\ncharter · security pre-check', 6.575),
    ('G3', 'Evidence\nfinal assessment vs criteria', 9.775),
]

for name, sub, desc, x in stages:
    box = FancyBboxPatch((x, BY), BW, BH, boxstyle='round,pad=0.02,rounding_size=0.12',
                         facecolor=LIGHT, edgecolor=TEAL, linewidth=1.6)
    ax.add_patch(box)
    ax.text(x + 0.18, BY + BH - 0.38, name, fontsize=13, fontweight='bold', color=NAVY)
    ax.text(x + 0.18, BY + BH - 0.74, sub, fontsize=8.5, color=TEAL, fontweight='bold')
    ax.text(x + 0.18, BY + 0.24, desc, fontsize=8, color=GRAY)

for gname, glabel, gx in gates:
    ax.add_patch(mpatches.RegularPolygon((gx + 0.135, BY + BH / 2), 4, radius=0.21,
                 orientation=0.785, facecolor=NAVY, edgecolor='none'))
    ax.text(gx + 0.135, BY + BH / 2 - 0.012, gname, fontsize=7.5, fontweight='bold',
            color='white', ha='center', va='center')
    ax.text(gx + 0.135, BY - 0.34, glabel, fontsize=7, color=NAVY, ha='center', va='top')

# gate G4 after SCALE entry: place between accelerate and scale already covered (G3) -> G4 = scale decision
# arrows between boxes
for x1, x2 in [(3.35, 3.65), (6.55, 6.85), (9.75, 10.05)]:
    pass  # gates occupy the gaps; arrows drawn under gates
for xa in [(3.35, 3.66), (6.55, 6.86), (9.75, 10.06)]:
    ar = FancyArrowPatch((xa[0], BY + BH/2), (xa[1], BY + BH/2),
                         arrowstyle='-', color=TEAL, linewidth=1.4)
    ax.add_patch(ar)

# intake entry arrow
ax.annotate('', xy=(0.45, BY + BH/2), xytext=(-0.25 + 0.3, BY + BH/2),
            arrowprops=dict(arrowstyle='-|>', color=NAVY, lw=1.6))
ax.text(0.06, BY + BH/2 - 0.30, 'INTAKE', fontsize=7.5,
        color=NAVY, fontweight='bold', va='top')
ax.text(0.06, BY + BH/2 - 0.56, 'one global\nfront door', fontsize=6.5,
        color=GRAY, va='top')

# retire lane
ry = 0.62
ax.add_patch(FancyBboxPatch((3.65, ry - 0.32), 6.1, 0.72,
             boxstyle='round,pad=0.02,rounding_size=0.1',
             facecolor='#FAF5EC', edgecolor=AMBER, linewidth=1.2))
ax.text(6.7, ry + 0.20, 'RETIRE', fontsize=9.5, fontweight='bold', color=AMBER,
        ha='center')
ax.text(6.7, ry - 0.13, 'any stage · lessons learned captured · knowledge asset created — retired is a result, not a failure',
        fontsize=7.5, color=GRAY, ha='center')
for gx in [5.1, 8.3]:
    ax.annotate('', xy=(gx, ry + 0.42), xytext=(gx, BY - 0.62),
                arrowprops=dict(arrowstyle='-|>', color=AMBER, lw=1.0,
                                linestyle=(0, (4, 3))))

# top annotation: orchestration
ax.text(0.45, 4.32, 'GLOBAL DESIGN AI PIPELINE', fontsize=10, fontweight='bold',
        color=TEAL)
ax.text(0.45, 4.02, 'Orchestrated by the Global AI Design Lead · owned and executed by the originating teams',
        fontsize=8.5, color=GRAY)
ax.text(12.95, 4.02, 'G4 = scale decision (Design leadership + enterprise partners)',
        fontsize=7.5, color=NAVY, ha='right')

plt.tight_layout(pad=0.4)
plt.savefig('/home/user/CLAUDE/work/framework_pipeline.png', dpi=200,
            bbox_inches='tight', facecolor=BG)
print('diagram saved')

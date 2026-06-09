# Design References

Curated visual + design system resources, installed from GitHub for offline reference during presentation and web design work.

## Files

### `design-resources-for-developers.md`
**Source:** [bradtraversy/design-resources-for-developers](https://github.com/bradtraversy/design-resources-for-developers) (~62K stars)
**Use for:** Raw visual assets — UI kits, mockups, free stock photo libraries, illustration libraries (unDraw, Open Doodles, Humaaans, etc.), icon sets (Heroicons, Lucide, Phosphor, etc.), font libraries, color palettes & gradients, animation libraries (Framer Motion, Lottie, GSAP examples), inspiration galleries, 3D / Blender resources, design tools & prototyping.

### `awesome-design-systems.md`
**Source:** [klaufel/awesome-design-systems](https://github.com/klaufel/awesome-design-systems)
**Use for:** Production design system references — Apple HIG, Material 3, IBM Carbon, Atlassian, Adobe Spectrum, Shopify Polaris, GitHub Primer, Airbnb, Uber Base, Mailchimp, Microsoft Fluent, etc. Each linked system is a premium visual reference (component galleries, token systems, motion specs, color palettes, typography scales).

## When to reach for which

| Need | Use |
|---|---|
| A specific icon set, font, illustration style, color palette | `design-resources-for-developers.md` |
| A pattern, component spec, motion guideline, design language | `awesome-design-systems.md` |
| Premium presentation aesthetics (color, type, spacing) | `awesome-design-systems.md` → pick a system, lift the tokens |
| Quick visual assets for a slide or web layout | `design-resources-for-developers.md` → search by asset type |

## Refresh

Re-fetch with:

```bash
curl -sL -o references/design-resources-for-developers.md \
  https://raw.githubusercontent.com/bradtraversy/design-resources-for-developers/master/readme.md

curl -sL -o references/awesome-design-systems.md \
  https://raw.githubusercontent.com/klaufel/awesome-design-systems/main/README.md
```

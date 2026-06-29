---
name: Sovereign Intelligence
colors:
  surface: '#0e131f'
  surface-dim: '#0e131f'
  surface-bright: '#343946'
  surface-container-lowest: '#090e1a'
  surface-container-low: '#161b28'
  surface-container: '#1b1f2c'
  surface-container-high: '#252a37'
  surface-container-highest: '#303542'
  on-surface: '#dee2f4'
  on-surface-variant: '#d0c5af'
  inverse-surface: '#dee2f4'
  inverse-on-surface: '#2b303d'
  outline: '#99907c'
  outline-variant: '#4d4635'
  surface-tint: '#e9c349'
  primary: '#f2ca50'
  on-primary: '#3c2f00'
  primary-container: '#d4af37'
  on-primary-container: '#554300'
  inverse-primary: '#735c00'
  secondary: '#f1bc8c'
  on-secondary: '#492905'
  secondary-container: '#66411b'
  on-secondary-container: '#e2ae7f'
  tertiary: '#c9cedf'
  on-tertiary: '#2a303d'
  tertiary-container: '#adb3c3'
  on-tertiary-container: '#3f4553'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffe088'
  primary-fixed-dim: '#e9c349'
  on-primary-fixed: '#241a00'
  on-primary-fixed-variant: '#574500'
  secondary-fixed: '#ffdcbf'
  secondary-fixed-dim: '#f1bc8c'
  on-secondary-fixed: '#2d1600'
  on-secondary-fixed-variant: '#633f19'
  tertiary-fixed: '#dde2f3'
  tertiary-fixed-dim: '#c1c6d7'
  on-tertiary-fixed: '#161c27'
  on-tertiary-fixed-variant: '#414754'
  background: '#0e131f'
  on-background: '#dee2f4'
  surface-variant: '#303542'
typography:
  display-lg:
    fontFamily: Playfair Display
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Playfair Display
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-lg-mobile:
    fontFamily: Playfair Display
    fontSize: 28px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Playfair Display
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.5'
  label-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 14px
    fontWeight: '600'
    lineHeight: '1.4'
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Plus Jakarta Sans
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.4'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 8px
  container-max: 1440px
  gutter: 24px
  margin-desktop: 64px
  margin-tablet: 32px
  margin-mobile: 16px
---

## Brand & Style
The brand personality is authoritative, prestigious, and intellectually rigorous. As a platform for legal contract risk intelligence, the design system must evoke a sense of absolute security and sovereign control. The visual language bridges the gap between traditional legal craftsmanship and cutting-edge machine learning.

The design style is **Modern Corporate with Glassmorphic accents**. It utilizes a "High-End Editorial" approach: deep obsidian depths contrasted against burnished metallic accents. The interface should feel like a high-end physical portfolio—substantial, private, and precise. Interactions are governed by smooth, intentional motion to reinforce a feeling of premium quality.

## Colors
The palette is centered on "Gold and Obsidian." 

- **Obsidian Navy:** The primary background for the dark mode, providing a deep, calm environment for focused legal analysis.
- **Burnished Gold & Bronze:** Reserved for primary actions, critical risk indicators, and brand moments. Use the gold gradient sparingly to maintain its prestige.
- **Parchment:** Used for document viewing areas and light-mode surfaces, providing the tactile feel of high-quality legal vellum.
- **Risk Semantic Colors:** 
    - Critical Risk: Deep Crimson (#991B1B)
    - Warning: Ochre (#B45309)
    - Low Risk: Sage (#065F46)

## Typography
The typographic hierarchy relies on the contrast between the traditional, Italian-influenced **Playfair Display** for headings and the modern, geometric **Plus Jakarta Sans** for UI elements and body text.

Headings should use tighter letter-spacing and generous line-height to maintain an editorial feel. Labels use uppercase styling with increased tracking to evoke the look of institutional archives. Document text should always be rendered in the body-lg or body-md sizes to ensure maximum legibility during long-form reading sessions.

## Layout & Spacing
The layout follows a **Fixed Grid** system for dashboard environments, centering content within a 1440px container to maintain an air of exclusivity and focus. 

- **Rhythm:** Use an 8px base grid.
- **Margins:** Generous outer margins (64px on desktop) are essential to evoke "white space" luxury.
- **Reflow:** On mobile, complex data tables transition to card-based summaries, and margins compress to 16px. Document viewers should maintain a "centered column" layout to mimic a page-turning experience.

## Elevation & Depth
Depth is achieved through **Glassmorphism** and **Tonal Layers** rather than heavy shadows.

- **Surface 0:** Obsidian Navy background.
- **Surface 1 (Cards/Panels):** 40% opacity Obsidian with a 1px Gold-tinted border (10% opacity) and a 20px backdrop blur.
- **Surface 2 (Modals/Popovers):** 60% opacity Obsidian with a sharper 40px backdrop blur and a subtle 2px outer glow in burnished bronze.
- **Transitions:** All state changes (hover, active, open) must use a `cubic-bezier(0.4, 0, 0.2, 1)` timing function for a smooth, heavy feel.

## Shapes
This design system uses **Soft (0.25rem)** roundedness to maintain a sharp, professional, and institutional edge. 

- UI Buttons and Input fields: 4px (0.25rem).
- Document Containers and Large Cards: 8px (0.5rem).
- Checkboxes: 2px (minimal rounding) to preserve a "legal form" aesthetic.
- Risk Progress Rings: Perfect circles, utilizing varying stroke weights to indicate severity.

## Components
- **Buttons:** Primary buttons use the Burnished Gold gradient with white or dark-navy text. Secondary buttons are "Ghost" style with a 1px gold border.
- **Risk Progress Rings:** Circular SVGs. The "track" is a low-opacity obsidian, while the "progress" is a solid metallic gold or semantic risk color.
- **Data Tables:** Highly structured. Use 1px horizontal dividers in low-opacity bronze. Header rows use `label-md` typography.
- **Document Upload Zones:** Large, dashed-border areas using a 2px bronze stroke. Background uses a subtle parchment-grain texture in light mode or a dark glass effect in dark mode.
- **Legal Clause Checklists:** Custom checkbox design that replaces the standard "tick" with a sharp vector "check" in gold. Highlighted clauses use a subtle gold left-border accent.
- **Iconography:** Use sharp, 1.5px stroke-weight vector icons. No rounded caps; use square or miter joins for a more technical, "engraved" appearance.
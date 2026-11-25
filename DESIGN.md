---
name: Simone Drago
description: The academic website of a Ph.D. researcher in reinforcement learning from human feedback, set as a quiet record.
colors:
  deep-teal: "#006967"
  deep-teal-night: "#77d4cc"
  teal-tint: "#d5f2f0"
  teal-tint-night: "#093b3b"
  paper-white: "#fbfdfd"
  mint-wash: "#e6f5f5"
  card-white: "#ffffff"
  ink: "#101d21"
  muted-slate: "#4f5e62"
  hairline: "#d4dfdf"
  petrol-night: "#09171c"
  petrol-band: "#0d1f24"
  petrol-card: "#12262c"
  ink-night: "#e4edef"
  muted-night: "#a3b9bd"
  hairline-night: "#293e45"
typography:
  display:
    fontFamily: "Newsreader, Newsreader Fallback, Iowan Old Style, Palatino Linotype, Palatino, Georgia, serif"
    fontSize: "clamp(2.6rem, 2rem + 3.6vw, 4.1rem)"
    fontWeight: 400
    lineHeight: 1
    letterSpacing: "-0.02em"
    fontVariation: "\"opsz\" 72"
  lead:
    fontFamily: "Newsreader, Newsreader Fallback, Iowan Old Style, Palatino Linotype, Palatino, Georgia, serif"
    fontSize: "clamp(1.45rem, 1.15rem + 1vw, 1.9rem)"
    fontWeight: 400
    lineHeight: 1.25
    letterSpacing: "-0.012em"
    fontVariation: "\"opsz\" 36"
  headline:
    fontFamily: "Newsreader, Newsreader Fallback, Iowan Old Style, Palatino Linotype, Palatino, Georgia, serif"
    fontSize: "2.05rem"
    fontWeight: 400
    lineHeight: 1.1
    letterSpacing: "-0.01em"
    fontVariation: "\"opsz\" 48"
  subtitle:
    fontFamily: "Newsreader, Newsreader Fallback, Iowan Old Style, Palatino Linotype, Palatino, Georgia, serif"
    fontSize: "1.3rem"
    fontWeight: 400
    lineHeight: 1.35
    fontVariation: "\"opsz\" 24"
  title:
    fontFamily: "Newsreader, Newsreader Fallback, Iowan Old Style, Palatino Linotype, Palatino, Georgia, serif"
    fontSize: "1.2rem"
    fontWeight: 500
    lineHeight: 1.3
    letterSpacing: "-0.005em"
    fontVariation: "\"opsz\" 20"
  body:
    fontFamily: "Hanken Grotesk, Hanken Grotesk Fallback, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "1.0625rem"
    fontWeight: 400
    lineHeight: 1.6
  small:
    fontFamily: "Hanken Grotesk, Hanken Grotesk Fallback, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "0.9375rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "Hanken Grotesk, Hanken Grotesk Fallback, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
    fontSize: "0.85rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "0.02em"
    fontFeature: "\"tnum\""
rounded:
  focus: "2px"
  label: "4px"
  card: "6px"
  full: "999px"
spacing:
  gutter: "8rem"
  gap: "2rem"
  measure: "45rem"
  page: "55rem"
  section: "4.25rem"
  section-phone: "3.25rem"
  bar: "3.75rem"
components:
  button-cv:
    textColor: "{colors.deep-teal}"
    typography: "{typography.small}"
    rounded: "{rounded.full}"
    height: "2.25rem"
    padding: "0 0.95rem 0 0.8rem"
  button-cv-hover:
    backgroundColor: "{colors.teal-tint}"
    textColor: "{colors.deep-teal}"
  button-icon:
    textColor: "{colors.ink}"
    rounded: "{rounded.full}"
    size: "2.25rem"
  button-icon-hover:
    backgroundColor: "{colors.teal-tint}"
  link:
    textColor: "{colors.deep-teal}"
  nav-link:
    textColor: "{colors.muted-slate}"
  nav-link-current:
    textColor: "{colors.ink}"
  card:
    backgroundColor: "{colors.card-white}"
    rounded: "{rounded.card}"
    padding: "1.15rem 1.3rem"
  section-band:
    backgroundColor: "{colors.mint-wash}"
  publication-label:
    textColor: "{colors.muted-slate}"
    typography: "{typography.label}"
    rounded: "{rounded.label}"
---

# Design System: Simone Drago

## Overview

**Creative North Star: "The Quiet Record"**

The site is a researcher's record, set quietly. The research question, the papers and their venues carry the page; the design stays out of the way and lets the evidence be read. It answers to two readers at once: a hiring committee member skimming for a few minutes, and a reader who checks every claim. Both are served by the same thing: a clear spine, honest labels, and nothing that competes with the content.

Restraint is the method, not the absence of one. Colour is rare and always means something: one accent, Deep Teal, with a short fixed list of jobs. Type does the ranking: the Newsreader serif for your name, the research question, section and paper titles; Hanken Grotesk for everything you read through. There is one authored moment of motion, the research figure drawing its Pareto front, plus the news ticker. Components are precise and quiet: hairline outlines, underlined links, no shadows, nothing that asks for attention it hasn't earned.

Confirmed rejections: the indigo, glow-lit "AI product" look the site started with; decorative colour on labels, icons and dividers; cards used as page structure.

**Key Characteristics:**
- One accent, Deep Teal, kept to six jobs
- A near-white page with Mint Wash bands; a deep Petrol Night in dark mode, composed rather than inverted
- Serif for names, titles and the question; sans for reading and labels
- A date and label column, the spine, running down every list
- Flat: tonal bands and 1px hairlines, never shadows
- Every link underlined; every text colour at 4.5:1 or more in both themes

## Colors

A restrained palette: neutral, faintly cool surfaces and one deep teal accent that appears only where it means something.

### Primary
- **Deep Teal** (#006967; Deep Teal (night) #77d4cc in dark): links, the CV button, the underline under your name in author lists, award badges, the current section's underline in the top bar, focus rings and text selection. 6.4:1 on Paper White, 5.8:1 on Mint Wash; 10.5:1 on Petrol Night.
- **Teal Tint** (#d5f2f0; #093b3b in dark): the hover fill of round buttons, text selection, and the background of a targeted paper label. Never a large area.

### Neutral
- **Paper White** (#fbfdfd): the light page. Near-white, so the page reads clean rather than grey.
- **Mint Wash** (#e6f5f5): the tinted band behind Research. The only place the teal owns a region.
- **Card White** (#ffffff): the Quick facts card and the research cards (when the figure is off).
- **Ink** (#101d21): body text and headings. 16.9:1 on Paper White.
- **Muted Slate** (#4f5e62): secondary text, dates, paper labels, year rules, icons. 6.6:1 on Paper White, 6.0:1 on Mint Wash.
- **Hairline** (#d4dfdf): card borders, dividers, rules.
- **Petrol Night** (#09171c), **Petrol Band** (#0d1f24), **Petrol Card** (#12262c): the dark page, band and card, from the same blue-teal family as the accent. Dark text is **Ink (night)** (#e4edef), secondary **Muted Slate (night)** (#a3b9bd, 8.9:1), lines **Hairline (night)** (#293e45).
- **Control outline** (`--control`, derived: Muted Slate mixed 70% into the page): the outline of round buttons, 3.3:1 in light and 4.9:1 in dark.

All tokens live at the top of `static/style.css`: the light block and two dark blocks that must match. The two `theme-color` tags in `templates/base.html.j2` repeat the page colours for phone browser bars.

### Named Rules
**The Rare Teal Rule.** Deep Teal does six jobs only: links, the CV button, your name in author lists, award badges, the current section in the top bar, focus and selection. Labels, years, icons, dots and dividers stay Ink or Muted Slate.

**The Underline Rule.** Every link is underlined. Colour never carries meaning on its own.

## Typography

**Display Font:** Newsreader (with Iowan Old Style, Palatino, Georgia)
**Body Font:** Hanken Grotesk (with system-ui, Segoe UI, Roboto)

**Character:** a scholarly serif with optical sizes for everything that names something, against a plain, warm grotesque for everything you read through. Both are self-hosted; the site makes no font requests to anyone. While they load, two stand-ins hold the layout still: *Newsreader Fallback* (Georgia scaled to 91.5%, matched at title size) and *Hanken Grotesk Fallback* (Arial, which already matches in width, with Hanken's line metrics).

### Hierarchy
- **Display** (400, clamp(2.6rem, 2rem + 3.6vw, 4.1rem), line-height 1, opsz 72): your name in the header, nowhere else.
- **Subtitle** (italic 400, 1.3rem, 1.35, Muted Slate): the position line under your name. The same size, roman 500 in Ink, sets your name in the top bar.
- **Lead** (400, clamp(1.45rem, 1.15rem + 1vw, 1.9rem), 1.25, Ink, balanced): the research question. The second thing a visitor reads.
- **Headline** (400, 2.05rem, 1.1, opsz 48): section titles.
- **Title** (500, 1.2rem, 1.3, opsz 20, -0.005em, balanced): every title of a work: papers, theses and research topics; also the Quick facts heading. On phones (760px and below) it steps to 1.125rem, all titles together.
- **Body** (400, 1.0625rem, 1.6): the bio, details and all running text, at most 38em wide. Paragraphs use `text-wrap: pretty`, so no word sits alone on a last line.
- **Small** (400, 0.9375rem, 1.6): secondary text: authors, the venue line, details, abstracts, research-topic text, the link row, navigation and the CV button. Links and controls in it use 500.
- **Label** (0.85rem, tabular figures, Muted Slate): dates on the spine, the figure caption and the footer small print at 400; paper labels (C5), year rules and Quick facts terms at 600 with 0.02em tracking.

**Weights.** Hanken Grotesk uses three: 400 for reading, 500 for links and controls (colour and underline already mark them), 600 for item headings and labels. Item headings (a role, degree, course or group title) are Body size at 600. Newsreader uses 400 and 500.

### Named Rules
**The Spine Rule.** Dates and paper labels sit in the left column with tabular figures, right-aligned; content sits in the text column to its right.

**The One Scale Rule.** Every font size is one of the eight `--text-*` tokens at the top of `static/style.css` (display, headline, lead, subtitle, title, body, small, label). A new element takes an existing role; it never gets a size of its own.

## Layout

One two-column grid carries the whole page: an 8rem **spine** (dates, paper labels), a 2rem gap, and a 45rem text column, centred in a 55rem page with at least a 1.25rem edge (more when a phone's notch needs it). Section titles, the research block, publication groups and Teaching all align to the text column, so the eye travels one straight line from top to bottom.

The header follows the reading order a hiring committee needs: name, position, research question, then the bio with the 16rem Quick facts card beside it, then the links (Email, CV, Scholar, LinkedIn), then the latest-news ticker. The CV also sits in the sticky top bar, always one tap away.

Sections are separated by rhythm and tone rather than boxes: 4.25rem of padding (3.25rem on phones), the Research section on a Mint Wash band, the others on the page split by a hairline divider with a small centre dot. Lists are rows on the spine (Education, Experience, Teaching, Awards & service, supervision), never cards.

- **1100px:** the top-bar links fade at the right edge and scroll sideways.
- **1000px:** Quick facts move under the bio; the photo stops hanging into the left margin.
- **760px:** the spine folds away and dates sit above their entries; the nav wraps to its own row and keeps the current section's link in view; the research figure stacks above the topics.

## Elevation & Depth

Flat. There are no shadows for depth anywhere. Surfaces separate by tone (Mint Wash bands, Card White cards) and by 1px hairlines. The only blur is the translucent sticky top bar (86% page colour, 12px backdrop blur), so content scrolls visibly beneath it. The two ring-shaped `box-shadow`s in the stylesheet are cut-outs (a page-coloured ring around the divider dot and the timeline dots), not elevation.

### Named Rules
**The Flat Rule.** Surfaces are flat at rest and on hover. Depth comes from tone and hairlines; a hover changes the outline or a tint, never a shadow.

## Shapes

Soft but sparing. Cards have 6px corners; buttons are fully round (pill or circle); paper labels round to 4px on hover; focus rings to 2px. Circles carry meaning: your portrait (with a hairline edge), the divider and timeline dots, and the points in the research figure. Everything else is square-cornered type and rules.

## Components

Precise and quiet: hairline outlines, underlined links, no shadows.

### Buttons
- **Shape:** fully round (999px), 2.25rem tall.
- **CV (primary):** Deep Teal text and icon, an outline of Deep Teal mixed 70% into the page; the only accent on the first screen.
- **Icon buttons (theme switch, ticker controls):** Ink icon, `--control` outline (3:1 or more). Ticker controls are 1.75rem, growing to 2.25rem on touch screens.
- **Hover / Focus:** outline turns Deep Teal with a Teal Tint fill (0.2s); focus is a 2px Deep Teal ring, 3px offset.

### Links
- **Style:** Deep Teal, 1px underline at 45% strength, 0.2em offset; the underline turns solid on hover.
- **Touch:** small text links (paper links, Abstract, BibTeX, Latest news) get a finger-sized hit area on touch screens without moving the layout.

### Cards / Containers
- **Corner Style:** 6px.
- **Background:** Card White (Petrol Card in dark).
- **Shadow Strategy:** none; see Elevation & Depth.
- **Border:** 1px Hairline.
- **Internal Padding:** 1.1–1.3rem.
- Used for the Quick facts panel, and for the research topics only when the figure is turned off.

### Navigation
- **Style:** Hanken Grotesk 500 at Small (0.9375rem), Muted Slate; hover turns Ink.
- **Current section:** Ink with a 2px Deep Teal underline, set as the visitor scrolls.
- **Mobile:** a sideways-scrolling row under the name that slides to keep the current link visible. Its right edge fades only while more links lie that way, so a row that fits never looks cut off. The row keeps room inside for focus rings.

### Publication entry (signature)
The muted label (C5, J1, W1, P1) on the spine; the title in the serif, balanced; authors in Muted Slate with your name in Ink, bold, underlined 2px in Deep Teal; the venue in bold Ink; then underlined links and an Abstract toggle with a chevron. Equal contribution is an asterisk read aloud as "equal contribution". Each entry has a permalink and a BibTeX download.

### Research figure (signature)
A two-objective chart: Muted Slate axes and dominated points, the Pareto front as Deep Teal points on a staircase, and two front outcomes, A and B, circled in Ink and joined by a dashed arc with a question mark: neither dominates the other. The caption sits underneath in Muted Slate. Axes and grey points are drawn at 0.7 opacity, which keeps them at 3:1 or more against the band in both themes; they go to full strength when the visitor asks for more contrast, and the chart switches to system colours in high-contrast modes. The first time it scrolls into view, the staircase draws itself through the front (1.3s, exponential ease-out); the points, A, B and the question are there from the start, so a view that never scrolls still shows what the caption describes. Without JavaScript, with reduced motion, or when printed, the staircase is simply there. Turned on and captioned from `content/research.yml`.

### Latest-news ticker
One news item at a time beside its date on the spine, with previous / pause / next controls, a counter and a thin Muted Slate progress bar. It pauses on hover, keyboard focus, the Pause button, or a tap on an arrow on phones; screen readers hear each item whenever it isn't rotating by itself. Its "Latest news" label links to the full archive.

## Do's and Don'ts

### Do:
- **Do** keep Deep Teal to its six jobs (The Rare Teal Rule).
- **Do** underline every link (The Underline Rule).
- **Do** keep every text colour at 4.5:1 or more against page, band and card, in both themes; check new colours with a contrast tool before shipping.
- **Do** put dates and labels on the spine, right-aligned, with tabular figures.
- **Do** add new lists as rows on the spine, like Education and Teaching.
- **Do** drive new features from fields in `content/` and document them in the README; updating the site never means editing templates.
- **Do** change colours in all three token blocks and the two `theme-color` tags together.
- **Do** respect reduced motion: anything that moves must stop under `prefers-reduced-motion`.

### Don't:
- **Don't** add glows, radial gradients or decorative backgrounds; the site deliberately left that look behind.
- **Don't** use the accent on labels, years, icons, dots, dividers or other decoration.
- **Don't** use shadows for depth.
- **Don't** add fonts, icon fonts, CDNs, analytics or any other third-party request.
- **Don't** use cards as page structure or for lists.
- **Don't** add motion beyond the research figure and the news ticker.
- **Don't** put the email address in plain text anywhere in the source.

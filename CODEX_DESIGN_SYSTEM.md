# PROMPTPULSE — UPDATED DESIGN SYSTEM
# Replace the entire Design Engine section in your Codex prompt with this

---

## UPDATED BRAND VISUAL IDENTITY

This completely replaces the previous light/minimal design.

### Color Palette

Background:         #000000 (pure black)
Primary gradient:   linear-gradient(135deg, #7C3AED, #2563EB, #EC4899)
Headline color:     White #FFFFFF (base) + gradient accent on key words
Body text:          #D1D5DB (light gray)
Card background:    rgba(255,255,255,0.05) with border rgba(255,255,255,0.1)
Accent glow:        #7C3AED with blur shadow
Button primary:     #5B21B6 to #2563EB gradient
Neon accent lines:  #06B6D4 (cyan) for decorative curves/lines
Number badges:      #5B21B6 filled circles

### Typography

Font family:        Inter (900 weight for headlines, 600 for subheadings, 400 for body)
Headline size:      96–120px, uppercase, tight line-height 0.95
Gradient words:     Apply purple→blue→pink gradient to 1–3 key words per headline
Body text:          32–36px, color #D1D5DB
Card labels:        28–32px bold white
Badge numbers:      32px bold white inside colored circle

### Visual Elements

Every slide MUST have:
- A cinematic AI-generated background image (dark, atmospheric, sci-fi or nature themed)
- Background image opacity: 20–35% so text stays readable
- Gradient overlay on top of background: linear-gradient(180deg, rgba(0,0,0,0.3), rgba(0,0,0,0.8))
- Slide counter top-right: "01 / 06" in gray
- Right arrow bottom-right: → in white
- Dot pagination bottom-center: ● ○ ○ ○ ○ ○ (filled dot = current slide)

Decorative elements allowed per slide:
- Glowing orbs (blurred circles in purple/blue at low opacity)
- Thin neon curved lines (like the wave line in slide 4)
- Handwritten-style annotation text (italic, small, in pink/purple)
- Feature icon badges (small rounded squares with emoji or SVG icon)

---

## SLIDE TEMPLATES — EXACT SPECIFICATIONS

### SLIDE 1 — HOOK / HERO

Layout:
- Full black background
- Cinematic background image (astronaut, futuristic city, landscape) at 25% opacity
- Top-right: "01 / 06"
- Large bold uppercase headline — 3–4 lines — white with 1–2 gradient words
- Below headline: 2–3 line subtext in gray (32px)
- Bottom-left: small italic handwritten annotation in purple/pink
- Bottom-right: → arrow
- Bottom-center: dot pagination

Example content rendering:
┌──────────────────────────────┐
│                        01/06 │
│                              │
│  [cinematic bg image faded]  │
│                              │
│  THIS AI                     │
│  TURNS YOUR                  │
│  IDEAS INTO                  │
│  [GRADIENT]STUNNING[/]       │
│  VIDEOS                      │
│                              │
│  Just a text prompt.         │
│  No camera. No editing.      │
│  Pure imagination.           │
│                              │
│  ↙ From thoughts             │
│    to visuals.               │
│    In minutes.               │
│                         →    │
│         ● ○ ○ ○ ○ ○          │
└──────────────────────────────┘

HTML template (hero_dark.html):
```html
<!DOCTYPE html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,400;0,600;0,700;0,900;1,400&display=swap" rel="stylesheet">
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body {
  width: 1080px; height: 1350px;
  background: #000000;
  font-family: 'Inter', sans-serif;
  position: relative;
  overflow: hidden;
}
.bg-image {
  position: absolute; inset: 0;
  background-image: url('{{background_image_url}}');
  background-size: cover;
  background-position: center;
  opacity: 0.28;
}
.bg-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(180deg, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.85) 100%);
}
.content {
  position: relative; z-index: 2;
  padding: 60px 70px;
  height: 100%;
  display: flex;
  flex-direction: column;
}
.slide-num {
  align-self: flex-end;
  font-size: 26px; color: #9CA3AF; font-weight: 500;
  letter-spacing: 2px;
}
.spacer { flex: 1; }
.headline {
  font-size: 108px; font-weight: 900;
  line-height: 0.95;
  text-transform: uppercase;
  color: #FFFFFF;
  margin-bottom: 36px;
}
.gradient-text {
  background: linear-gradient(135deg, #A855F7, #3B82F6, #EC4899);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.subtext {
  font-size: 34px; color: #D1D5DB;
  line-height: 1.4; margin-bottom: 48px;
}
.annotation {
  font-style: italic; font-size: 28px;
  color: #A855F7; margin-bottom: 60px;
  line-height: 1.5;
}
.bottom-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.dots span {
  display: inline-block;
  width: 12px; height: 12px;
  border-radius: 50%;
  background: #4B5563;
  margin: 0 4px;
}
.dots span.active { background: #7C3AED; width: 32px; border-radius: 6px; }
.arrow { font-size: 40px; color: #FFFFFF; }
</style>
</head>
<body>
<div class="bg-image"></div>
<div class="bg-overlay"></div>
<div class="content">
  <div class="slide-num">01 / 06</div>
  <div class="spacer"></div>
  <div class="headline">
    {{line1}}<br>
    {{line2}}<br>
    {{line3}}<br>
    <span class="gradient-text">{{gradient_word}}</span><br>
    {{line5}}
  </div>
  <div class="subtext">{{subtext}}</div>
  <div class="annotation">{{annotation}}</div>
  <div class="bottom-row">
    <div class="dots">
      <span class="active"></span>
      <span></span><span></span><span></span><span></span><span></span>
    </div>
    <div class="arrow">→</div>
  </div>
</div>
</body>
</html>
```

---

### SLIDE 2 — MEET THE TOOL

Layout:
- Black background with atmospheric bg image at 20% opacity
- Top: small eyebrow text "MEET" in gray uppercase spaced letters
- Center: Tool name in massive typography — white + gradient
- Below name: one-line description in gray
- Center visual: 3D rendered tool logo/icon image (large, glowing)
- Handwritten annotation beside the logo
- Bottom: 4 feature badges in a row (icon + label)
- Dot pagination + arrow

Feature badges style:
  Rounded rectangle, border: 1px solid rgba(255,255,255,0.15)
  Background: rgba(255,255,255,0.05)
  Icon on top, label below, 32px font

HTML template styles (tool_intro_dark.html):
```css
.eyebrow {
  font-size: 28px; letter-spacing: 8px;
  color: #9CA3AF; font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 16px;
}
.tool-name {
  font-size: 120px; font-weight: 900;
  line-height: 0.9;
}
.tool-name .brand { color: #FFFFFF; }
.tool-name .version {
  background: linear-gradient(135deg, #A855F7, #3B82F6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.tool-logo {
  width: 400px; height: 400px;
  margin: 40px auto;
  filter: drop-shadow(0 0 60px rgba(124,58,237,0.6));
}
.feature-badges {
  display: flex; gap: 20px;
  justify-content: space-around;
  margin-top: 40px;
}
.badge {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 20px;
  padding: 24px 20px;
  text-align: center;
  flex: 1;
}
.badge-icon { font-size: 40px; margin-bottom: 12px; }
.badge-label { font-size: 26px; color: #D1D5DB; font-weight: 600; }
```

---

### SLIDE 3 — WHAT CAN YOU CREATE / USE CASES

Layout:
- Dark background with subtle bg image
- Bold headline with gradient word
- Short subtext
- 4 use-case cards stacked vertically (full width)
  Each card: dark glass background, bold label left, thumbnail image right
- Handwritten annotation bottom-right
- Dot + arrow

Use-case card style:
```css
.use-case-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 20px;
  padding: 28px 32px;
  margin-bottom: 20px;
}
.card-label {
  font-size: 36px; font-weight: 700;
  color: #FFFFFF;
  display: flex; align-items: center; gap: 16px;
}
.play-btn {
  width: 160px; height: 90px;
  border-radius: 12px;
  overflow: hidden;
  position: relative;
}
.play-icon {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  background: rgba(0,0,0,0.4);
  font-size: 32px; color: white;
}
```

---

### SLIDE 4 — HOW IT WORKS (Steps)

Layout:
- Black bg + faint bg image
- Large bold headline: "HOW IT" white + "WORKS" gradient
- Subtext: one line description
- 4 numbered steps — each step has:
  - Purple circle badge with number (01, 02, 03, 04)
  - Small icon in rounded square (purple background)
  - Bold step title
  - Gray step description
- Bottom: italic handwritten annotation + neon wave line decoration
- Dot + arrow

Step row style:
```css
.step-row {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 36px;
}
.step-num {
  width: 70px; height: 70px;
  border-radius: 50%;
  background: #5B21B6;
  display: flex; align-items: center; justify-content: center;
  font-size: 28px; font-weight: 900; color: white;
  flex-shrink: 0;
}
.step-icon {
  width: 70px; height: 70px;
  border-radius: 16px;
  background: rgba(124,58,237,0.3);
  border: 1px solid rgba(124,58,237,0.5);
  display: flex; align-items: center; justify-content: center;
  font-size: 32px;
  flex-shrink: 0;
}
.step-text-title {
  font-size: 34px; font-weight: 700; color: #FFFFFF;
}
.step-text-desc {
  font-size: 26px; color: #9CA3AF; margin-top: 4px;
}
.neon-wave {
  position: absolute;
  bottom: 140px; left: 0; right: 0;
  height: 3px;
  background: linear-gradient(90deg, transparent, #06B6D4, transparent);
  filter: blur(2px);
  box-shadow: 0 0 20px #06B6D4;
}
```

---

### SLIDE 5 — REAL EXAMPLES / PRACTICAL VALUE

Layout:
- Dark bg with bg image
- Bold headline: "REAL" white + "EXAMPLES" gradient
- Subtext
- 3 example cards stacked:
  Each card: left side = prompt text box, right side = result thumbnail
  "Text in. This out." handwritten annotation beside cards
- Quote at bottom in italic gray
- Dot + arrow

Example card style:
```css
.example-card {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  align-items: center;
}
.prompt-box {
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 16px;
  padding: 20px 24px;
  flex: 1;
}
.prompt-label {
  font-size: 22px; color: #7C3AED;
  font-weight: 700; margin-bottom: 8px;
  text-transform: uppercase; letter-spacing: 2px;
}
.prompt-text {
  font-size: 28px; color: #F3F4F6;
  font-style: italic; line-height: 1.3;
}
.result-thumb {
  width: 200px; height: 130px;
  border-radius: 14px;
  overflow: hidden;
  position: relative;
  flex-shrink: 0;
}
.bottom-quote {
  font-size: 28px; color: #9CA3AF;
  font-style: italic;
  text-align: center;
  margin-top: 24px;
  padding: 0 40px;
}
```

---

### SLIDE 6 — CTA / CLOSER

Layout:
- Black bg + cinematic background image at 25% opacity
- Bold 3-line headline — white + gradient
- Short subtext
- 4 benefit rows with gradient icon badges
- Large CTA button at bottom:
  Full-width rounded button
  Purple→blue gradient background
  Bookmark icon left + text center + arrow right
- Dot + arrow

Benefit row style:
```css
.benefit-row {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 28px;
}
.benefit-icon {
  width: 64px; height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #7C3AED, #2563EB);
  display: flex; align-items: center; justify-content: center;
  font-size: 28px;
  flex-shrink: 0;
}
.benefit-text {
  font-size: 34px; font-weight: 600; color: #FFFFFF;
}
.cta-button {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #5B21B6, #2563EB);
  border-radius: 100px;
  padding: 32px 48px;
  margin-top: 40px;
  width: 100%;
}
.cta-left { display: flex; align-items: center; gap: 20px; }
.cta-icon { font-size: 40px; color: white; }
.cta-main-text { font-size: 40px; font-weight: 900; color: white; }
.cta-sub-text { font-size: 24px; color: rgba(255,255,255,0.7); }
.cta-arrow {
  width: 64px; height: 64px;
  background: rgba(255,255,255,0.2);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 32px; color: white;
}
```

---

## BACKGROUND IMAGE SYSTEM

For each slide, the Design Agent must source or generate a cinematic background image.

Options in order of preference:

1. Use Gemini Imagen API to generate:
   Prompt examples:
   - "Cinematic dark sci-fi landscape, lone astronaut, purple nebula, photorealistic, 16:9"
   - "Futuristic city at night, neon lights, dark atmosphere, cinematic, ultra detailed"
   - "Deep space scene, glowing planets, dark background, cinematic photography"
   - "Dark forest with bioluminescent elements, moody, cinematic"
   - "Abstract dark technology background, circuit patterns, purple blue glow"

2. Use Unsplash API (free) with search terms:
   "dark cinematic space", "futuristic city night", "dark abstract technology"
   Filter for dark/moody images only.

3. Use a curated set of 20 pre-downloaded cinematic dark backgrounds.
   Rotate through them, never use the same one twice in a row.

Background image requirements:
- Must be dark (average brightness < 80/255)
- Must be high resolution (min 1080px wide)
- Must be atmospheric/cinematic
- Applied at 20-30% opacity so text remains readable

---

## REMOVED FROM ORIGINAL DESIGN SPEC

Remove these from the original Codex prompt design section:
- Light background #F8FAFC (REPLACED with #000000)
- Minimalist/clean/SaaS aesthetic (REPLACED with cinematic/dark/premium)
- "Avoid neon glows" (REVERSED — neon glows are now required)
- "Avoid excessive gradients" (REVERSED — gradients are the primary design element)
- "Avoid glassmorphism" (REVERSED — glass cards are now used)
- Light typography on dark (REPLACED with white/gradient on black)

---

## DESIGN QUALITY CHECKLIST (Updated)

Before approving any slide visually:
- [ ] Background is dark (near black)
- [ ] At least one gradient text element per slide
- [ ] Cinematic background image present at correct opacity
- [ ] Neon glow effect on at least one element
- [ ] Slide counter visible top-right
- [ ] Dot pagination bottom-center
- [ ] Arrow bottom-right
- [ ] Text is fully readable (contrast ratio > 4.5:1)
- [ ] Cards use glass morphism style (rgba background + subtle border)
- [ ] Handwritten annotation present on at least 3 slides
- [ ] CTA slide has the full-width gradient button
- [ ] No element extends beyond slide boundaries
- [ ] All 6 slides feel like one cohesive carousel when viewed together

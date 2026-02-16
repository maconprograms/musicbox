# MusicBox Chord Sheet: Creative & Design Brief

> **Purpose:** Define the visual design, layout principles, and information architecture for printable guitar chord sheets.

---

## 1. Product Vision

**One sentence:** A clean, information-dense single-page PDF that teaches you a song at a glance.

**Target user:** Intermediate guitarist who wants to learn songs by ear but needs a visual reference for chord voicings, structure, and timing.

**Use context:** Printed on standard letter/A4 paper, placed on a music stand or table while practicing with guitar in hand.

---

## 2. Design Principles

### 2.1 Information Hierarchy (Top to Bottom)

The eye should flow naturally through the page:

```
1. IDENTITY       → What song is this?
2. CONTEXT        → How do I play it? (Key, Capo, Tempo)
3. VOCABULARY     → What chords do I need to know?
4. ROADMAP        → What's the song structure?
5. TECHNIQUE      → How do I strum/pick?
6. CONTENT        → The actual song (chords + lyrics + tabs)
7. REFERENCE      → Links to audio
```

### 2.2 Core Design Values

| Value | Meaning |
|-------|---------|
| **Scannable** | Find any section instantly. Clear visual anchors. |
| **Dense** | Maximum info in minimum space. No wasted whitespace. |
| **Printable** | Works in B&W. No bleeding. Standard margins. |
| **Learnable** | Teaches technique, not just chords over words. |
| **Beautiful** | Clean typography. Professional appearance. |

---

## 3. Page Layout Specification

### 3.1 Page Setup

- **Size:** A4 (210 × 297 mm) or Letter (8.5 × 11 in)
- **Orientation:** Portrait
- **Margins:** 12mm all sides
- **Content width:** ~186mm

### 3.2 Layout Zones

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                    [HEADER ZONE - 40mm]                      │
│   Title (large, bold, centered)                              │
│   Attribution (italic, smaller)                              │
│   Meta bar: Key | Capo | Tempo | Difficulty                  │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                  [CHORD ZONE - 30mm]                         │
│   ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐                             │
│   │ G │ │ C │ │ D │ │Am │ │ A │  (SVG chord diagrams)       │
│   └───┘ └───┘ └───┘ └───┘ └───┘                             │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                 [STRUCTURE ZONE - 8mm]                       │
│   Intro → V1 → V2 → C → V3 → V4 → C → Bridge → C → Outro    │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                 [PATTERN ZONE - 20mm] (optional)             │
│   Picking Pattern:                                           │
│   e|---0-------0---|                                         │
│   B|-----0-------0-|  (compact tab notation)                 │
│   ...                                                        │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                 [CONTENT ZONE - remaining]                   │
│                                                              │
│   INTRO                                                      │
│   |: G | G | C | C | C | C | G :|                           │
│                                                              │
│   VERSE 1                                                    │
│        G                              C                      │
│   If my words did glow, with the gold of sunshine           │
│                                       G                      │
│   And my tunes were played on the harp unstrung,            │
│   ...                                                        │
│                                                              │
│   CHORUS                                                     │
│        Am            D                                       │
│   Ripple in still water,                                    │
│   ...                                                        │
│                                                              │
├──────────────────────────────────────────────────────────────┤
│                                                       [QR]   │
│   Notes: Playing tips here...                         ▓▓▓   │
│                                                       ▓▓▓   │
└──────────────────────────────────────────────────────────────┘
```

---

## 4. Typography Specification

### 4.1 Font Stack

| Element | Font | Weight | Size | Color |
|---------|------|--------|------|-------|
| Title | Helvetica/Arial | Bold | 22pt | #1E1E1E |
| Attribution | Helvetica/Arial | Italic | 12pt | #505050 |
| Meta info | Helvetica/Arial | Regular | 9pt | #646464 |
| Section headers | Helvetica/Arial | Bold | 11pt | #3C3C3C |
| Chords | Courier/Mono | Bold | 10pt | #005AA0 |
| Lyrics | Courier/Mono | Regular | 10pt | #141414 |
| Tab notation | Courier/Mono | Regular | 8pt | #323232 |
| Bar progression | Courier/Mono | Bold | 10pt | #282828 |
| Structure roadmap | Helvetica/Arial | Regular | 8pt | #787878 |
| Notes | Helvetica/Arial | Italic | 8pt | #646464 |

### 4.2 Why Monospace for Chords/Lyrics?

Chord alignment depends on character-width consistency. With proportional fonts, a `G` and an `Am` have different widths, breaking the visual alignment above lyrics. Monospace ensures:

```
     G                C        D       G
If my words did glow with the gold of sunshine
     ↑                ↑        ↑       ↑
     Perfect alignment because each character = same width
```

---

## 5. Chord Diagram Specification

### 5.1 Diagram Anatomy

```
          G          ← Chord name (bold, centered)
        o   o o      ← String markers (o=open, x=muted)
       ┌─┬─┬─┬─┬─┐
       │ │ │ │ │ │   ← Nut (thick bar for open chords)
       ├─┼─┼─┼─┼─┤
       │②│ │ │ │ │   ← Fret 1 (circled numbers = fingers)
       ├─┼─┼─┼─┼─┤
       │ │①│ │ │ │   ← Fret 2
       ├─┼─┼─┼─┼─┤
       │ │ │ │ │③│   ← Fret 3
       ├─┼─┼─┼─┼─┤
       │ │ │ │ │ │   ← Fret 4
       └─┴─┴─┴─┴─┘
        E A D G B e  ← String labels (optional)
```

### 5.2 Diagram Dimensions

- **Width:** 60px (18mm when rendered)
- **Height:** 80px (24mm when rendered)
- **Frets shown:** 5 (enough for most open chords)
- **Dot radius:** 4px
- **Finger numbers:** 6pt white text inside dots

### 5.3 Visual Elements

| Element | Style |
|---------|-------|
| Nut | 4px black bar (only for base_fret=1) |
| Fret position | "3fr" text for barre chords |
| Fret lines | 1px gray horizontal lines |
| String lines | 1px gray vertical lines |
| Finger dots | Black filled circles |
| Finger numbers | White text centered in dots |
| Open string | Empty circle above nut |
| Muted string | X mark above nut |
| Barre | Rounded rectangle across strings |

---

## 6. Content Formatting Rules

### 6.1 Section Headers

- **Style:** Bold, slightly larger, gray
- **Format:** "VERSE 1" not "Verse 1" (all caps for scannability)
- **Repeat indicator:** "CHORUS (x2)" if section repeats

### 6.2 Bar Progressions

Used for instrumental sections (intros, outros, solos):

```
|: G | G | C | C | C | C | G :|
```

- Repeat signs: `|:` and `:|`
- One chord per bar, separated by `|`
- Bold monospace font
- Same size as chord text

### 6.3 Chord-Over-Lyrics Alignment

```
ChordPro input:  [G]If my [C]words did [D]glow

Rendered output:
   G       C          D
   If my   words did  glow
```

Rules:
1. Chord appears above the syllable it changes on
2. Minimum 1 space between chord and next chord
3. If chord is longer than syllable, pad the syllable

### 6.4 Tablature

Standard 6-line ASCII format:

```
e|---0-------0-------0-------0---|
B|-----0-------1-------0-------0-|
G|-------0-------0-------0-------|
D|---------0-----------------0---|
A|-------------------------------|
E|-3-----------------------------|
```

- Monospace font (8pt)
- String labels on left
- Bar lines at logical divisions
- Compact vertical spacing (3.5pt line height)

---

## 7. Color Palette

Designed for B&W printing with good contrast:

| Use | Hex | RGB | Purpose |
|-----|-----|-----|---------|
| Title | #1E1E1E | (30,30,30) | Near-black for hierarchy |
| Chords | #005AA0 | (0,90,160) | Blue accent (prints as dark gray) |
| Lyrics | #141414 | (20,20,20) | True black for readability |
| Section headers | #3C3C3C | (60,60,60) | Medium gray |
| Meta/structure | #646464 | (100,100,100) | Light gray, secondary |
| Tab notation | #323232 | (50,50,50) | Slightly lighter than lyrics |

**Print test:** All colors should remain legible when printed on a B&W laser printer.

---

## 8. Information Requirements

### 8.1 Required Fields

| Field | Description | Example |
|-------|-------------|---------|
| title | Song title | "Ripple" |
| artist | Performing artist | "Grateful Dead" |
| key | Musical key | "G", "Am" |
| sections | Song content | Array of verse/chorus/etc |
| chords | Chord definitions | Dict of ChordDefinition |

### 8.2 Optional (Highly Recommended)

| Field | Description | Why Include |
|-------|-------------|-------------|
| writers | Songwriters | Attribution |
| capo | Capo fret | Essential for playing along |
| tempo | BPM | Practice timing |
| difficulty | Skill level | User expectation |
| structure | Section order | Quick song overview |
| patterns | Strum/pick patterns | Teaches technique |
| audio_url | Link to recording | QR code reference |
| notes | Playing tips | Expert advice |

### 8.3 Section Types

| Type | Use Case |
|------|----------|
| Intro | Opening instrumental |
| Verse | Lyrical verse sections |
| Chorus | Repeated hook |
| Bridge | Contrasting middle section |
| Solo | Instrumental break |
| Outro | Ending section |
| Pre-Chorus | Build-up to chorus |
| Interlude | Short instrumental between sections |

---

## 9. Edge Cases & Rules

### 9.1 Long Song Handling

If content exceeds one page:
1. Reduce font sizes by 1pt
2. Compress vertical spacing
3. If still too long, split into 2-page PDF
4. Never truncate content

### 9.2 Many Chords

If >8 unique chords:
1. Wrap chord diagram strip to second row
2. Or reduce diagram size to 50px width
3. Prioritize most-used chords in first row

### 9.3 No Lyrics (Instrumental)

For instrumental pieces:
1. Show tab prominently
2. Use bar progressions for structure
3. Include timing/count markers if helpful

### 9.4 Complex Chords

For jazz/complex voicings:
1. Show base_fret indicator ("5fr")
2. Always include finger numbers
3. Consider showing alternative voicings

---

## 10. Quality Checklist

Before generating a chord sheet, verify:

- [ ] Title and artist are correct
- [ ] Key matches the chords used
- [ ] All chord diagrams are present and correct
- [ ] Structure roadmap matches sections
- [ ] Chords align with correct syllables
- [ ] Tab notation is accurate (if included)
- [ ] QR code links to valid audio
- [ ] Fits on single page (or intentionally multi-page)
- [ ] Prints cleanly in B&W

---

## 11. Future Enhancements

### Phase 2 Ideas

- **Transpose button:** Generate variants in different keys
- **Capo calculator:** Auto-suggest easiest voicings
- **Difficulty auto-detect:** Based on chord complexity
- **Audio sync:** QR links to specific timestamps
- **Multiple voicings:** Show alternate fingerings
- **Chord dictionary:** Inline "how to play" popups

### Phase 3 Ideas

- **Full notation:** MusicXML for complex arrangements
- **Rhythm notation:** Standard notation above tab
- **Setlist mode:** Multi-song PDF generation
- **Practice tracker:** Integration with learning apps

---

## 12. Reference Examples

### Good Chord Sheet Examples

1. **Ultimate Guitar Pro** - Dense, scannable, chord diagrams
2. **Hal Leonard sheet music** - Professional typography
3. **Songsterr** - Clean tab rendering

### Design Inspiration

- Swiss typography (clean grids, hierarchy)
- Technical documentation (information density)
- Recipe cards (one-page, action-oriented)

---

*Document version: 1.0*  
*Last updated: January 2026*

# MusicBox: Project Planning Document

> **Last Updated:** January 2026  
> **Status:** Foundation Complete, PDF Generation Working

---

## 1. Project Vision

### What We're Building
A tool that generates **beautiful, single-page printable guitar chord sheets** from song data. The output is a PDF designed to be placed on a music stand while learning a song.

### The Problem We're Solving
- Web tabs are messy (ads, inconsistent formatting, wrong keys)
- Most chord sheets lack teaching elements (no fingering diagrams, no picking patterns)
- No single source gives you everything: chords, lyrics, tab, structure, and technique

### The Solution
A **"source of truth" data model** (TabCore) that stores everything needed to learn a song, paired with a **PDF renderer** that outputs a clean, information-dense chord sheet.

---

## 2. Current State

### What's Built

| Component | Status | Description |
|-----------|--------|-------------|
| `core/models.py` | ✅ Complete | Pydantic models: TabCore, ChordDefinition, SongSection, TabLine, PickingPattern |
| `core/diagrams.py` | ✅ Complete | SVG chord diagram generator with finger positions |
| `core/renderer.py` | ✅ Complete | PDF generator with embedded chord diagrams, tab, structure |
| `library/data/ripple.json` | ✅ Complete | Sample song data for testing |
| `DESIGN_BRIEF.md` | ✅ Complete | Visual design specification |
| `requirements.txt` | ✅ Complete | All dependencies listed |

### What's Not Built Yet

| Component | Status | Description |
|-----------|--------|-------------|
| `core/scraper.py` | 🔲 Stub | Web scraper to fetch tabs from Ultimate Guitar, etc. |
| `core/parser.py` | 🔲 Stub | Convert raw tab text to ChordPro/TabCore format |
| `core/agent.py` | 🔲 Stub | LLM agent to "gussy up" messy tabs |
| `core/music_theory.py` | 🔲 Stub | Transpose chords, suggest capo positions |
| `main.py` | 🔲 Stub | FastHTML web interface |

---

## 3. Data Model Overview

### TabCore (The Source of Truth)

```
TabCore
├── Metadata
│   ├── title, artist, writers
│   ├── key, capo, tempo, time_signature
│   ├── tuning, difficulty
│   └── source_url, audio_url
├── Structure
│   ├── structure: ["intro", "verse1", "chorus1", ...]
│   └── sections: [SongSection, ...]
├── Chord Library
│   └── chords: {name: ChordDefinition, ...}
├── Playing Guides
│   ├── patterns: [PickingPattern, ...]
│   └── notes: "Free-form tips"
```

### ChordDefinition

```
ChordDefinition
├── name: "G"
├── frets: [3, 2, 0, 0, 0, 3]    # E A D G B e
├── fingers: [2, 1, 0, 0, 0, 3]  # Which finger on each string
├── barre: null or fret number
└── base_fret: 1                  # For moveable shapes
```

### SongSection

```
SongSection
├── type: "Verse" | "Chorus" | "Bridge" | "Intro" | "Outro" | "Solo"
├── label: "Verse 1"              # Display label
├── content: "[G]Lyrics with [C]chords inline"
├── tab: [TabLine, ...]           # Optional tablature
├── bar_progression: "|G|G|C|C|"  # For instrumentals
├── pattern_ref: "Verse Picking"  # Reference to pattern
└── repeat: 2                     # Number of repeats
```

---

## 4. PDF Layout Specification

```
┌─────────────────────────────────────────────────────────────┐
│                         HEADER                               │
│  Title (large, bold, centered)                               │
│  "Words & Music by..." (italic)                              │
│  Key: G | Tempo: 78 BPM | ** Intermediate                    │
├─────────────────────────────────────────────────────────────┤
│                      CHORD DIAGRAMS                          │
│  [G] [C] [D] [Am] [A]  (SVG rendered as PNG)                │
├─────────────────────────────────────────────────────────────┤
│                    STRUCTURE ROADMAP                         │
│  Intro → V1 → V2 → C → V3 → V4 → C → Br → C → Outro         │
├─────────────────────────────────────────────────────────────┤
│                   PICKING PATTERN (optional)                 │
│  e|---0-------0---|                                          │
│  B|-----0-------0-|                                          │
│  ...                                                         │
├─────────────────────────────────────────────────────────────┤
│                        SECTIONS                              │
│                                                              │
│  INTRO                                                       │
│  |: G | G | C | C | C | C | G :|                            │
│                                                              │
│  VERSE 1                                                     │
│       G                              C                       │
│  If my words did glow, with the gold of sunshine            │
│  ...                                                         │
├─────────────────────────────────────────────────────────────┤
│  Notes: Playing tips...                              [QR]    │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Technical Architecture

### File Structure

```
musicbox/
├── core/                    # Core library
│   ├── __init__.py
│   ├── models.py           # Pydantic data models
│   ├── diagrams.py         # SVG chord diagram generator
│   ├── renderer.py         # PDF generation
│   ├── parser.py           # Raw text → TabCore
│   ├── scraper.py          # Web fetching
│   ├── agent.py            # LLM integration
│   ├── music_theory.py     # Transpose, capo calc
│   └── tools.py            # Agent tool definitions
├── library/                 # User's song library
│   ├── data/               # JSON song files
│   └── pdfs/               # Generated PDFs
├── assets/
│   ├── chord_diagrams/     # Generated SVGs
│   └── fonts/              # Custom fonts (if needed)
├── main.py                 # FastHTML web app
├── test_render.py          # Test script
├── requirements.txt
├── PLANNING.md             # This document
├── DESIGN_BRIEF.md         # Visual design spec
└── BUILD_PLAN.md           # Original build plan
```

### Dependencies

| Package | Purpose |
|---------|---------|
| fpdf2 | PDF generation |
| cairosvg | SVG → PNG conversion |
| qrcode + pillow | QR code generation |
| pydantic | Data validation |
| pychord | Music theory (transposition) |
| httpx | HTTP client for scraping |
| beautifulsoup4 | HTML parsing |
| google-genai | LLM for parsing/cleanup |
| python-fasthtml | Web UI framework |

---

## 6. Workflow: From URL to PDF

### Target User Flow

```
1. User provides: Song name + Artist (or URL)
         ↓
2. Scraper: Fetch raw tab from web
         ↓
3. Parser: Convert to ChordPro format
         ↓
4. Agent (LLM): Clean up, fix errors, add missing info
         ↓
5. Validator: Ensure TabCore is complete
         ↓
6. Renderer: Generate PDF
         ↓
7. Output: Beautiful chord sheet ready to print
```

### Alternative Flows

**Paste Mode:** User pastes raw tab text directly → Parser → Agent → PDF

**Library Mode:** User selects from saved songs → PDF

**Edit Mode:** User modifies TabCore JSON → Re-render PDF

---

## 7. Next Steps (Priority Order)

### Phase 1: Polish the PDF (Current)
- [ ] Review PDF output and gather feedback
- [ ] Adjust typography, spacing, layout based on feedback
- [ ] Add proper font embedding for consistent printing
- [ ] Test printing on actual paper

### Phase 2: Build the Parser
- [ ] Implement ChordPro parser (standard format)
- [ ] Implement "chords over lyrics" parser (Ultimate Guitar style)
- [ ] Handle common edge cases (inline chords, tab sections)

### Phase 3: Build the Scraper
- [ ] Ultimate Guitar scraper
- [ ] Songsterr scraper (optional)
- [ ] Generic HTML tab extraction

### Phase 4: LLM Integration
- [ ] Agent to clean up messy tabs
- [ ] Auto-detect song structure
- [ ] Suggest chord fingerings
- [ ] Generate picking patterns from audio (stretch goal)

### Phase 5: Web Interface
- [ ] FastHTML app with chat interface
- [ ] Paste mode for manual input
- [ ] Library view for saved songs
- [ ] Print/download buttons

---

## 8. Open Questions

### Design Decisions Needed

1. **Multi-page songs:** How do we handle songs that don't fit on one page?
   - Option A: Force fit (reduce font size)
   - Option B: Smart page breaks between sections
   - Option C: Always allow 2 pages max

2. **Chord diagram placement:** Top of page or inline near first use?
   - Current: Top of page (reference strip)
   - Alternative: Show diagram on first occurrence

3. **Tab vs. Chords:** When to show full tab vs. just chord names?
   - Current: Tab for patterns/intros, chords for verses
   - Alternative: User preference toggle

4. **Copyright:** How to handle copyrighted lyrics?
   - Current: User provides/pastes their own content
   - Alternative: Link to lyrics sites, don't store

### Technical Decisions Needed

1. **Storage format:** JSON files vs. SQLite database?
2. **Font licensing:** Embed custom fonts or use system fonts?
3. **Offline mode:** Should it work without internet?

---

## 9. Success Metrics

### MVP Success
- [ ] Can generate a printable PDF for any song with basic chords
- [ ] Chord diagrams are accurate and readable
- [ ] Lyrics and chords align correctly
- [ ] Fits on one page for typical songs

### V1.0 Success  
- [ ] Can scrape and parse tabs from Ultimate Guitar
- [ ] LLM cleans up messy input automatically
- [ ] Web interface for easy input/output
- [ ] Library of 10+ saved songs

### Future Success
- [ ] Transpose to any key with one click
- [ ] Auto-suggest easiest chord voicings
- [ ] Practice mode with audio sync
- [ ] Mobile-friendly web app

---

## 10. Reference Links

- [ChordPro Format Spec](https://www.chordpro.org/)
- [fpdf2 Documentation](https://py-pdf.github.io/fpdf2/)
- [Ultimate Guitar](https://www.ultimate-guitar.com/) (scraping target)
- [Songsterr](https://www.songsterr.com/) (tab reference)

---

*This is a living document. Update as the project evolves.*

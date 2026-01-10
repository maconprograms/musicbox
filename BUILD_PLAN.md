# MusicBox Build Plan

> **Goal:** A fun chatbot that helps you and your son find, format, and print beautiful guitar chord sheets.

---

## Project Overview

**MusicBox** is a **FastHTML** web application powered by an LLM (Gemini) that acts as a **Curator & Polisher**.
It solves the "Web Tab Problem" (messy formatting, ads, incorrect keys) by converting everything into a clean, standardized format before printing.

**Core Philosophy:**
1.  **Source of Truth:** All songs are stored/processed as **ChordPro** text (`[G]Hello [C]World`).
2.  **Strict Validation:** Pydantic models enforce valid chords and structure.
3.  **Smart Features:** Transposition and simplification happen mathematically, not textually.

---

## Architecture

```
/musicbox
├── main.py                 # FastHTML app server
├── requirements.txt
├── .env.example            # API key template
├── core/
│   ├── __init__.py
│   ├── models.py           # Pydantic models (TabCore, ChordPro logic)
│   ├── agent.py            # Gemini agent (The "Gussying" Engine)
│   ├── tools.py            # Tool definitions
│   ├── scraper.py          # Web fetcher
│   ├── parser.py           # Raw Text -> ChordPro converter
│   ├── music_theory.py     # Transposition (PyChord wrapper)
│   └── renderer.py         # ChordPro -> PDF with SVG/QR
├── assets/
│   ├── fonts/
│   │   └── RobotoMono.ttf  # Monospace font
└── library/
    ├── pdfs/
    └── data/
```

---

## Phase 1: Foundation (The ChordPro Engine)

### 1.1 Data Models (`core/models.py`)

We treat songs as structured objects, not strings.

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional

class ChordDefinition(BaseModel):
    """Guitar chord fingering."""
    name: str  # e.g., "Am7"
    fingering: str # e.g., "x 0 2 0 1 0"

class SongSection(BaseModel):
    """A logical block of the song."""
    type: str = Field(..., description="Verse, Chorus, Bridge, etc.")
    content: str = Field(..., description="ChordPro formatted text lines")
    # Example content: "It's a [G]beautiful [C]day"

class TabCore(BaseModel):
    """The Source of Truth."""
    title: str
    artist: str
    key: str = "C"
    capo: Optional[int] = None
    tuning: str = "Standard"
    strumming_pattern: Optional[str] = None
    sections: List[SongSection] = Field(default_factory=list)
    chords: Dict[str, ChordDefinition] = Field(default_factory=dict)
    source_url: Optional[str] = None
    audio_url: Optional[str] = None

    def to_chordpro_text(self) -> str:
        """Export full valid ChordPro file string."""
        pass
```

### 1.2 Music Theory & Logic (`core/music_theory.py`)

Use `pychord` to handle the math.

```python
from pychord import Chord

def transpose_chordpro(text: str, semitones: int) -> str:
    """
    Parses a ChordPro string, identifies brackets [Am], 
    and shifts them by N semitones.
    Returns new ChordPro string.
    """
    pass

def simplify_song(tab: TabCore) -> TabCore:
    """
    1. Analyze chords in the tab.
    2. If difficult chords (F, Bm, F#m) exist:
       - Calculate best Capo position to use open shapes (G, C, D, A, E).
    3. Transpose the content and set tab.capo.
    """
    pass
```

### 1.3 PDF Renderer (`core/renderer.py`)

Generates a visual artifact from the ChordPro data.

**Features:**
- **Vector Chord Diagrams:** Drawn at the top or bottom using `fpdf` primitives.
- **Smart QR:** Links to `audio_url`.
- **Lyric/Chord Alignment:** Parses ChordPro `[G]Word` to render the G above the 'W'.

```python
class ChordSheetPDF(FPDF):
    def render_chordpro_line(self, line: str):
        """
        Splits "[G]Hello [C]World" into:
        [(G, Hello), (C, World)]
        And renders chords above lyrics, preserving spacing.
        """
        pass
```

---

## Phase 2: Ingestion Pipeline

### 2.1 The "Gussying" Agent Strategy

The LLM is the best tool for converting "Web Format" to "ChordPro".

**Prompt Strategy:**
"You are a music editor. Convert this raw text into valid ChordPro format. Place chords in brackets inline with lyrics. If chords are floating above lyrics, merge them correctly."

### 2.2 Parser (`core/parser.py`)

```python
async def parse_to_model(raw_text: str, artist: str, title: str) -> TabCore:
    """
    1. If raw_text is already ChordPro-ish, clean it.
    2. If raw_text is 'lines over lyrics', use Gemini to 'gussy it up' into ChordPro.
    3. Validate against TabCore Pydantic model.
    """
    pass
```

---

## Phase 3: FastHTML UI

### 3.1 Views (`main.py`)

1.  **Chat Mode:** Conversational search.
2.  **Paste Mode:** Large text area for manual input.
3.  **Editor Mode (Optional but cool):** Show the generated ChordPro text in a textarea so the dad can manually fix a wrong chord before generating the PDF.

---

## Phase 4: Tools & Deployment

### 4.1 Requirements (`requirements.txt`)

```
python-fasthtml
uvicorn
google-genai>=1.0.0
pydantic>=2.0.0
fpdf2>=2.7.0
qrcode[pil]>=7.0.0
pychord>=1.0.0   # For transposition logic
httpx>=0.25.0
beautifulsoup4>=4.12.0
python-dotenv>=1.0.0
```

---

## Build Order

1.  **Foundation:** `models.py` (ChordPro structure), `music_theory.py` (Transposition), `renderer.py`.
2.  **Ingestion:** `parser.py` (LLM-based conversion).
3.  **Interface:** FastHTML App + Paste Mode.
4.  **Polish:** QR Codes + SVG Diagrams.
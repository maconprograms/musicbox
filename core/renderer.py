"""
PDF Renderer for MusicBox.

Generates clean, printable guitar chord sheets from TabCore data.
Designed for single-page printing with maximum information density.
"""

from fpdf import FPDF
import qrcode
import tempfile
import re
import io
from typing import List, Optional, Tuple
from core.models import TabCore, SongSection, ChordDefinition, TabLine
from core.diagrams import ChordDiagramSVG, get_chord_definition, COMMON_CHORDS

# Try to import cairosvg for SVG to PNG conversion
try:
    import cairosvg
    HAS_CAIROSVG = True
except ImportError:
    HAS_CAIROSVG = False


class ChordSheetPDF(FPDF):
    """
    Generates a clean, information-dense chord sheet PDF.
    
    Layout zones (top to bottom):
    1. Header: Title, Artist, Meta info (Key, Capo, Tempo, Difficulty)
    2. Chord Strip: Visual chord diagrams for all chords used
    3. Structure Map: Quick roadmap of song sections
    4. Patterns: Strumming/picking patterns if provided
    5. Content: Sections with chords, lyrics, tabs, bar progressions
    6. Footer: QR code, notes
    """
    
    # Layout constants
    MARGIN = 12
    CONTENT_WIDTH = 210 - (2 * 12)  # A4 width minus margins
    
    # Font sizes
    TITLE_SIZE = 22
    ARTIST_SIZE = 12
    META_SIZE = 9
    SECTION_HEADER_SIZE = 11
    CHORD_SIZE = 10
    LYRIC_SIZE = 10
    TAB_SIZE = 8
    
    # Colors (R, G, B)
    COLOR_TITLE = (30, 30, 30)
    COLOR_ARTIST = (80, 80, 80)
    COLOR_META = (100, 100, 100)
    COLOR_CHORD = (0, 90, 160)
    COLOR_SECTION = (60, 60, 60)
    COLOR_LYRIC = (20, 20, 20)
    COLOR_TAB = (50, 50, 50)
    COLOR_BAR = (40, 40, 40)
    COLOR_STRUCTURE = (120, 120, 120)
    
    def __init__(self, tab: TabCore):
        super().__init__()
        self.tab = tab
        self.set_auto_page_break(auto=True, margin=15)
        self.set_margins(self.MARGIN, self.MARGIN, self.MARGIN)
        
    def _set_color(self, color: Tuple[int, int, int]):
        """Set text color from RGB tuple."""
        self.set_text_color(*color)
        
    def header(self):
        """Render the header section."""
        # Title
        self._set_color(self.COLOR_TITLE)
        self.set_font('Helvetica', 'B', self.TITLE_SIZE)
        self.cell(0, 10, self.tab.title, ln=True, align='C')
        
        # Artist / Writers
        self._set_color(self.COLOR_ARTIST)
        self.set_font('Helvetica', 'I', self.ARTIST_SIZE)
        if self.tab.writers:
            attribution = f"Words & Music by {' & '.join(self.tab.writers)}"
        else:
            attribution = self.tab.artist
        self.cell(0, 6, attribution, ln=True, align='C')
        
        # Meta info line
        self._render_meta_line()
        
        self.ln(4)
        
        # Chord diagrams
        self._render_chord_diagrams()
        
        # Structure roadmap
        if self.tab.structure:
            self._render_structure_map()
        
        # Picking patterns
        if self.tab.patterns:
            self._render_patterns()
            
        self.ln(3)
        
    def _render_meta_line(self):
        """Render Key | Capo | Tempo | Difficulty line."""
        meta_parts = []
        
        if self.tab.key:
            meta_parts.append(f"Key: {self.tab.key}")
        if self.tab.capo:
            meta_parts.append(f"Capo: Fret {self.tab.capo}")
        if self.tab.tempo:
            meta_parts.append(f"Tempo: {self.tab.tempo} BPM")
        if self.tab.time_signature and self.tab.time_signature != "4/4":
            meta_parts.append(f"Time: {self.tab.time_signature}")
        if self.tab.tuning and self.tab.tuning != "Standard":
            meta_parts.append(f"Tuning: {self.tab.tuning}")
        if self.tab.difficulty:
            meta_parts.append(self._difficulty_indicator(self.tab.difficulty))
        
        if meta_parts:
            self._set_color(self.COLOR_META)
            self.set_font('Helvetica', '', self.META_SIZE)
            self.cell(0, 5, "  |  ".join(meta_parts), ln=True, align='C')
            
    def _difficulty_indicator(self, difficulty: str) -> str:
        """Convert difficulty to star rating."""
        stars = {
            "Beginner": "* Easy",
            "Intermediate": "** Intermediate", 
            "Advanced": "*** Advanced"
        }
        return stars.get(difficulty, difficulty)
    
    def _render_chord_diagrams(self):
        """Render chord diagram strip."""
        # Get all chords used in the song
        chord_names = self.tab.get_all_chord_names()
        if not chord_names:
            return
            
        # Build chord definitions (from tab or common library)
        chords_to_render = []
        for name in chord_names:
            if name in self.tab.chords:
                chords_to_render.append(self.tab.chords[name])
            elif name in COMMON_CHORDS:
                chords_to_render.append(COMMON_CHORDS[name])
        
        if not chords_to_render:
            return
        
        # Render SVG chord diagrams as images
        if HAS_CAIROSVG:
            self._render_svg_chord_diagrams(chords_to_render)
        else:
            # Fallback: render text-based diagrams
            self._render_text_chord_diagrams(chords_to_render)
            
        self.ln(2)
        
    def _render_svg_chord_diagrams(self, chords: List[ChordDefinition]):
        """Render SVG chord diagrams as images (requires cairosvg)."""
        import os
        
        diagram_width = 16  # mm per diagram
        diagram_height = 22  # mm
        spacing = 3  # mm between diagrams
        
        # Calculate how many fit per row
        available_width = self.CONTENT_WIDTH
        diagrams_per_row = int(available_width / (diagram_width + spacing))
        
        x_start = self.MARGIN
        y_start = self.get_y()
        
        for i, chord in enumerate(chords):
            # Calculate position
            row = i // diagrams_per_row
            col = i % diagrams_per_row
            
            x_pos = x_start + col * (diagram_width + spacing)
            y_pos = y_start + row * (diagram_height + 2)
            
            # Generate SVG and convert to PNG
            svg = ChordDiagramSVG(chord).to_svg()
            png_data = cairosvg.svg2png(bytestring=svg.encode(), output_width=120)
            
            # Save to temp file and embed
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp.write(png_data)
                tmp.flush()
                self.image(tmp.name, x=x_pos, y=y_pos, w=diagram_width)
                os.unlink(tmp.name)  # Clean up temp file
        
        # Move cursor below diagrams
        total_rows = (len(chords) - 1) // diagrams_per_row + 1
        self.set_y(y_start + total_rows * (diagram_height + 2) + 2)
        
    def _render_text_chord_diagrams(self, chords: List[ChordDefinition]):
        """Fallback: render simple text-based chord boxes."""
        self.set_font('Courier', '', 7)
        self._set_color(self.COLOR_TAB)
        
        # Render each chord as a mini grid
        for chord in chords[:8]:  # Limit to 8 chords on one line
            fret_str = ' '.join(
                'x' if f == -1 else 'o' if f == 0 else str(f) 
                for f in chord.frets
            )
            self.cell(25, 4, f"{chord.name}: {fret_str}", ln=False)
        self.ln()
        
    def _render_structure_map(self):
        """Render song structure roadmap."""
        self._set_color(self.COLOR_STRUCTURE)
        self.set_font('Helvetica', '', 8)
        
        # Abbreviate section names
        abbrev = {
            'intro': 'Intro', 'verse': 'V', 'verse1': 'V1', 'verse2': 'V2',
            'verse3': 'V3', 'verse4': 'V4', 'chorus': 'C', 'chorus1': 'C1',
            'chorus2': 'C2', 'bridge': 'Br', 'outro': 'Outro', 'solo': 'Solo',
            'prechorus': 'Pre', 'interlude': 'Int'
        }
        
        structure_str = " -> ".join(
            abbrev.get(s.lower(), s) for s in self.tab.structure
        )
        self.cell(0, 4, f"Structure: {structure_str}", ln=True, align='C')
        self.ln(1)
        
    def _render_patterns(self):
        """Render strumming/picking patterns."""
        self._set_color(self.COLOR_META)
        self.set_font('Helvetica', 'B', 8)
        
        for pattern in self.tab.patterns[:2]:  # Max 2 patterns in header
            self.cell(0, 4, f"{pattern.name}:", ln=False)
            self.set_font('Courier', '', 8)
            self.cell(0, 4, f"  {pattern.notation}", ln=True)
            
            # If pattern has tab, render it
            if pattern.tab:
                self._render_tab_lines(pattern.tab)
                
    def render_section(self, section: SongSection):
        """Render a song section."""
        # Section header
        self._set_color(self.COLOR_SECTION)
        self.set_font('Helvetica', 'B', self.SECTION_HEADER_SIZE)
        
        label = section.display_label
        if section.repeat and section.repeat > 1:
            label += f" (x{section.repeat})"
        self.cell(0, 6, label, ln=True)
        
        # Bar progression (for intros, instrumentals)
        if section.bar_progression:
            self._render_bar_progression(section.bar_progression)
            
        # Tablature
        if section.tab:
            self._render_tab_lines(section.tab)
            
        # Lyrics with chords
        if section.content.strip():
            lines = section.content.split('\n')
            for line in lines:
                if line.strip():
                    self._render_chordpro_line(line)
                else:
                    self.ln(2)
                    
        self.ln(3)
        
    def _render_bar_progression(self, progression: str):
        """Render bar notation like |G|G|C|C|."""
        self._set_color(self.COLOR_BAR)
        self.set_font('Courier', 'B', self.CHORD_SIZE)
        self.cell(0, 5, progression, ln=True)
        self.ln(1)
        
    def _render_tab_lines(self, tab_lines: List[TabLine]):
        """Render tablature."""
        self._set_color(self.COLOR_TAB)
        self.set_font('Courier', '', self.TAB_SIZE)
        
        for tab_line in tab_lines:
            lines = [
                f"e|{tab_line.e}|",
                f"B|{tab_line.B}|",
                f"G|{tab_line.G}|",
                f"D|{tab_line.D}|",
                f"A|{tab_line.A}|",
                f"E|{tab_line.E}|",
            ]
            for line in lines:
                self.cell(0, 3.5, line, ln=True)
            self.ln(1)
            
    def _render_chordpro_line(self, line: str):
        """
        Render a ChordPro line with chords above lyrics.
        Parses "[G]Hello [C]World" into aligned chord and lyric lines.
        """
        # Parse tokens: [chord]text pairs
        tokens = re.findall(r'(\[[^\]]+\])?([^\[]*)', line)
        
        chord_line = ""
        lyric_line = ""
        
        for chord_token, lyric_token in tokens:
            if not chord_token and not lyric_token:
                continue
                
            chord = chord_token[1:-1] if chord_token else ""
            lyric = lyric_token
            
            # Calculate padding
            len_chord = len(chord)
            len_lyric = len(lyric)
            max_len = max(len_chord, len_lyric)
            
            chord_line += chord.ljust(max_len)
            lyric_line += lyric.ljust(max_len)
        
        # Render chord line (if any chords)
        if chord_line.strip():
            self._set_color(self.COLOR_CHORD)
            self.set_font('Courier', 'B', self.CHORD_SIZE)
            self.cell(0, 4, chord_line, ln=True)
            
        # Render lyric line
        self._set_color(self.COLOR_LYRIC)
        self.set_font('Courier', '', self.LYRIC_SIZE)
        self.cell(0, 4, lyric_line, ln=True)
        
    def _render_qr_code(self):
        """Generate and place QR code if audio URL exists."""
        url = self.tab.audio_url or self.tab.source_url
        if not url:
            return
            
        img = qrcode.make(url)
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            img.save(tmp.name)
            # Position: Bottom right corner
            self.image(tmp.name, x=185, y=self.get_y(), w=18)
            
    def _render_notes(self):
        """Render any playing notes/tips."""
        if not self.tab.notes:
            return
            
        self._set_color(self.COLOR_META)
        self.set_font('Helvetica', 'I', 8)
        self.multi_cell(0, 4, f"Notes: {self.tab.notes}")
        
    def generate(self, output_path: str) -> str:
        """Generate the complete PDF."""
        self.add_page()
        
        # Sections
        for section in self.tab.sections:
            self.render_section(section)
            
        # Footer elements
        self._render_notes()
        self._render_qr_code()
        
        self.output(output_path)
        return output_path


def render_chord_sheet(tab: TabCore, output_path: str) -> str:
    """Convenience function to render a chord sheet PDF."""
    pdf = ChordSheetPDF(tab)
    return pdf.generate(output_path)

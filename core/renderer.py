from fpdf import FPDF
import qrcode
import tempfile
import re
from core.models import TabCore, SongSection

class ChordSheetPDF(FPDF):
    def __init__(self, tab: TabCore):
        super().__init__()
        self.tab = tab
        self.set_auto_page_break(auto=True, margin=15)
        # Use built-in Courier for monospace reliability
        self.add_font('Mono', '', 'Courier', uni=True) 
        self.add_font('MonoB', '', 'Courier-Bold', uni=True)

    def header(self):
        # Title
        self.set_font('Helvetica', 'B', 24)
        self.cell(0, 10, self.tab.title, ln=True, align='C')
        
        # Artist
        self.set_font('Helvetica', 'I', 14)
        self.cell(0, 8, self.tab.artist, ln=True, align='C')
        
        # QR Code (Top Right)
        self.render_qr_code()
        
        # Meta info line
        meta_parts = []
        if self.tab.key: meta_parts.append(f"Key: {self.tab.key}")
        if self.tab.capo: meta_parts.append(f"Capo: {self.tab.capo}")
        
        self.set_font('Helvetica', '', 10)
        self.cell(0, 6, " | ".join(meta_parts), ln=True, align='C')
        self.ln(10)

    def render_qr_code(self):
        """Generate and stamp QR code."""
        url = self.tab.audio_url or self.tab.source_url
        if not url:
            return
            
        img = qrcode.make(url)
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            img.save(tmp.name)
            # Position: Top Right
            self.image(tmp.name, x=180, y=10, w=20)
            
    def render_section(self, section: SongSection):
        # Section Header
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, section.type, ln=True)
        self.set_text_color(0, 0, 0)
        
        # Content
        self.set_font('Mono', '', 11)
        lines = section.content.split('\n')
        for line in lines:
            if line.strip():
                self.render_chordpro_line(line)
            else:
                self.ln(5)
        self.ln(5)

    def render_chordpro_line(self, line: str):
        """
        Parses "[G]Hello [C]World" and renders aligned chords/lyrics.
        Strategy: Tokenize and pad.
        """
        # Split by chords: [G]Hello -> [('[G]', 'Hello')] 
        # Regex to find [chord]lyric chunks
        # This regex matches a chord block [..] optionally followed by text until the next [
        tokens = re.findall(r'(\[[^\]]+\])?([^\[]*)', line)
        
        chord_line = ""
        lyric_line = ""
        
        for chord_token, lyric_token in tokens:
            if not chord_token and not lyric_token:
                continue
                
            # Strip brackets from chord: [G] -> G
            chord = chord_token[1:-1] if chord_token else ""
            lyric = lyric_token
            
            # Calculate length needed
            # We add at least 1 space of padding if there's a chord
            len_chord = len(chord)
            len_lyric = len(lyric)
            
            max_len = max(len_chord, len_lyric)
            
            # If there is a chord, we often want a bit of spacing after it if the lyric is short
            # to prevent chords directly touching. 
            # E.g. [G][C] -> G C
            
            # Padding
            pad_chord = chord.ljust(max_len)
            pad_lyric = lyric.ljust(max_len)
            
            # If the chord is longer than the lyric (e.g. changing chord on a single letter word "I")
            # we need to extend the lyric line with spaces so the next word starts later.
            # AND vice versa. 
            
            chord_line += pad_chord
            lyric_line += pad_lyric
            
        # Render
        # 1. Chord Line (Blue)
        if chord_line.strip():
            self.set_text_color(0, 100, 180)
            self.set_font('MonoB', '', 11)
            self.cell(0, 5, chord_line, ln=True)
            
        # 2. Lyric Line (Black)
        self.set_text_color(0, 0, 0)
        self.set_font('Mono', '', 11)
        self.cell(0, 5, lyric_line, ln=True)

    def generate(self, output_path: str):
        self.add_page()
        for section in self.tab.sections:
            self.render_section(section)
        self.output(output_path)
        return output_path

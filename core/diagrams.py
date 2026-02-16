"""
SVG Chord Diagram Generator for MusicBox.

Generates clean, printable chord diagrams as SVG strings.
These can be embedded directly in HTML or converted to PNG for PDF rendering.
"""

from typing import Optional, List
from core.models import ChordDefinition


class ChordDiagramSVG:
    """Generates SVG chord diagrams."""
    
    # Default dimensions
    WIDTH = 60
    HEIGHT = 80
    PADDING_TOP = 18  # Space for chord name
    PADDING_BOTTOM = 8
    PADDING_SIDE = 8
    
    # Grid settings
    NUM_STRINGS = 6
    NUM_FRETS = 5
    
    # Colors
    COLOR_LINE = "#333333"
    COLOR_DOT = "#111111"
    COLOR_TEXT = "#111111"
    COLOR_MUTED = "#666666"
    COLOR_BARRE = "#222222"
    
    def __init__(self, chord: ChordDefinition):
        self.chord = chord
        self.string_spacing = (self.WIDTH - 2 * self.PADDING_SIDE) / (self.NUM_STRINGS - 1)
        self.fret_spacing = (self.HEIGHT - self.PADDING_TOP - self.PADDING_BOTTOM) / self.NUM_FRETS
        
    def _string_x(self, string_num: int) -> float:
        """Get X coordinate for a string (0 = low E, 5 = high e)."""
        return self.PADDING_SIDE + string_num * self.string_spacing
    
    def _fret_y(self, fret_num: int) -> float:
        """Get Y coordinate for a fret (0 = nut, 1-5 = frets)."""
        return self.PADDING_TOP + fret_num * self.fret_spacing
    
    def _render_grid(self) -> str:
        """Render the fretboard grid."""
        lines = []
        
        # Nut (thick line at top) or fret number indicator
        if self.chord.base_fret == 1:
            # Draw nut as thick line
            lines.append(
                f'<rect x="{self.PADDING_SIDE - 1}" y="{self.PADDING_TOP - 3}" '
                f'width="{self.WIDTH - 2 * self.PADDING_SIDE + 2}" height="4" '
                f'fill="{self.COLOR_LINE}"/>'
            )
        else:
            # Show fret number
            lines.append(
                f'<text x="{self.PADDING_SIDE - 6}" y="{self._fret_y(1)}" '
                f'font-family="Arial, sans-serif" font-size="8" '
                f'fill="{self.COLOR_TEXT}" text-anchor="end" dominant-baseline="middle">'
                f'{self.chord.base_fret}fr</text>'
            )
        
        # Horizontal fret lines
        for fret in range(self.NUM_FRETS + 1):
            y = self._fret_y(fret)
            lines.append(
                f'<line x1="{self.PADDING_SIDE}" y1="{y}" '
                f'x2="{self.WIDTH - self.PADDING_SIDE}" y2="{y}" '
                f'stroke="{self.COLOR_LINE}" stroke-width="1"/>'
            )
        
        # Vertical string lines
        for string in range(self.NUM_STRINGS):
            x = self._string_x(string)
            lines.append(
                f'<line x1="{x}" y1="{self.PADDING_TOP}" '
                f'x2="{x}" y2="{self._fret_y(self.NUM_FRETS)}" '
                f'stroke="{self.COLOR_LINE}" stroke-width="1"/>'
            )
        
        return '\n'.join(lines)
    
    def _render_chord_name(self) -> str:
        """Render the chord name at the top."""
        return (
            f'<text x="{self.WIDTH / 2}" y="12" '
            f'font-family="Arial, sans-serif" font-size="12" font-weight="bold" '
            f'fill="{self.COLOR_TEXT}" text-anchor="middle">{self.chord.name}</text>'
        )
    
    def _render_string_markers(self) -> str:
        """Render X (muted) and O (open) markers above the nut."""
        markers = []
        marker_y = self.PADDING_TOP - 8
        
        for string, fret in enumerate(self.chord.frets):
            x = self._string_x(string)
            
            if fret == -1:  # Muted
                # Draw X
                size = 3
                markers.append(
                    f'<line x1="{x - size}" y1="{marker_y - size}" '
                    f'x2="{x + size}" y2="{marker_y + size}" '
                    f'stroke="{self.COLOR_MUTED}" stroke-width="1.5"/>'
                )
                markers.append(
                    f'<line x1="{x - size}" y1="{marker_y + size}" '
                    f'x2="{x + size}" y2="{marker_y - size}" '
                    f'stroke="{self.COLOR_MUTED}" stroke-width="1.5"/>'
                )
            elif fret == 0:  # Open
                # Draw O
                markers.append(
                    f'<circle cx="{x}" cy="{marker_y}" r="3" '
                    f'fill="none" stroke="{self.COLOR_LINE}" stroke-width="1"/>'
                )
        
        return '\n'.join(markers)
    
    def _render_finger_dots(self) -> str:
        """Render the finger position dots."""
        dots = []
        dot_radius = 4
        
        for string, fret in enumerate(self.chord.frets):
            if fret > 0:  # Fretted note
                x = self._string_x(string)
                # Position dot in the middle of the fret space
                display_fret = fret - self.chord.base_fret + 1
                if 1 <= display_fret <= self.NUM_FRETS:
                    y = self._fret_y(display_fret) - self.fret_spacing / 2
                    
                    # Draw filled circle
                    dots.append(
                        f'<circle cx="{x}" cy="{y}" r="{dot_radius}" '
                        f'fill="{self.COLOR_DOT}"/>'
                    )
                    
                    # Add finger number if available
                    if self.chord.fingers and len(self.chord.fingers) > string:
                        finger = self.chord.fingers[string]
                        if finger > 0:
                            dots.append(
                                f'<text x="{x}" y="{y + 1}" '
                                f'font-family="Arial, sans-serif" font-size="6" '
                                f'fill="white" text-anchor="middle" '
                                f'dominant-baseline="middle">{finger}</text>'
                            )
        
        return '\n'.join(dots)
    
    def _render_barre(self) -> str:
        """Render barre indicator if present."""
        if not self.chord.barre:
            return ''
        
        # Find the extent of the barre (which strings)
        barre_fret = self.chord.barre
        display_fret = barre_fret - self.chord.base_fret + 1
        
        if not (1 <= display_fret <= self.NUM_FRETS):
            return ''
        
        # Find strings that are part of the barre (have this fret or lower)
        barre_strings = [i for i, f in enumerate(self.chord.frets) if f == barre_fret]
        
        if len(barre_strings) < 2:
            return ''
        
        start_string = min(barre_strings)
        end_string = max(barre_strings)
        
        x1 = self._string_x(start_string)
        x2 = self._string_x(end_string)
        y = self._fret_y(display_fret) - self.fret_spacing / 2
        
        return (
            f'<rect x="{x1 - 4}" y="{y - 3}" '
            f'width="{x2 - x1 + 8}" height="6" rx="3" '
            f'fill="{self.COLOR_BARRE}"/>'
        )
    
    def to_svg(self) -> str:
        """Generate the complete SVG string."""
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.WIDTH}" height="{self.HEIGHT}" '
            f'viewBox="0 0 {self.WIDTH} {self.HEIGHT}">',
            self._render_chord_name(),
            self._render_grid(),
            self._render_string_markers(),
            self._render_barre(),
            self._render_finger_dots(),
            '</svg>'
        ]
        return '\n'.join(svg_parts)


def generate_chord_diagram(chord: ChordDefinition) -> str:
    """Convenience function to generate SVG for a chord."""
    return ChordDiagramSVG(chord).to_svg()


def generate_chord_strip(chords: List[ChordDefinition], spacing: int = 10) -> str:
    """Generate a horizontal strip of chord diagrams."""
    if not chords:
        return ''
    
    diagram_width = ChordDiagramSVG.WIDTH
    diagram_height = ChordDiagramSVG.HEIGHT
    total_width = len(chords) * diagram_width + (len(chords) - 1) * spacing
    
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{total_width}" height="{diagram_height}" '
        f'viewBox="0 0 {total_width} {diagram_height}">'
    ]
    
    for i, chord in enumerate(chords):
        x_offset = i * (diagram_width + spacing)
        diagram_svg = ChordDiagramSVG(chord).to_svg()
        # Wrap in a group with translation
        parts.append(f'<g transform="translate({x_offset}, 0)">')
        # Extract just the content (remove outer svg tags)
        content = diagram_svg.split('>', 1)[1].rsplit('<', 1)[0]
        parts.append(content)
        parts.append('</g>')
    
    parts.append('</svg>')
    return '\n'.join(parts)


# Common chord definitions library
COMMON_CHORDS = {
    "G": ChordDefinition(name="G", frets=[3, 2, 0, 0, 0, 3], fingers=[2, 1, 0, 0, 0, 3]),
    "C": ChordDefinition(name="C", frets=[-1, 3, 2, 0, 1, 0], fingers=[0, 3, 2, 0, 1, 0]),
    "D": ChordDefinition(name="D", frets=[-1, -1, 0, 2, 3, 2], fingers=[0, 0, 0, 1, 3, 2]),
    "Am": ChordDefinition(name="Am", frets=[-1, 0, 2, 2, 1, 0], fingers=[0, 0, 2, 3, 1, 0]),
    "A": ChordDefinition(name="A", frets=[-1, 0, 2, 2, 2, 0], fingers=[0, 0, 1, 2, 3, 0]),
    "E": ChordDefinition(name="E", frets=[0, 2, 2, 1, 0, 0], fingers=[0, 2, 3, 1, 0, 0]),
    "Em": ChordDefinition(name="Em", frets=[0, 2, 2, 0, 0, 0], fingers=[0, 2, 3, 0, 0, 0]),
    "F": ChordDefinition(name="F", frets=[1, 3, 3, 2, 1, 1], fingers=[1, 3, 4, 2, 1, 1], barre=1),
    "Dm": ChordDefinition(name="Dm", frets=[-1, -1, 0, 2, 3, 1], fingers=[0, 0, 0, 2, 3, 1]),
    "B7": ChordDefinition(name="B7", frets=[-1, 2, 1, 2, 0, 2], fingers=[0, 2, 1, 3, 0, 4]),
    "Cadd9": ChordDefinition(name="Cadd9", frets=[-1, 3, 2, 0, 3, 0], fingers=[0, 2, 1, 0, 3, 0]),
    "Dsus4": ChordDefinition(name="Dsus4", frets=[-1, -1, 0, 2, 3, 3], fingers=[0, 0, 0, 1, 2, 3]),
    "G/B": ChordDefinition(name="G/B", frets=[-1, 2, 0, 0, 0, 3], fingers=[0, 1, 0, 0, 0, 2]),
}


def get_chord_definition(name: str) -> Optional[ChordDefinition]:
    """Look up a chord by name from the common library."""
    return COMMON_CHORDS.get(name)

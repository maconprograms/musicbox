from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional

class ChordDefinition(BaseModel):
    """Complete chord voicing with visual diagram data."""
    name: str = Field(..., description="Chord name, e.g., 'G', 'Cadd9', 'Am7'")
    frets: List[int] = Field(..., description="Fret positions for each string [E,A,D,G,B,e]. Use -1 for muted, 0 for open.")
    fingers: Optional[List[int]] = Field(None, description="Finger numbers [1-4] for each string. 0 = open/muted.")
    barre: Optional[int] = Field(None, description="Barre fret number if this is a barre chord")
    base_fret: int = Field(1, description="Starting fret for diagram (for moveable shapes)")
    
    @field_validator('frets')
    @classmethod
    def validate_frets(cls, v: List[int]) -> List[int]:
        if len(v) != 6:
            raise ValueError('Must have exactly 6 fret positions (one per string)')
        for fret in v:
            if fret < -1 or fret > 24:
                raise ValueError('Fret must be -1 (muted), 0 (open), or 1-24')
        return v


class TabLine(BaseModel):
    """A single measure/bar of tablature notation."""
    e: str = Field(..., description="High e string tab notation")
    B: str = Field(..., description="B string tab notation")
    G: str = Field(..., description="G string tab notation")
    D: str = Field(..., description="D string tab notation")
    A: str = Field(..., description="A string tab notation")
    E: str = Field(..., description="Low E string tab notation")
    
    def to_ascii(self) -> str:
        """Render as standard ASCII tab."""
        return f"e|{self.e}|\nB|{self.B}|\nG|{self.G}|\nD|{self.D}|\nA|{self.A}|\nE|{self.E}|"

class PickingPattern(BaseModel):
    """Fingerpicking or strumming pattern."""
    name: str = Field(..., description="Pattern name, e.g., 'Verse Picking', 'Chorus Strum'")
    notation: str = Field(..., description="Pattern notation: 'D DU UDU' for strums or tab")
    beats_per_bar: int = Field(4, description="Time signature numerator")
    tab: Optional[List['TabLine']] = Field(None, description="Optional tab representation of pattern")

class SongSection(BaseModel):
    """A logical block of the song with optional tab and pattern references."""
    type: str = Field(..., description="Section type: Verse, Chorus, Bridge, Intro, Outro, Solo")
    label: Optional[str] = Field(None, description="Custom label like 'Verse 1', 'Pre-Chorus'")
    content: str = Field("", description="ChordPro formatted lyrics with inline chords")
    tab: Optional[List[TabLine]] = Field(None, description="Tablature for riffs, intros, solos")
    bar_progression: Optional[str] = Field(None, description="Bar notation like '|G|G|C|C|' for instrumentals")
    pattern_ref: Optional[str] = Field(None, description="Reference to a PickingPattern by name")
    repeat: Optional[int] = Field(None, description="Number of times to repeat this section")
    
    @field_validator('content')
    @classmethod
    def content_can_be_empty_for_instrumental(cls, v: str, info) -> str:
        # Content can be empty for instrumental sections (intro, solo, outro)
        return v
    
    @property
    def display_label(self) -> str:
        """Returns the label to display, falling back to type."""
        return self.label or self.type

class TabCore(BaseModel):
    """
    The Source of Truth for a song.
    Complete data model for generating printable guitar chord/tab sheets.
    """
    # === METADATA ===
    title: str = Field(..., description="Song title")
    artist: str = Field(..., description="Performing artist/band")
    writers: Optional[List[str]] = Field(None, description="Songwriters if different from artist")
    
    # === MUSICAL INFO ===
    key: str = Field("C", description="Musical key, e.g., 'G', 'Am', 'F#m'")
    capo: Optional[int] = Field(None, description="Capo position (fret number)")
    tempo: Optional[int] = Field(None, description="Tempo in BPM")
    time_signature: str = Field("4/4", description="Time signature")
    tuning: str = Field("Standard", description="Guitar tuning, e.g., 'Standard', 'Drop D', 'DADGAD'")
    difficulty: Optional[str] = Field(None, description="Difficulty: Beginner, Intermediate, Advanced")
    
    # === STRUCTURE ===
    structure: Optional[List[str]] = Field(None, description="Song roadmap: ['intro', 'verse1', 'chorus1', ...]")
    sections: List[SongSection] = Field(default_factory=list)
    
    # === CHORD LIBRARY ===
    chords: Dict[str, ChordDefinition] = Field(default_factory=dict, description="Chord voicings used in this song")
    
    # === PLAYING GUIDES ===
    patterns: Optional[List[PickingPattern]] = Field(None, description="Strumming/picking patterns")
    notes: Optional[str] = Field(None, description="Free-form playing tips and notes")
    
    # === REFERENCES ===
    source_url: Optional[str] = Field(None, description="URL where tab was sourced")
    audio_url: Optional[str] = Field(None, description="URL to audio for practice")

    def get_all_chord_names(self) -> List[str]:
        """Extract all unique chord names used in sections."""
        import re
        chord_pattern = re.compile(r'\[([^\]]+)\]')
        chords_found = set()
        for section in self.sections:
            chords_found.update(chord_pattern.findall(section.content))
            if section.bar_progression:
                # Parse bar progressions like |G|G|C|C| or |: G | G :|
                # Remove repeat markers and bars, then extract chord names
                cleaned = section.bar_progression.replace('|', ' ').replace(':', '')
                bars = cleaned.split()
                # Only include valid chord names (start with letter)
                chords_found.update(b for b in bars if b and b[0].isalpha())
        return sorted(list(chords_found))

    def to_chordpro_text(self) -> str:
        """Export the full song as a standard ChordPro string."""
        output = []
        
        # Meta directives
        output.append(f"{{title: {self.title}}}")
        output.append(f"{{artist: {self.artist}}}")
        if self.key:
            output.append(f"{{key: {self.key}}}")
        if self.capo:
            output.append(f"{{capo: {self.capo}}}")
        if self.tempo:
            output.append(f"{{tempo: {self.tempo}}}")
        
        output.append("")  # Spacer
        
        # Content
        for section in self.sections:
            output.append(f"{{comment: {section.display_label}}}")
            if section.bar_progression:
                output.append(section.bar_progression)
            if section.content:
                output.append(section.content)
            output.append("")
            
        return "\n".join(output)
    
    def to_json(self) -> str:
        """Export as JSON for storage."""
        return self.model_dump_json(indent=2)

from pydantic import BaseModel, Field, field_validator
from typing import List, Dict, Optional

class ChordDefinition(BaseModel):
    """Guitar chord fingering for diagrams."""
    name: str = Field(..., description="Chord name, e.g., 'G', 'Cadd9'")
    fingering: str = Field(..., description="Fret positions EADGBe, e.g., '3 2 0 0 3 3' or 'x 0 2 2 1 0'")

class SongSection(BaseModel):
    """A logical block of the song."""
    type: str = Field(..., description="Section type: Verse, Chorus, Bridge, Intro, Outro")
    content: str = Field(..., description="The content in ChordPro format (chords in brackets inline)")
    
    @field_validator('content')
    @classmethod
    def content_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Section content cannot be empty')
        return v

class TabCore(BaseModel):
    """
    The Source of Truth for a song.
    Stores the song in a structured format compatible with ChordPro.
    """
    title: str
    artist: str
    key: str = "C"
    capo: Optional[int] = None
    tuning: str = "Standard"
    strumming_pattern: Optional[str] = None
    
    sections: List[SongSection] = Field(default_factory=list)
    chords: Dict[str, ChordDefinition] = Field(default_factory=dict, description="Dictionary of specific chord voicings used")
    
    source_url: Optional[str] = None
    audio_url: Optional[str] = None

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
        
        output.append("") # Spacer
        
        # Content
        for section in self.sections:
            output.append(f"{{soc}}") # Start of chorus/component (generic)
            # Actually, standard ChordPro uses {sov} {soc} etc, but typically comments are better for section headers in simple parsers
            # We will just print the header label
            output.append(f"{{comment: {section.type}}}")
            output.append(section.content)
            output.append(f"{{eoc}}") # End
            output.append("")
            
        return "\n".join(output)

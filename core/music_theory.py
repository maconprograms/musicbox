import re
from pychord import Chord
from core.models import TabCore, SongSection

def transpose_chord_name(chord_name: str, semitones: int) -> str:
    """Safely transpose a single chord name."""
    try:
        # Handle slash chords manually if pychord struggles, 
        # but pychord usually handles them. 
        # Let's try basic pychord first.
        c = Chord(chord_name)
        c.transpose(semitones)
        return str(c)
    except Exception:
        # Fallback for complex chords or non-chords in brackets
        return chord_name

def transpose_chordpro_text(text: str, semitones: int) -> str:
    """
    Parses a ChordPro string, identifies brackets [Am], 
    and shifts them by N semitones.
    """
    def replace_chord(match):
        chord_text = match.group(1)
        new_chord = transpose_chord_name(chord_text, semitones)
        return f"[{new_chord}]"

    # Regex to find content inside brackets: [Am7]
    # We use non-greedy matching .*?
    return re.sub(r'\[(.*?)\]', replace_chord, text)

def transpose_song(tab: TabCore, semitones: int) -> TabCore:
    """
    Returns a NEW TabCore object transposed by N semitones.
    """
    new_sections = []
    for section in tab.sections:
        new_content = transpose_chordpro_text(section.content, semitones)
        new_sections.append(SongSection(type=section.type, content=new_content))
    
    # Also need to transpose the key if present
    new_key = tab.key
    if tab.key:
        try:
            # Simple key transposition using pychord (treating key as a major chord for now)
            k = Chord(tab.key) 
            k.transpose(semitones)
            new_key = k.root
        except:
            pass

    return TabCore(
        title=tab.title,
        artist=tab.artist,
        key=new_key,
        capo=tab.capo, # Capo might need adjustment if we are transposing to avoid capo, but here we just shift pitch
        tuning=tab.tuning,
        sections=new_sections,
        source_url=tab.source_url,
        audio_url=tab.audio_url
    )

def simplify_song(tab: TabCore) -> TabCore:
    """
    Analyzes the song and suggests a transposition that maximizes "Easy Open Chords".
    The "CAGED" keys: C, A, G, E, D are usually best.
    
    For now, this just returns the original song. 
    (Placeholder for Phase 2 implementation)
    """
    # TODO: Implement "Kid Mode" logic
    return tab

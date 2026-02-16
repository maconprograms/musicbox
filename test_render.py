"""Test script to render Ripple chord sheet PDF."""

import json
from pathlib import Path
from core.models import TabCore
from core.renderer import render_chord_sheet
from core.diagrams import ChordDiagramSVG, COMMON_CHORDS

def test_chord_diagrams():
    """Test SVG chord diagram generation."""
    print("Testing chord diagram generation...")
    
    for name in ["G", "C", "D", "Am", "A"]:
        chord = COMMON_CHORDS[name]
        svg = ChordDiagramSVG(chord).to_svg()
        
        # Save to file for inspection
        output_path = Path(f"assets/chord_diagrams/{name}.svg")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(svg)
        print(f"  Generated: {output_path}")
    
    print("Chord diagrams saved to assets/chord_diagrams/")

def test_pdf_render():
    """Test PDF rendering from Ripple JSON."""
    print("\nTesting PDF render...")
    
    # Load the JSON
    json_path = Path("library/data/ripple.json")
    with open(json_path) as f:
        data = json.load(f)
    
    # Parse into model
    tab = TabCore(**data)
    print(f"  Loaded: {tab.title} by {tab.artist}")
    print(f"  Key: {tab.key}, Tempo: {tab.tempo} BPM")
    print(f"  Chords used: {tab.get_all_chord_names()}")
    print(f"  Sections: {len(tab.sections)}")
    
    # Render PDF
    output_path = "library/pdfs/ripple_test.pdf"
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    result = render_chord_sheet(tab, output_path)
    print(f"  Generated: {result}")

def main():
    test_chord_diagrams()
    test_pdf_render()
    print("\nDone!")

if __name__ == "__main__":
    main()

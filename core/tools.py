import os
import asyncio
from typing import Dict, Any, Optional
from core.scraper import search_song, fetch_tab_content
from core.parser import parse_raw_to_model
from core.music_theory import simplify_song
from core.renderer import ChordSheetPDF
from core.models import TabCore
from pathlib import Path

# Tool Definitions for Pydantic AI or Gemini
# These can be used directly with Gemini's function calling

async def do_web_search(query: str) -> list:
    """Search the web for song suggestions or music information."""
    return await search_song(query)

async def fetch_and_render_chords(song: str, artist: str, simplify: bool = False) -> Dict[str, Any]:
    """
    The main pipeline:
    1. Search for the song
    2. Fetch raw content
    3. Parse into TabCore model
    4. (Optional) Simplify/Transpose
    5. Generate PDF
    """
    try:
        # 1. Search for a good source URL
        search_query = f"{song} {artist} chords"
        search_results = await search_song(search_query, limit=3)
        
        if not search_results:
            return {"success": False, "error": "Could not find any chords for this song."}
            
        # Try the first result (usually the best match)
        target_url = search_results[0]['url']
        
        # 2. Fetch raw content
        raw_data = await fetch_tab_content(target_url)
        if not raw_data.get("raw_content"):
            return {"success": False, "error": f"Failed to extract content from {target_url}"}
            
        # 3. Parse into TabCore (The Brain)
        # We pass the hints from search results if metadata extraction was partial
        tab = await parse_raw_to_model(
            raw_data["raw_content"], 
            artist_hint=artist or raw_data.get("artist"),
            title_hint=song or raw_data.get("title")
        )
        
        # 4. Optional: Simplify (Kid Mode)
        if simplify:
            tab = simplify_song(tab)
            
        # 5. Generate PDF
        renderer = ChordSheetPDF(tab)
        
        # Ensure directories exist
        pdf_dir = Path("library/pdfs")
        pdf_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{tab.artist} - {tab.title}.pdf".replace("/", "_")
        output_path = str(pdf_dir / filename)
        
        renderer.generate(output_path)
        
        # Save JSON data for library tracking
        data_dir = Path("library/data")
        data_dir.mkdir(parents=True, exist_ok=True)
        json_path = data_dir / f"{tab.artist} - {tab.title}.json"
        with open(json_path, 'w') as f:
            f.write(tab.model_dump_json(indent=2))
            
        return {
            "success": True,
            "pdf_path": output_path,
            "title": tab.title,
            "artist": tab.artist,
            "key": tab.key,
            "url": target_url
        }
        
    except Exception as e:
        return {
            "success": False, 
            "error": str(e),
            "suggestion": "I ran into a problem fetching those chords. Try pasting the text manually in the 'Paste' tab!"
        }

async def handle_tool_call(name: str, args: dict) -> Any:
    """Routing helper for tool calls."""
    if name == "web_search":
        return await do_web_search(args.get("query", ""))
    elif name == "fetch_chords":
        return await fetch_and_render_chords(
            args.get("song", ""), 
            args.get("artist", ""), 
            args.get("simplify", False)
        )
    return {"error": f"Unknown tool: {name}"}

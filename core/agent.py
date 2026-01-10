import os
from typing import List, Optional, Dict, Any
from pydantic_ai import Agent, RunContext
from core.tools import do_web_search, fetch_and_render_chords
from core.models import TabCore

SYSTEM_PROMPT = """
You are MusicBox, a friendly and enthusiastic guitar learning assistant! 🎸

Your goal is to help a dad and his son find, learn, and print guitar chord sheets. 
You're encouraging, practical, and love sharing the joy of music.

YOUR ABILITIES:
1. **Brainstorming**: Suggest beginner-friendly songs (G, D, C, Em are great starters).
2. **Finding Chords**: Use `fetch_chords` to find a song and generate a beautiful PDF.
3. **Simplifying**: If they find a song too hard, suggest "Kid Mode" (simplification).
4. **Research**: Use `web_search` to find info about artists or guitar tips.

PERSONALITY:
- Use music emojis (🎸, 🎵, 🤘).
- Keep responses relatively concise but warm.
- If a user asks for chords, ALWAYS trigger `fetch_chords`.
- After generating a PDF, mention that it's ready in their library.

Example Beginner Songs to suggest:
- "Knockin' on Heaven's Door" (G, D, Am, C)
- "Three Little Birds" (A, D, E)
- "Horse With No Name" (Em, D6/9)
"""

def get_musicbox_agent():
    api_key = os.getenv("GEMINI_API_KEY")
    # pydantic-ai will use the GEMINI_API_KEY env var automatically if using google-gla
    
    agent = Agent(
        'google-gla:gemini-2.0-flash-exp',
        system_prompt=SYSTEM_PROMPT,
        retries=2
    )

    @agent.tool_plain
    async def web_search(query: str) -> list:
        """Search the web for song suggestions, music tips, or artist info."""
        return await do_web_search(query)

    @agent.tool_plain
    async def fetch_chords(song: str, artist: str, simplify: bool = False) -> Dict[str, Any]:
        """
        Fetch chords for a specific song and generate a printable PDF.
        Set simplify=True for 'Kid Mode' (avoiding hard barre chords).
        """
        return await fetch_and_render_chords(song, artist, simplify)

    return agent

class MusicBoxSession:
    """Manages a single chat session with history."""
    def __init__(self):
        self.agent = get_musicbox_agent()
        self.message_history = []

    async def chat(self, user_msg: str) -> Dict[str, Any]:
        """
        Processes a user message and returns the response plus any generated artifacts.
        """
        result = await self.agent.run(
            user_msg, 
            message_history=self.message_history
        )
        
        # Update history
        self.message_history = result.all_messages()
        
        # Look for PDF generation in tool results
        pdf_path = None
        # In pydantic-ai, we can inspect tool results from the result object
        for msg in result.new_messages():
            if hasattr(msg, 'parts'):
                for part in msg.parts:
                    # Look for tool call results that contain pdf_path
                    if hasattr(part, 'content') and isinstance(part.content, dict):
                        if part.content.get('pdf_path'):
                            pdf_path = part.content.get('pdf_path')

        return {
            "content": result.data,
            "pdf_path": pdf_path
        }

import os
from pydantic_ai import Agent
from core.models import TabCore
import nest_asyncio

# Apply nest_asyncio to allow nested event loops if necessary (often needed in notebooks or complex app servers)
nest_asyncio.apply()

# Define the Agent
# We use a robust model for this structured task
model_name = 'google-gla:gemini-1.5-flash' 
# Note: 'google-gla' is the provider prefix for Google Gen AI in pydantic-ai (if using that provider)
# Or we can just use the standard vertex/openai providers. 
# Let's assume the user has the google-genai package and pydantic-ai supports it.
# Actually, pydantic-ai supports 'google-vertex' or 'google-gla' (Generative Language API).
# We will use 'gemini-1.5-flash' and let pydantic-ai infer or configure the provider.

SYSTEM_PROMPT = """
You are an expert Music Editor and Transcriber. 🎸

Your task is to take RAW, MESSY text from a guitar tab website and convert it into a clean, structured `TabCore` object.

RULES:
1. **ChordPro Format**: The content of each section MUST be in ChordPro format.
   - RAW: 
     G       C
     Hello World
   - CONVERT TO: [G]Hello [C]World
   
2. **Merge Lines**: You must accurately align chords with the lyrics they belong to.
3. **Sections**: Identify Verses, Choruses, Bridges. 
   - If no explicit headers exist, try to infer them or just use "Main".
4. **Clean Up**: Remove "Strumming: DDU...", "Difficulty: Novice", or other metadata from the *content* and put them in the appropriate fields (like `strumming_pattern`).
5. **Validation**: Ensure all chords are valid. 
"""

def get_parser_agent():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set")
        
    return Agent(
        'google-gla:gemini-2.0-flash-exp', # Using the fast, smart model
        result_type=TabCore,
        system_prompt=SYSTEM_PROMPT
    )

async def parse_raw_to_model(raw_text: str, artist_hint: str = None, title_hint: str = None) -> TabCore:
    """
    Uses Gemini to parse raw text into TabCore.
    """
    agent = get_parser_agent()
    
    prompt = f"""
    Here is the raw text to parse:
    
    ---BEGIN RAW TEXT---
    {raw_text}
    ---END RAW TEXT---
    
    Hints (use if missing in text):
    Artist: {artist_hint}
    Title: {title_hint}
    """
    
    result = await agent.run(prompt)
    return result.data

import httpx
from bs4 import BeautifulSoup
import json
import re
from duckduckgo_search import DDGS

async def search_song(query: str, limit: int = 5) -> list:
    """
    Search for guitar tabs using DuckDuckGo.
    Prefer sites like Ultimate-Guitar, Chordie, etc.
    """
    results = []
    # Force "guitar chords" or "tabs" into the query
    full_query = f"{query} guitar chords ultimate-guitar"
    
    try:
        # DDGS is synchronous, so we might want to run it in a thread or just accept blocking for MVP
        # Using a context manager for DDGS
        with DDGS() as ddgs:
            ddg_results = list(ddgs.text(full_query, max_results=limit))
            
        for r in ddg_results:
            results.append({
                "title": r['title'],
                "url": r['href'],
                "snippet": r['body']
            })
    except Exception as e:
        print(f"Search failed: {e}")
        
    return results

async def fetch_tab_content(url: str) -> dict:
    """
    Fetches the page and attempts to extract the raw tab content.
    Returns dictionary with raw_content, title, artist.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        html = resp.text

    soup = BeautifulSoup(html, 'html.parser')
    
    # 1. Ultimate Guitar Specific Extraction (JSON Store)
    if "ultimate-guitar.com" in url:
        try:
            # Find the JSON data embedded in the page
            # Look for: window.UGAPP.store.page = { ... };
            script_pattern = re.compile(r'window\.UGAPP\.store\.page\s*=\s*(\{.*?\});', re.DOTALL)
            script = soup.find('script', string=script_pattern)
            
            if script:
                match = script_pattern.search(script.string)
                if match:
                    data = json.loads(match.group(1))
                    
                    # Navigate the deep JSON structure of UG
                    # data['data']['tab_view']['wiki_tab']['content']
                    tab_view = data.get('data', {}).get('tab_view', {})
                    wiki_tab = tab_view.get('wiki_tab', {})
                    content = wiki_tab.get('content', '')
                    
                    meta = data.get('data', {}).get('tab', {})
                    song_name = meta.get('song_name')
                    artist_name = meta.get('artist_name')
                    
                    if content:
                        # Clean up [ch] tags to be standard brackets
                        content = content.replace('[ch]', '[').replace('[/ch]', ']')
                        content = content.replace('[tab]', '').replace('[/tab]', '')
                        
                        return {
                            "raw_content": content,
                            "title": song_name,
                            "artist": artist_name,
                            "url": url,
                            "source": "Ultimate-Guitar"
                        }
        except Exception as e:
            print(f"UG extraction failed: {e}")

    # 2. Generic <pre> extraction (Fall back)
    # Most tab sites use <pre>
    pre = soup.find('pre')
    if pre:
        # Extract text
        return {
            "raw_content": pre.get_text(),
            "title": soup.title.string if soup.title else "Unknown Song",
            "artist": "Unknown Artist",
            "url": url,
            "source": "Generic"
        }
        
    return {
        "raw_content": "",
        "error": "Could not extract tab content"
    }

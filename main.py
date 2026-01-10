from fasthtml.common import *
import os
from dotenv import load_dotenv
from core.agent import MusicBoxSession
from core.parser import parse_raw_to_model
from core.renderer import ChordSheetPDF
from pathlib import Path
import asyncio

load_dotenv()

# Initialize Global Session (In a real app, use session IDs)
session = MusicBoxSession()

# App Setup
app, rt = fast_app(
    hdrs=(pico_css, Style("""
        .chat-bubble { padding: 1rem; border-radius: 10px; margin-bottom: 1rem; max-width: 80%; }
        .user { background: #e3f2fd; margin-left: auto; text-align: right; }
        .bot { background: #f5f5f5; }
        #chat-window { height: 500px; overflow-y: auto; padding: 1rem; border: 1px solid #ccc; border-radius: 5px; }
        .hidden { display: none; }
    """)),
    title="MusicBox 🎸"
)

# Components
def ChatBubble(msg, role="bot", pdf_path=None):
    cls = f"chat-bubble {role}"
    content = [P(msg)]
    if pdf_path:
        fname = Path(pdf_path).name
        content.append(A(f"📄 Download {fname}", href=f"/download/{fname}", cls="button", target="_blank"))
    return Div(*content, cls=cls)

def LibraryItem(pdf_path):
    p = Path(pdf_path)
    return Li(A(f"🎵 {p.stem}", href=f"/download/{p.name}", target="_blank"))

@rt("/")
def get():
    return Titled("MusicBox 🎸",
        Main(cls="container",
            Grid(
                # Sidebar
                Div(
                    H3("📚 Your Library"),
                    Ul(id="library-list"),
                    hx_get="/library", hx_trigger="load",
                    cls="col-span-1"
                ),
                # Main Chat
                Div(
                    # Tabs
                    Nav(
                        Ul(
                            Li(A("Chat", href="#", onclick="showView('chat')")),
                            Li(A("Paste & Clean", href="#", onclick="showView('paste')")),
                        )
                    ),
                    # Chat View
                    Div(id="chat-view",
                        Div(id="chat-window",
                            ChatBubble("Hey! 🎸 I'm MusicBox. What song should we learn today?")
                        ),
                        Form(
                            Group(
                                Input(name="msg", placeholder="Ask for a song or suggestions...", id="chat-input"),
                                Button("Send", cls="primary")
                            ),
                            hx_post="/chat", hx_target="#chat-window", hx_swap="beforeend",
                            hx_on__after_request="this.reset()"
                        )
                    ),
                    # Paste View
                    Div(id="paste-view", cls="hidden",
                        H4("Gussy Up Your Tabs"),
                        P("Paste messy text here and I'll turn it into a beautiful PDF."),
                        Form(
                            Input(name="title", placeholder="Song Title"),
                            Input(name="artist", placeholder="Artist"),
                            Textarea(name="raw_text", placeholder="Paste chords/lyrics here...", rows=10),
                            Button("Generate PDF", cls="primary"),
                            hx_post="/clean", hx_target="#chat-window", hx_swap="beforeend"
                        )
                    ),
                    cls="col-span-3"
                )
            ),
            Script("""
                function showView(view) {
                    document.getElementById('chat-view').classList.toggle('hidden', view !== 'chat');
                    document.getElementById('paste-view').classList.toggle('hidden', view !== 'paste');
                }
            """)
        )
    )

@rt("/chat")
async def post(msg: str):
    # 1. Show user message immediately
    user_msg = ChatBubble(msg, role="user")
    
    # 2. Get AI response
    response = await session.chat(msg)
    bot_msg = ChatBubble(response["content"], role="bot", pdf_path=response["pdf_path"])
    
    # 3. If PDF was made, trigger library refresh
    res = [user_msg, bot_msg]
    if response["pdf_path"]:
        res.append(Div(hx_get="/library", hx_target="#library-list", hx_swap="innerHTML", hx_trigger="load"))
    
    return res

@rt("/clean")
async def post(title: str, artist: str, raw_text: str):
    # Direct gussying via parser
    tab = await parse_raw_to_model(raw_text, artist_hint=artist, title_hint=title)
    renderer = ChordSheetPDF(tab)
    
    pdf_dir = Path("library/pdfs")
    pdf_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{tab.artist} - {tab.title}.pdf".replace("/", "_")
    output_path = str(pdf_dir / filename)
    renderer.generate(output_path)
    
    return ChatBubble(f"Finished gussying up '{title}'! Check your library.", pdf_path=output_path)

@rt("/library")
def get():
    pdf_dir = Path("library/pdfs")
    pdf_dir.mkdir(parents=True, exist_ok=True)
    pdfs = sorted(pdf_dir.glob("*.pdf"), key=os.path.getmtime, reverse=True)
    return [LibraryItem(p) for p in pdfs]

@rt("/download/{fname}")
def get(fname: str):
    return FileResponse(f"library/pdfs/{fname}")

serve()

import streamlit as st
from datetime import datetime
from backend import ChatBackend

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="ChatGPT",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Theme State (Dark / Light)
# ---------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

is_dark = (st.session_state.theme == "dark")

# Color Palettes
if is_dark:
    colors = {
        "bg_app": "#111113",
        "bg_sidebar": "#18181b",
        "bg_header": "#1f1f23",
        "bg_card": "#1e1e22",
        "bg_chat_user": "#27272a",
        "bg_chat_asst": "#18181b",
        "bg_expander": "#161618",
        "text_primary": "#f4f4f5",
        "text_secondary": "#a1a1aa",
        "text_muted": "#71717a",
        "border": "#2e2e34",
        "border_light": "rgba(255, 255, 255, 0.08)",
        "accent": "#3b82f6",
        "accent_hover": "#2563eb",
        "active_chat_bg": "#2a2a30",
        "input_bg": "#1e1e22",
        "badge_bg": "rgba(16, 185, 129, 0.15)",
        "badge_border": "rgba(16, 185, 129, 0.3)",
        "badge_text": "#34d399",
        "dot_color": "#10b981"
    }
else:
    colors = {
        "bg_app": "#f8fafc",
        "bg_sidebar": "#f1f5f9",
        "bg_header": "#ffffff",
        "bg_card": "#ffffff",
        "bg_chat_user": "#f1f5f9",
        "bg_chat_asst": "#ffffff",
        "bg_expander": "#f8fafc",
        "text_primary": "#0f172a",
        "text_secondary": "#475569",
        "text_muted": "#64748b",
        "border": "#e2e8f0",
        "border_light": "rgba(0, 0, 0, 0.06)",
        "accent": "#2563eb",
        "accent_hover": "#1d4ed8",
        "active_chat_bg": "#e2e8f0",
        "input_bg": "#ffffff",
        "badge_bg": "rgba(16, 185, 129, 0.12)",
        "badge_border": "rgba(16, 185, 129, 0.25)",
        "badge_text": "#059669",
        "dot_color": "#059669"
    }

# ---------------------------------------------------------
# Dynamic Modern CSS
# ---------------------------------------------------------
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}

    /* Hide standard deploy button for cleaner ChatGPT look */
    .stDeployButton {{
        display: none !important;
    }}

    /* Main background */
    .stApp {{
        background-color: {colors["bg_app"]} !important;
        color: {colors["text_primary"]} !important;
    }}

    /* Give ample top padding so header is NEVER clipped */
    .block-container {{
        padding-top: 4.5rem !important;
        padding-bottom: 5.5rem !important;
        max-width: 880px !important;
        margin: 0 auto !important;
    }}

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {{
        background-color: {colors["bg_sidebar"]} !important;
        border-right: 1px solid {colors["border"]} !important;
    }}
    
    section[data-testid="stSidebar"] div.block-container {{
        padding-top: 2rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }}

    /* Primary Buttons */
    div.stButton > button[kind="primary"] {{
        background: {colors["accent"]} !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: 1px solid {colors["accent_hover"]} !important;
        padding: 0.5rem 0.9rem !important;
        transition: all 0.2s ease !important;
    }}
    
    div.stButton > button[kind="primary"]:hover {{
        background: {colors["accent_hover"]} !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25) !important;
    }}

    /* Secondary / Default Buttons */
    div.stButton > button {{
        background-color: {colors["bg_card"]} !important;
        color: {colors["text_primary"]} !important;
        border: 1px solid {colors["border"]} !important;
        border-radius: 8px !important;
        transition: all 0.15s ease !important;
    }}

    div.stButton > button:hover {{
        border-color: {colors["accent"]} !important;
        color: {colors["accent"]} !important;
    }}

    /* Chat Session List Items in Sidebar */
    .chat-nav-btn > div.stButton > button {{
        text-align: left !important;
        justify-content: flex-start !important;
        background-color: transparent !important;
        border: 1px solid transparent !important;
        color: {colors["text_secondary"]} !important;
        font-size: 0.88rem !important;
        font-weight: 500 !important;
        padding: 0.45rem 0.65rem !important;
        width: 100% !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        border-radius: 8px !important;
    }}

    .chat-nav-btn > div.stButton > button:hover {{
        background-color: {colors["active_chat_bg"]} !important;
        color: {colors["text_primary"]} !important;
        border-color: {colors["border"]} !important;
    }}

    .active-nav-btn > div.stButton > button {{
        background-color: {colors["active_chat_bg"]} !important;
        border-left: 3px solid {colors["accent"]} !important;
        border-top: 1px solid {colors["border"]} !important;
        border-right: 1px solid {colors["border"]} !important;
        border-bottom: 1px solid {colors["border"]} !important;
        color: {colors["text_primary"]} !important;
        font-weight: 600 !important;
    }}

    .del-btn > div.stButton > button {{
        background-color: transparent !important;
        border: none !important;
        color: {colors["text_muted"]} !important;
        padding: 0.45rem 0.2rem !important;
    }}

    .del-btn > div.stButton > button:hover {{
        color: #ef4444 !important;
        background-color: {colors["active_chat_bg"]} !important;
        border-radius: 6px !important;
    }}

    /* Modern Top Header Card */
    .top-header-card {{
        background-color: {colors["bg_header"]};
        border: 1px solid {colors["border"]};
        border-radius: 14px;
        padding: 0.85rem 1.25rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 2px 8px {colors["border_light"]};
    }}

    .header-left {{
        display: flex;
        flex-direction: column;
        gap: 4px;
    }}

    .header-chat-title {{
        font-size: 1.2rem;
        font-weight: 700;
        color: {colors["text_primary"]};
        margin: 0;
        display: flex;
        align-items: center;
        gap: 8px;
    }}

    .header-chat-subtitle {{
        font-size: 0.8rem;
        color: {colors["text_secondary"]};
        margin: 0;
    }}

    .model-badge {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 0.76rem;
        font-weight: 600;
        color: {colors["badge_text"]};
        background-color: {colors["badge_bg"]};
        padding: 4px 12px;
        border-radius: 20px;
        border: 1px solid {colors["badge_border"]};
    }}
    
    .model-dot {{
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background-color: {colors["dot_color"]};
        box-shadow: 0 0 6px {colors["dot_color"]};
    }}

    /* Chat Messages Styling */
    [data-testid="stChatMessage"] {{
        background-color: {colors["bg_chat_asst"]} !important;
        border: 1px solid {colors["border"]} !important;
        border-radius: 12px !important;
        padding: 1rem 1.2rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 1px 4px {colors["border_light"]} !important;
    }}

    [data-testid="stChatMessage"] * {{
        color: {colors["text_primary"]} !important;
    }}

    /* Welcome Hero Section */
    .hero-box {{
        text-align: center;
        padding: 3rem 1rem 2rem 1rem;
    }}

    .hero-title {{
        font-size: 1.8rem;
        font-weight: 700;
        color: {colors["text_primary"]};
        margin-bottom: 0.4rem;
    }}

    .hero-subtitle {{
        font-size: 0.95rem;
        color: {colors["text_secondary"]};
        max-width: 500px;
        margin: 0 auto 2rem auto;
    }}

    /* Expanders for RAG context */
    div[data-testid="stExpander"] {{
        background-color: {colors["bg_expander"]} !important;
        border: 1px solid {colors["border"]} !important;
        border-radius: 10px !important;
        margin-top: 0.4rem !important;
        margin-bottom: 0.8rem !important;
    }}

    div[data-testid="stExpander"] summary {{
        color: {colors["text_secondary"]} !important;
        font-size: 0.85rem !important;
    }}

    /* Chat input styling */
    [data-testid="stChatInput"] {{
        background-color: {colors["input_bg"]} !important;
        border-color: {colors["border"]} !important;
    }}

    [data-testid="stChatInput"] textarea {{
        color: {colors["text_primary"]} !important;
    }}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Backend Initialization (Cached)
# ---------------------------------------------------------
@st.cache_resource(show_spinner="Initializing RAG Pipeline & Vector DB...")
def load_backend():
    return ChatBackend()

backend = load_backend()

# ---------------------------------------------------------
# Session State Setup
# ---------------------------------------------------------
if "current_session_id" not in st.session_state:
    existing_sessions = backend.list_sessions()
    if existing_sessions:
        st.session_state.current_session_id = existing_sessions[0]["id"]
    else:
        st.session_state.current_session_id = backend.create_session("New Chat")

if "messages" not in st.session_state:
    st.session_state.messages = backend.load_session_history(st.session_state.current_session_id)

if "retrieval_metadata" not in st.session_state:
    st.session_state.retrieval_metadata = {}

# ---------------------------------------------------------
# Sidebar: Controls, Theme Switcher & Chat History
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(f"<h3 style='margin-bottom: 0.2rem; font-weight: 700; color: {colors['text_primary']};'>ChatGPT</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 0.8rem; color: {colors['text_muted']}; margin-top: -6px; margin-bottom: 1rem;'>Local RAG Assistant • Ollama + Chroma</p>", unsafe_allow_html=True)

    # Top Controls: Theme Switcher & New Chat button
    col_theme, col_new = st.columns([0.45, 0.55])
    with col_theme:
        theme_label = "☀️ Light" if is_dark else "🌙 Dark"
        if st.button(theme_label, use_container_width=True, help="Toggle Light / Dark mode"):
            st.session_state.theme = "light" if is_dark else "dark"
            st.rerun()
            
    with col_new:
        if st.button("➕ New Chat", use_container_width=True, type="primary"):
            new_id = backend.create_session("New Chat")
            st.session_state.current_session_id = new_id
            st.session_state.messages = []
            st.rerun()

    st.markdown(f"<hr style='border: none; border-top: 1px solid {colors['border']}; margin: 1rem 0;'>", unsafe_allow_html=True)
    st.markdown(f"<p style='font-size: 0.74rem; font-weight: 700; color: {colors['text_muted']}; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.5rem;'>Previous Chats</p>", unsafe_allow_html=True)

    sessions = backend.list_sessions()
    
    for s in sessions:
        s_id = s["id"]
        title = s.get("title") or s_id
        is_active = (s_id == st.session_state.current_session_id)
        
        col_chat, col_del = st.columns([0.84, 0.16])
        
        with col_chat:
            button_label = f"💬 {title}"
            btn_key = f"sess_{s_id}"
            
            css_class = "active-nav-btn" if is_active else "chat-nav-btn"
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            if st.button(button_label, key=btn_key, use_container_width=True):
                st.session_state.current_session_id = s_id
                st.session_state.messages = backend.load_session_history(s_id)
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
            
        with col_del:
            st.markdown('<div class="del-btn">', unsafe_allow_html=True)
            if st.button("✕", key=f"del_{s_id}", help=f"Delete '{title}'"):
                backend.delete_session(s_id)
                remaining = backend.list_sessions()
                if remaining:
                    st.session_state.current_session_id = remaining[0]["id"]
                    st.session_state.messages = backend.load_session_history(remaining[0]["id"])
                else:
                    new_id = backend.create_session("New Chat")
                    st.session_state.current_session_id = new_id
                    st.session_state.messages = []
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"<hr style='border: none; border-top: 1px solid {colors['border']}; margin: 1.2rem 0;'>", unsafe_allow_html=True)
    
    # System Info card
    st.markdown(f"""
    <div style='background: {colors["bg_card"]}; padding: 0.85rem; border-radius: 10px; border: 1px solid {colors["border"]}; font-size: 0.78rem;'>
        <div style='display:flex; justify-content:space-between; margin-bottom:6px;'>
            <span style='color: {colors["text_muted"]};'>Model</span>
            <span style='color: {colors["text_primary"]}; font-weight:600;'>llama3.2:3b</span>
        </div>
        <div style='display:flex; justify-content:space-between; margin-bottom:6px;'>
            <span style='color: {colors["text_muted"]};'>Vector DB</span>
            <span style='color: {colors["text_primary"]}; font-weight:600;'>Chroma</span>
        </div>
        <div style='display:flex; justify-content:space-between;'>
            <span style='color: {colors["text_muted"]};'>Embeddings</span>
            <span style='color: {colors["text_primary"]}; font-weight:600;'>MiniLM-L6-v2</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Main Top Header Bar (High Visibility & Never Cut Off)
# ---------------------------------------------------------
current_meta = next((s for s in sessions if s["id"] == st.session_state.current_session_id), None)
current_title = current_meta["title"] if current_meta else "Chat"

col_header_left, col_header_right = st.columns([0.72, 0.28])

with col_header_left:
    st.markdown(f"""
    <div class="top-header-card">
        <div class="header-left">
            <h2 class="header-chat-title">💬 {current_title}</h2>
            <p class="header-chat-subtitle">Session: <code>{st.session_state.current_session_id}</code></p>
        </div>
        <div class="model-badge">
            <span class="model-dot"></span>
            <span>llama3.2:3b</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_header_right:
    # Rename button positioned cleanly aligned with header
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    with st.popover("✏️ Rename Chat", use_container_width=True):
        st.markdown(f"<p style='font-weight:600; font-size:0.9rem; color:{colors['text_primary']}; margin-bottom:4px;'>Edit Title</p>", unsafe_allow_html=True)
        new_title_input = st.text_input("Title", value=current_title, label_visibility="collapsed")
        if st.button("Save Changes", use_container_width=True, type="primary"):
            if new_title_input.strip():
                backend.update_session_title(st.session_state.current_session_id, new_title_input.strip())
                st.rerun()

# ---------------------------------------------------------
# Welcome Screen (when chat is empty)
# ---------------------------------------------------------
suggestion_clicked = None

if not st.session_state.messages:
    st.markdown(f"""
    <div class="hero-box">
        <div style="font-size: 2.8rem; margin-bottom: 0.6rem;">💬</div>
        <div class="hero-title">What can I help with today?</div>
        <div class="hero-subtitle">Ask questions, recall prior context, or test your Chroma vector memory.</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("👤 Who is Dangal and where does he live?", use_container_width=True):
            suggestion_clicked = "Who is Dangal and where does he live?"
        if st.button("🏢 Name the CEO of Google and his spouse", use_container_width=True):
            suggestion_clicked = "Name the CEO of Google and his spouse"
    with col2:
        if st.button("📍 Where do I live and who is my friend?", use_container_width=True):
            suggestion_clicked = "Where do I live and who is my friend?"
        if st.button("⚡ Give a short summary of my identity", use_container_width=True):
            suggestion_clicked = "Give a short summary of my identity"

# ---------------------------------------------------------
# Display Chat Messages
# ---------------------------------------------------------
for idx, msg in enumerate(st.session_state.messages):
    role = msg["role"]
    avatar = "👤" if role == "user" else "🤖"
    with st.chat_message(role, avatar=avatar):
        st.markdown(msg["content"])
        
        # Display retrieval drawer if metadata exists for this response
        meta_key = f"{st.session_state.current_session_id}_{idx}"
        if meta_key in st.session_state.retrieval_metadata:
            meta = st.session_state.retrieval_metadata[meta_key]
            with st.expander("🔍 Retrieved Memory & Standalone Query", expanded=False):
                st.markdown(f"**Standalone Query:** `{meta.get('standalone_question')}`")
                chunks = meta.get("chunks", [])
                if chunks:
                    st.markdown("**Chroma DB Context Chunks:**")
                    for c_idx, c in enumerate(chunks):
                        st.info(f"{c_idx+1}. {c}")
                else:
                    st.caption("No prior context chunks were retrieved.")

# ---------------------------------------------------------
# Chat Input & Response Handling
# ---------------------------------------------------------
user_input = st.chat_input("Message ChatGPT...")
prompt_to_process = suggestion_clicked or user_input

if prompt_to_process:
    # 1. Append user message to state
    st.session_state.messages.append({"role": "user", "content": prompt_to_process})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt_to_process)

    # 2. Assistant response preparation and streaming
    with st.chat_message("assistant", avatar="🤖"):
        standalone_q, chunks, stream_gen = backend.prepare_chat_turn(
            session_id=st.session_state.current_session_id,
            user_question=prompt_to_process,
            history_messages=st.session_state.messages[:-1]
        )
        
        # Stream response token by token
        response_text = st.write_stream(stream_gen)
        
        # Save retrieval metadata for this assistant response
        resp_idx = len(st.session_state.messages)
        meta_key = f"{st.session_state.current_session_id}_{resp_idx}"
        st.session_state.retrieval_metadata[meta_key] = {
            "standalone_question": standalone_q,
            "chunks": chunks
        }
        
        # Expandable drawer
        with st.expander("🔍 Retrieved Memory & Standalone Query", expanded=False):
            st.markdown(f"**Standalone Query:** `{standalone_q}`")
            if chunks:
                st.markdown("**Chroma DB Context Chunks:**")
                for c_idx, c in enumerate(chunks):
                    st.info(f"{c_idx+1}. {c}")
            else:
                st.caption("No prior context chunks were retrieved.")

    # 3. Append assistant response to messages state
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    
    # Rerun to refresh sidebar and titles
    st.rerun()

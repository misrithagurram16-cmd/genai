from groq import Groq
import streamlit as st
import os
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi
import re

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.set_page_config(page_title="YouTube Summarizer", page_icon="▶️", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; background: #0f0f0f; }
.stApp { background: #0f0f0f; }
#MainMenu, footer, header { visibility: hidden; }

.top-bar {
    text-align: center;
    padding: 32px 0 28px;
    margin-bottom: 28px;
}
.logo {
    font-size: 26px;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.5px;
}
.logo span { color: #ff0000; }

.card {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 16px;
}
.card-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #666;
    margin-bottom: 10px;
}
.card-title {
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 12px;
    line-height: 1.3;
}
.card-text {
    font-size: 14px;
    color: #aaaaaa;
    line-height: 1.8;
}
.card-text ul { padding-left: 20px; margin: 0; }
.card-text li { margin-bottom: 8px; color: #aaaaaa; }

.stat-row { display: flex; gap: 10px; margin: 16px 0; flex-wrap: wrap; }
.stat-pill {
    background: #1a1a1a;
    border: 1px solid #2a2a2a;
    border-radius: 100px;
    padding: 6px 14px;
    font-size: 13px;
    color: #aaaaaa;
    font-weight: 500;
}

div[data-testid="stTextInput"] input {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-size: 15px !important;
    padding: 14px 18px !important;
    font-family: 'Inter', sans-serif !important;
}
div[data-testid="stTextInput"] input::placeholder { color: #555 !important; }
div[data-testid="stTextInput"] input:focus {
    border-color: #ff0000 !important;
    box-shadow: 0 0 0 3px rgba(255,0,0,0.1) !important;
}

div[data-testid="stSelectbox"] > div {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 10px !important;
    color: #ffffff !important;
}

.stButton > button {
    background: #ff0000 !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 24px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    width: 100% !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover { background: #cc0000 !important; }

.stDownloadButton > button {
    background: #1a1a1a !important;
    color: #aaaaaa !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 10px !important;
    width: 100% !important;
}

.stChatMessage { background: #1a1a1a !important; border-radius: 12px !important; }
.stStatus {
    background: #1a1a1a !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 12px !important;
}

label { color: #aaaaaa !important; font-size: 13px !important; }
h1, h2, h3 { color: #ffffff !important; }
p { color: #aaaaaa !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="top-bar">
    <div class="logo">▶<span>YouTube</span> Summarizer</div>
</div>
""", unsafe_allow_html=True)

def get_video_id(url):
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_transcript(video_id):
    from youtube_transcript_api import YouTubeTranscriptApi
    ytt_api = YouTubeTranscriptApi()
    fetched = ytt_api.fetch(video_id)
    return " ".join([snippet.text for snippet in fetched])
def summarize(transcript, style):
    style_map = {
        "Concise": "Be very concise. Keep each section short.",
        "Detailed": "Be thorough and detailed in each section.",
        "Bullet Points": "Use bullet points everywhere possible."
    }

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"""You are an expert video summarizer. {style_map[style]}

Analyze this transcript and return a JSON object:
{{
  "title": "video topic title",
  "summary": "2-3 sentence overview",
  "key_points": ["point 1", "point 2", "point 3", "point 4", "point 5"],
  "highlights": ["highlight 1", "highlight 2", "highlight 3"],
  "takeaways": "what the viewer should take away from this video",
  "word_count": {len(transcript.split())}
}}

Return ONLY raw JSON, no backticks."""},
            {"role": "user", "content": f"Transcript:\n{transcript[:8000]}"}
        ]
    )
    import json
    text = response.choices[0].message.content.strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])

# UI
url = st.text_input("", placeholder="Paste YouTube URL here...", label_visibility="collapsed")

c1, c2 = st.columns(2)
with c1:
    style = st.selectbox("Summary Style", ["Concise", "Detailed", "Bullet Points"])
with c2:
    show_chat = st.checkbox("Enable Q&A chat after summary", value=True)

summarize_btn = st.button("▶ Summarize Video")

if "transcript" not in st.session_state:
    st.session_state.transcript = None
if "summary_data" not in st.session_state:
    st.session_state.summary_data = None
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

if summarize_btn and url:
    video_id = get_video_id(url)
    if not video_id:
        st.error("Invalid YouTube URL!")
    else:
        with st.status("Processing video...", expanded=True) as status:
            st.write("📥 Fetching transcript...")
            try:
                transcript = get_transcript(video_id)
                st.session_state.transcript = transcript
                word_count = len(transcript.split())
                st.write(f"✅ Got transcript — {word_count} words")

                st.write("🧠 Analyzing video...")
                data = summarize(transcript, style)
                st.session_state.summary_data = data
                st.session_state.chat_messages = []
                status.update(label="✅ Done!", state="complete")
            except Exception as e:
                st.error(f"Error: {str(e)} — Video may not have captions.")

if st.session_state.summary_data:
    import time
    data = st.session_state.summary_data

    # Stats
    st.markdown(f"""
    <div class="stat-row">
        <span class="stat-pill">📝 {data.get('word_count', '?')} words</span>
        <span class="stat-pill">🎯 {len(data.get('key_points', []))} key points</span>
        <span class="stat-pill">✨ {style} style</span>
    </div>
    """, unsafe_allow_html=True)

    # Cards
    # Magazine layout - big on left, small stacked on right
    left_col, right_col = st.columns([3, 2])

    with left_col:
        time.sleep(0.2)
        points_html = "".join([f"<li>{p}</li>" for p in data.get('key_points', [])])
        st.markdown(f"""
        <div class="card" style="height: 100%;">
            <div class="card-label">📌 Video Topic</div>
            <div class="card-title">{data.get('title', 'Video Summary')}</div>
            <div class="card-label" style="margin-top:16px;">⚡ Summary</div>
            <div class="card-text" style="margin-bottom:16px;">{data.get('summary', '')}</div>
            <div class="card-label">🔑 Key Points</div>
            <div class="card-text"><ul>{points_html}</ul></div>
        </div>
        """, unsafe_allow_html=True)

    with right_col:
        time.sleep(0.2)
        highlights_html = "".join([f"<li>{h}</li>" for h in data.get('highlights', [])])
        st.markdown(f"""
        <div class="card">
            <div class="card-label">✨ Highlights</div>
            <div class="card-text"><ul>{highlights_html}</ul></div>
        </div>
        """, unsafe_allow_html=True)

        time.sleep(0.2)
        st.markdown(f"""
        <div class="card">
            <div class="card-label">🎯 Key Takeaway</div>
            <div class="card-text">{data.get('takeaways', '')}</div>
        </div>
        """, unsafe_allow_html=True)

        time.sleep(0.2)
        st.markdown(f"""
        <div class="card">
            <div class="card-label">📊 Stats</div>
            <div class="card-text">
                <p>📝 {data.get('word_count', '?')} words in transcript</p>
                <p>🎯 {len(data.get('key_points', []))} key points found</p>
                <p>✨ {style} summary style</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
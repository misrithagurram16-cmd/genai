from groq import Groq
import streamlit as st
import os
import time
import json
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

st.set_page_config(page_title="Research.ai", page_icon="🔍", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #fafafa;
}
.stApp { background: #fafafa; }
#MainMenu, footer, header {visibility: hidden;}

.top-bar {
    text-align: center;
    padding: 28px 0 24px;
    border-bottom: 1px solid #dbdbdb;
    margin-bottom: 32px;
}
.logo {
    font-size: 24px;
    font-weight: 700;
    color: #000;
    letter-spacing: -0.5px;
}
.logo span {
    background: linear-gradient(45deg, #833ab4, #fd1d1d, #fcb045);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.section-card {
    background: #ffffff;
    border: 1px solid #dbdbdb;
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 16px;
    animation: fadeSlideUp 0.4s ease forwards;
    opacity: 0;
    transform: translateY(16px);
}
@keyframes fadeSlideUp {
    to { opacity: 1; transform: translateY(0); }
}

.card-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #8e8e8e;
    margin-bottom: 10px;
}
.card-title {
    font-size: 20px;
    font-weight: 700;
    color: #000000;
    margin-bottom: 14px;
    line-height: 1.3;
}
.card-text {
    font-size: 14px;
    color: #262626;
    line-height: 1.8;
}
.card-text ul {
    padding-left: 20px;
    margin: 0;
}
.card-text li {
    margin-bottom: 8px;
    color: #262626;
}

.card-icon {
    font-size: 28px;
    margin-bottom: 12px;
}

.stat-row {
    display: flex;
    gap: 10px;
    margin: 16px 0;
    flex-wrap: wrap;
}
.stat-pill {
    background: #ffffff;
    border: 1px solid #dbdbdb;
    border-radius: 100px;
    padding: 6px 14px;
    font-size: 13px;
    color: #262626;
    font-weight: 500;
}

div[data-testid="stTextInput"] input {
    background: #ffffff !important;
    border: 1px solid #dbdbdb !important;
    border-radius: 12px !important;
    color: #262626 !important;
    font-size: 15px !important;
    padding: 14px 18px !important;
    font-family: 'Inter', sans-serif !important;
}
div[data-testid="stTextInput"] input::placeholder { color: #8e8e8e !important; }
div[data-testid="stTextInput"] input:focus {
    border-color: #833ab4 !important;
    box-shadow: 0 0 0 3px rgba(131,58,180,0.1) !important;
}

div[data-testid="stSelectbox"] > div {
    background: #ffffff !important;
    border: 1px solid #dbdbdb !important;
    border-radius: 10px !important;
    color: #262626 !important;
    font-size: 14px !important;
}

.stButton > button {
    background: linear-gradient(45deg, #833ab4, #fd1d1d, #fcb045) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px 24px !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    width: 100% !important;
    font-family: 'Inter', sans-serif !important;
}
.stButton > button:hover { opacity: 0.92 !important; }

.stDownloadButton > button {
    background: #ffffff !important;
    color: #262626 !important;
    border: 1px solid #dbdbdb !important;
    border-radius: 10px !important;
    font-size: 14px !important;
    width: 100% !important;
}

.stStatus {
    background: #ffffff !important;
    border: 1px solid #dbdbdb !important;
    border-radius: 12px !important;
}

label { color: #262626 !important; font-size: 13px !important; font-weight: 500 !important; }
h1, h2, h3 { color: #000 !important; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="top-bar">
    <div class="logo">research<span>.ai</span></div>
</div>
""", unsafe_allow_html=True)

def search_web(query):
    results = tavily.search(query=query, max_results=5)
    return results['results']

def get_report_json(topic, context, style):
    style_instruction = {
        "Professional": "formal and analytical",
        "Simple": "simple and easy to understand",
        "Technical": "technical and detailed for engineers"
    }[style]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": f"""You are a research analyst. Write in a {style_instruction} tone.

Return ONLY a valid JSON object. No markdown, no backticks, no explanation. Just raw JSON.

{{
  "title": "report title here",
  "summary": "2-3 sentence executive summary here",
  "findings": ["finding 1", "finding 2", "finding 3", "finding 4", "finding 5"],
  "analysis": "paragraph 1 here. paragraph 2 here. paragraph 3 here.",
  "trends": "paragraph 1 here. paragraph 2 here.",
  "conclusion": "conclusion paragraph here.",
  "sources": ["url1", "url2", "url3"]
}}"""},
            {"role": "user", "content": f"Topic: {topic}\n\nSources:\n{context}"}
        ]
    )
    text = response.choices[0].message.content.strip()

    # Clean up any markdown formatting
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                text = part
                break

    # Find JSON object
    start = text.find("{")
    end = text.rfind("}") + 1
    if start != -1 and end > start:
        text = text[start:end]

    return json.loads(text)
# Search form
topic = st.text_input("", placeholder="What do you want to research?", label_visibility="collapsed")

c1, c2 = st.columns(2)
with c1:
    depth = st.selectbox("Depth", ["Quick", "Standard", "Deep"])
with c2:
    style = st.selectbox("Style", ["Professional", "Simple", "Technical"])

search_btn = st.button("Research →")

if search_btn:
    if not topic:
        st.warning("Enter a topic first!")
    else:
        with st.status("Researching...", expanded=True) as status:
            st.write("🌐 Searching the web...")
            results = search_web(topic)
            st.write(f"✅ {len(results)} sources found")

            all_results = results
            if depth != "Quick":
                st.write("🔍 Going deeper...")
                results2 = search_web(f"{topic} latest 2026")
                all_results += results2

            if depth == "Deep":
                st.write("🔬 Deep analysis...")
                results3 = search_web(f"{topic} expert analysis")
                all_results += results3

            context = "\n\n".join([
                f"Source: {r['url']}\nTitle: {r['title']}\nContent: {r['content']}"
                for r in all_results[:8]
            ])

            st.write("✍️ Writing report...")
            try:
                data = get_report_json(topic, context, style)
            except:
                st.error("JSON parse failed — retrying...")
                data = get_report_json(topic, context, style)

            status.update(label="✅ Done!", state="complete")

        # Stats row
        st.markdown(f"""
        <div class="stat-row">
            <span class="stat-pill">📚 {len(all_results[:8])} sources</span>
            <span class="stat-pill">🔍 {depth}</span>
            <span class="stat-pill">✍️ {style}</span>
        </div>
        """, unsafe_allow_html=True)

        # Cards revealed one by one
        cards = [
            ("📌", "Title", "card-title", data.get("title", topic)),
            ("⚡", "Executive Summary", "summary", data.get("summary", "")),
            ("🔑", "Key Findings", "findings", data.get("findings", [])),
            ("🔬", "Detailed Analysis", "analysis", data.get("analysis", "")),
            ("📈", "Current Trends", "trends", data.get("trends", "")),
            ("✅", "Conclusion", "conclusion", data.get("conclusion", "")),
        ]

        full_report = f"# {data.get('title', topic)}\n\n"

        for icon, label, key, content in cards:
            time.sleep(0.3)  # animate delay

            if key == "card-title":
                st.markdown(f"""
                <div class="section-card">
                    <div class="card-icon">{icon}</div>
                    <div class="card-label">Research Report</div>
                    <div class="card-title">{content}</div>
                </div>
                """, unsafe_allow_html=True)
                full_report += f"## {content}\n\n"

            elif key == "findings":
                bullets = "".join([f"<li>{f}</li>" for f in content])
                plain = "\n".join([f"- {f}" for f in content])
                st.markdown(f"""
                <div class="section-card">
                    <div class="card-label">{icon} {label}</div>
                    <div class="card-text"><ul>{bullets}</ul></div>
                </div>
                """, unsafe_allow_html=True)
                full_report += f"## {label}\n{plain}\n\n"

            else:
                paragraphs = "".join([f"<p>{p}</p>" for p in content.split("\n") if p.strip()])
                st.markdown(f"""
                <div class="section-card">
                    <div class="card-label">{icon} {label}</div>
                    <div class="card-text">{paragraphs}</div>
                </div>
                """, unsafe_allow_html=True)
                full_report += f"## {label}\n{content}\n\n"

        # Sources card
        time.sleep(0.3)
        sources = data.get("sources", [r['url'] for r in all_results[:5]])
        source_html = "".join([f'<p style="margin:6px 0; font-size:13px;"><a href="{s}" style="color:#833ab4; text-decoration:none;">{s[:60]}...</a></p>' for s in sources[:5]])
        st.markdown(f"""
        <div class="section-card">
            <div class="card-label">🔗 Sources</div>
            <div class="card-text">{source_html}</div>
        </div>
        """, unsafe_allow_html=True)

        # Download
        st.download_button(
            "📥 Download Report",
            full_report,
            file_name=f"research_{topic[:20].replace(' ','_')}.md",
            mime="text/markdown"
        )
import streamlit as st
import pandas as pd
from openai import OpenAI
import requests
import time
from streamlit_lottie import st_lottie
import base64
import os

# --- 1. PAGE CONFIGURATION & FULL VIEWPORT CSS ---
st.set_page_config(
    page_title="NA Pharma Care AI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
div[data-testid="stAppViewBlockContainer"] {
    padding: 0px !important;
    max-width: 100% !important;
}
div[data-testid="stSidebar"] > div:first-child {
    padding-top: 0px !important;
}
header {visibility: hidden !important;}
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}

html, body, [data-testid="stAppViewContainer"] {
    background-color: #020617 !important;
    height: 100dvh !important;
    overflow-x: hidden !important;
}

[data-testid="column"] {
    width: auto !important;
    flex: 1 1 0% !important;
    min-width: 0px !important;
}
</style>
""", unsafe_allow_html=True)


# --- 2. THEME & CHAT ALIGNMENT STYLING ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
    color: #f8fafc;
}
.stApp {
    background: radial-gradient(circle at top left, #1e293b, #0f172a, #020617);
    background-attachment: fixed;
}

@media (max-width: 768px) {
    #dynamic-notch {
        position: fixed;
        top: 6px;
        left: 50%;
        transform: translateX(-50%);
        width: 140px;
        height: 28px;
        background-color: #020617;
        border-radius: 50px;
        box-shadow: 0 0 15px rgba(16, 185, 129, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
        z-index: 9999;
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    #notch-glow {
        position: fixed;
        top: 0px;
        left: 50%;
        transform: translateX(-50%);
        width: 160px;
        height: 8px;
        background: radial-gradient(circle at top, #10b981 0%, transparent 70%);
        filter: blur(10px);
        opacity: 0.8;
        z-index: 9998;
    }
}
@media (min-width: 769px) {
    #dynamic-notch { display: none; }
    #notch-glow { display: none; }
}

.glass-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 16px;
    padding: 15px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    text-align: center;
}

.text-muted { color: #94a3b8; font-size: 0.82rem; }
.card-value { font-size: 1.8rem; font-weight: 700; margin: 4px 0; color: #f8fafc; }
.status-badge {
    display: inline-flex;
    align-items: center;
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
    padding: 4px 12px;
    border-radius: 50px;
    font-size: 0.78rem;
    font-weight: 600;
    border: 1px solid rgba(16, 185, 129, 0.2);
    margin-bottom: 10px;
}
.pulse {
    width: 6px; height: 6px;
    background-color: #10b981;
    border-radius: 50%;
    margin-right: 6px;
    box-shadow: 0 0 8px #10b981;
    animation: pulse-animation 2s infinite;
}
@keyframes pulse-animation {
    0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.3); }
    70% { box-shadow: 0 0 0 6px rgba(16, 185, 129, 0); }
    100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

[data-testid="stChatMessage"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin-bottom: 20px !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    flex-direction: row !important;
}

[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    flex-direction: row-reverse !important;
    text-align: right !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: linear-gradient(145deg, rgba(59, 130, 246, 0.25), rgba(29, 78, 216, 0.35)) !important;
    border: 1px solid rgba(59, 130, 246, 0.3) !important;
}

[data-testid="stChatMessageContent"] {
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.9)) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 18px !important;
    padding: 14px 18px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2) !important;
    backdrop-filter: blur(12px) !important;
    color: #f8fafc !important;
    max-width: 85% !important;
}

[data-testid="stChatMessageContent"] div p {
    font-size: 0.95rem !important;
    line-height: 1.4 !important;
    margin-bottom: 0px !important;
}

/* Compact File Uploader Styling */
[data-testid="stFileUploader"] {
    max-width: 220px !important;
}
[data-testid="stFileUploader"] section {
    padding: 4px 10px !important;
    background: rgba(59, 130, 246, 0.1) !important;
    border: 1px dashed rgba(59, 130, 246, 0.4) !important;
    border-radius: 10px !important;
}
[data-testid="stFileUploader"] section button {
    background: linear-gradient(135deg, #3b82f6, #1d4ed8) !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    padding: 2px 10px !important;
    font-size: 0.85rem !important;
}
</style>
""", unsafe_allow_html=True)

# --- 3. ANIMATION LOADER & STREAM CLEANER ---
@st.cache_data
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None

def generate_cleaned_content(response):
    text_buffer = ""
    inside_think = False
    for chunk in response:
        content = chunk.choices[0].delta.content
        if not content:
            continue
        text_buffer += content
        
        while True:
            if not inside_think:
                if "<think>" in text_buffer:
                    parts = text_buffer.split("<think>", 1)
                    if parts[0]:
                        yield parts[0]
                    text_buffer = parts[1]
                    inside_think = True
                else:
                    if len(text_buffer) > 10:
                        yield text_buffer[:-10]
                        text_buffer = text_buffer[-10:]
                    break
            else:
                if "</think>" in text_buffer:
                    parts = text_buffer.split("</think>", 1)
                    text_buffer = parts[1]
                    inside_think = False
                else:
                    if len(text_buffer) > 10:
                        text_buffer = text_buffer[-10:]
                    break
    if text_buffer and not inside_think:
        yield text_buffer

lottie_pulse = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_jcikwtux.json")

if 'splash_shown' not in st.session_state:
    st.session_state.splash_shown = False

if not st.session_state.splash_shown:
    splash_placeholder = st.empty()
    with splash_placeholder.container():
        st.markdown("<div style='position: fixed; top:0; left:0; width:100vw; height:100dvh; background-color: #0f172a; z-index: 10000; display:flex; flex-direction:column; align-items:center; justify-content:center;'>", unsafe_allow_html=True)
        if lottie_pulse:
            st_lottie(lottie_pulse, height=130, key="splash_lottie")
        st.markdown("<h1 style='color: #10b981; font-weight: 700; margin-top:15px; font-size:1.8rem;'>NAPC AI</h1></div>", unsafe_allow_html=True)
    time.sleep(1.5)
    splash_placeholder.empty()
    st.session_state.splash_shown = True

st.markdown("""
<div id="notch-glow"></div>
<div id="dynamic-notch">SYS: LIVE</div>
""", unsafe_allow_html=True)

# --- 4. DATA LOADER ---
EXCEL_FILE = "inventory.xlsx"
api_key = st.secrets.get("GROQ_API_KEY")

@st.cache_data
def load_inventory_data():
    if not os.path.exists(EXCEL_FILE):
        return None, None
    try:
        df_master = pd.read_excel(EXCEL_FILE, sheet_name='Full Master Medicine List', header=3)
        df_symptom = pd.read_excel(EXCEL_FILE, sheet_name='Quick Symptom & Keyword Index', header=3)
        return df_master, df_symptom
    except Exception:
        return None, None

df_master, df_symptom = load_inventory_data()
total_medicines = len(df_master) if df_master is not None else 0
total_categories = len(df_symptom) if df_symptom is not None else 0

# --- 5. DASHBOARD HEADER ---
st.markdown("<div style='margin-top: 35px;'></div>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 5px 0;">
    <div class="status-badge"><span class="pulse"></span> System Connected</div>
    <h1 style="margin:0; font-size: 2.2rem; font-weight: 700; background: linear-gradient(90deg, #10b981, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">💊 NA Pharma Care AI</h1>
    <p style="color: #94a3b8; font-size: 0.9rem; margin-top: 2px;">Smart Internal Pharmacy Assistant</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="glass-card"><p class="text-muted" style="margin:0; text-transform:uppercase; font-size:0.75rem;">📦 Medicines</p><p class="card-value">{total_medicines}</p></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="glass-card"><p class="text-muted" style="margin:0; text-transform:uppercase; font-size:0.75rem;">📚 Categories</p><p class="card-value">{total_categories}</p></div>', unsafe_allow_html=True)
with col3:
    st.markdown('<div class="glass-card"><p class="text-muted" style="margin:0; text-transform:uppercase; font-size:0.75rem;">🤖 AI Status</p><p class="card-value" style="color:#10b981; font-size:1.5rem;">LIVE</p></div>', unsafe_allow_html=True)
with col4:
    st.markdown("<div style='display:flex; justify-content:center; align-items:center; height:100%;' class='glass-card'>", unsafe_allow_html=True)
    if lottie_pulse:
        st_lottie(lottie_pulse, height=45, key="live_pulse")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. TABS NAVIGATION ---
tab1, tab2, tab3 = st.tabs(["🤖 AI Assistant", "📚 Database", "🧾 Bill Calculator"])

# --- TAB 1: AI ASSISTANT ---
with tab1:
    if not api_key:
        st.error("⚠️ GROQ_API_KEY is missing in Streamlit secrets.")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        if "file_uploader_key" not in st.session_state:
            st.session_state.file_uploader_key = 0

        st.markdown("<h5 style='color: #e2e8f0; font-weight: 500; margin-bottom:8px; font-size:0.95rem;'>⚡ Counter Lookup</h5>", unsafe_allow_html=True)
        q1, q2, q3, q4, q5 = st.columns(5)
        
        selected_prompt = None
        if q1.button("🩹 Pain", use_container_width=True): selected_prompt = "Quick check: pain relief medicines in stock."
        if q2.button("🤒 Fever", use_container_width=True): selected_prompt = "Quick check: fever medications."
        if q3.button("🤧 Cold", use_container_width=True): selected_prompt = "Quick check: cold and flu stock."
        if q4.button("💊 Antibiotic", use_container_width=True): selected_prompt = "Quick check: antibiotics list."
        if q5.button("🧹 Clear", use_container_width=True): 
            st.session_state.messages = []
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Compact Upload Button
        uploaded_img = st.file_uploader("➕ Upload Image", type=["jpg", "png", "jpeg"], key=f"file_uploader_{st.session_state.file_uploader_key}")

        chat_container = st.container(height=400)
        with chat_container:
            if not st.session_state.messages:
                st.markdown("""
                <div style='text-align:center; padding: 30px; color:#94a3b8; font-size: 0.85rem;'>
                    <h4 style='color:#e2e8f0; font-weight: 500; font-size:1rem;'>Search medicine, generic, or upload image...</h4>
                    <p>Uses of Panadol • Alternative to Brufen</p>
                </div>
                """, unsafe_allow_html=True)
                
            for message in st.session_state.messages:
                avatar_icon = "👨‍⚕️" if message["role"] == "assistant" else "😿"
                with st.chat_message(message["role"], avatar=avatar_icon):
                    st.markdown(message["content"])

        user_input = st.chat_input("Ask AI...")
        
        prompt = selected_prompt or user_input

        image_bytes = None
        if uploaded_img is not None:
            image_bytes = uploaded_img.getvalue()
            if not prompt:
                prompt = "Please analyze this uploaded medicine or prescription image and provide full inventory details."

        if prompt or image_bytes:
            display_prompt = prompt if prompt else "📷 [Uploaded Medicine Image]"
            st.session_state.messages.append({"role": "user", "content": display_prompt})
            
            with chat_container:
                with st.chat_message("user", avatar="😿"):
                    st.markdown(display_prompt)
                    if uploaded_img is not None:
                        st.image(uploaded_img, width=200)

                with st.chat_message("assistant", avatar="👨‍⚕️"):
                    with st.spinner("👨‍⚕️ Analyzing database & image..."):
                        try:
                            q = prompt.lower().strip() if prompt else ""
                            context = "--- DATABASE SCAN RESULTS ---\n"
                            
                            if df_master is not None and q:
                                master_matches = df_master[df_master.apply(lambda row: row.astype(str).str.lower().str.contains(q, na=False).any(), axis=1)]
                                context += master_matches.head(10).to_string(index=False) if not master_matches.empty else "No exact matches found in master list."

                            system_instruction = """
                            You are NA Pharma Care AI V3, the direct, internal pharmacy assistant led by a professional doctor persona.

                            STRICT RESPONSE FORMAT (DO NOT USE TABLES OR CODE BLOCKS). Whenever you suggest a medicine, format it EXACTLY like this:

                            **💊 [Brand Name]**  
                            🔬 *Generic: [Salt Name]*  
                            📝 *Categories: [Primary Categories]*  
                            ---
                            🔹 **Uses:** [Primary uses, short]  
                            🔹 **Dosage:** [Standard dosage, short]  
                            ⚠️ **Warnings:** [Key precaution, short]  
                            🔄 **Alternatives:** [List max 2 alternative brands sharing salt]  
                            ---
                            Be concise, focus on immediate counter-lookup needs, and output minimal text.
                            """

                            messages_payload = [{"role": "system", "content": system_instruction}]
                            for m in st.session_state.messages:
                                if "📷" not in m["content"]:
                                    messages_payload.append({"role": m["role"], "content": m["content"]})

                            if image_bytes is not None:
                                base64_image = base64.b64encode(image_bytes).decode('utf-8')
                                messages_payload.append({
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": prompt if prompt else "Analyze this image"},
                                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                                    ]
                                })
                                response = client.chat.completions.create(
                                    model="qwen/qwen3.6-27b",
                                    messages=messages_payload,
                                    stream=True
                                )
                            else:
                                response = client.chat.completions.create(
                                    model="llama-3.1-8b-instant",
                                    messages=messages_payload,
                                    stream=True
                                )
                            
                            answer = st.write_stream(generate_cleaned_content(response))
                            st.session_state.messages.append({"role": "assistant", "content": answer})
                        
                        except Exception as e:
                            st.error(f"Processing Error: {e}")

            # Automatically clear the uploaded photo after processing
            if uploaded_img is not None:
                st.session_state.file_uploader_key += 1
                st.rerun()

# --- TAB 2: INVENTORY DATABASE ---
with tab2:
    if df_master is not None:
        st.markdown("<h3 style='color: #f8fafc; margin-bottom:10px; font-size:1.2rem;'>📦 Master Database Scan</h3>", unsafe_allow_html=True)
        search_term = st.text_input("🔍 Filter database instantly...", "")
        if search_term:
            filtered_df = df_master[df_master.apply(lambda row: row.astype(str).str.lower().str.contains(search_term.lower(), na=False).any(), axis=1)]
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(df_master, use_container_width=True)
    else:
        st.info("ℹ️ inventory.xlsx not found in the directory. Please upload your master database file.")

# --- TAB 3: BILL CALCULATOR ---
with tab3:
    st.markdown("<h3 style='color: #f8fafc; margin-bottom:10px; font-size:1.2rem;'>🧾 Bill Estimator</h3>", unsafe_allow_html=True)
    if df_master is not None and "Brand Name" in df_master.columns:
        medicine_list = df_master["Brand Name"].dropna().tolist()
        selected_meds = st.multiselect("Select Medicines:", medicine_list)
        
        if selected_meds:
            total_amount = 0.0
            for med in selected_meds:
                col_n, col_p, col_q = st.columns([2, 1, 1])
                with col_n: st.markdown(f"<p style='margin-top:10px; font-weight:600; font-size:0.9rem;'>{med}</p>", unsafe_allow_html=True)
                with col_p: price = st.number_input(f"Price", min_value=0.0, value=100.0, step=10.0, key=f"p_{med}")
                with col_q: qty = st.number_input(f"Qty", min_value=1, value=1, step=1, key=f"q_{med}")
                total_amount += (price * qty)
            
            st.markdown("<br><hr style='border-color: #334155;'>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color: #10b981; font-weight:700; font-size:1.5rem;'>Grand Total: Rs. {total_amount:,.2f}</h2>", unsafe_allow_html=True)
    else:
        st.info("ℹ️ Load inventory database to use bill calculator.")

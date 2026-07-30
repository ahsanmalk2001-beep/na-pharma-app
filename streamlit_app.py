import streamlit as st
import pandas as pd
from openai import OpenAI
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NA Pharma Care",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. DYNAMIC ISLAND, ANIMATIONS & PREMIUM CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* Base Theme & Live Ambient Background */
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
    color: #f8fafc;
}
.stApp {
    background: radial-gradient(circle at 50% 0%, #1e293b, #020617);
    background-attachment: fixed;
    animation: ambientBreathe 10s ease-in-out infinite alternate;
}
@keyframes ambientBreathe {
    0% { background: radial-gradient(circle at 50% 0%, #0f172a, #020617); }
    100% { background: radial-gradient(circle at 50% 10%, #1e293b, #020617); }
}

/* 📱 DYNAMIC ISLAND (iOS NOTCH INTEGRATION) */
.dynamic-island {
    position: fixed;
    top: max(15px, env(safe-area-inset-top));
    left: 50%;
    transform: translateX(-50%);
    background: #000000;
    color: #10b981;
    padding: 8px 24px;
    border-radius: 40px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 1px;
    z-index: 999999;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.8), 0 0 15px rgba(16, 185, 129, 0.2);
    border: 1px solid rgba(16, 185, 129, 0.2);
    animation: islandBreathe 3s ease-in-out infinite alternate;
    backdrop-filter: blur(10px);
}
@keyframes islandBreathe {
    0% { width: 140px; box-shadow: 0 0 10px rgba(16, 185, 129, 0.1); }
    100% { width: 155px; box-shadow: 0 0 25px rgba(16, 185, 129, 0.4); }
}
.island-dot {
    width: 6px; height: 6px;
    background-color: #10b981;
    border-radius: 50%;
    animation: blink 1.5s infinite;
}
@keyframes blink { 0%, 100% {opacity: 1;} 50% {opacity: 0.3;} }

/* Glassmorphism Cards */
.glass-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    text-align: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.glass-card:active {
    transform: scale(0.95);
}
.card-value { font-size: 2rem; font-weight: 700; margin: 5px 0; color: #f8fafc; }

/* Custom Chat Bubbles - Mobile Optimized */
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 18px;
    padding: 15px;
    margin-bottom: 12px;
    font-size: 0.95rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #10b981, #3b82f6) !important;
}

/* UI Hiding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>

<!-- THE DYNAMIC ISLAND HTML -->
<div class="dynamic-island">
    <div class="island-dot"></div> AI ACTIVE
</div>
""", unsafe_allow_html=True)

# --- 3. SPLASH SCREEN ANIMATION ---
if 'splash_shown' not in st.session_state:
    st.session_state.splash_shown = False

if not st.session_state.splash_shown:
    splash = st.empty()
    with splash.container():
        st.markdown('''
        <style>
        .splash-screen {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background: #020617;
            z-index: 9999999;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .splash-logo {
            font-size: 4rem;
            animation: floatLogo 2s ease-in-out infinite, glow 2s alternate infinite;
        }
        .splash-text {
            font-family: 'Poppins', sans-serif;
            font-size: 1.5rem;
            font-weight: 700;
            color: #10b981;
            margin-top: 20px;
            letter-spacing: 4px;
            animation: fadeInOut 2.5s ease-in-out forwards;
        }
        @keyframes floatLogo { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-15px); } }
        @keyframes glow { from { text-shadow: 0 0 10px #10b981; } to { text-shadow: 0 0 30px #10b981, 0 0 40px #3b82f6; } }
        </style>
        <div class="splash-screen">
            <div class="splash-logo">💊</div>
            <div class="splash-text">PHARMA AI</div>
        </div>
        ''', unsafe_allow_html=True)
    time.sleep(2.5) # Splash screen stays for 2.5 seconds
    splash.empty()
    st.session_state.splash_shown = True

# --- 4. DATA LOADER ---
EXCEL_FILE = "inventory.xlsx"
api_key = st.secrets.get("GROQ_API_KEY")

@st.cache_data
def load_inventory_data():
    try:
        df_master = pd.read_excel(EXCEL_FILE, sheet_name='Full Master Medicine List', header=3)
        return df_master
    except Exception as e:
        return None

df_master = load_inventory_data()
total_medicines = len(df_master) if df_master is not None else 0

# --- 5. DASHBOARD ---
st.markdown("<br><br>", unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    <div class="glass-card">
        <p style="margin:0; color:#94a3b8; font-size:0.8rem;">📦 TOTAL ITEMS</p>
        <p class="card-value">{total_medicines}</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown("""
    <div class="glass-card">
        <p style="margin:0; color:#94a3b8; font-size:0.8rem;">⚡ SYSTEM</p>
        <p class="card-value" style="color:#10b981;">SYNCED</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. TABS NAVIGATION ---
tab1, tab2, tab3 = st.tabs(["🤖 AI", "📚 DB", "🧾 Calc"])

# --- TAB 1: AI ASSISTANT ---
with tab1:
    if not api_key:
        st.error("⚠️ GROQ_API_KEY is missing.")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        q1, q2, q3 = st.columns(3)
        selected_prompt = None
        if q1.button("🩹 Pain", use_container_width=True): selected_prompt = "Pain relief"
        if q2.button("🤒 Fever", use_container_width=True): selected_prompt = "Fever meds"
        if q3.button("🧹 Clear", use_container_width=True): 
            st.session_state.messages = []
            st.rerun()

        chat_container = st.container(height=400)
        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        user_input = st.chat_input("Search medicine...")
        prompt = selected_prompt or user_input

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("..."):
                        try:
                            q = prompt.lower().strip()
                            context = ""
                            if df_master is not None:
                                master_matches = df_master[df_master.apply(lambda row: row.astype(str).str.lower().str.contains(q, na=False).any(), axis=1)]
                                context += master_matches.head(10).to_string(index=False) if not master_matches.empty else "None"

                            # SUPER COMPRESSED MOBILE PROMPT
                            system_instruction = f"""
                            You are a high-speed mobile pharmacy AI. 
                            CRITICAL RULE: DO NOT WRITE PARAGRAPHS. DO NOT SAY HELLO. NO CONVERSATIONAL FILLER.
                            Answers must be EXTREMELY short and direct. Use 1-3 words per bullet point if possible.

                            FORMAT EXACTLY LIKE THIS:
                            **💊 [Name]** | *[Category]*
                            🔹 **Use:** [Direct symptom]
                            🔹 **Dose:** [Quick dose]
                            ⚠️ **Warn:** [1 key warning]
                            🔄 **Alt:** [1 alternative name]

                            Keep it highly compressed for small phone screens.
                            DATA: {context}
                            """

                            messages_payload = [{"role": "system", "content": system_instruction}]
                            for m in st.session_state.messages[-3:]: # Only keep last 3 to save memory/speed
                                messages_payload.append({"role": m["role"], "content": m["content"]})

                            response = client.chat.completions.create(
                                model="llama-3.1-8b-instant",
                                messages=messages_payload,
                                stream=True
                            )
                            
                            answer = st.write_stream((chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content))
                            st.session_state.messages.append({"role": "assistant", "content": answer})
                        except Exception as e:
                            st.error(f"API Error")

# --- TAB 2: INVENTORY DATABASE ---
with tab2:
    if df_master is not None:
        search_term = st.text_input("🔍 Filter DB:", "")
        if search_term:
            filtered_df = df_master[df_master.apply(lambda row: row.astype(str).str.lower().str.contains(search_term.lower(), na=False).any(), axis=1)]
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(df_master, use_container_width=True)

# --- TAB 3: BILL CALCULATOR ---
with tab3:
    if df_master is not None and "Brand Name" in df_master.columns:
        medicine_list = df_master["Brand Name"].dropna().tolist()
        selected_meds = st.multiselect("Select Meds:", medicine_list)
        
        if selected_meds:
            total_amount = 0.0
            for med in selected_meds:
                col_p, col_q = st.columns(2)
                with col_p:
                    price = st.number_input(f"Rs", min_value=0.0, value=100.0, step=10.0, key=f"p_{med}")
                with col_q:
                    qty = st.number_input(f"Qty", min_value=1, value=1, step=1, key=f"q_{med}")
                total_amount += (price * qty)
            
            st.markdown(f"<h2 style='color: #10b981; text-align:center;'>Total: Rs. {total_amount:,.2f}</h2>", unsafe_allow_html=True)

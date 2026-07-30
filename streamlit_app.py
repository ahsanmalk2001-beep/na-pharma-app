import streamlit as st
import pandas as pd
from openai import OpenAI
import requests
import time
from streamlit_lottie import st_lottie

# --- 1. PAGE CONFIGURATION & ZERO PADDING CSS ---
st.set_page_config(
    page_title="NA Pharma Care AI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Force zero padding on all containers to remove empty spaces on web and mobile
st.markdown("""
<style>
/* Remove all container padding */
div[data-testid="stAppViewBlockContainer"] {
    padding-top: 0px !important;
    padding-right: 0px !important;
    padding-left: 0px !important;
    padding-bottom: 0px !important;
}
div[data-testid="stSidebar"] > div:first-child {
    padding-top: 0px !important;
}
header {visibility: hidden !important;}
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}

/* Force full width on standard containers */
[data-testid="column"] {
    width: auto !important;
    flex: 1 1 0% !important;
    min-width: 0px !important;
}
</style>
""", unsafe_allow_html=True)


# --- 2. PREMIUM DARK THEME & DYNAMIC NOTCH CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* Base Theme */
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
    color: #f8fafc;
}
.stApp {
    background: radial-gradient(circle at top left, #1e293b, #0f172a, #020617);
    background-attachment: fixed;
}

/* --- THE DYNAMIC NOTCH INSPIRED HEADER --- */
/* Mobile: The top pill-shaped "notch" simulator */
@media (max-width: 768px) {
    #dynamic-notch {
        position: fixed;
        top: 10px;
        left: 50%;
        transform: translateX(-50%);
        width: 140px;
        height: 30px;
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
        height: 10px;
        background: radial-gradient(circle at top, #10b981 0%, transparent 70%);
        filter: blur(10px);
        opacity: 0.8;
        z-index: 9998;
    }
}
/* Web: A subtle, full-width top bar integration instead of a notch pill */
@media (min-width: 769px) {
    #dynamic-notch { display: none; }
    #notch-glow { display: none; }
}


/* Glassmorphism Cards */
.glass-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
    text-align: center;
}
.glass-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
}

/* Typography & Colors */
.text-primary { color: #10b981; } /* Medical Green */
.text-secondary { color: #3b82f6; } /* Medical Blue */
.text-muted { color: #94a3b8; font-size: 0.85rem; }
.card-value { font-size: 2.2rem; font-weight: 700; margin: 8px 0; color: #f8fafc; }
.status-badge {
    display: inline-flex;
    align-items: center;
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
    padding: 5px 14px;
    border-radius: 50px;
    font-size: 0.82rem;
    font-weight: 600;
    border: 1px solid rgba(16, 185, 129, 0.2);
    margin-bottom: 15px;
}
.pulse {
    width: 7px; height: 7px;
    background-color: #10b981;
    border-radius: 50%;
    margin-right: 7px;
    box-shadow: 0 0 10px #10b981;
    animation: pulse-animation 2s infinite;
}
@keyframes pulse-animation {
    0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.3); }
    70% { box-shadow: 0 0 0 8px rgba(16, 185, 129, 0); }
    100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* Custom Chat Bubbles for Mobile */
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 15px;
}
[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #10b981, #3b82f6) !important;
}
/* Simplified chatbot font sizing */
[data-testid="stChatMessage"] div p {
    font-size: 0.95rem;
    line-height: 1.5;
}
</style>
""", unsafe_allow_html=True)

# --- 3. ANIMATION LOADER & SPLASH SCREEN ---
@st.cache_data
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    return None

lottie_pulse = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_jcikwtux.json") # A pulsing heart/DNA strand

# FAKE BEGINNING ANIMATION SPLASH SCREEN
if 'splash_shown' not in st.session_state:
    st.session_state.splash_shown = False

if not st.session_state.splash_shown:
    splash_placeholder = st.empty()
    with splash_placeholder.container():
        st.markdown("<div style='position: fixed; top:0; left:0; width:100vw; height:100dvh; background-color: #0f172a; z-index: 10000; display:flex; flex-direction:column; align-items:center; justify-content:center;'>", unsafe_allow_html=True)
        if lottie_pulse:
            st_lottie(lottie_pulse, height=150, key="splash_lottie")
        st.markdown("<h1 style='color: #10b981; font-weight: 700; margin-top:20px;'>NAPC AI</h1></div>", unsafe_allow_html=True)
    
    time.sleep(2.5) # Show splash for 2.5 seconds
    splash_placeholder.empty()
    st.session_state.splash_shown = True

# --- 4. THE LIVE DYNAMIC NOTCH INJECTION ---
st.markdown("""
<div id="notch-glow"></div>
<div id="dynamic-notch">SYS: LIVE</div>
""", unsafe_allow_html=True)


# --- 5. DATA LOADER ---
EXCEL_FILE = "inventory.xlsx"
api_key = st.secrets.get("GROQ_API_KEY")

@st.cache_data
def load_inventory_data():
    try:
        # Assuming the inventory file structure hasn't changed
        df_master = pd.read_excel(EXCEL_FILE, sheet_name='Full Master Medicine List', header=3)
        df_symptom = pd.read_excel(EXCEL_FILE, sheet_name='Quick Symptom & Keyword Index', header=3)
        return df_master, df_symptom
    except Exception as e:
        return None, None

df_master, df_symptom = load_inventory_data()
total_medicines = len(df_master) if df_master is not None else 0
total_categories = len(df_symptom) if df_symptom is not None else 0

# --- 6. BRANDING & COMPACT DASHBOARD ---
# Spacer for the dynamic notch/header on mobile
st.markdown("<div style='margin-top: 45px;' class='mobile-spacer'></div>", unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; padding: 10px 0;">
    <div class="status-badge"><span class="pulse"></span> System Connected</div>
    <h1 style="margin:0; font-size: 2.8rem; font-weight: 700; background: linear-gradient(90deg, #10b981, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">💊 NA Pharma Care AI</h1>
    <p style="color: #94a3b8; font-size: 1rem; margin-top: 4px;">Smart Internal Pharmacy Assistant</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    st.markdown(f"""
    <div class="glass-card">
        <p class="text-muted" style="margin:0; text-transform:uppercase; letter-spacing:1px; font-size:0.8rem;">📦 Medicines</p>
        <p class="card-value">{total_medicines}</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="glass-card">
        <p class="text-muted" style="margin:0; text-transform:uppercase; letter-spacing:1px; font-size:0.8rem;">📚 Categories</p>
        <p class="card-value">{total_categories}</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="glass-card">
        <p class="text-muted" style="margin:0; text-transform:uppercase; letter-spacing:1px; font-size:0.8rem;">🤖 AI Status</p>
        <p class="card-value" style="color:#10b981;">LIVE</p>
    </div>
    """, unsafe_allow_html=True)
with col4:
    st.markdown("<div style='display:flex; justify-content:center; align-items:center; height:100%;' class='glass-card'>", unsafe_allow_html=True)
    if lottie_pulse:
        st_lottie(lottie_pulse, height=60, key="live_pulse")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- 7. TABS NAVIGATION ---
tab1, tab2, tab3 = st.tabs(["🤖 AI Assistant", "📚 Database", "🧾 Bill Calculator"])

# --- TAB 1: AI ASSISTANT ---
with tab1:
    if not api_key:
        st.error("⚠️ GROQ_API_KEY is missing.")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Compact Quick Lookup Categories
        st.markdown("<h5 style='color: #e2e8f0; font-weight: 500; margin-bottom:10px;'>⚡ Counter Lookup</h5>", unsafe_allow_html=True)
        q1, q2, q3, q4, q5 = st.columns(5)
        
        selected_prompt = None
        if q1.button("🩹 Pain", use_container_width=True): selected_prompt = "Quick check: pain relief medicines in stock."
        if q2.button("🤒 Fever", use_container_width=True): selected_prompt = "Quick check: fever medications."
        if q3.button("🤧 Cold", use_container_width=True): selected_prompt = "Quick check: cold and flu stock."
        if q4.button("💊 Antibiotic", use_container_width=True): selected_prompt = "Quick check: antibiotics list."
        if q5.button("🧹 Clear", use_container_width=True): 
            st.session_state.messages = []
            st.rerun()

        # Chat Interface with optimized height
        chat_container = st.container(height=450)
        with chat_container:
            if not st.session_state.messages:
                st.markdown("""
                <div style='text-align:center; padding: 40px; color:#94a3b8; font-size: 0.9rem;'>
                    <h4 style='color:#e2e8f0; font-weight: 500;'>Search medicine, generic, or symptoms instantly...</h4>
                    <p>Uses of Panadol • Alternative to Brufen • Medicine for sore throat</p>
                </div>
                """, unsafe_allow_html=True)
                
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Sticky Input Bar styling via CSS injection
        st.markdown("""
        <style>
        .stChatInputContainer {
            position: fixed !important;
            bottom: 10px !important;
            left: 50% !important;
            transform: translateX(-50%) !important;
            width: 90% !important;
            border-radius: 50px !important;
            backdrop-filter: blur(10px) !important;
            -webkit-backdrop-filter: blur(10px) !important;
            z-index: 999 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        user_input = st.chat_input("Ask AI...")
        prompt = selected_prompt or user_input

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("🔍 Scanning Database..."):
                        try:
                            q = prompt.lower().strip()
                            context = "--- DATABASE SCAN RESULTS ---\n"
                            
                            if df_master is not None:
                                master_matches = df_master[df_master.apply(lambda row: row.astype(str).str.lower().str.contains(q, na=False).any(), axis=1)]
                                # Provide less context data to model to keep it focused
                                context += master_matches.head(10).to_string(index=False) if not master_matches.empty else "No exact matches found in master list."

                            # REVISED PROMPT FOR DIRECT, COMPACT MOBILE ANSWERS
                            system_instruction = f"""
                            You are NA Pharma Care AI V3, the direct, internal pharmacy assistant for the NA family counter team.

                            STRICT RESPONSE FORMAT (DO NOT USE TABLES OR CODE BLOCKS). Whenever you suggest a medicine, you MUST format it EXACTLY like this beautiful *Simplified* virtual card:

                            **💊 [Brand Name]**  
                            🔬 *Generic: [Salt Name]*  
                            📝 *Categories: [Primary Categories]*  
                            ---
                            
                            🔹 **Uses:** [Primary uses, keep short]  
                            🔹 **Dosage:** [Standard dosage, keep short]  
                            ⚠️ **Warnings:** [Key precaution, keep short]  
                            🔄 **Alternatives:** [List max 2 alternative brands sharing salt]  
                            ---
                            
                            RETRIEVED INVENTORY DATA FOR THIS QUERY:
                            {context}

                            ACT AS EXPENSIVE MEDICAL SOFTWARE: Be concise, focus on immediate counter-lookup needs, and output minimal text while maintaining professional clarity. NEVER use long paragraphs.
                            """

                            messages_payload = [{"role": "system", "content": system_instruction}]
                            for m in st.session_state.messages:
                                messages_payload.append({"role": m["role"], "content": m["content"]})

                            response = client.chat.completions.create(
                                model="llama-3.1-8b-instant",
                                messages=messages_payload,
                                stream=True
                            )
                            
                            answer = st.write_stream((chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content))
                            st.session_state.messages.append({"role": "assistant", "content": answer})
                        
                        except Exception as e:
                            st.error(f"API Error: {e}")

# --- TAB 2: INVENTORY DATABASE (REMAINS SAME LOGIC, REFINED VISUALS) ---
with tab2:
    if df_master is not None:
        st.markdown("<h3 style='color: #f8fafc; margin-bottom:10px;'>📦 Master Database Scan</h3>", unsafe_allow_html=True)
        search_term = st.text_input("🔍 Filter database instantly...", "")
        if search_term:
            filtered_df = df_master[df_master.apply(lambda row: row.astype(str).str.lower().str.contains(search_term.lower(), na=False).any(), axis=1)]
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(df_master, use_container_width=True)

# --- TAB 3: BILL CALCULATOR (REMAINS SAME LOGIC, REFINED VISUALS) ---
with tab3:
    st.markdown("<h3 style='color: #f8fafc; margin-bottom:10px;'>🧾 Bill Estimator</h3>", unsafe_allow_html=True)
    if df_master is not None and "Brand Name" in df_master.columns:
        medicine_list = df_master["Brand Name"].dropna().tolist()
        selected_meds = st.multiselect("Select Medicines:", medicine_list)
        
        if selected_meds:
            total_amount = 0.0
            bill_items = []
            
            for med in selected_meds:
                col_n, col_p, col_q = st.columns([2, 1, 1])
                with col_n: st.markdown(f"<p style='margin-top:10px; font-weight:600;'>{med}</p>", unsafe_allow_html=True)
                with col_p: price = st.number_input(f"Price", min_value=0.0, value=100.0, step=10.0, key=f"p_{med}")
                with col_q: qty = st.number_input(f"Qty", min_value=1, value=1, step=1, key=f"q_{med}")
                
                item_total = price * qty
                total_amount += item_total
                bill_items.append({"Medicine": med, "Qty": qty, "Price": price, "Total": item_total})
            
            st.markdown("<br><hr style='border-color: #334155;'>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color: #10b981; font-weight:700;'>Grand Total: Rs. {total_amount:,.2f}</h2>", unsafe_allow_html=True)

import streamlit as st
import pandas as pd
from openai import OpenAI
import requests
import time
from streamlit_lottie import st_lottie

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NA Pharma Care AI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS STYLING ---
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.header-card {
    background: linear-gradient(135deg, rgba(17, 153, 142, 0.18), rgba(56, 239, 125, 0.12));
    border: 1px solid rgba(56, 239, 125, 0.35);
    border-radius: 18px;
    padding: 22px 28px;
    margin-bottom: 20px;
}

.main-title {
    background: linear-gradient(90deg, #11998e, #38ef7d);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem;
    font-weight: 800;
    margin: 0px;
    line-height: 1.1;
}

.sub-title {
    color: #b0b0b0;
    font-size: 1.05rem;
    font-weight: 500;
    margin-top: 6px;
    margin-bottom: 0px;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    background: rgba(46, 204, 113, 0.15);
    color: #2ecc71;
    padding: 5px 14px;
    border-radius: 50px;
    font-size: 0.82rem;
    font-weight: 600;
    border: 1px solid rgba(46, 204, 113, 0.35);
    margin-bottom: 12px;
}

.pulse-dot {
    width: 8px;
    height: 8px;
    background-color: #2ecc71;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
    box-shadow: 0 0 8px #2ecc71;
}

.kpi-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 16px;
    text-align: center;
}

.kpi-num {
    font-size: 1.9rem;
    font-weight: 800;
    color: #38ef7d;
    margin: 0;
}

.kpi-label {
    font-size: 0.8rem;
    color: #999;
    margin-top: 4px;
    margin-bottom: 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Chat Animations */
@keyframes slideUpFade {
    0% { opacity: 0; transform: translateY(20px) scale(0.98); }
    100% { opacity: 1; transform: translateY(0) scale(1); }
}

[data-testid="stChatMessage"] {
    animation: slideUpFade 0.4s ease-out forwards;
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 15px;
    box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}

[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #11998e, #38ef7d) !important;
    box-shadow: 0 0 12px rgba(56, 239, 125, 0.5);
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>""", unsafe_allow_html=True)

# --- 3. ANIMATION LOADER ---
@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

lottie_health = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_jcikwtux.json")

# --- 4. HIGH-END CINEMATIC SPLASH SCREEN (LIVE HOLOGRAM) ---
if 'splash_shown' not in st.session_state:
    st.session_state.splash_shown = False

if not st.session_state.splash_shown:
    splash_placeholder = st.empty()
    with splash_placeholder.container():
        st.markdown('''
        <style>
        /* Pitch black cinematic background */
        .splash-bg {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            background-color: #050505;
            z-index: 99999;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        
        /* Realistic Glowing AI Core */
        .live-core {
            position: relative;
            width: 220px;
            height: 220px;
            border-radius: 50%;
            background: radial-gradient(circle at 50% 50%, rgba(56, 239, 125, 0.15), transparent 70%);
            box-shadow: 0 0 80px rgba(56, 239, 125, 0.2), inset 0 0 50px rgba(17, 153, 142, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            animation: coreBreathe 3s ease-in-out infinite alternate;
        }

        /* 3D Spinning Hologram Rings */
        .ring1, .ring2, .ring3 {
            position: absolute;
            border-radius: 50%;
            border: 2px solid transparent;
        }
        .ring1 {
            width: 100%; height: 100%;
            border-top: 3px solid #38ef7d;
            border-bottom: 3px solid #11998e;
            animation: spinX 2s linear infinite;
            filter: drop-shadow(0 0 10px #38ef7d);
        }
        .ring2 {
            width: 80%; height: 80%;
            border-left: 2px solid #38ef7d;
            border-right: 2px solid #11998e;
            animation: spinY 1.5s linear infinite;
        }
        .ring3 {
            width: 60%; height: 60%;
            border-top: 2px dashed #38ef7d;
            animation: spinZ 3s linear infinite;
        }

        /* The Floating Medicine in the Center */
        .core-pill {
            font-size: 75px;
            animation: floatPill 2s ease-in-out infinite;
            filter: drop-shadow(0 0 25px rgba(56, 239, 125, 0.9));
        }

        /* Movie Intro Text Expanding */
        .movie-text {
            margin-top: 60px;
            font-size: 3rem;
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-weight: 800;
            color: #ffffff;
            letter-spacing: 15px;
            text-shadow: 0 0 25px rgba(56, 239, 125, 0.9);
            animation: trackingExpand 2s cubic-bezier(0.215, 0.610, 0.355, 1.000) both;
        }

        /* Live Physics & Keyframes */
        @keyframes coreBreathe {
            0% { transform: scale(0.95); box-shadow: 0 0 40px rgba(56, 239, 125, 0.2); }
            100% { transform: scale(1.05); box-shadow: 0 0 120px rgba(56, 239, 125, 0.7); }
        }
        @keyframes spinX { 100% { transform: rotate(360deg); } }
        @keyframes spinY { 100% { transform: rotate(-360deg); } }
        @keyframes spinZ { 100% { transform: rotate(360deg) scale(1.1); } }
        
        @keyframes floatPill {
            0%, 100% { transform: translateY(0px) rotate(0deg); }
            50% { transform: translateY(-12px) rotate(5deg); }
        }
        
        @keyframes trackingExpand {
            0% { letter-spacing: -0.5em; opacity: 0; }
            40% { opacity: 0.6; }
            100% { opacity: 1; letter-spacing: 15px; }
        }
        </style>

        <div class="splash-bg">
            <div class="live-core">
                <div class="ring1"></div>
                <div class="ring2"></div>
                <div class="ring3"></div>
                <div class="core-pill">💊</div>
            </div>
            <div class="movie-text">HI.</div>
        </div>
        ''', unsafe_allow_html=True)
        
    # Wait exactly 3.5 seconds while the movie intro plays
    time.sleep(3.5)
    
    # Erase the splash screen and permanently mark it as shown
    splash_placeholder.empty()
    st.session_state.splash_shown = True

# --- 5. DATA LOADER ---
EXCEL_FILE = "inventory.xlsx"
api_key = st.secrets.get("GROQ_API_KEY")

@st.cache_data
def load_inventory_data():
    try:
        df_master = pd.read_excel(EXCEL_FILE, sheet_name='Full Master Medicine List', header=3)
        df_symptom = pd.read_excel(EXCEL_FILE, sheet_name='Quick Symptom & Keyword Index', header=3)
        return df_master, df_symptom
    except Exception as e:
        return None, None

df_master, df_symptom = load_inventory_data()

total_medicines = len(df_master) if df_master is not None else 0
total_categories = len(df_symptom) if df_symptom is not None else 0

# --- 6. HEADER SECTION WITH LIVE METRICS ---
st.markdown("""
<div class="header-card">
    <div class="status-badge"><span class="pulse-dot"></span> System Live & Connected</div>
    <p class="main-title">NA Pharma Care</p>
    <p class="sub-title">Internal Family Management & Automated Counter System</p>
</div>
""", unsafe_allow_html=True)

col_stat1, col_stat2, col_stat3, col_anim = st.columns([2, 2, 2, 2])

with col_stat1:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-num">{total_medicines}</p>
        <p class="kpi-label">📦 Tracked Products</p>
    </div>
    """, unsafe_allow_html=True)

with col_stat2:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-num">{total_categories}</p>
        <p class="kpi-label">🔍 Symptom Categories</p>
    </div>
    """, unsafe_allow_html=True)

with col_stat3:
    st.markdown("""
    <div class="kpi-card">
        <p class="kpi-num" style="color:#11998e;">Active</p>
        <p class="kpi-label">⚡ Smart Substitute Engine</p>
    </div>
    """, unsafe_allow_html=True)

with col_anim:
    if lottie_health:
        st_lottie(lottie_health, height=75, key="header_lottie")

st.markdown("<br>", unsafe_allow_html=True)

# --- 7. NAVIGATION TABS ---
tab1, tab2, tab3 = st.tabs(["💬 Counter AI Assistant", "📊 Inventory Database", "🧮 Walk-in Bill Estimator"])

# --- TAB 1: AI ASSISTANT ---
with tab1:
    if not api_key:
        st.error("⚠️ GROQ_API_KEY is missing in Streamlit Cloud Secrets. Please add it in Settings -> Secrets.")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        st.markdown("**💡 Quick Counter Lookups:**")
        qcol1, qcol2, qcol3, qcol4, qcol5 = st.columns(5)
        
        selected_prompt = None
        if qcol1.button("👂 Ear Drops"):
            selected_prompt = "Do we have any ear drops in stock right now?"
        if qcol2.button("👁️ Eye Drops"):
            selected_prompt = "List all eye drop solutions available."
        if qcol3.button("💊 Antibiotics"):
            selected_prompt = "What antibiotics do we have in inventory?"
        if qcol4.button("🤒 Pain Relief"):
            selected_prompt = "Show pain relief medications and dosages."
        if qcol5.button("🧹 Clear Screen"):
            st.session_state.messages = []
            st.rerun()

        chat_container = st.container(height=500)

        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        user_input = st.chat_input("Type medicine name, active formula, or symptom for customer...")
        prompt = selected_prompt or user_input

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Scanning inventory for counter..."):
                        try:
                            q = prompt.lower().strip()
                            
                            master_matches = pd.DataFrame()
                            symptom_matches = pd.DataFrame()
                            
                            if df_master is not None:
                                master_matches = df_master[df_master.apply(lambda row: row.astype(str).str.lower().str.contains(q, na=False).any(), axis=1)]
                            if df_symptom is not None:
                                symptom_matches = df_symptom[df_symptom.apply(lambda row: row.astype(str).str.lower().str.contains(q, na=False).any(), axis=1)]

                            context = "--- SYMPTOM & CATEGORY INDEX ---\n"
                            context += symptom_matches.to_string(index=False) + "\n\n" if not symptom_matches.empty else "No direct matches in symptom index.\n\n"
                            context += "--- MASTER MEDICINE LIST ---\n"
                            context += master_matches.head(20).to_string(index=False) if not master_matches.empty else "No exact matches found in master list."

                            system_instruction = f"""
                            You are the dedicated internal AI assistant for the NA Pharma Care family counter team.

                            STRICT VISUAL FORMATTING RULES:
                            1. NEVER use markdown tables (| Column | Column |).
                            2. NEVER use markdown code blocks (```).
                            3. ALWAYS format medicines as clean, visually appealing "Virtual Cards" using emojis and soft dividers.
                            
                            Example Format to copy:
                            💊 **[Brand Name]**  
                            🔬 *Formula: [Active Salt]*  
                            📝 *Category: [Primary Use]*  
                            ---
                            
                            COUNTER OPERATOR RULES:
                            1. **Instant Medicine Lookup:** Confirm if the item is in stock using the Virtual Card format above.
                            2. **Smart Alternatives:** If requested brand is missing, immediately list alternative brands sharing the EXACT same active salt.
                            3. **Customer Guidance:** Keep responses fast to read, avoiding long paragraphs.

                            RETRIEVED INVENTORY DATA FOR THIS QUERY:
                            {context}
                            """

                            messages_payload = [{"role": "system", "content": system_instruction}]
                            for m in st.session_state.messages:
                                messages_payload.append({"role": m["role"], "content": m["content"]})

                            response = client.chat.completions.create(
                                model="llama-3.1-8b-instant",
                                messages=messages_payload,
                                stream=True
                            )
                            
                            def stream_generator():
                                for chunk in response:
                                    content = chunk.choices[0].delta.content
                                    if content:
                                        yield content

                            answer = st.write_stream(stream_generator())
                            st.session_state.messages.append({"role": "assistant", "content": answer})
                        
                        except Exception as e:
                            st.error(f"API Error: {e}")

# --- TAB 2: INVENTORY DATABASE ---
with tab2:
    st.subheader("📦 Master Inventory Database")
    if df_master is not None:
        search_term = st.text_input("🔍 Search to filter database instantly:", "")
        if search_term:
            filtered_df = df_master[df_master.apply(lambda row: row.astype(str).str.lower().str.contains(search_term.lower(), na=False).any(), axis=1)]
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(df_master, use_container_width=True)
            
        csv_data = df_master.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Inventory as CSV", csv_data, "na_pharma_inventory.csv", "text/csv")
    else:
        st.error("Could not load master inventory list. Check your Excel file.")

# --- TAB 3: QUICK BILL ESTIMATOR ---
with tab3:
    st.subheader("🧮 Walk-in Counter Bill Estimator")
    st.markdown("Quickly calculate totals for walk-in customer purchases to speed up checkout.")
    
    if df_master is not None and "Brand Name" in df_master.columns:
        medicine_list = df_master["Brand Name"].dropna().tolist()
        selected_meds = st.multiselect("Scan / Select Medicines:", medicine_list)
        
        if selected_meds:
            bill_items = []
            total_amount = 0.0
            
            for med in selected_meds:
                col_m, col_p, col_q = st.columns([3, 2, 2])
                with col_m:
                    st.write(f"**{med}**")
                with col_p:
                    price = st.number_input(f"Unit Price for {med}", min_value=0.0, value=100.0, step=10.0, key=f"p_{med}")
                with col_q:
                    qty = st.number_input(f"Quantity for {med}", min_value=1, value=1, step=1, key=f"q_{med}")
                
                item_total = price * qty
                total_amount += item_total
                bill_items.append({"Medicine": med, "Unit Price": price, "Qty": qty, "Total": item_total})
            
            st.markdown("---")
            st.markdown(f"### 💳 Total Estimated Bill: **Rs. {total_amount:,.2f}**")
            st.dataframe(pd.DataFrame(bill_items), use_container_width=True)
    else:
        st.info("Inventory brand names column not detected. Make sure your 'Full Master Medicine List' sheet has a 'Brand Name' column.")

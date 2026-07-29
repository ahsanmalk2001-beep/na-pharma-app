import streamlit as st
import pandas as pd
from openai import OpenAI
import requests
from streamlit_lottie import st_lottie

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NA Pharma Care AI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS & ANIMATED STYLES ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    <style>
    * { font-family: 'Poppins', sans-serif; }
    
    /* Header Container */
    .header-card {
        background: linear-gradient(135deg, rgba(17, 153, 142, 0.12), rgba(56, 239, 125, 0.12));
        border: 1px solid rgba(56, 239, 125, 0.25);
        border-radius: 20px;
        padding: 24px 30px;
        margin-bottom: 25px;
        backdrop-filter: blur(10px);
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
        color: #888888;
        font-size: 1.05rem;
        font-weight: 500;
        margin-top: 6px;
        margin-bottom: 0px;
    }

    /* Live Pulsing Status Badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(46, 204, 113, 0.12);
        color: #2ecc71;
        padding: 6px 14px;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 600;
        border: 1px solid rgba(46, 204, 113, 0.3);
        margin-bottom: 12px;
    }

    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #2ecc71;
        border-radius: 50%;
        display: inline-block;
        margin-right: 8px;
        box-shadow: 0 0 0 rgba(46, 204, 113, 0.4);
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0.7); }
        70% { box-shadow: 0 0 0 10px rgba(46, 204, 113, 0); }
        100% { box-shadow: 0 0 0 0 rgba(46, 204, 113, 0); }
    }

    /* Modern KPI Cards */
    .kpi-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 16px;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(56, 239, 125, 0.15);
    }
    .kpi-num {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38ef7d;
        margin: 0;
    }
    .kpi-label {
        font-size: 0.82rem;
        color: #aaa;
        font-weight: 500;
        margin-top: 4px;
    }

    /* Hide standard clutter */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

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

# --- 4. DATA LOADER ---
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

# --- 5. HEADER SECTION WITH LIVE METRICS ---
st.markdown("""
    <div class="header-card">
        <div class="status-badge">
            <span class="pulse-dot"></span> System Live 24/7 & Connected
        </div>
        <p class="main-title">NA Pharma Care</p>
        <p class="sub-title">AI Pharmacy Management & Automated Inventory System</p>
    </div>
""", unsafe_allow_html=True)

# KPI Metric Row
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
            <p class="kpi-num" style="color:#11998e;">Llama-3.1</p>
            <p class="kpi-label">⚡ AI Neural Core</p>
        </div>
    """, unsafe_allow_html=True)

with col_anim:
    if lottie_health:
        st_lottie(lottie_health, height=80, key="header_lottie")

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. MAIN TABS ---
tab1, tab2 = st.tabs(["💬 AI Assistant Chat", "📊 Master Inventory Database"])

with tab1:
    if not api_key:
        st.error("⚠️ GROQ_API_KEY is missing in Streamlit Cloud Secrets. Please add it in App Settings -> Secrets.")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Quick Query Chips
        st.markdown("**💡 Quick Suggestions:**")
        qcol1, qcol2, qcol3, qcol4 = st.columns(4)
        
        selected_prompt = None
        if qcol1.button("👂 Check Ear Drops"):
            selected_prompt = "Do we have any ear drops in stock?"
        if qcol2.button("💊 Search Antibiotics"):
            selected_prompt = "List all antibiotics in our inventory."
        if qcol3.button("🤒 Pain Relief Options"):
            selected_prompt = "What medicines do we have for pain relief or fever?"
        if qcol4.button("🧹 Clear Conversation"):
            st.session_state.messages = []
            st.rerun()

        # Chat display container
        chat_container = st.container(autoscroll=True)

        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        # Input handling from chat input or button chips
        user_input = st.chat_input("Ask anything about products, salts, symptoms...")
        prompt = selected_prompt or user_input

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Analyzing inventory database..."):
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
                            You are the professional and friendly pharmacy assistant for NA Pharma Care. 
                            Answer customer queries strictly using the retrieved inventory data provided below.
                            Format your responses clearly with bullet points and bold text for readability.
                            
                            RETRIEVED EXCEL DATA FOR THIS QUERY:
                            {context}
                            """

                            messages_payload = [{"role": "system", "content": system_instruction}]
                            for m in st.session_state.messages:
                                messages_payload.append({"role": m["role"], "content": m["content"]})

                            # Stream response chunk-by-chunk for continuous live typing
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

with tab2:
    st.subheader("📦 Master Medicine Database")
    if df_master is not None:
        search_term = st.text_input("🔍 Filter database in real-time:", "")
        if search_term:
            filtered_df = df_master[df_master.apply(lambda row: row.astype(str).str.lower().str.contains(search_term.lower(), na=False).any(), axis=1)]
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(df_master, use_container_width=True)
    else:
        st.error("Could not load master inventory list.")
        
    st.subheader("🔍 Quick Symptom Index")
    if df_symptom is not None:
        st.dataframe(df_symptom, use_container_width=True)
    else:
        st.error("Could not load symptom index list.")

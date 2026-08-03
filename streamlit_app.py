import io
import os
import base64
import time
import streamlit as st
import pandas as pd
from openai import OpenAI

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NA Pharma Care - Cinematic AI Terminal",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. 4K CINEMATIC INTRO & FUTURISTIC DESIGN SYSTEM ---
st.markdown("""
<style>
/* --- HIDE STREAMLIT BRANDING --- */
#MainMenu {visibility: hidden !important;}
header {visibility: hidden !important; background: transparent !important;}
footer {visibility: hidden !important; display: none !important;}
.stDeployButton {display: none !important;}
[data-testid="stToolbar"] {visibility: hidden !important;}

/* --- GLOBAL APP BACKGROUND (Futuristic Void & Holographic Glow) --- */
.stApp, html, body, [data-testid="stAppViewContainer"] {
    background-color: #020408 !important;
    background-image: 
        radial-gradient(circle at 50% 30%, rgba(0, 243, 255, 0.08) 0%, transparent 50%),
        radial-gradient(circle at 85% 85%, rgba(0, 255, 102, 0.06) 0%, transparent 45%),
        linear-gradient(135deg, #020408 0%, #080d1a 100%) !important;
    color: #F8FAFC !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}

/* --- 4K CINEMATIC INTRO OVERLAY --- */
.cinematic-splash {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: radial-gradient(circle at center, #060b18 0%, #010204 100%);
    z-index: 999999; display: flex; flex-direction: column;
    justify-content: center; align-items: center; text-align: center;
    overflow: hidden; perspective: 1200px;
}
.cinematic-splash::after {
    content: " "; display: block; position: absolute; top: 0; left: 0; bottom: 0; right: 0;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.3) 50%), linear-gradient(90deg, rgba(0, 243, 255, 0.03), rgba(0, 255, 102, 0.01), rgba(128, 0, 255, 0.03));
    z-index: 2000000; background-size: 100% 4px, 6px 100%; pointer-events: none;
}

/* --- 3D AI CORE & ROTATING HUD RINGS --- */
.ai-core-container {
    position: absolute; width: 260px; height: 260px;
    display: flex; justify-content: center; align-items: center;
    animation: coreFadeIn 5.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.ai-core-orb {
    width: 70px; height: 70px; background: radial-gradient(circle, #00F3FF 0%, #00FF66 60%, transparent 100%);
    border-radius: 50%; box-shadow: 0 0 50px #00F3FF, 0 0 100px #00FF66, inset 0 0 15px #FFFFFF;
    animation: corePulse 2s infinite ease-in-out; z-index: 3;
}
.hud-ring {
    position: absolute; border-radius: 50%; border: 2px dashed rgba(0, 243, 255, 0.4);
    box-shadow: 0 0 20px rgba(0, 243, 255, 0.2);
}
.ring-1 { width: 160px; height: 160px; border-color: rgba(0, 243, 255, 0.6); border-top-color: transparent; border-bottom-color: transparent; animation: spinClockwise 4s linear infinite; }
.ring-2 { width: 220px; height: 220px; border-color: rgba(0, 255, 102, 0.5); border-left-color: transparent; border-right-color: transparent; animation: spinCounter 6s linear infinite; }
.ring-3 { width: 280px; height: 280px; border-color: rgba(128, 0, 255, 0.4); border-style: dotted; animation: spinClockwise 10s linear infinite; }

@keyframes corePulse {
    0% { transform: scale(0.9); opacity: 0.8; box-shadow: 0 0 40px #00F3FF, 0 0 80px #00FF66; }
    50% { transform: scale(1.15); opacity: 1; box-shadow: 0 0 70px #00F3FF, 0 0 120px #00FF66; }
    100% { transform: scale(0.9); opacity: 0.8; box-shadow: 0 0 40px #00F3FF, 0 0 80px #00FF66; }
}
@keyframes spinClockwise { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
@keyframes spinCounter { 0% { transform: rotate(0deg); } 100% { transform: rotate(-360deg); } }
@keyframes coreFadeIn {
    0% { opacity: 0; transform: scale(0.2); }
    30% { opacity: 1; transform: scale(1); }
    85% { opacity: 1; transform: scale(1); filter: blur(0px); }
    100% { opacity: 0; transform: scale(1.8); filter: blur(8px); }
}

/* --- CINEMATIC 3D ZOOMING WELCOME TEXT --- */
.text-3d-container {
    position: absolute; width: 100%; text-align: center; z-index: 10;
    animation: cinematicTextZoom 5.5s cubic-bezier(0.15, 0.85, 0.35, 1) forwards;
}
.welcome-3d-text {
    font-weight: 900; font-size: 3rem !important; letter-spacing: 3px;
    background: linear-gradient(135deg, #FFFFFF 20%, #00F3FF 60%, #00FF66 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-transform: uppercase;
    filter: drop-shadow(0 0 30px rgba(0, 243, 255, 0.6));
    margin: 0;
}
@keyframes cinematicTextZoom {
    0% { transform: scale(0.1) translateZ(-800px); opacity: 0; filter: blur(15px); }
    25% { opacity: 1; filter: blur(0px); }
    75% { transform: scale(1) translateZ(0px); opacity: 1; filter: blur(0px); }
    100% { transform: scale(2.4) translateZ(400px); opacity: 0; filter: blur(10px); }
}

/* --- BOOT SEQUENCE STATUS CONSOLE --- */
.boot-console {
    position: absolute; bottom: 60px; width: 80%; max-width: 500px;
    background: rgba(6, 11, 24, 0.85); border: 1px solid rgba(0, 243, 255, 0.3);
    border-radius: 6px; padding: 14px 20px; font-family: 'Courier New', monospace;
    font-size: 0.85rem; color: #00F3FF; text-align: left;
    box-shadow: 0 0 25px rgba(0, 243, 255, 0.2);
    animation: consoleFade 5.5s ease forwards; z-index: 15;
}
.boot-line { margin: 4px 0; opacity: 0; animation: revealLine 1.2s forwards; }
.l1 { animation-delay: 0.8s; }
.l2 { animation-delay: 2.0s; color: #00FF66; }
.l3 { animation-delay: 3.2s; color: #A855F7; }
.l4 { animation-delay: 4.4s; color: #FFFFFF; font-weight: bold; }

@keyframes revealLine {
    0% { opacity: 0; transform: translateX(-10px); }
    100% { opacity: 1; transform: translateX(0); }
}
@keyframes consoleFade {
    0% { opacity: 1; }
    85% { opacity: 1; }
    100% { opacity: 0; transform: scale(0.95); }
}

/* --- PROFESSIONAL STATUS BADGE --- */
.live-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(0, 243, 255, 0.1);
    border: 1px solid rgba(0, 243, 255, 0.3);
    padding: 6px 14px; border-radius: 6px;
    font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px;
    color: #00F3FF;
    box-shadow: 0 0 15px rgba(0, 243, 255, 0.15);
}
.pulse-dot {
    width: 6px; height: 6px; background-color: #00FF66; border-radius: 50%;
    box-shadow: 0 0 10px rgba(0, 255, 102, 0.9);
    animation: livePulse 2s infinite ease-in-out;
}
@keyframes livePulse {
    0% { transform: scale(0.95); opacity: 0.8; }
    50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 18px rgba(0, 255, 102, 1); }
    100% { transform: scale(0.95); opacity: 0.8; }
}

/* --- GLASSMORPHISM HELD CARDS (3D Medical Panels) --- */
.hud-card {
    background: rgba(13, 20, 35, 0.75) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(0, 243, 255, 0.15) !important;
    border-radius: 8px !important;
    padding: 24px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.1) !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
.hud-card:hover {
    border-color: rgba(0, 243, 255, 0.4) !important;
    box-shadow: 0 12px 40px rgba(0, 243, 255, 0.12), inset 0 1px 2px rgba(0, 243, 255, 0.2) !important;
    transform: translateY(-2px);
}

/* --- ACTION BUTTONS --- */
.stButton button {
    background: linear-gradient(135deg, rgba(13, 20, 35, 0.9) 0%, rgba(20, 32, 56, 0.9) 100%) !important;
    border: 1px solid rgba(0, 243, 255, 0.4) !important;
    border-radius: 6px !important;
    color: #F8FAFC !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1.2px !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
}
.stButton button:hover {
    background: linear-gradient(135deg, rgba(0, 243, 255, 0.2) 0%, rgba(0, 255, 102, 0.15) 100%) !important;
    border-color: #00F3FF !important;
    color: #00F3FF !important;
    box-shadow: 0 0 20px rgba(0, 243, 255, 0.4) !important;
}

/* --- INPUT FIELDS --- */
[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea {
    background: rgba(5, 9, 18, 0.9) !important;
    border: 1px solid rgba(0, 243, 255, 0.2) !important;
    border-radius: 6px !important;
    color: #FFFFFF !important;
    font-size: 0.95rem !important;
    padding: 12px 16px !important;
    transition: all 0.25s ease !important;
}
[data-testid="stTextInput"] input:focus, [data-testid="stTextArea"] textarea:focus {
    border-color: #00F3FF !important;
    box-shadow: 0 0 15px rgba(0, 243, 255, 0.25) !important;
}

/* --- FUTURISTIC HEADINGS --- */
.clean-title {
    margin: 0 auto; font-weight: 900; font-size: 2.8rem !important; text-align: center;
    background: linear-gradient(135deg, #FFFFFF 20%, #00F3FF 70%, #00FF66 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    display: inline-block;
    padding: 4px 16px;
    letter-spacing: -1px;
    text-transform: uppercase;
    filter: drop-shadow(0 0 20px rgba(0, 243, 255, 0.3));
}

/* --- DATAFRAMES --- */
[data-testid="stDataFrame"] {
    background: rgba(13, 20, 35, 0.85) !important;
    border-radius: 8px !important;
    border: 1px solid rgba(0, 243, 255, 0.2) !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE FOR CINEMATIC INTRO ---
if 'intro_played' not in st.session_state:
    st.session_state.intro_played = False

if not st.session_state.intro_played:
    st.markdown("""
    <div class="cinematic-splash">
        <!-- 3D AI Core & Rotating HUD Rings -->
        <div class="ai-core-container">
            <div class="hud-ring ring-1"></div>
            <div class="hud-ring ring-2"></div>
            <div class="hud-ring ring-3"></div>
            <div class="ai-core-orb"></div>
        </div>

        <!-- Cinematic 3D Zooming Text -->
        <div class="text-3d-container">
            <h1 class="welcome-3d-text">WELCOME TO NA PHARMA CARE AI</h1>
        </div>

        <!-- Phased Boot Console -->
        <div class="boot-console">
            <div class="boot-line l1">> INITIALIZING AI NEURAL CORE... [OK]</div>
            <div class="boot-line l2">> CONNECTING PHARMACY DATABASE... [SECURE]</div>
            <div class="boot-line l3">> ANALYZING MEDICINE LIBRARY & MOLECULES... [LOADED]</div>
            <div class="boot-line l4">> SYSTEM READY. ACTIVATING HOLOGRAPHIC TERMINAL...</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    time.sleep(5.3)
    st.session_state.intro_played = True
    st.rerun()

# --- 3. HIGH-SPEED DATA LOADER ---
EXCEL_FILE = "inventory.xlsx"
api_key = st.secrets.get("GROQ_API_KEY")

@st.cache_data(show_spinner=False)
def load_inventory_data():
    if not os.path.exists(EXCEL_FILE):
        return None
    try:
        df_master = pd.read_excel(EXCEL_FILE, sheet_name='Full Master Medicine List', header=3)
        df_master.dropna(how='all', inplace=True)
        return df_master
    except Exception as e:
        return None

df_master = load_inventory_data()

# --- 4. SMART SEARCH ALGORITHM ---
def perform_smart_inventory_search(df, query):
    if df is None or df.empty:
        return pd.DataFrame(), "Inventory is empty or uninitialized."
    
    query_clean = query.lower().strip()
    brand_col = 'Brand Name' if 'Brand Name' in df.columns else df.columns[0]
    salt_col = 'Active Salt / Generic Composition' if 'Active Salt / Generic Composition' in df.columns else None
    category_col = 'Therapeutic Category' if 'Therapeutic Category' in df.columns else None
    uses_col = 'Primary Uses & Indications' if 'Primary Uses & Indications' in df.columns else None
    
    matches = pd.DataFrame()
    
    if brand_col in df.columns:
        b_match = df[df[brand_col].astype(str).str.contains(query_clean, case=False, na=False)]
        matches = pd.concat([matches, b_match]).drop_duplicates()
        
    if salt_col and salt_col in df.columns:
        s_match = df[df[salt_col].astype(str).str.contains(query_clean, case=False, na=False)]
        matches = pd.concat([matches, s_match]).drop_duplicates()

    if category_col and category_col in df.columns:
        c_match = df[df[category_col].astype(str).str.contains(query_clean, case=False, na=False)]
        matches = pd.concat([matches, c_match]).drop_duplicates()

    if uses_col and uses_col in df.columns:
        u_match = df[df[uses_col].astype(str).str.contains(query_clean, case=False, na=False)]
        matches = pd.concat([matches, u_match]).drop_duplicates()

    if matches.empty:
        ignore_words = {'find', 'medicine', 'medicines', 'in', 'stock', 'the', 'is', 'are', 'for', 'a', 'an', 'what', 'do', 'you', 'have', 'show'}
        words = [w for w in query_clean.split() if w not in ignore_words and len(w) > 1]
        if not words:
            words = query_clean.split()
            
        exclude_cols = ['Common Side Effects', 'Warnings & Contraindications', 'S.No', 'S. No']
        target_cols = [c for c in df.columns if c not in exclude_cols]
        
        mask = pd.Series([False] * len(df))
        for word in words:
            mask = mask | df[target_cols].astype(str).apply(lambda x: x.str.contains(word, case=False, na=False)).any(axis=1)
        matches = df[mask]
        
    display_cols = [c for c in ['Brand Name', 'Active Salt / Generic Composition', 'Therapeutic Category', 'Primary Uses & Indications'] if c in df.columns]
    
    if not matches.empty:
        return matches[display_cols].head(15), matches[display_cols].head(15).to_string(index=False)
    else:
        return pd.DataFrame(), "No exact or matching medications found in current inventory records."

# --- 5. HEADER WITH SYSTEM STATUS ---
st.markdown("""
<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 8px;">
    <div class="live-badge">
        <div class="pulse-dot"></div> S.H.I.E.L.D. Holographic Node • Live
    </div>
</div>
<div style="text-align: center; padding: 0 0 24px 0;">
    <h1 class="clean-title">NA Pharma Care AI</h1>
    <p style="color: #94A3B8; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 2.5px; margin-top: 6px;">Futuristic Clinical Intelligence Matrix & Inventory Engine</p>
</div>
""", unsafe_allow_html=True)

# --- 6. TABS NAVIGATION ---
tab1, tab2 = st.tabs(["⚡ Command Center", "➕ Inventory Ingestion Hub"])

# --- TAB 1: COMMAND CENTER ---
with tab1:
    if not api_key:
        st.error("⚠️ GROQ_API_KEY missing in Streamlit secrets.")
    else:
        client = OpenAI(base_url="https://" + "api.groq.com/openai/v1", api_key=api_key)
        
        st.markdown("<p style='color: #94A3B8; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px;'>Quick Filters:</p>", unsafe_allow_html=True)
        c1, c2, c3, c4, c5, c6 = st.columns([1,1,1,1,1,1.2])
        chip_query = None
        if c1.button("Pain"): chip_query = "pain"
        if c2.button("Fever"): chip_query = "fever"
        if c3.button("Cough"): chip_query = "cough"
        if c4.button("Antibiotic"): chip_query = "antibiotic"
        if c5.button("Stomach"): chip_query = "stomach"
        if c6.button("Clear Search"): chip_query = ""

        search_input = st.text_input("Search inventory by brand, generic salt, or symptom...", value=chip_query if chip_query is not None else "")
        active_query = search_input.strip()

        if active_query:
            total_meds_count = len(df_master) if df_master is not None else 0
            
            # --- FUTURISTIC ANIMATED AI LOADING STATES ---
            status_container = st.empty()
            with status_container.container():
                st.markdown("""
                <div class="hud-card" style="text-align: center; padding: 25px; margin-bottom: 15px;">
                    <div style="color: #00F3FF; font-weight: 700; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px;">Accessing pharmacy database...</div>
                    <div style="color: #94A3B8; font-size: 0.8rem;">Querying encrypted nodes & molecular structures...</div>
                </div>
                """, unsafe_allow_html=True)
            time.sleep(0.3)
            
            df_matches, context_data = perform_smart_inventory_search(df_master, active_query)
            
            with status_container.container():
                st.markdown("""
                <div class="hud-card" style="text-align: center; padding: 25px; margin-bottom: 15px;">
                    <div style="color: #00FF66; font-weight: 700; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px;">Analyzing medicine information...</div>
                    <div style="color: #94A3B8; font-size: 0.8rem;">Synthesizing clinical indicators & stock availability...</div>
                </div>
                """, unsafe_allow_html=True)
            time.sleep(0.3)
            status_container.empty()

            col_left, col_right = st.columns([1.2, 1])

            with col_left:
                st.markdown("### Inventory Results")
                if not df_matches.empty:
                    st.success(f"Matched {len(df_matches)} active records.")
                    st.dataframe(df_matches, use_container_width=True, height=380)
                else:
                    st.warning(f"No direct matches found for '{active_query}'.")

            with col_right:
                st.markdown("### Clinical Synthesis")
                with st.spinner("Preparing response..."):
                    try:
                        system_instruction = f"""
                        You are the internal futuristic clinical assistant for NA Pharma Care AI.
                        TOTAL INVENTORY: {total_meds_count} medications registered.
                        
                        RULES:
                        1. If medications appear in matches, they ARE IN STOCK.
                        2. Present each item clearly with clean line breaks inside futuristic medical cards.
                        
                        --- MATCHED DATA ---
                        {context_data}
                        """
                        
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {"role": "system", "content": system_instruction},
                                {"role": "user", "content": f"Provide availability and usage guidance for: {active_query}"}
                            ],
                            stream=False
                        )
                        
                        st.markdown(f"""
                        <div class="hud-card" style="margin-top: 10px; line-height: 1.6; border-left: 3px solid #00F3FF !important;">
                            {response.choices[0].message.content}
                        </div>
                        """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Neural Error: {e}")
        else:
            st.markdown("""
            <div class="hud-card" style="text-align: center; padding: 45px 20px; margin-top: 15px;">
                <h3 style="color: #F8FAFC; margin-bottom: 8px; font-weight: 700; font-size: 1.2rem;">Holographic Matrix Online</h3>
                <p style="color: #94A3B8; font-size: 0.9rem; max-width: 500px; margin: 0 auto;">Enter a search query above or select a quick filter to query the live pharmacy inventory matrix.</p>
            </div>
            """, unsafe_allow_html=True)

# --- TAB 2: ADVANCED INGESTION HUB ---
with tab2:
    st.markdown("### Inventory Ingestion Hub")
    
    sub_tab1, sub_tab2, sub_tab3, sub_tab4, sub_tab5 = st.tabs([
        "Handwritten Scanner", 
        "Text / WhatsApp Parser", 
        "Bulk Importer", 
        "Live Grid Editor", 
        "Single Item Form"
    ])
    
    # --- SUB-TAB 1: HANDWRITTEN PAPER SCANNER ---
    with sub_tab1:
        st.markdown("""
        <div class="hud-card" style="margin-bottom: 15px;">
            <h4 style="color: #F8FAFC; margin-top: 0; font-size: 1rem;">Handwritten Document OCR</h4>
            <p style="color: #94A3B8; font-size: 0.85rem;">Upload an image of a handwritten list or prescription to automatically extract and review items.</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_handwriting_image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
        
        if uploaded_handwriting_image is not None:
            st.image(uploaded_handwriting_image, caption="Source Document", use_container_width=True)
            
            if st.button("Extract & Process Document"):
                if api_key:
                    with st.spinner("Decoding document..."):
                        try:
                            client_vision = OpenAI(base_url="https://" + "api.groq.com/openai/v1", api_key=api_key)
                            image_bytes = uploaded_handwriting_image.getvalue()
                            base64_image = base64.b64encode(image_bytes).decode('utf-8')
                            
                            vision_response = client_vision.chat.completions.create(
                                model="llama-3.2-11b-vision-preview",
                                messages=[
                                    {
                                            "role": "user",
                                            "content": [
                                                {
                                                    "type": "text",
                                                    "text": "Extract medications into a clean CSV format with exact headers: Brand Name, Active Salt / Generic Composition, Therapeutic Category, Primary Uses & Indications"
                                                },
                                                {
                                                    "type": "image_url",
                                                    "image_url": {
                                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                                    }
                                                }
                                            ]
                                    }
                                ],
                                stream=False
                            )
                            
                            decoded_csv = vision_response.choices[0].message.content
                            cleaned_csv_text = decoded_csv.replace(chr(96) * 3 + "csv", "").replace(chr(96) * 3, "").strip()
                            df_temp_preview = pd.read_csv(io.StringIO(cleaned_csv_text))
                            
                            st.session_state['ocr_preview_df'] = df_temp_preview
                            st.success("Extraction complete. Review entries below.")
                        except Exception as e:
                            st.error(f"OCR Error: {e}")

        if 'ocr_preview_df' in st.session_state:
            st.markdown("#### Review Extracted Rows")
            final_reviewed_df = st.data_editor(st.session_state['ocr_preview_df'], num_rows="dynamic", use_container_width=True)
            
            if st.button("Commit Verified Rows"):
                if df_master is not None:
                    valid_rows = final_reviewed_df.dropna(how='all')
                    if 'Brand Name' in valid_rows.columns:
                        valid_rows['Brand Name'] = valid_rows['Brand Name'].astype(str).str.strip().str.title()
                    
                    combined_df = pd.concat([df_master, valid_rows], ignore_index=True).drop_duplicates(subset=['Brand Name'] if 'Brand Name' in valid_rows.columns else None)
                    
                    try:
                        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='w') as writer:
                            combined_df.to_excel(writer, sheet_name='Full Master Medicine List', startrow=3, index=False)
                        st.success(f"Successfully committed {len(valid_rows)} records.")
                        st.cache_data.clear()
                        del st.session_state['ocr_preview_df']
                    except PermissionError:
                        st.error("File locked. Please close 'inventory.xlsx' in Microsoft Excel and try again.")
                    except Exception as e:
                        st.error(f"Commit error: {e}")

    # --- SUB-TAB 2: AI TEXT & WHATSAPP PARSER ---
    with sub_tab2:
        st.markdown("""
        <div class="hud-card" style="margin-bottom: 15px;">
            <h4 style="color: #F8FAFC; margin-top: 0; font-size: 1rem;">Text Log Parser</h4>
            <p style="color: #94A3B8; font-size: 0.85rem;">Paste supplier lists or chat messages to parse items into structured format.</p>
        </div>
        """, unsafe_allow_html=True)
        
        raw_supplier_text = st.text_area("Paste raw text here...", height=120)
        if st.button("Parse Text"):
            if raw_supplier_text.strip() and api_key:
                with st.spinner("Parsing text..."):
                    try:
                        parsing_prompt = f"""
                        Extract all medications and return strictly as CSV with columns:
                        Brand Name, Active Salt / Generic Composition, Therapeutic Category, Primary Uses & Indications
                        
                        Text:
                        {raw_supplier_text}
                        """
                        parse_response = OpenAI(base_url="https://" + "api.groq.com/openai/v1", api_key=api_key).chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[{"role": "user", "content": parsing_prompt}],
                            stream=False
                        )
                        st.code(parse_response.choices[0].message.content, language="csv")
                        st.success("Parsed successfully.")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # --- SUB-TAB 3: BULK FILE IMPORTER ---
    with sub_tab3:
        uploaded_bulk_file = st.file_uploader("Upload File (.xlsx or .csv)", type=["xlsx", "csv"])
        if uploaded_bulk_file is not None:
            try:
                df_incoming = pd.read_csv(uploaded_bulk_file) if uploaded_bulk_file.name.endswith('.csv') else pd.read_excel(uploaded_bulk_file)
                st.dataframe(df_incoming.head(5), use_container_width=True)
                if st.button("Merge Spreadsheet"):
                    if df_master is not None:
                        combined_df = pd.concat([df_master, df_incoming], ignore_index=True).drop_duplicates()
                        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='w') as writer:
                            combined_df.to_excel(writer, sheet_name='Full Master Medicine List', startrow=3, index=False)
                        st.success(f"Merged successfully. Total records: {len(combined_df)}")
                        st.cache_data.clear()
            except PermissionError:
                st.error("File locked. Please close 'inventory.xlsx' in Microsoft Excel.")
            except Exception as e:
                st.error(f"Error: {e}")

    # --- SUB-TAB 4: LIVE BROWSER GRID ---
    with sub_tab4:
        if df_master is not None:
            empty_template = pd.DataFrame(columns=df_master.columns)
            edited_grid_df = st.data_editor(empty_template, num_rows="dynamic", use_container_width=True, height=250)
            if st.button("Commit Grid Rows"):
                valid_new_rows = edited_grid_df.dropna(how='all')
                if not valid_new_rows.empty:
                    updated_df = pd.concat([df_master, valid_new_rows], ignore_index=True).drop_duplicates()
                    try:
                        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='w') as writer:
                            updated_df.to_excel(writer, sheet_name='Full Master Medicine List', startrow=3, index=False)
                        st.success(f"Committed {len(valid_new_rows)} rows.")
                        st.cache_data.clear()
                    except PermissionError:
                        st.error("File locked. Please close 'inventory.xlsx' in Microsoft Excel.")
                    except Exception as e:
                        st.error(f"Error: {e}")

    # --- SUB-TAB 5: SINGLE ITEM FORM ---
    with sub_tab5:
        if df_master is not None:
            with st.form("add_single_form"):
                new_brand = st.text_input("Brand Name*")
                new_generic = st.text_input("Generic Salt")
                new_category = st.text_input("Category")
                new_uses = st.text_input("Primary Uses")
                if st.form_submit_button("Save Item"):
                    if new_brand:
                        cols = list(df_master.columns)
                        new_row = {col: "" for col in cols}
                        if len(cols) > 0: new_row[cols[0]] = new_brand.strip().title()
                        if len(cols) > 1: new_row[cols[1]] = new_generic
                        if len(cols) > 2: new_row[cols[2]] = new_category
                        if len(cols) > 3: new_row[cols[3]] = new_uses
                        
                        updated_df = pd.concat([df_master, pd.DataFrame([new_row])], ignore_index=True)
                        try:
                            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='w') as writer:
                                updated_df.to_excel(writer, sheet_name='Full Master Medicine List', startrow=3, index=False)
                            st.success(f"Committed '{new_brand}'.")
                            st.cache_data.clear()
                        except PermissionError:
                            st.error("File locked. Please close 'inventory.xlsx' in Microsoft Excel.")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Brand Name is required.")

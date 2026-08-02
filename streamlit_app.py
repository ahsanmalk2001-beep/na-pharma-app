import io
import os
import base64
import streamlit as st
import pandas as pd
from openai import OpenAI

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NA Pharma Care - Cinematic Terminal",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CINEMATIC CRIMSON & OBSIDIAN DESIGN SYSTEM ---
st.markdown("""
<style>
/* --- HIDE STREAMLIT BRANDING --- */
#MainMenu {visibility: hidden !important;}
header {visibility: hidden !important; background: transparent !important;}
footer {visibility: hidden !important; display: none !important;}
.stDeployButton {display: none !important;}
[data-testid="stToolbar"] {visibility: hidden !important;}

/* --- GLOBAL APP BACKGROUND (Cinematic Deep Black & Crimson Gradient) --- */
.stApp, html, body, [data-testid="stAppViewContainer"] {
    background-color: #050205 !important;
    background-image: radial-gradient(circle at 50% 20%, #160408 0%, #050205 70%) !important;
    color: #f1f5f9 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* --- STRUCTURAL CINEMATIC FRAMING LINES --- */
.stApp::before {
    content: "";
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background-image: linear-gradient(rgba(255, 30, 77, 0.03) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(255, 30, 77, 0.03) 1px, transparent 1px);
    background-size: 48px 48px;
    z-index: 0; pointer-events: none;
}

/* --- CINEMATIC STATUS BADGE --- */
.live-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(255, 30, 77, 0.08);
    border: 1px solid rgba(255, 30, 77, 0.3);
    padding: 6px 14px; border-radius: 4px;
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px;
    color: #ff1e4d;
}
.pulse-dot {
    width: 6px; height: 6px; background-color: #ff1e4d; border-radius: 50%;
    box-shadow: 0 0 10px rgba(255, 30, 77, 0.8);
    animation: livePulse 1.8s infinite ease-in-out;
}
@keyframes livePulse {
    0% { transform: scale(0.95); opacity: 0.7; }
    50% { transform: scale(1.2); opacity: 1; }
    100% { transform: scale(0.95); opacity: 0.7; }
}

/* --- OBSIDIAN GLASS CARDS WITH SHARP BORDERS --- */
.hud-card {
    background: rgba(12, 5, 8, 0.85) !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(255, 30, 77, 0.2) !important;
    border-radius: 6px !important;
    padding: 24px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.8) !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}
.hud-card:hover {
    border-color: rgba(255, 30, 77, 0.5) !important;
    box-shadow: 0 12px 40px rgba(255, 30, 77, 0.15) !important;
}

/* --- STRIKING CRIMSON BUTTONS --- */
.stButton button {
    background: #0f0407 !important;
    border: 1px solid rgba(255, 30, 77, 0.4) !important;
    border-radius: 4px !important;
    color: #f1f5f9 !important;
    font-weight: 700 !important;
    font-size: 0.82rem !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    transition: all 0.25s ease !important;
}
.stButton button:hover {
    background: #ff1e4d !important;
    border-color: #ff1e4d !important;
    color: #ffffff !important;
    box-shadow: 0 0 20px rgba(255, 30, 77, 0.6) !important;
}

/* --- COMMAND INPUT FIELDS --- */
[data-testid="stTextInput"] input {
    background: #080204 !important;
    border: 1px solid rgba(255, 30, 77, 0.35) !important;
    border-radius: 4px !important;
    color: #f1f5f9 !important;
    font-size: 1rem !important;
    padding: 14px 18px !important;
    transition: all 0.25s ease !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #ff1e4d !important;
    box-shadow: 0 0 0 2px rgba(255, 30, 77, 0.25) !important;
}

/* --- BOLD CINEMATIC HEADINGS --- */
.cinematic-title {
    margin: 0; font-weight: 900; font-size: 2.8rem !important; text-align: center;
    color: #ffffff;
    letter-spacing: -1px;
    text-transform: uppercase;
}
.cinematic-title span {
    color: #ff1e4d;
}

/* --- DATAFRAMES --- */
[data-testid="stDataFrame"] {
    background: rgba(8, 2, 4, 0.9) !important;
    border-radius: 4px !important;
    border: 1px solid rgba(255, 30, 77, 0.2) !important;
}
</style>
""", unsafe_allow_html=True)

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

# --- 5. CINEMATIC HEADER ---
st.markdown("""
<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 10px;">
    <div class="live-badge">
        <div class="pulse-dot"></div> Cinematic Matrix • Secure Live
    </div>
</div>
<div style="text-align: center; padding: 0 0 28px 0;">
    <h1 class="cinematic-title">NA Pharma <span>Care</span></h1>
    <p style="color: #94a3b8; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 3px; margin-top: 8px;">High-Speed Intelligence & Counter Terminal</p>
</div>
""", unsafe_allow_html=True)

# --- 6. TABS NAVIGATION ---
tab1, tab2 = st.tabs(["⚡ Command Center", "➕ Inventory Ingestion Hub"])

# --- TAB 1: COMMAND CENTER ---
with tab1:
    if not api_key:
        st.error("⚠️ GROQ_API_KEY missing in Streamlit secrets.")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        
        st.markdown("<p style='color: #ff1e4d; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 8px;'>Quick Symptom Filters:</p>", unsafe_allow_html=True)
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
            df_matches, context_data = perform_smart_inventory_search(df_master, active_query)

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
                with st.spinner("Analyzing matrix records..."):
                    try:
                        system_instruction = f"""
                        You are the internal clinical assistant for NA Pharma Care.
                        TOTAL INVENTORY: {total_meds_count} medications registered.
                        
                        RULES:
                        1. If medications appear in matches, they ARE IN STOCK.
                        2. Present each item clearly with clean line breaks.
                        
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
                        <div class="hud-card" style="margin-top: 10px; line-height: 1.6;">
                            {response.choices[0].message.content}
                        </div>
                        """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Neural Error: {e}")
        else:
            st.markdown("""
            <div class="hud-card" style="text-align: center; padding: 45px 20px; margin-top: 15px;">
                <h3 style="color: #ffffff; margin-bottom: 8px; font-weight: 700; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px;">Terminal Online</h3>
                <p style="color: #94a3b8; font-size: 0.88rem; max-width: 500px; margin: 0 auto;">Enter a search query above or select a quick filter to query the live inventory matrix.</p>
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
            <h4 style="color: #ffffff; margin-top: 0; font-size: 1rem;">Handwritten Document OCR</h4>
            <p style="color: #94a3b8; font-size: 0.85rem;">Upload an image of a handwritten list or prescription to automatically extract and review items.</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_handwriting_image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
        
        if uploaded_handwriting_image is not None:
            st.image(uploaded_handwriting_image, caption="Source Document", use_container_width=True)
            
            if st.button("Extract & Process Document"):
                if api_key:
                    with st.spinner("Decoding document..."):
                        try:
                            client_vision = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
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
                            cleaned_csv_text = decoded_csv.replace("```csv", "").replace("

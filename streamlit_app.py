import streamlit as st
import pandas as pd
from openai import OpenAI
import base64
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NA Pharma Care - Live Neural Terminal",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ADVANCED CYBER-CLINICAL HUD & DYNAMIC ANIMATIONS ---
st.markdown("""
<div class="animated-bg">
    <ul class="cube-container">
        <li></li><li></li><li></li><li></li><li></li>
        <li></li><li></li><li></li><li></li><li></li>
    </ul>
</div>

<div class="medical-toss">
    <span>💊</span><span>💉</span><span>🩺</span><span>💊</span><span>🩹</span>
    <span>🧬</span><span>💉</span><span>💊</span><span>🩺</span><span>🩹</span>
    <span>💊</span><span>💉</span><span>🩺</span><span>💊</span><span>🩹</span>
</div>

<div class="grid-overlay"></div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* --- HIDE STREAMLIT BRANDING --- */
#MainMenu {visibility: hidden !important;}
header {visibility: hidden !important; background: transparent !important;}
footer {visibility: hidden !important; display: none !important;}
.stDeployButton {display: none !important;}
[data-testid="stToolbar"] {visibility: hidden !important;}

/* --- TRANSPARENT LAYERS --- */
.stApp, html, body, [data-testid="stAppViewContainer"] {
    background: transparent !important;
    background-color: transparent !important;
    color: #ffffff !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* --- SUBTLE GRID OVERLAY (MAKES IT FEEL "ALIVE" & SCI-FI) --- */
.grid-overlay {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background-image: linear-gradient(rgba(0, 229, 255, 0.03) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(0, 229, 255, 0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    z-index: -997; pointer-events: none;
}

/* --- VIBRANT 3D BACKGROUND CUBES --- */
.animated-bg {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: linear-gradient(135deg, #05020c, #120724, #081128, #000c1c);
    background-size: 400% 400%;
    animation: gradientShift 18s ease infinite;
    z-index: -999; pointer-events: none;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.cube-container {
    position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; margin:0; padding:0;
}
.cube-container li {
    position: absolute; list-style: none; display: block;
    background: rgba(0, 229, 255, 0.08);
    border: 1px solid rgba(0, 229, 255, 0.4);
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.3), inset 0 0 10px rgba(0, 229, 255, 0.2);
    animation: float3D 22s linear infinite; bottom: -150px; border-radius: 8px;
}
.cube-container li:nth-child(even) {
    background: rgba(255, 0, 127, 0.08);
    border: 1px solid rgba(255, 0, 127, 0.4);
    box-shadow: 0 0 20px rgba(255, 0, 127, 0.3), inset 0 0 10px rgba(255, 0, 127, 0.2);
}

.cube-container li:nth-child(1) { left: 10%; width: 60px; height: 60px; animation-duration: 25s; animation-delay: 0s; }
.cube-container li:nth-child(2) { left: 25%; width: 30px; height: 30px; animation-duration: 16s; animation-delay: 2s; }
.cube-container li:nth-child(3) { left: 45%; width: 90px; height: 90px; animation-duration: 28s; animation-delay: 4s; }
.cube-container li:nth-child(4) { left: 65%; width: 45px; height: 45px; animation-duration: 20s; animation-delay: 0s; }
.cube-container li:nth-child(5) { left: 80%; width: 75px; height: 75px; animation-duration: 32s; animation-delay: 1s; }
.cube-container li:nth-child(6) { left: 15%; width: 50px; height: 50px; animation-duration: 19s; animation-delay: 5s; }
.cube-container li:nth-child(7) { left: 55%; width: 110px; height: 110px; animation-duration: 38s; animation-delay: 7s; }
.cube-container li:nth-child(8) { left: 35%; width: 25px; height: 25px; animation-duration: 14s; animation-delay: 3s; }
.cube-container li:nth-child(9) { left: 75%; width: 70px; height: 70px; animation-duration: 24s; animation-delay: 6s; }
.cube-container li:nth-child(10) { left: 90%; width: 40px; height: 40px; animation-duration: 15s; animation-delay: 2s; }

@keyframes float3D {
    0% { transform: translateY(0) rotateX(0deg) rotateY(0deg) rotateZ(0deg); opacity: 0; }
    15% { opacity: 0.8; }
    85% { opacity: 0.8; }
    100% { transform: translateY(-120vh) rotateX(360deg) rotateY(720deg) rotateZ(360deg); opacity: 0; }
}

/* --- MEDICAL TOSS ANIMATION --- */
.medical-toss {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    z-index: -998; pointer-events: none; overflow: hidden;
}
.medical-toss span {
    position: absolute; display: block; font-size: 2.5rem;
    animation: tossAndPile 3.2s cubic-bezier(0.2, 0.8, 0.2, 1) 1 forwards;
    top: -100px; opacity: 0; user-select: none;
    filter: drop-shadow(0 6px 12px rgba(0,0,0,0.7));
}
.medical-toss span:nth-child(1)  { left: 8%;  animation-delay: 0.05s; --land: 78vh; --rot: 480deg; }
.medical-toss span:nth-child(2)  { left: 15%; animation-delay: 0.15s; --land: 81vh; --rot: 610deg; }
.medical-toss span:nth-child(3)  { left: 22%; animation-delay: 0.08s; --land: 76vh; --rot: 390deg; }
.medical-toss span:nth-child(4)  { left: 30%; animation-delay: 0.22s; --land: 80vh; --rot: 720deg; }
.medical-toss span:nth-child(5)  { left: 38%; animation-delay: 0.12s; --land: 77vh; --rot: 510deg; }
.medical-toss span:nth-child(6)  { left: 45%; animation-delay: 0.25s; --land: 82vh; --rot: 450deg; }
.medical-toss span:nth-child(7)  { left: 52%; animation-delay: 0.02s; --land: 75vh; --rot: 650deg; }
.medical-toss span:nth-child(8)  { left: 60%; animation-delay: 0.18s; --land: 79vh; --rot: 580deg; }
.medical-toss span:nth-child(9)  { left: 68%; animation-delay: 0.10s; --land: 81vh; --rot: 340deg; }
.medical-toss span:nth-child(10) { left: 75%; animation-delay: 0.28s; --land: 77vh; --rot: 690deg; }
.medical-toss span:nth-child(11) { left: 82%; animation-delay: 0.06s; --land: 80vh; --rot: 530deg; }
.medical-toss span:nth-child(12) { left: 90%; animation-delay: 0.20s; --land: 76vh; --rot: 420deg; }
.medical-toss span:nth-child(13) { left: 18%; animation-delay: 0.30s; --land: 83vh; --rot: 600deg; }
.medical-toss span:nth-child(14) { left: 48%; animation-delay: 0.14s; --land: 84vh; --rot: 470deg; }
.medical-toss span:nth-child(15) { left: 72%; animation-delay: 0.24s; --land: 82vh; --rot: 550deg; }

@keyframes tossAndPile {
    0% { transform: translateY(0px) rotate(0deg) scale(0.5); opacity: 0; }
    15% { opacity: 1; }
    50% { transform: translateY(var(--land)) rotate(var(--rot)) scale(1.15); opacity: 1; }
    60% { transform: translateY(calc(var(--land) - 4vh)) rotate(calc(var(--rot) + 30deg)) scale(1); opacity: 1; }
    70% { transform: translateY(var(--land)) rotate(var(--rot)) scale(1); opacity: 1; }
    88% { transform: translateY(var(--land)) rotate(var(--rot)) scale(1); opacity: 1; }
    100% { transform: translateY(var(--land)) rotate(var(--rot)) scale(1); opacity: 0; }
}

/* --- LIVE PULSING HUD BADGE ---. */
.live-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(0, 229, 255, 0.1);
    border: 1px solid rgba(0, 229, 255, 0.5);
    padding: 6px 14px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1.5px;
    color: #00e5ff; box-shadow: 0 0 15px rgba(0, 229, 255, 0.2);
}
.pulse-dot {
    width: 8px; height: 8px; background-color: #00e5ff; border-radius: 50%;
    box-shadow: 0 0 10px #00e5ff;
    animation: livePulse 1.5s infinite ease-in-out;
}
@keyframes livePulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 229, 255, 0.7); }
    70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(0, 229, 255, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 229, 255, 0); }
}

/* --- HUD GLASS PANELS WITH HOVER GLOW --- */
.hud-card {
    background: rgba(12, 8, 25, 0.75) !important;
    backdrop-filter: blur(18px) !important;
    border: 1px solid rgba(0, 229, 255, 0.3) !important;
    border-radius: 16px !important;
    padding: 22px !important;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.7) !important;
    transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
.hud-card:hover {
    border-color: rgba(0, 229, 255, 0.7) !important;
    box-shadow: 0 15px 50px rgba(0, 229, 255, 0.25) !important;
    transform: translateY(-2px);
}

/* --- NEON BUTTONS & CHIPS --- */
.stButton button {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(0, 229, 255, 0.35) !important;
    border-radius: 12px !important;
    color: #00e5ff !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
.stButton button:hover {
    background: rgba(0, 229, 255, 0.2) !important;
    border-color: #00e5ff !important;
    box-shadow: 0 0 25px rgba(0, 229, 255, 0.8) !important;
    color: #ffffff !important;
    transform: scale(1.03) !important;
}

/* --- SPOTLIGHT SEARCH BAR --- */
[data-testid="stTextInput"] input {
    background: rgba(10, 5, 22, 0.9) !important;
    border: 1.5px solid rgba(0, 229, 255, 0.5) !important;
    border-radius: 14px !important;
    color: #ffffff !important;
    font-size: 1.05rem !important;
    padding: 14px 18px !important;
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.15), inset 0 0 10px rgba(0, 229, 255, 0.05) !important;
    transition: all 0.3s ease !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #00e5ff !important;
    box-shadow: 0 0 30px rgba(0, 229, 255, 0.5), inset 0 0 15px rgba(0, 229, 255, 0.2) !important;
}

/* --- GLOWING TITLE --- */
.glowing-title {
    margin: 0; font-weight: 900; font-size: 3.2rem !important; text-align: center;
    background: linear-gradient(90deg, #00e5ff, #ff007f, #00e5ff);
    background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: neonShine 3.5s linear infinite;
    text-shadow: 0 0 40px rgba(0, 229, 255, 0.5);
}
@keyframes neonShine {
    to { background-position: 200% center; }
}

/* --- DATA TABLES --- */
[data-testid="stDataFrame"] {
    background: rgba(10, 6, 20, 0.7) !important;
    backdrop-filter: blur(15px) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(0, 229, 255, 0.3) !important;
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

# --- 5. HEADER WITH LIVE BADGE ---
st.markdown("""
<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 5px;">
    <div class="live-badge">
        <div class="pulse-dot"></div> Live Neural Counter Terminal • Synced
    </div>
</div>
<div style="text-align: center; padding: 5px 0 20px 0;">
    <h1 class="glowing-title">NA Pharma Care</h1>
    <p style="color: #00e5ff; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 3px; margin-top: 5px;">Advanced Counter-Speed Intelligence Matrix</p>
</div>
""", unsafe_allow_html=True)

# --- 6. TABS NAVIGATION ---
tab1, tab2 = st.tabs(["⚡ Command Center", "➕ Add Med"])

# --- TAB 1: COMMAND CENTER (UNIFIED SEARCH & AI) ---
with tab1:
    if not api_key:
        st.error("⚠️ GROQ_API_KEY missing in Streamlit secrets.")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        
        # One-Tap Symptom Chips
        st.markdown("<p style='color: #00e5ff; font-size: 0.8rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;'>⚡ Instant Neural Symptom Chips:</p>", unsafe_allow_html=True)
        c1, c2, c3, c4, c5, c6 = st.columns([1,1,1,1,1,1.2])
        chip_query = None
        if c1.button("🩹 Pain"): chip_query = "pain"
        if c2.button("🤒 Fever"): chip_query = "fever"
        if c3.button("🤧 Cough"): chip_query = "cough"
        if c4.button("💊 Anti"): chip_query = "antibiotic"
        if c5.button("🤢 Stomach"): chip_query = "stomach"
        if c6.button("🧹 Clear Matrix"): chip_query = ""

        # Spotlight Search Bar
        search_input = st.text_input("🔍 Spotlight Command Search (Type brand, generic salt, or symptom e.g., 'fever')...", value=chip_query if chip_query is not None else "")
        active_query = search_input.strip()

        if active_query:
            total_meds_count = len(df_master) if df_master is not None else 0
            df_matches, context_data = perform_smart_inventory_search(df_master, active_query)

            col_left, col_right = st.columns([1.2, 1])

            with col_left:
                st.markdown("### 📦 Instant Inventory Matches")
                if not df_matches.empty:
                    st.success(f"🟢 Found {len(df_matches)} active options in inventory matrix!")
                    st.dataframe(df_matches, use_container_width=True, height=380)
                else:
                    st.warning(f"🔴 No direct matches for '{active_query}' in active inventory.")

            with col_right:
                st.markdown("### 🤖 Neural Clinical Guidance")
                with st.spinner("Processing live matrix query..."):
                    try:
                        system_instruction = f"""
                        You are the elite internal pharmacy assistant for NA Pharma Care counter terminal.
                        
                        TOTAL INVENTORY: {total_meds_count} medications registered.
                        
                        RULES:
                        1. If medications are found in the matches below, **they ARE IN STOCK**. Never claim stock is missing if items appear in matches.
                        2. ONLY state "⚠️ Not currently in stock" if matches state no records found.
                        3. **CRITICAL FORMATTING:** Present each matching medication on its **own separate new line** using a vertical bullet point (*). Ensure a strict line break before and after each item so they are easy to scan individually.
                        
                        --- MATCHED DATA ---
                        {context_data}
                        """
                        
                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=[
                                {"role": "system", "content": system_instruction},
                                {"role": "user", "content": f"Provide the availability and usage breakdown for: {active_query}"}
                            ],
                            stream=False
                        )
                        
                        # Wrapped inside an elite HUD card for realistic live feed look
                        st.markdown(f"""
                        <div class="hud-card" style="margin-top: 10px;">
                            {response.choices[0].message.content}
                        </div>
                        """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Neural Error: {e}")
        else:
            st.markdown("""
            <div class="hud-card" style="text-align: center; padding: 50px 20px; margin-top: 15px;">
                <h3 style="color: #00e5ff; margin-bottom: 12px; font-weight: 800; letter-spacing: 1px;">TERMINAL READY • WAITING FOR INPUT</h3>
                <p style="color: #a0aec0; font-size: 0.95rem; max-width: 600px; margin: 0 auto; line-height: 1.6;">Type any brand name, active generic salt, or symptom into the spotlight search above, or select a quick chip to query the live inventory matrix instantaneously.</p>
            </div>
            """, unsafe_allow_html=True)

# --- TAB 2: ADD MEDICINE ---
with tab2:
    st.markdown("### ➕ Register New Medicine into Matrix")
    if df_master is not None:
        with st.form("add_medicine_form"):
            new_brand = st.text_input("Brand Name / Medicine Name*")
            new_generic = st.text_input("Generic / Active Salt")
            new_category = st.text_input("Therapeutic Category")
            new_uses = st.text_input("Primary Uses (e.g., Headache, Fever, Pain, Cough)")
            
            cols = list(df_master.columns)
            submit_med = st.form_submit_button("Commit to Inventory File")
            
            if submit_med:
                if new_brand:
                    new_row_data = {col: "" for col in cols}
                    if len(cols) > 0: new_row_data[cols[0]] = new_brand
                    if len(cols) > 1: new_row_data[cols[1]] = new_generic
                    if len(cols) > 2: new_row_data[cols[2]] = new_category
                    if len(cols) > 3: new_row_data[cols[3]] = new_uses
                    
                    new_df = pd.DataFrame([new_row_data])
                    updated_df = pd.concat([df_master, new_df], ignore_index=True)
                    
                    try:
                        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='w') as writer:
                            updated_df.to_excel(writer, sheet_name='Full Master Medicine List', startrow=3, index=False)
                        st.success(f"✅ Successfully committed '{new_brand}' to inventory matrix!")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Commit error: {e}. Make sure inventory.xlsx is closed.")
                else:
                    st.warning("Brand Name is required.")
    else:
        st.info("ℹ️ inventory.xlsx not found.")

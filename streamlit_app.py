import io
import os
import base64
import streamlit as st
import pandas as pd
from openai import OpenAI

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NA Pharma Care - Futuristic AI Terminal",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CINEMATIC INTRO & FUTURISTIC DESIGN SYSTEM ---
st.markdown("""
<style>
/* --- HIDE STREAMLIT BRANDING --- */
#MainMenu {visibility: hidden !important;}
header {visibility: hidden !important; background: transparent !important;}
footer {visibility: hidden !important; display: none !important;}
.stDeployButton {display: none !important;}
[data-testid="stToolbar"] {visibility: hidden !important;}

/* --- GLOBAL APP BACKGROUND --- */
.stApp, html, body, [data-testid="stAppViewContainer"] {
    background-color: #030508 !important;
    background-image: 
        radial-gradient(circle at 50% 20%, rgba(0, 243, 255, 0.07) 0%, transparent 40%),
        radial-gradient(circle at 80% 80%, rgba(0, 255, 102, 0.05) 0%, transparent 40%),
        linear-gradient(135deg, #030508 0%, #0a0f1d 100%) !important;
    color: #F8FAFC !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}

/* --- CINEMATIC INTRO OVERLAY (NON-BLOCKING) ---
   Uses a CSS-only timed fade instead of a server-side time.sleep().
   "visibility" only changes at the final keyframe, so the overlay still
   blocks clicks while visible and stops blocking the instant it's gone -
   no JavaScript required, and the app underneath starts rendering immediately. */
@keyframes matrixZoom {
    0% { transform: scale(0.6); opacity: 0; filter: blur(10px); }
    50% { opacity: 1; filter: blur(0px); }
    100% { transform: scale(1); opacity: 1; filter: blur(0px); }
}
@keyframes splashFade {
    0% { opacity: 1; }
    78% { opacity: 1; }
    100% { opacity: 0; visibility: hidden; }
}
@keyframes loadBar {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}
.cinematic-splash {
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background: radial-gradient(circle at center, #0a1128 0%, #020408 100%);
    z-index: 999999; display: flex; flex-direction: column;
    justify-content: center; align-items: center; text-align: center;
    overflow: hidden; padding: 20px;
    animation: splashFade 1.6s ease-in-out forwards;
}
.cinematic-splash::after {
    content: " "; display: block; position: absolute; top: 0; left: 0; bottom: 0; right: 0;
    background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.25) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.06), rgba(0, 255, 0, 0.02), rgba(0, 0, 255, 0.06));
    z-index: 2000000; background-size: 100% 4px, 6px 100%; pointer-events: none;
}
.holo-text {
    font-weight: 900; font-size: 3.2rem !important;
    background: linear-gradient(135deg, #FFFFFF 0%, #00F3FF 50%, #00FF66 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-transform: uppercase; letter-spacing: 2px;
    animation: matrixZoom 1.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    filter: drop-shadow(0 0 25px rgba(0, 243, 255, 0.5));
    margin-bottom: 15px;
}
.holo-subtext {
    color: #94A3B8; font-size: 1rem; text-transform: uppercase;
    letter-spacing: 4px; font-weight: 600;
    animation: matrixZoom 1.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
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

/* --- GLASSMORPHISM CARDS --- */
@keyframes cardEnter {
    0% { opacity: 0; transform: translateY(8px); }
    100% { opacity: 1; transform: translateY(0); }
}
.hud-card {
    background: rgba(13, 20, 35, 0.75) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(0, 243, 255, 0.15) !important;
    border-radius: 8px !important;
    padding: 24px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5), inset 0 1px 1px rgba(255, 255, 255, 0.1) !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    animation: cardEnter 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
.hud-card:hover {
    border-color: rgba(0, 243, 255, 0.4) !important;
    box-shadow: 0 12px 40px rgba(0, 243, 255, 0.12), inset 0 1px 2px rgba(0, 243, 255, 0.2) !important;
    transform: translateY(-2px);
}
.hud-card {
    position: relative !important;
    overflow: hidden !important;
}
.hud-card::before {
    content: "";
    position: absolute; top: 0; left: -60%; width: 40%; height: 100%;
    background: linear-gradient(120deg, transparent, rgba(0, 243, 255, 0.12), transparent);
    transform: skewX(-20deg);
    transition: left 0.6s ease;
    pointer-events: none;
}
.hud-card:hover::before {
    left: 130%;
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
.stButton button:active {
    transform: scale(0.97) !important;
}
.stButton button {
    position: relative !important;
    overflow: hidden !important;
}
.stButton button::after {
    content: "";
    position: absolute; top: 0; left: -75%; width: 50%; height: 100%;
    background: linear-gradient(120deg, transparent, rgba(0, 243, 255, 0.25), transparent);
    transform: skewX(-20deg);
    transition: left 0.5s ease;
    pointer-events: none;
}
.stButton button:hover::after {
    left: 130%;
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
    background-size: 200% 200%;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    display: inline-block; padding: 4px 16px; letter-spacing: -1px;
    text-transform: uppercase; filter: drop-shadow(0 0 20px rgba(0, 243, 255, 0.3));
    animation: titleShift 6s ease-in-out infinite;
}
@keyframes titleShift {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

/* --- LIVE ANIMATED BACKDROP ---
   Pure CSS, transform/opacity driven (GPU-compositable), no JS particle
   engine, no extra network or Python work - this is decorative only and
   does not touch app logic or load time. */
.bg-fx {
    position: fixed; inset: 0; z-index: -1; pointer-events: none; overflow: hidden;
}
.bg-orb {
    position: absolute; border-radius: 50%; filter: blur(70px);
    will-change: transform;
}
.orb1 {
    width: 420px; height: 420px; top: -10%; left: -8%;
    background: radial-gradient(circle, rgba(0,243,255,0.22) 0%, rgba(0,243,255,0) 70%);
    animation: orbDrift1 22s ease-in-out infinite;
}
.orb2 {
    width: 380px; height: 380px; bottom: -12%; right: -6%;
    background: radial-gradient(circle, rgba(0,255,102,0.18) 0%, rgba(0,255,102,0) 70%);
    animation: orbDrift2 26s ease-in-out infinite;
}
.orb3 {
    width: 300px; height: 300px; top: 42%; left: 58%;
    background: radial-gradient(circle, rgba(140,100,255,0.16) 0%, rgba(140,100,255,0) 70%);
    animation: orbDrift3 30s ease-in-out infinite;
}
@keyframes orbDrift1 {
    0%, 100% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(60px, 40px) scale(1.15); }
}
@keyframes orbDrift2 {
    0%, 100% { transform: translate(0, 0) scale(1); }
    50% { transform: translate(-50px, -30px) scale(1.1); }
}
@keyframes orbDrift3 {
    0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.75; }
    50% { transform: translate(-40px, 50px) scale(0.9); opacity: 1; }
}

.bg-grid {
    position: absolute; inset: -60px;
    background-image:
        linear-gradient(rgba(0,243,255,0.05) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,243,255,0.05) 1px, transparent 1px);
    background-size: 48px 48px;
    animation: gridDrift 40s linear infinite;
    -webkit-mask-image: radial-gradient(circle at 50% 30%, rgba(0,0,0,0.9) 0%, transparent 72%);
    mask-image: radial-gradient(circle at 50% 30%, rgba(0,0,0,0.9) 0%, transparent 72%);
}
@keyframes gridDrift {
    0% { background-position: 0 0, 0 0; }
    100% { background-position: 480px 240px, 480px 240px; }
}

.bg-scanline {
    position: absolute; left: 0; width: 100%; height: 140px;
    background: linear-gradient(180deg, rgba(0,243,255,0) 0%, rgba(0,243,255,0.06) 50%, rgba(0,243,255,0) 100%);
    animation: scanMove 9s ease-in-out infinite;
    will-change: transform;
}
@keyframes scanMove {
    0% { transform: translateY(-20vh); }
    100% { transform: translateY(120vh); }
}

.bg-particles .p {
    position: absolute; width: 3px; height: 3px; border-radius: 50%;
    background: #00F3FF; box-shadow: 0 0 6px 1px rgba(0,243,255,0.8);
    opacity: 0; animation: particleFloat 8s ease-in-out infinite;
    will-change: transform, opacity;
}
@keyframes particleFloat {
    0% { transform: translateY(0); opacity: 0; }
    15% { opacity: 0.9; }
    85% { opacity: 0.5; }
    100% { transform: translateY(-90px); opacity: 0; }
}

/* --- DATAFRAMES --- */
[data-testid="stDataFrame"] {
    background: rgba(13, 20, 35, 0.85) !important;
    border-radius: 8px !important;
    border: 1px solid rgba(0, 243, 255, 0.2) !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
    animation: cardEnter 0.35s cubic-bezier(0.16, 1, 0.3, 1) !important;
}
</style>
""", unsafe_allow_html=True)

# --- LIVE ANIMATED BACKDROP ---
# Fixed, hand-picked particle positions/delays (not random) so the backdrop
# doesn't jump or reshuffle every time Streamlit reruns the script on a
# button click or text input - it just keeps animating smoothly in place.
st.markdown("""
<div class="bg-fx">
    <div class="bg-orb orb1"></div>
    <div class="bg-orb orb2"></div>
    <div class="bg-orb orb3"></div>
    <div class="bg-grid"></div>
    <div class="bg-scanline"></div>
    <div class="bg-particles">
        <span class="p" style="left:6%; top:82%; animation-delay:0.0s; animation-duration:7.5s;"></span>
        <span class="p" style="left:14%; top:35%; animation-delay:1.2s; animation-duration:8.5s;"></span>
        <span class="p" style="left:22%; top:66%; animation-delay:2.4s; animation-duration:6.8s;"></span>
        <span class="p" style="left:31%; top:18%; animation-delay:0.6s; animation-duration:9.2s;"></span>
        <span class="p" style="left:39%; top:74%; animation-delay:3.1s; animation-duration:7.0s;"></span>
        <span class="p" style="left:47%; top:44%; animation-delay:1.8s; animation-duration:8.0s;"></span>
        <span class="p" style="left:55%; top:88%; animation-delay:0.3s; animation-duration:7.8s;"></span>
        <span class="p" style="left:63%; top:28%; animation-delay:2.7s; animation-duration:9.5s;"></span>
        <span class="p" style="left:71%; top:60%; animation-delay:1.0s; animation-duration:6.5s;"></span>
        <span class="p" style="left:78%; top:15%; animation-delay:3.5s; animation-duration:8.3s;"></span>
        <span class="p" style="left:85%; top:70%; animation-delay:0.9s; animation-duration:7.2s;"></span>
        <span class="p" style="left:91%; top:40%; animation-delay:2.1s; animation-duration:9.0s;"></span>
        <span class="p" style="left:10%; top:52%; animation-delay:4.0s; animation-duration:8.8s;"></span>
        <span class="p" style="left:66%; top:80%; animation-delay:1.5s; animation-duration:7.4s;"></span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- SESSION STATE FOR CINEMATIC INTRO ---
# Rendered once per session. No time.sleep() and no st.rerun() here anymore -
# the CSS animation above (splashFade) handles the timed fade-out on its own,
# so the rest of the app starts rendering immediately instead of waiting on
# the server thread.
if 'intro_played' not in st.session_state:
    st.session_state.intro_played = True
    st.markdown("""
    <div class="cinematic-splash" id="splash-screen">
        <div>
            <div style="font-size: 3.5rem; margin-bottom: 10px;">🧬</div>
            <h1 class="holo-text">Welcome to NA Pharma Care AI</h1>
            <p class="holo-subtext">Initializing Holographic Medical Matrix...</p>
            <div style="margin-top: 30px;">
                <div style="width: 200px; height: 3px; background: rgba(255,255,255,0.1); margin: 0 auto; border-radius: 3px; overflow: hidden;">
                    <div style="width: 100%; height: 100%; background: linear-gradient(90deg, #00F3FF, #00FF66); animation: loadBar 1.2s cubic-bezier(0.16, 1, 0.3, 1) infinite;"></div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 3. HIGH-SPEED DATA LOADER ---
EXCEL_FILE = "inventory.xlsx"
SEARCH_BLOB_COL = "_search_blob"
api_key = st.secrets.get("GROQ_API_KEY")


@st.cache_data(show_spinner=False)
def load_inventory_data():
    if not os.path.exists(EXCEL_FILE):
        return None
    try:
        df_master = pd.read_excel(EXCEL_FILE, sheet_name='Full Master Medicine List', header=3)
        df_master.dropna(how='all', inplace=True)

        # Pre-build one lowercase "search blob" column combining every
        # searchable field. This is the expensive part of a text search
        # (casting every column to string), so we do it once here at load
        # time instead of redoing it inside every single search call.
        exclude_cols = ['Common Side Effects', 'Warnings & Contraindications', 'S.No', 'S. No']
        target_cols = [c for c in df_master.columns if c not in exclude_cols]
        df_master[SEARCH_BLOB_COL] = (
            df_master[target_cols].astype(str).agg(' | '.join, axis=1).str.lower()
        )
        return df_master
    except Exception:
        return None


df_master = load_inventory_data()


# --- 4. OPTIMIZED SMART SEARCH ALGORITHM ---
@st.cache_data(show_spinner=False)
def perform_smart_inventory_search(query_clean):
    global df_master
    if df_master is None or df_master.empty:
        return pd.DataFrame(), "Inventory is empty or uninitialized."

    # Single-column substring search against the precomputed blob -
    # equivalent in result to searching every column, but far cheaper
    # since no per-query string casting is needed.
    mask = df_master[SEARCH_BLOB_COL].str.contains(query_clean, case=False, na=False)
    matches = df_master[mask]

    display_cols = [c for c in ['Brand Name', 'Active Salt / Generic Composition', 'Therapeutic Category', 'Primary Uses & Indications'] if c in df_master.columns]

    if not matches.empty:
        result_df = matches[display_cols].head(15)
        return result_df, result_df.to_string(index=False)
    else:
        return pd.DataFrame(), "No exact or matching medications found in current inventory records."


# --- CACHED AI CLIENT ---
# Building an OpenAI/Groq client is cheap, but there's no reason to build a
# fresh one on every search, OCR call, and parse call within the same
# session - reuse a single cached instance instead.
@st.cache_resource(show_spinner=False)
def get_groq_client():
    return OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)


def commit_dataframe(updated_df: pd.DataFrame):
    """Write the master dataframe back to the Excel file, dropping the
    internal search-blob helper column first so it never leaks into the
    saved spreadsheet."""
    to_save = updated_df.drop(columns=[SEARCH_BLOB_COL], errors='ignore')
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='w') as writer:
        to_save.to_excel(writer, sheet_name='Full Master Medicine List', startrow=3, index=False)


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
        client = get_groq_client()

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
        active_query = search_input.strip().lower()

        if active_query:
            total_meds_count = len(df_master) if df_master is not None else 0

            # --- HIGH-PERFORMANCE INSTANT EXECUTION ---
            df_matches, context_data = perform_smart_inventory_search(active_query)

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
                with st.spinner("Synthesizing clinical data..."):
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
                            client_vision = get_groq_client()
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
                            cleaned_csv_text = decoded_csv.replace("```csv", "").replace("```", "").strip()
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
                        commit_dataframe(combined_df)
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
                        parse_response = get_groq_client().chat.completions.create(
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
                        commit_dataframe(combined_df)
                        st.success(f"Merged successfully. Total records: {len(combined_df)}")
                        st.cache_data.clear()
            except PermissionError:
                st.error("File locked. Please close 'inventory.xlsx' in Microsoft Excel.")
            except Exception as e:
                st.error(f"Error: {e}")

    # --- SUB-TAB 4: LIVE BROWSER GRID ---
    with sub_tab4:
        if df_master is not None:
            empty_template = pd.DataFrame(columns=[c for c in df_master.columns if c != SEARCH_BLOB_COL])
            edited_grid_df = st.data_editor(empty_template, num_rows="dynamic", use_container_width=True, height=250)
            if st.button("Commit Grid Rows"):
                valid_new_rows = edited_grid_df.dropna(how='all')
                if not valid_new_rows.empty:
                    updated_df = pd.concat([df_master, valid_new_rows], ignore_index=True).drop_duplicates()
                    try:
                        commit_dataframe(updated_df)
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
                        cols = [c for c in df_master.columns if c != SEARCH_BLOB_COL]
                        new_row = {col: "" for col in cols}
                        if len(cols) > 0: new_row[cols[0]] = new_brand.strip().title()
                        if len(cols) > 1: new_row[cols[1]] = new_generic
                        if len(cols) > 2: new_row[cols[2]] = new_category
                        if len(cols) > 3: new_row[cols[3]] = new_uses

                        updated_df = pd.concat([df_master, pd.DataFrame([new_row])], ignore_index=True)
                        try:
                            commit_dataframe(updated_df)
                            st.success(f"Committed '{new_brand}'.")
                            st.cache_data.clear()
                        except PermissionError:
                            st.error("File locked. Please close 'inventory.xlsx' in Microsoft Excel.")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Brand Name is required.")

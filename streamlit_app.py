import streamlit as st
import pandas as pd
from openai import OpenAI
import base64
import os

# --- 1. PAGE CONFIGURATION & 3D ANIMATED CSS ---
st.set_page_config(
    page_title="NA Pharma Care AI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Injecting 3D floating HTML shapes directly into the background
st.markdown("""
<div class="hologram-orb orb-1"></div>
<div class="hologram-orb orb-2"></div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* --- HIDE STREAMLIT BRANDING --- */
#MainMenu {visibility: hidden !important;}
header {visibility: hidden !important;}
footer {visibility: hidden !important; display: none !important;}
.stDeployButton {display: none !important;}
[data-testid="stToolbar"] {display: none !important;}
[data-testid="stDecoration"] {display: none !important;}

/* --- CORE APP BACKGROUND --- */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #030712 !important;
    color: #f8fafc !important;
    overflow-x: hidden !important;
}

/* --- 3D MOVING CYBER-GRID (PARALLAX FLOOR) --- */
.stApp::before {
    content: '';
    position: fixed;
    top: 0; left: -50vw;
    width: 200vw; height: 200vh;
    background-image: 
        linear-gradient(rgba(16, 185, 129, 0.15) 2px, transparent 2px),
        linear-gradient(90deg, rgba(16, 185, 129, 0.15) 2px, transparent 2px);
    background-size: 80px 80px;
    transform: perspective(600px) rotateX(60deg) translateY(-100px) translateZ(-200px);
    animation: gridScroll 10s linear infinite;
    z-index: -3;
    pointer-events: none;
}

@keyframes gridScroll {
    0% { transform: perspective(600px) rotateX(60deg) translateY(0) translateZ(-200px); }
    100% { transform: perspective(600px) rotateX(60deg) translateY(80px) translateZ(-200px); }
}

/* --- 3D MORPHING LIQUID ORBS --- */
.hologram-orb {
    position: fixed;
    border-radius: 50%;
    filter: blur(80px);
    z-index: -2;
    pointer-events: none;
    opacity: 0.45;
}

.orb-1 {
    top: -10%; left: -10%;
    width: 500px; height: 500px;
    background: linear-gradient(135deg, #0ea5e9, #10b981);
    animation: liquidSpin 20s infinite linear alternate, orbFloat 15s infinite ease-in-out;
}

.orb-2 {
    bottom: -10%; right: -10%;
    width: 600px; height: 600px;
    background: linear-gradient(135deg, #ec4899, #8b5cf6);
    animation: liquidSpin 25s infinite linear alternate-reverse, orbFloat 18s infinite ease-in-out reverse;
}

@keyframes liquidSpin {
    0% { transform: perspective(1000px) rotateX(0deg) rotateY(0deg) scale(1); border-radius: 40% 60% 70% 30% / 40% 50% 60% 50%; }
    100% { transform: perspective(1000px) rotateX(180deg) rotateY(360deg) scale(1.2); border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
}

@keyframes orbFloat {
    0% { top: -10%; left: -10%; }
    50% { top: 20%; left: 10%; }
    100% { top: -5%; left: -15%; }
}

/* --- HIGH-END GLASSMORPHISM FOR PANELS --- */
div[data-testid="stAppViewBlockContainer"] {
    padding: 20px !important; 
    max-width: 95% !important;
    z-index: 1;
}

[data-testid="stChatMessageContent"] {
    background: rgba(15, 23, 42, 0.4) !important;
    backdrop-filter: blur(25px) !important;
    -webkit-backdrop-filter: blur(25px) !important;
    border-top: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-left: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.5) !important;
    border-right: 1px solid rgba(0, 0, 0, 0.5) !important;
    border-radius: 16px !important;
    padding: 16px !important; 
    box-shadow: 10px 15px 35px rgba(0, 0, 0, 0.4) !important;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
    transform-style: preserve-3d;
}

/* 3D TILT HOVER EFFECT ON CHAT */
[data-testid="stChatMessageContent"]:hover {
    transform: perspective(1000px) scale(1.02) rotateX(3deg) rotateY(-3deg) !important;
    box-shadow: -15px 25px 45px rgba(16, 185, 129, 0.2) !important;
    border-top: 1px solid rgba(16, 185, 129, 0.5) !important;
}

/* --- TACTICAL 3D BUTTONS --- */
.stButton button {
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.6), rgba(15, 23, 42, 0.8)) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px) !important;
    transition: all 0.3s ease-in-out !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.3) !important;
    color: #e2e8f0 !important;
    font-weight: bold !important;
}

.stButton button:hover {
    transform: perspective(500px) translateZ(20px) translateY(-3px) scale(1.05) !important;
    box-shadow: 0 15px 30px rgba(59, 130, 246, 0.4), inset 0 0 15px rgba(16, 185, 129, 0.3) !important;
    border-color: rgba(16, 185, 129, 0.8) !important;
    color: #fff !important;
}

/* --- NEON SHINING HEADER --- */
.animated-title {
    margin:0; 
    font-weight: 900; 
    font-size: 3rem !important;
    letter-spacing: -1px;
    background: linear-gradient(90deg, #0ea5e9, #10b981, #ec4899, #0ea5e9);
    background-size: 300% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: textShine 4s linear infinite;
    text-shadow: 0 10px 30px rgba(16, 185, 129, 0.2);
}

@keyframes textShine {
    to { background-position: 300% center; }
}

/* Table styling for dark UI */
[data-testid="stDataFrame"] {
    background: rgba(15, 23, 42, 0.6) !important;
    backdrop-filter: blur(20px) !important;
    border-radius: 12px !important;
    padding: 10px;
    border: 1px solid rgba(255,255,255,0.05) !important;
}
</style>
""", unsafe_allow_html=True)

# --- 2. HIGH-SPEED DATA LOADER ---
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
        st.error(f"Error loading Excel file: {e}")
        return None

df_master = load_inventory_data()

# --- 3. HELPER FUNCTIONS ---
def generate_cleaned_content(response):
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

# --- 4. HEADER ---
st.markdown("""
<div style="text-align: center; padding: 20px 0 40px 0;">
    <h1 class="animated-title">NA Pharma Care AI</h1>
    <p style="color: #94a3b8; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 2px;">Smart Internal Pharmacy Terminal</p>
</div>
""", unsafe_allow_html=True)

# --- 5. TABS NAVIGATION ---
tab1, tab2, tab3, tab4 = st.tabs(["🤖 AI & Vision", "📚 Database", "🧾 Bill Calc", "➕ Add Med"])

# --- TAB 1: AI ASSISTANT & VISION ---
with tab1:
    if not api_key:
        st.error("⚠️ GROQ_API_KEY is missing in Streamlit secrets.")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Quick Actions
        cols = st.columns([1,1,1,1,1.5])
        selected_prompt = None
        if cols[0].button("🩹 Pain"): selected_prompt = "Find pain relief medicines in stock."
        if cols[1].button("🤒 Fever"): selected_prompt = "Find fever medications in stock."
        if cols[2].button("🤧 Cold"): selected_prompt = "Find cold and allergy stock."
        if cols[3].button("💊 Anti"): selected_prompt = "Find antibiotics in stock."
        if cols[4].button("🧹 Clear Chat"): 
            st.session_state.messages = []
            st.rerun()

        # Prescription / Medicine Image Upload
        uploaded_img = st.file_uploader("📷 Upload Prescription or Medicine Image", type=["png", "jpg", "jpeg"])
        
        # Chat History Container
        chat_container = st.container(height=400)
        with chat_container:
            for message in st.session_state.messages:
                avatar_icon = "👨‍⚕️" if message["role"] == "assistant" else "👤"
                with st.chat_message(message["role"], avatar=avatar_icon):
                    if isinstance(message["content"], list):
                        st.markdown(message["content"][0]["text"])
                    else:
                        st.markdown(message["content"])

        user_input = st.chat_input("Ask AI, search symptoms, or analyze image...")
        prompt = selected_prompt or user_input

        if prompt:
            # Vision vs Text model selector
            if uploaded_img:
                base64_img = encode_image(uploaded_img)
                user_content = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                ]
                selected_model = "llama-3.2-11b-vision-preview"
            else:
                user_content = prompt
                selected_model = "llama-3.1-8b-instant"

            st.session_state.messages.append({"role": "user", "content": user_content})
            
            with chat_container:
                with st.chat_message("user", avatar="👤"):
                    st.markdown(prompt)
                    if uploaded_img:
                        st.image(uploaded_img, width=150)

                with st.chat_message("assistant", avatar="👨‍⚕️"):
                    with st.spinner("Analyzing inventory..."):
                        try:
                            context_data = "No specific medication matches found for this query."
                            total_meds_count = len(df_master) if df_master is not None else 0
                            
                            # Filter inventory for context (Excluding side effects column)
                            if df_master is not None and not uploaded_img: 
                                search_words = [w for w in prompt.lower().split() if len(w) > 3]
                                exclude_cols = ['Common Side Effects', 'Warnings & Contraindications', 'S.No', 'S. No']
                                target_cols = [c for c in df_master.columns if c not in exclude_cols]
                                
                                if search_words:
                                    mask = pd.Series([False] * len(df_master))
                                    for word in search_words:
                                        mask = mask | df_master[target_cols].astype(str).apply(lambda x: x.str.contains(word, case=False, na=False)).any(axis=1)
                                    matches = df_master[mask]
                                    if not matches.empty:
                                        display_cols = [c for c in ['Brand Name', 'Active Salt / Generic Composition', 'Therapeutic Category', 'Primary Uses & Indications'] if c in df_master.columns]
                                        context_data = matches[display_cols].head(10).to_string(index=False)

                            system_instruction = f"""
                            You are the internal pharmacy AI assistant for NA Pharma Care.
                            
                            CURRENT DATABASE STATS:
                            - Total medications registered in inventory: {total_meds_count}
                            
                            STRICT RULES:
                            1. If the user asks how many medications or items are in stock, inform them directly that there are {total_meds_count} total medications registered in our inventory.
                            2. Check the "SEARCH MATCHES" below for specific medicine or symptom queries.
                            3. If a requested medicine or symptom treatment IS in our inventory, list those specific available brand names clearly.
                            4. If a requested medicine is NOT in our inventory, explicitly state: "⚠️ Not currently in stock in our branch" before offering alternatives.
                            5. Format responses cleanly with short bullet points.
                            
                            --- SEARCH MATCHES ---
                            {context_data}
                            """

                            messages_payload = [{"role": "system", "content": system_instruction}]
                            for m in st.session_state.messages[-3:]: 
                                messages_payload.append(m)

                            response = client.chat.completions.create(
                                model=selected_model,
                                messages=messages_payload,
                                stream=True
                            )
                            
                            answer = st.write_stream(generate_cleaned_content(response))
                            st.session_state.messages.append({"role": "assistant", "content": answer})
                        
                        except Exception as e:
                            st.error(f"Processing Error: {e}")

# --- TAB 2: DIRECT MEDICINE DATABASE LOOKUP ---
with tab2:
    st.markdown("### 📦 Direct Medicine Lookup")
    
    if df_master is not None:
        search_term = st.text_input("🔍 Search symptom, category, or medicine (e.g., 'Headache', 'Pain', 'Allergy')...", "")
        
        essential_cols = [c for c in ['Brand Name', 'Active Salt / Generic Composition', 'Therapeutic Category', 'Primary Uses & Indications'] if c in df_master.columns]
        display_cols = essential_cols if essential_cols else df_master.columns[:4]
        exclude_from_search = ['Common Side Effects', 'Warnings & Contraindications', 'S.No', 'S. No']
        search_target_cols = [c for c in df_master.columns if c not in exclude_from_search]

        show_full_details = st.checkbox("Show full technical details", value=False)

        if search_term:
            mask = df_master[search_target_cols].astype(str).apply(
                lambda x: x.str.contains(search_term, case=False, na=False)
            ).any(axis=1)
            
            filtered_df = df_master[mask]
            
            if not filtered_df.empty:
                st.success(f"Found {len(filtered_df)} direct matching medications:")
                if show_full_details:
                    st.dataframe(filtered_df, use_container_width=True)
                else:
                    st.dataframe(filtered_df[display_cols], use_container_width=True)
            else:
                st.warning(f"No medications found directly treating or matching '{search_term}'.")
        else:
            if show_full_details:
                st.dataframe(df_master, use_container_width=True)
            else:
                st.dataframe(df_master[display_cols], use_container_width=True)
    else:
        st.info("ℹ️ inventory.xlsx file not found.")

# --- TAB 3: BILL CALCULATOR ---
with tab3:
    st.markdown("### 🧾 Bill Estimator")
    if df_master is not None and len(df_master.columns) > 0:
        med_col = "Brand Name" if "Brand Name" in df_master.columns else df_master.columns[0]
        medicine_list = df_master[med_col].dropna().unique().tolist()
        selected_meds = st.multiselect("Select Medicines:", medicine_list)
        
        if selected_meds:
            total_amount = 0.0
            for med in selected_meds:
                col_n, col_p, col_q = st.columns([2, 1, 1])
                with col_n: st.write(f"**{med}**")
                with col_p: price = st.number_input(f"Price (Rs)", min_value=0.0, value=100.0, step=10.0, key=f"p_{med}")
                with col_q: qty = st.number_input(f"Qty", min_value=1, value=1, step=1, key=f"q_{med}")
                total_amount += (price * qty)
            st.markdown(f"<h2 style='color: #10b981; text-shadow: 0 0 20px rgba(16, 185, 129, 0.4);'>Total Bill: Rs. {total_amount:,.2f}</h2>", unsafe_allow_html=True)

# --- TAB 4: ADD NEW MEDICINE ---
with tab4:
    st.markdown("### ➕ Add Medicine to Inventory")
    if df_master is not None:
        with st.form("add_medicine_form"):
            new_brand = st.text_input("Brand Name / Medicine Name*")
            new_generic = st.text_input("Generic / Active Salt")
            new_category = st.text_input("Therapeutic Category")
            new_uses = st.text_input("Primary Uses (e.g., Headache, Fever, Pain)")
            
            cols = list(df_master.columns)
            submit_med = st.form_submit_button("Save to Inventory File")
            
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
                        
                        st.success(f"✅ Successfully added '{new_brand}' to the database!")
                        st.cache_data.clear() 
                        
                    except Exception as e:
                        st.error(f"Could not save file: {e}. Please make sure inventory.xlsx is closed on your PC.")
                else:
                    st.warning("Brand Name is required.")
    else:
        st.info("ℹ️ Load or create inventory.xlsx first.")

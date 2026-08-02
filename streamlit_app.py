import streamlit as st
import pandas as pd
from openai import OpenAI
import base64
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NA Pharma Care AI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. LIVE DYNAMIC MEDICAL DEBRIS DROP & PILE-UP EFFECT ---
st.markdown("""
<div class="debris-container">
    <span style="--x: 5%; --delay: 0.1s; --rot: 45deg;">💊</span>
    <span style="--x: 12%; --delay: 0.4s; --rot: -30deg;">💉</span>
    <span style="--x: 20%; --delay: 0.2s; --rot: 90deg;">🩺</span>
    <span style="--x: 28%; --delay: 0.6s; --rot: -120deg;">🩹</span>
    <span style="--x: 35%; --delay: 0.3s; --rot: 15deg;">🧬</span>
    <span style="--x: 42%; --delay: 0.7s; --rot: -60deg;">💊</span>
    <span style="--x: 50%; --delay: 0.15s; --rot: 180deg;">💉</span>
    <span style="--x: 58%; --delay: 0.5s; --rot: -15deg;">🩺</span>
    <span style="--x: 65%; --delay: 0.35s; --rot: 110deg;">🩹</span>
    <span style="--x: 72%; --delay: 0.8s; --rot: -90deg;">💊</span>
    <span style="--x: 80%; --delay: 0.25s; --rot: 30deg;">🧬</span>
    <span style="--x: 88%; --delay: 0.55s; --rot: -45deg;">💉</span>
    <span style="--x: 95%; --delay: 0.05s; --rot: 75deg;">🩺</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* --- HIDE STREAMLIT BRANDING --- */
#MainMenu {visibility: hidden !important;}
header {visibility: hidden !important; background: transparent !important;}
footer {visibility: hidden !important; display: none !important;}
.stDeployButton {display: none !important;}
[data-testid="stToolbar"] {visibility: hidden !important;}

/* --- FORCE TRANSPARENT STREAMLIT LAYERS --- */
.stApp, html, body, [data-testid="stAppViewContainer"] {
    background: transparent !important;
    background-color: transparent !important;
    color: #ffffff !important;
}

/* --- DYNAMIC BACKGROUND & REALISTIC THROW / PILE EFFECT --- */
.debris-container {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background: linear-gradient(135deg, #050511, #120826, #0a192f, #000c18);
    background-size: 400% 400%;
    animation: gradientShift 15s ease infinite;
    z-index: -999;
    overflow: hidden;
    pointer-events: none;
}

@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.debris-container span {
    position: absolute;
    display: block;
    font-size: 2.2rem;
    left: var(--x);
    top: -10vh;
    opacity: 0;
    animation: throwAndPile 4s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    animation-delay: var(--delay);
    user-select: none;
    z-index: -998;
}

@keyframes throwAndPile {
    0% {
        top: -10vh;
        opacity: 0;
        transform: translateY(0) rotate(0deg) scale(1.2);
    }
    10% {
        opacity: 1;
    }
    /* Fast gravity drop ending up right at the bottom screen bounds */
    70% {
        top: 88vh;
        opacity: 1;
        transform: translateY(0) rotate(var(--rot)) scale(1);
    }
    /* Settle into a junk pile */
    82% {
        top: 86vh;
        opacity: 1;
        transform: translateY(0) rotate(calc(var(--rot) + 10deg)) scale(0.95);
    }
    /* Fade out / disappear cleanly after sitting as junk */
    92% {
        top: 86vh;
        opacity: 0.8;
        transform: scale(0.9);
    }
    100% {
        top: 86vh;
        opacity: 0;
        transform: scale(0.5);
    }
}

/* --- GLASSMORPHISM UI PANELS --- */
[data-testid="stChatMessageContent"] {
    background: rgba(15, 10, 30, 0.65) !important;
    backdrop-filter: blur(14px) !important;
    border: 1px solid rgba(0, 229, 255, 0.3) !important;
    border-radius: 16px !important;
    padding: 16px !important; 
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.6) !important;
    transition: all 0.3s ease !important;
}

[data-testid="stChatMessageContent"]:hover {
    transform: translateY(-5px) !important;
    box-shadow: 0 12px 40px rgba(0, 229, 255, 0.4) !important;
    border-color: rgba(0, 229, 255, 0.9) !important;
}

/* --- NEON BUTTONS --- */
.stButton button {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(0, 229, 255, 0.4) !important;
    border-radius: 12px !important;
    color: #00e5ff !important;
    font-weight: bold !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    transition: all 0.3s ease !important;
}

.stButton button:hover {
    background: rgba(0, 229, 255, 0.2) !important;
    border-color: #00e5ff !important;
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.7) !important;
    color: #ffffff !important;
    transform: scale(1.05) !important;
}

/* --- TEXT INPUT & TABS --- */
[data-testid="stChatInput"] {
    background: rgba(10, 5, 20, 0.85) !important;
    border: 1px solid rgba(255, 0, 127, 0.6) !important;
    box-shadow: 0 0 15px rgba(255, 0, 127, 0.3) !important;
    border-radius: 12px !important;
}

[data-baseweb="tab"] {
    background: transparent !important;
    color: #b3b3b3 !important;
}
[data-baseweb="tab"][aria-selected="true"] {
    color: #00e5ff !important;
    border-bottom-color: #00e5ff !important;
    text-shadow: 0 0 10px rgba(0, 229, 255, 0.6) !important;
}

/* --- SUPER GLOWING HEADER --- */
.glowing-title {
    margin: 0; 
    font-weight: 900; 
    font-size: 3.5rem !important;
    text-align: center;
    background: linear-gradient(90deg, #00e5ff, #ff007f, #00e5ff);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: neonShine 3s linear infinite;
    text-shadow: 0 0 30px rgba(0, 229, 255, 0.4);
}

@keyframes neonShine {
    to { background-position: 200% center; }
}

/* Table styling */
[data-testid="stDataFrame"] {
    background: rgba(15, 10, 30, 0.6) !important;
    backdrop-filter: blur(15px) !important;
    border-radius: 12px !important;
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
        st.error(f"Error loading Excel file: {e}")
        return None

df_master = load_inventory_data()

# --- 4. HELPER FUNCTIONS ---
def generate_cleaned_content(response):
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

# --- 5. HEADER ---
st.markdown("""
<div style="text-align: center; padding: 20px 0 40px 0;">
    <h1 class="glowing-title">NA Pharma Care AI</h1>
    <p style="color: #00e5ff; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 2px;">Smart Internal Pharmacy Terminal</p>
</div>
""", unsafe_allow_html=True)

# --- 6. TABS NAVIGATION ---
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

        uploaded_img = st.file_uploader("📷 Upload Prescription or Medicine Image", type=["png", "jpg", "jpeg"])
        
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
        search_term = st.text_input("🔍 Search symptom, category, or medicine...", "")
        
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
            st.markdown(f"<h2 style='color: #00e5ff; text-shadow: 0 0 20px rgba(0, 229, 255, 0.4);'>Total Bill: Rs. {total_amount:,.2f}</h2>", unsafe_allow_html=True)

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

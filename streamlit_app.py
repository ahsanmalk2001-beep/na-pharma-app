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

# --- 2. 3D BACKGROUND CUBES + ONE-TIME REALISTIC THROW & PILE ANIMATION ---
st.markdown("""
<div class="animated-bg">
    <ul class="cube-container">
        <li></li><li></li><li></li><li></li><li></li>
        <li></li><li></li><li></li><li></li><li></li>
    </ul>
</div>

<div class="medical-toss">
    <span>💊</span>
    <span>💉</span>
    <span>🩺</span>
    <span>💊</span>
    <span>🩹</span>
    <span>🧬</span>
    <span>💉</span>
    <span>💊</span>
    <span>🩺</span>
    <span>🩹</span>
    <span>💊</span>
    <span>💉</span>
    <span>🩺</span>
    <span>💊</span>
    <span>🩹</span>
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

/* --- VIBRANT 3D BACKGROUND CUBES --- */
.animated-bg {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    background: linear-gradient(135deg, #09031a, #1a0b2e, #0f1c3f, #001429);
    background-size: 400% 400%;
    animation: gradientShift 15s ease infinite;
    z-index: -999;
    pointer-events: none;
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
    background: rgba(0, 229, 255, 0.1);
    border: 1px solid rgba(0, 229, 255, 0.5);
    box-shadow: 0 0 15px rgba(0, 229, 255, 0.5), inset 0 0 15px rgba(0, 229, 255, 0.3);
    animation: float3D 20s linear infinite;
    bottom: -150px;
    border-radius: 8px;
}

.cube-container li:nth-child(even) {
    background: rgba(255, 0, 127, 0.1);
    border: 1px solid rgba(255, 0, 127, 0.5);
    box-shadow: 0 0 15px rgba(255, 0, 127, 0.5), inset 0 0 15px rgba(255, 0, 127, 0.3);
}

.cube-container li:nth-child(1) { left: 10%; width: 60px; height: 60px; animation-duration: 25s; animation-delay: 0s; }
.cube-container li:nth-child(2) { left: 25%; width: 30px; height: 30px; animation-duration: 15s; animation-delay: 2s; }
.cube-container li:nth-child(3) { left: 45%; width: 100px; height: 100px; animation-duration: 30s; animation-delay: 4s; }
.cube-container li:nth-child(4) { left: 65%; width: 45px; height: 45px; animation-duration: 20s; animation-delay: 0s; }
.cube-container li:nth-child(5) { left: 80%; width: 80px; height: 80px; animation-duration: 35s; animation-delay: 1s; }
.cube-container li:nth-child(6) { left: 15%; width: 50px; height: 50px; animation-duration: 18s; animation-delay: 5s; }
.cube-container li:nth-child(7) { left: 55%; width: 120px; height: 120px; animation-duration: 40s; animation-delay: 7s; }
.cube-container li:nth-child(8) { left: 35%; width: 25px; height: 25px; animation-duration: 12s; animation-delay: 3s; }
.cube-container li:nth-child(9) { left: 75%; width: 70px; height: 70px; animation-duration: 22s; animation-delay: 6s; }
.cube-container li:nth-child(10) { left: 90%; width: 40px; height: 40px; animation-duration: 14s; animation-delay: 2s; }

@keyframes float3D {
    0% { transform: translateY(0) rotateX(0deg) rotateY(0deg) rotateZ(0deg); opacity: 0; }
    10% { opacity: 1; }
    90% { opacity: 1; }
    100% { transform: translateY(-120vh) rotateX(360deg) rotateY(720deg) rotateZ(360deg); opacity: 0; }
}

/* --- REALISTIC ONE-TIME THROW, BOUNCE & PILE ANIMATION --- */
.medical-toss {
    position: fixed;
    top: 0; left: 0; width: 100vw; height: 100vh;
    z-index: -998;
    pointer-events: none;
    overflow: hidden;
}

.medical-toss span {
    position: absolute;
    display: block;
    font-size: 2.5rem;
    animation: tossAndPile 3.2s cubic-bezier(0.2, 0.8, 0.2, 1) 1 forwards;
    top: -100px;
    opacity: 0;
    user-select: none;
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

def perform_smart_inventory_search(df, query):
    """Enhanced precise search algorithm targeting Brand Name, Generic Salt, and Uses."""
    if df is None or df.empty:
        return "Inventory is empty or uninitialized."
    
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
        
    if not matches.empty:
        display_cols = [c for c in ['Brand Name', 'Active Salt / Generic Composition', 'Therapeutic Category', 'Primary Uses & Indications'] if c in df.columns]
        return matches[display_cols].head(15).to_string(index=False)
    else:
        return "No exact or matching medications found in current inventory records."

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

        user_input = st.chat_input("Ask AI, search exact medicine or symptom...")
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
                    with st.spinner("Searching enhanced inventory records..."):
                        try:
                            total_meds_count = len(df_master) if df_master is not None else 0
                            context_data = perform_smart_inventory_search(df_master, prompt) if (df_master is not None and not uploaded_img) else "Image analyzed or general query."

                            # FORCED VERTICAL BULLET FORMATTING INSTRUCTION
                            system_instruction = f"""
                            You are the precise internal pharmacy AI assistant for NA Pharma Care.
                            
                            CURRENT DATABASE STATS:
                            - Total medications registered in inventory: {total_meds_count}
                            
                            STRICT RULES FOR ACCURACY AND FORMATTING:
                            1. If the user asks how many medications or items are in stock, state exactly that there are {total_meds_count} total medications registered in our inventory.
                            2. The table under "EXACT INVENTORY MATCHES" below contains the medications found in our database for the user's query.
                            3. If medications are listed in the matches below, **they ARE IN STOCK in our branch**. Never claim items shown in the inventory matches are out of stock.
                            4. ONLY if the matches below explicitly state "No exact or matching medications found", you should state: "⚠️ Not currently in stock in our branch".
                            5. **CRITICAL FORMATTING RULE:** You must present each matching medication on its **own separate new line** using a vertical bullet point (`*`). Never bunch medications together into a single paragraph or inline list. Each item must have a line break before and after it so it reads cleanly.
                            
                            --- EXACT INVENTORY MATCHES ---
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
    st.markdown("### 📦 Enhanced Direct Medicine Lookup")
    
    if df_master is not None:
        search_term = st.text_input("🔍 Type exact brand name, active salt, or use...", "")
        
        essential_cols = [c for c in ['Brand Name', 'Active Salt / Generic Composition', 'Therapeutic Category', 'Primary Uses & Indications'] if c in df_master.columns]
        display_cols = essential_cols if essential_cols else df_master.columns[:4]
        
        show_full_details = st.checkbox("Show full technical details", value=False)

        if search_term:
            brand_col = 'Brand Name' if 'Brand Name' in df_master.columns else df_master.columns[0]
            salt_col = 'Active Salt / Generic Composition' if 'Active Salt / Generic Composition' in df_master.columns else None
            
            q_clean = search_term.lower().strip()
            filtered_df = pd.DataFrame()
            
            if brand_col in df_master.columns:
                b_match = df_master[df_master[brand_col].astype(str).str.contains(q_clean, case=False, na=False)]
                filtered_df = pd.concat([filtered_df, b_match]).drop_duplicates()
            if salt_col and salt_col in df_master.columns:
                s_match = df_master[df_master[salt_col].astype(str).str.contains(q_clean, case=False, na=False)]
                filtered_df = pd.concat([filtered_df, s_match]).drop_duplicates()
                
            if filtered_df.empty:
                exclude_from_search = ['Common Side Effects', 'Warnings & Contraindications', 'S.No', 'S. No']
                search_target_cols = [c for c in df_master.columns if c not in exclude_from_search]
                mask = df_master[search_target_cols].astype(str).apply(
                    lambda x: x.str.contains(q_clean, case=False, na=False)
                ).any(axis=1)
                filtered_df = df_master[mask]
            
            if not filtered_df.empty:
                st.success(f"Found {len(filtered_df)} exact matching medications in inventory:")
                if show_full_details:
                    st.dataframe(filtered_df, use_container_width=True)
                else:
                    st.dataframe(filtered_df[display_cols], use_container_width=True)
            else:
                st.warning(f"No medications found matching '{search_term}' in inventory.")
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

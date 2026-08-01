import streamlit as st
import pandas as pd
from openai import OpenAI
import base64
import os

# --- 1. PAGE CONFIGURATION & CSS ---
st.set_page_config(
    page_title="NA Pharma Care AI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
#MainMenu {visibility: hidden !important;}
header {visibility: hidden !important;}
footer {visibility: hidden !important; display: none !important;}
.stDeployButton {display: none !important;}

/* Background & Mobile Enhancements */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #020617 !important;
    background: radial-gradient(circle at top left, #1e293b, #0f172a, #020617) !important;
    color: #f8fafc !important;
}

div[data-testid="stAppViewBlockContainer"] {
    padding: 10px !important; 
    max-width: 100% !important;
}

/* Chat Bubbles */
[data-testid="stChatMessageContent"] {
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.9)) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important; 
    color: #f8fafc !important;
    word-wrap: break-word !important; 
    overflow-wrap: break-word !important;
}

@media (max-width: 768px) {
    [data-testid="stChatMessageContent"] { max-width: 95% !important; }
    h1 { font-size: 1.8rem !important; }
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
        # Load master list, bypassing the first 3 header rows
        df_master = pd.read_excel(EXCEL_FILE, sheet_name='Full Master Medicine List', header=3)
        # Drop rows that are completely empty
        df_master.dropna(how='all', inplace=True)
        return df_master
    except Exception as e:
        st.error(f"Error loading Excel: {e}")
        return None

df_master = load_inventory_data()

# --- 3. STREAM CLEANER ---
def generate_cleaned_content(response):
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# --- 4. IMAGE ENCODER ---
def encode_image(uploaded_file):
    return base64.b64encode(uploaded_file.getvalue()).decode('utf-8')

# --- 5. DASHBOARD HEADER ---
st.markdown("""
<div style="text-align: center; padding: 10px 0;">
    <h1 style="margin:0; font-weight: 700; background: linear-gradient(90deg, #10b981, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">💊 NA Pharma Care AI</h1>
    <p style="color: #94a3b8; font-size: 0.9rem;">Smart Internal Pharmacy Assistant</p>
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
        if cols[0].button("🩹 Pain"): selected_prompt = "Find pain relief medicines."
        if cols[1].button("🤒 Fever"): selected_prompt = "Find fever medications."
        if cols[2].button("🤧 Cold"): selected_prompt = "Find cold and allergy stock."
        if cols[3].button("💊 Anti"): selected_prompt = "Find antibiotics."
        if cols[4].button("🧹 Clear Chat"): 
            st.session_state.messages = []
            st.rerun()

        # Image Upload Section
        uploaded_img = st.file_uploader("📷 Upload Prescription or Medicine Image", type=["png", "jpg", "jpeg"])
        
        # Chat Display
        chat_container = st.container(height=350)
        with chat_container:
            for message in st.session_state.messages:
                avatar_icon = "👨‍⚕️" if message["role"] == "assistant" else "👤"
                with st.chat_message(message["role"], avatar=avatar_icon):
                    if type(message["content"]) is list:
                        # Handle displaying text if the payload was a vision list
                        st.markdown(message["content"][0]["text"])
                    else:
                        st.markdown(message["content"])

        user_input = st.chat_input("Ask AI, search symptoms, or analyze image...")
        prompt = selected_prompt or user_input

        if prompt:
            # Build user message content based on whether an image was uploaded
            if uploaded_img:
                base64_img = encode_image(uploaded_img)
                user_content = [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                ]
                selected_model = "llama-3.2-11b-vision-preview" # Groq Vision Model
            else:
                user_content = prompt
                selected_model = "llama-3.1-8b-instant" # Fast Text Model

            st.session_state.messages.append({"role": "user", "content": user_content})
            
            with chat_container:
                with st.chat_message("user", avatar="👤"):
                    st.markdown(prompt)
                    if uploaded_img:
                        st.image(uploaded_img, width=150)

                with st.chat_message("assistant", avatar="👨‍⚕️"):
                    with st.spinner("Analyzing..."):
                        try:
                            # Search Inventory for Context
                            context_data = "No matching medicines found in current inventory."
                            if df_master is not None and not uploaded_img: 
                                # Fast string matching across all columns for the prompt
                                search_words = [w for w in prompt.lower().split() if len(w) > 3]
                                if search_words:
                                    mask = pd.Series([False] * len(df_master))
                                    for word in search_words:
                                        mask = mask | df_master.astype(str).apply(lambda x: x.str.contains(word, case=False, na=False)).any(axis=1)
                                    matches = df_master[mask]
                                    if not matches.empty:
                                        context_data = matches.head(10).to_string(index=False)

                            system_instruction = f"""
                            You are the AI assistant for NA Pharma Care.
                            
                            INSTRUCTIONS:
                            1. Check the "AVAILABLE INVENTORY" below. 
                            2. If analyzing an image/prescription, read the text on the image and check if those medicines are in our inventory.
                            3. If a requested medicine is NOT in stock, strictly say: "⚠️ Not currently in stock" before suggesting alternatives.
                            
                            --- AVAILABLE INVENTORY (Based on query) ---
                            {context_data}
                            """

                            messages_payload = [{"role": "system", "content": system_instruction}]
                            # Append history (keep it light)
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

# --- TAB 2: SMART DATABASE ---
with tab2:
    st.markdown("### 📦 Master Inventory Scan")
    if df_master is not None:
        search_term = st.text_input("🔍 Search by Name, Symptom, Category (e.g. 'Allergy', 'Pain')...", "")
        if search_term:
            # Fixed robust search logic that accurately filters only matching rows
            mask = df_master.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
            filtered_df = df_master[mask]
            st.dataframe(filtered_df, use_container_width=True)
            if filtered_df.empty:
                st.warning("No medicines found matching that exact search.")
        else:
            st.dataframe(df_master, use_container_width=True)
    else:
        st.info("ℹ️ inventory.xlsx not found.")

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
                with col_n: st.write(med)
                with col_p: price = st.number_input(f"Price", min_value=0.0, value=100.0, step=10.0, key=f"p_{med}")
                with col_q: qty = st.number_input(f"Qty", min_value=1, value=1, step=1, key=f"q_{med}")
                total_amount += (price * qty)
            st.markdown(f"<h2 style='color: #10b981;'>Total: Rs. {total_amount:,.2f}</h2>", unsafe_allow_html=True)

# --- TAB 4: ADD NEW MEDICINE ---
with tab4:
    st.markdown("### ➕ Add to Inventory")
    if df_master is not None:
        with st.form("add_medicine_form"):
            new_brand = st.text_input("Brand Name / Medicine Name*")
            new_generic = st.text_input("Generic / Salt")
            new_category = st.text_input("Category / Symptoms (e.g., Pain, Allergy, Cold)")
            
            cols = list(df_master.columns)
            submit_med = st.form_submit_button("Save Medicine")
            
            if submit_med:
                if new_brand:
                    new_row_data = {col: "" for col in cols}
                    if len(cols) > 0: new_row_data[cols[0]] = new_brand
                    if len(cols) > 1: new_row_data[cols[1]] = new_generic
                    if len(cols) > 2: new_row_data[cols[2]] = new_category
                    
                    new_df = pd.DataFrame([new_row_data])
                    updated_df = pd.concat([df_master, new_df], ignore_index=True)
                    
                    try:
                        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='w') as writer:
                            updated_df.to_excel(writer, sheet_name='Full Master Medicine List', startrow=3, index=False)
                        
                        st.success(f"✅ Successfully added {new_brand}!")
                        # Instantly clear cache so the app updates without restarting
                        st.cache_data.clear() 
                        
                    except Exception as e:
                        st.error(f"Error saving: {e}. Ensure the Excel file is closed on your PC.")
                else:
                    st.warning("Brand Name is required.")
    else:
        st.info("Upload or create an inventory.xlsx file first.")

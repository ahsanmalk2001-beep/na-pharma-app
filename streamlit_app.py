import streamlit as st
import pandas as pd
from openai import OpenAI
import requests
import base64
import os

# --- 1. PAGE CONFIGURATION & FULL VIEWPORT CSS ---
st.set_page_config(
    page_title="NA Pharma Care AI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
/* --- FULL REMOVAL OF STREAMLIT BRANDING & FIXING MOBILE TEXT --- */
#MainMenu {visibility: hidden !important;}
header {visibility: hidden !important;}
footer {visibility: hidden !important; display: none !important;}
.stDeployButton {display: none !important;}
[data-testid="stStatusWidget"] {visibility: hidden !important;}
[data-testid="stToolbar"] {display: none !important;}
[data-testid="stDecoration"] {display: none !important;}

/* Hide floating badges */
.viewerBadge_container__1QSob, div[class*="viewerBadge"], a[href*="streamlit.cloud"] {
    display: none !important; opacity: 0 !important; pointer-events: none !important;
}

/* Background */
html, body, [data-testid="stAppViewContainer"], .stApp {
    background-color: #020617 !important;
    background: radial-gradient(circle at top left, #1e293b, #0f172a, #020617) !important;
    color: #f8fafc !important;
}

div[data-testid="stAppViewBlockContainer"] {
    padding: 10px !important; /* Fixed padding for mobile */
    max-width: 100% !important;
}

/* --- MOBILE SPECIFIC CHAT FIXES --- */
[data-testid="stChatMessageContent"] {
    background: linear-gradient(145deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.9)) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    padding: 12px 16px !important; /* Better padding */
    color: #f8fafc !important;
    max-width: 90% !important;
    word-wrap: break-word !important; /* Forces weird text to wrap on phones */
    overflow-wrap: break-word !important;
}

[data-testid="stChatMessageContent"] div p {
    font-size: 16px !important; /* highly readable on mobile */
    line-height: 1.5 !important;
    margin-bottom: 8px !important;
}

@media (max-width: 768px) {
    [data-testid="stChatMessageContent"] {
        max-width: 95% !important;
    }
    h1 { font-size: 1.8rem !important; }
}
</style>
""", unsafe_allow_html=True)

# --- 2. DATA LOADER & SAVER ---
EXCEL_FILE = "inventory.xlsx"
api_key = st.secrets.get("GROQ_API_KEY")

@st.cache_data
def load_inventory_data():
    if not os.path.exists(EXCEL_FILE):
        return None, None
    try:
        # Assuming header is at row 3 based on your original code
        df_master = pd.read_excel(EXCEL_FILE, sheet_name='Full Master Medicine List', header=3)
        
        # Load symptom sheet if it exists, otherwise return None for it
        try:
            df_symptom = pd.read_excel(EXCEL_FILE, sheet_name='Quick Symptom & Keyword Index', header=3)
        except:
            df_symptom = None
            
        return df_master, df_symptom
    except Exception as e:
        st.error(f"Error loading Excel: {e}")
        return None, None

df_master, df_symptom = load_inventory_data()
total_medicines = len(df_master) if df_master is not None else 0

# --- 3. STREAM CLEANER ---
def generate_cleaned_content(response):
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            yield content

# --- 4. DASHBOARD HEADER ---
st.markdown("""
<div style="text-align: center; padding: 10px 0;">
    <h1 style="margin:0; font-weight: 700; background: linear-gradient(90deg, #10b981, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">💊 NA Pharma Care AI</h1>
    <p style="color: #94a3b8; font-size: 0.9rem;">Smart Internal Pharmacy Assistant</p>
</div>
""", unsafe_allow_html=True)

# --- 5. TABS NAVIGATION (Added "Add Medicine" Tab) ---
tab1, tab2, tab3, tab4 = st.tabs(["🤖 AI Assistant", "📚 Database", "🧾 Bill Calc", "➕ Add Med"])

# --- TAB 1: AI ASSISTANT ---
with tab1:
    if not api_key:
        st.error("⚠️ GROQ_API_KEY is missing in Streamlit secrets.")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Quick Links
        q1, q2, q3, q4, q5 = st.columns(5)
        selected_prompt = None
        if q1.button("🩹 Pain"): selected_prompt = "Find pain relief medicines."
        if q2.button("🤒 Fever"): selected_prompt = "Find fever medications."
        if q3.button("🤧 Cold"): selected_prompt = "Find cold and allergy stock."
        if q4.button("💊 Anti"): selected_prompt = "Find antibiotics."
        if q5.button("🧹 Clear"): 
            st.session_state.messages = []
            st.rerun()

        chat_container = st.container(height=350)
        with chat_container:
            for message in st.session_state.messages:
                avatar_icon = "👨‍⚕️" if message["role"] == "assistant" else "👤"
                with st.chat_message(message["role"], avatar=avatar_icon):
                    st.markdown(message["content"])

        user_input = st.chat_input("Ask AI or search symptoms...")
        prompt = selected_prompt or user_input

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with chat_container:
                with st.chat_message("user", avatar="👤"):
                    st.markdown(prompt)

                with st.chat_message("assistant", avatar="👨‍⚕️"):
                    with st.spinner("Searching inventory..."):
                        try:
                            q = prompt.lower().strip()
                            context_data = "No matching medicines found in current inventory."
                            
                            # Smart Search: Check if the user's prompt matches ANY column in the dataframe
                            if df_master is not None:
                                # Look for words from the prompt inside the dataframe
                                search_words = q.split()
                                mask = pd.Series([False] * len(df_master))
                                for word in search_words:
                                    if len(word) > 2: # ignore tiny words like "a", "is"
                                        # Check across all columns for the keyword
                                        mask = mask | df_master.apply(lambda row: row.astype(str).str.lower().str.contains(word, na=False).any(), axis=1)
                                
                                matches = df_master[mask]
                                if not matches.empty:
                                    context_data = matches.head(8).to_string(index=False)

                            system_instruction = f"""
                            You are the internal assistant for a specific pharmacy branch.
                            
                            CRITICAL INSTRUCTIONS:
                            1. You MUST check the "AVAILABLE INVENTORY" below before answering.
                            2. If the user asks for a medication, symptom, or allergy relief, FIRST recommend the items listed in the AVAILABLE INVENTORY.
                            3. If there is NO relevant medicine in the AVAILABLE INVENTORY, you MUST explicitly say: "⚠️ Not currently in stock in our database."
                            4. Only AFTER stating it is out of stock, you may suggest a standard alternative they could look for elsewhere.
                            
                            --- AVAILABLE INVENTORY (Based on user query) ---
                            {context_data}
                            -------------------------------------------------
                            
                            FORMATTING: Keep it brief, formatted with bullet points for easy reading on mobile phones.
                            """

                            messages_payload = [{"role": "system", "content": system_instruction}]
                            for m in st.session_state.messages[-5:]: # Keep last 5 messages for context speed
                                messages_payload.append({"role": m["role"], "content": m["content"]})

                            response = client.chat.completions.create(
                                model="llama-3.1-8b-instant", # Faster model for text
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
            # Smart filter checks all columns for the keyword
            filtered_df = df_master[df_master.apply(lambda row: row.astype(str).str.lower().str.contains(search_term.lower(), na=False).any(), axis=1)]
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(df_master, use_container_width=True)
    else:
        st.info("ℹ️ inventory.xlsx not found.")

# --- TAB 3: BILL CALCULATOR ---
with tab3:
    st.markdown("### 🧾 Bill Estimator")
    if df_master is not None and len(df_master.columns) > 0:
        # Assumes the first column is the medicine name if 'Brand Name' isn't explicitly found
        med_col = "Brand Name" if "Brand Name" in df_master.columns else df_master.columns[0]
        medicine_list = df_master[med_col].dropna().tolist()
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
    st.markdown("New entries are saved directly to your `inventory.xlsx` file.")
    
    if df_master is not None:
        with st.form("add_medicine_form"):
            new_brand = st.text_input("Brand Name / Medicine Name*")
            new_generic = st.text_input("Generic / Salt")
            new_category = st.text_input("Category / Symptoms (e.g., Pain, Allergy, Cold)")
            
            # Dynamically grab the exact column names from your excel file to match format
            cols = list(df_master.columns)
            
            submit_med = st.form_submit_button("Save Medicine")
            
            if submit_med:
                if new_brand:
                    # Create a dictionary matching your Excel columns. 
                    # We map basic inputs to the first few columns assuming standard layout.
                    new_row_data = {col: "" for col in cols}
                    
                    # Try to map inputs to likely column names
                    if len(cols) > 0: new_row_data[cols[0]] = new_brand
                    if len(cols) > 1: new_row_data[cols[1]] = new_generic
                    if len(cols) > 2: new_row_data[cols[2]] = new_category
                    
                    new_df = pd.DataFrame([new_row_data])
                    updated_df = pd.concat([df_master, new_df], ignore_index=True)
                    
                    try:
                        # Save back to Excel, preserving the 3 blank rows at the top
                        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='w') as writer:
                            updated_df.to_excel(writer, sheet_name='Full Master Medicine List', startrow=3, index=False)
                        
                        st.success(f"✅ Successfully added {new_brand} to the database!")
                        st.cache_data.clear() # Clear cache so it instantly shows up in searches
                        
                    except Exception as e:
                        st.error(f"Could not save to file. Make sure the file isn't open in another program. Error: {e}")
                else:
                    st.warning("Brand Name is required.")
    else:
        st.info("Upload or create an inventory.xlsx file first.")

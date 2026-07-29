import streamlit as st
import pandas as pd
from openai import OpenAI

# Page Configuration
st.set_page_config(
    page_title="NA Pharma Care Management System",
    page_icon="💊",
    layout="wide"
)

EXCEL_FILE = "inventory.xlsx"

# Get API key automatically from Streamlit Secrets (DO NOT PASTE YOUR REAL KEY HERE)
api_key = st.secrets.get("GROQ_API_KEY")

# Load Excel Sheets safely with caching
@st.cache_data
def load_inventory_data():
    try:
        df_master = pd.read_excel(EXCEL_FILE, sheet_name='Full Master Medicine List', header=3)
        df_symptom = pd.read_excel(EXCEL_FILE, sheet_name='Quick Symptom & Keyword Index', header=3)
        return df_master, df_symptom
    except Exception as e:
        return None, None

df_master, df_symptom = load_inventory_data()

st.title("💊 NA Pharma Care Management & AI System")

# Main Navigation Tabs
tab1, tab2 = st.tabs(["💬 Chatbot Assistant", "📊 Inventory Master View"])

with tab1:
    st.subheader("NA Pharma AI Assistant")
    st.markdown("Ask anything about inventory, medications, ear drops, symptoms, or active salts.")
    
    if not api_key:
        st.error("⚠️ GROQ_API_KEY is missing in Streamlit Cloud Secrets. Please add it under App Settings -> Secrets.")
    else:
        client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=api_key,
        )
        
        # Initialize chat history in session state
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display prior chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Accept user input
        if prompt := st.chat_input("e.g. Do we have any ear drops? Or tell me about Azomax"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Searching inventory database..."):
                    try:
                        q = prompt.lower().strip()
                        
                        # Smart Search across sheets
                        master_matches = pd.DataFrame()
                        symptom_matches = pd.DataFrame()
                        
                        if df_master is not None:
                            master_matches = df_master[
                                df_master.apply(lambda row: row.astype(str).str.lower().str.contains(q, na=False).any(), axis=1)
                            ]
                        if df_symptom is not None:
                            symptom_matches = df_symptom[
                                df_symptom.apply(lambda row: row.astype(str).str.lower().str.contains(q, na=False).any(), axis=1)
                            ]

                        # Build context package
                        context = "--- SYMPTOM & CATEGORY INDEX ---\n"
                        if not symptom_matches.empty:
                            context += symptom_matches.to_string(index=False) + "\n\n"
                        else:
                            context += "No direct matches in symptom index.\n\n"
                            
                        context += "--- MASTER MEDICINE LIST ---\n"
                        if not master_matches.empty:
                            context += master_matches.head(20).to_string(index=False)
                        else:
                            context += "No exact matches found in master list."

                        system_instruction = f"""
                        You are the professional and friendly pharmacy assistant for NA Pharma Care. 
                        You have direct access to the store's inventory database retrieved below from their Excel sheets.
                        
                        INSTRUCTIONS:
                        1. Answer customer queries strictly using the retrieved inventory data provided below.
                        2. If the user asks about items like ear drops, eye drops, antibiotics, or specific brands/symptoms, list the exact matches found (including brand name, active salt, category, and uses).
                        3. Be helpful, clear, and accurate.
                        
                        RETRIEVED EXCEL DATA FOR THIS QUERY:
                        {context}
                        """

                        # Construct messages payload including history
                        messages_payload = [{"role": "system", "content": system_instruction}]
                        for m in st.session_state.messages:
                            messages_payload.append({"role": m["role"], "content": m["content"]})

                        response = client.chat.completions.create(
                            model="llama-3.1-8b-instant",
                            messages=messages_payload
                        )
                        
                        answer = response.choices[0].message.content
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    except Exception as e:
                        st.error(f"API Error: {e}")

with tab2:
    st.subheader("📦 Master Inventory Database")
    if df_master is not None:
        st.dataframe(df_master, use_container_width=True)
    else:
        st.error("Could not load 'Full Master Medicine List' from inventory.xlsx.")
        
    st.subheader("🔍 Quick Symptom Index")
    if df_symptom is not None:
        st.dataframe(df_symptom, use_container_width=True)
    else:
        st.error("Could not load 'Quick Symptom & Keyword Index' from inventory.xlsx.")

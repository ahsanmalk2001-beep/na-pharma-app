import streamlit as st
import pandas as pd
from openai import OpenAI
import requests
from streamlit_lottie import st_lottie

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NA Pharma Care AI",
    page_icon="💊",
    layout="wide"
)

# --- CUSTOM CSS STYLING & GRADIENTS ---
st.markdown("""
    <style>
    .main-title {
        background: linear-gradient(90deg, #00b09b, #96c93d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #7f8c8d;
        font-size: 1.1rem;
        font-weight: 400;
        margin-bottom: 20px;
    }
    .stChatMessage {
        border-radius: 12px;
        padding: 10px;
    }
    /* Hide standard footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- LOAD ANIMATION ---
@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

# Clean medical/health vector animation
lottie_med = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_jcikwtux.json")

# --- HEADER LAYOUT ---
col_anim, col_text = st.columns([1, 6])
with col_anim:
    if lottie_med:
        st_lottie(lottie_med, height=100, key="med_anim")
with col_text:
    st.markdown('<p class="main-title">NA Pharma Care</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Intelligent Pharmacy Management & AI Assistant</p>', unsafe_allow_html=True)

EXCEL_FILE = "inventory.xlsx"
api_key = st.secrets.get("GROQ_API_KEY")

@st.cache_data
def load_inventory_data():
    try:
        df_master = pd.read_excel(EXCEL_FILE, sheet_name='Full Master Medicine List', header=3)
        df_symptom = pd.read_excel(EXCEL_FILE, sheet_name='Quick Symptom & Keyword Index', header=3)
        return df_master, df_symptom
    except Exception as e:
        return None, None

df_master, df_symptom = load_inventory_data()

# --- TABS ---
tab1, tab2 = st.tabs(["💬 AI Chatbot Assistant", "📊 Master Inventory Database"])

with tab1:
    if not api_key:
        st.error("⚠️ GROQ_API_KEY is missing in Streamlit Cloud Secrets. Add it to your app settings.")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Auto-scrolling chat window container
        chat_container = st.container(autoscroll=True)

        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        if prompt := st.chat_input("Ask about any medicine, salt, or symptom... (e.g. Do we have ear drops?)"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Searching inventory records..."):
                        try:
                            q = prompt.lower().strip()
                            
                            master_matches = pd.DataFrame()
                            symptom_matches = pd.DataFrame()
                            
                            if df_master is not None:
                                master_matches = df_master[df_master.apply(lambda row: row.astype(str).str.lower().str.contains(q, na=False).any(), axis=1)]
                            if df_symptom is not None:
                                symptom_matches = df_symptom[df_symptom.apply(lambda row: row.astype(str).str.lower().str.contains(q, na=False).any(), axis=1)]

                            context = "--- SYMPTOM & CATEGORY INDEX ---\n"
                            context += symptom_matches.to_string(index=False) + "\n\n" if not symptom_matches.empty else "No direct matches in symptom index.\n\n"
                            context += "--- MASTER MEDICINE LIST ---\n"
                            context += master_matches.head(20).to_string(index=False) if not master_matches.empty else "No exact matches found in master list."

                            system_instruction = f"""
                            You are the professional and friendly pharmacy assistant for NA Pharma Care. 
                            Answer customer queries strictly using the retrieved inventory data provided below.
                            RETRIEVED EXCEL DATA FOR THIS QUERY:
                            {context}
                            """

                            messages_payload = [{"role": "system", "content": system_instruction}]
                            for m in st.session_state.messages:
                                messages_payload.append({"role": m["role"], "content": m["content"]})

                            # API Call with live streaming enabled for typewriter text effect
                            response = client.chat.completions.create(
                                model="llama-3.1-8b-instant",
                                messages=messages_payload,
                                stream=True
                            )
                            
                            def response_generator():
                                for chunk in response:
                                    content = chunk.choices[0].delta.content
                                    if content:
                                        yield content

                            answer = st.write_stream(response_generator())
                            st.session_state.messages.append({"role": "assistant", "content": answer})
                        
                        except Exception as e:
                            st.error(f"API Error: {e}")

with tab2:
    st.subheader("📦 Master Medicine Database")
    if df_master is not None:
        st.dataframe(df_master, use_container_width=True)
    else:
        st.error("Could not load master inventory list.")
        
    st.subheader("🔍 Quick Symptom Index")
    if df_symptom is not None:
        st.dataframe(df_symptom, use_container_width=True)
    else:
        st.error("Could not load symptom index list.")

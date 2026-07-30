import streamlit as st
import pandas as pd
from openai import OpenAI
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NA Pharma Care AI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. PREMIUM DARK THEME & GLASSMORPHISM CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

/* Base Theme */
html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif !important;
    color: #f8fafc;
}
.stApp {
    background: radial-gradient(circle at top left, #1e293b, #0f172a, #020617);
    background-attachment: fixed;
}

/* Glassmorphism Cards */
.glass-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
    text-align: center;
}
.glass-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.3);
}

/* Typography & Colors */
.text-primary { color: #10b981; } /* Medical Green */
.text-secondary { color: #3b82f6; } /* Medical Blue */
.text-muted { color: #94a3b8; font-size: 0.9rem; }
.card-value { font-size: 2.5rem; font-weight: 700; margin: 10px 0; color: #f8fafc; }
.status-badge {
    display: inline-flex;
    align-items: center;
    background: rgba(16, 185, 129, 0.1);
    color: #10b981;
    padding: 6px 16px;
    border-radius: 50px;
    font-size: 0.85rem;
    font-weight: 600;
    border: 1px solid rgba(16, 185, 129, 0.2);
    margin-bottom: 20px;
}
.pulse {
    width: 8px; height: 8px;
    background-color: #10b981;
    border-radius: 50%;
    margin-right: 8px;
    box-shadow: 0 0 10px #10b981;
    animation: pulse-animation 2s infinite;
}
@keyframes pulse-animation {
    0% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
    100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }
}

/* Clean UI Hiding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Custom Chat Bubbles */
[data-testid="stChatMessage"] {
    background: rgba(255, 255, 255, 0.02) !important;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
}
[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #10b981, #3b82f6) !important;
}
</style>
""", unsafe_allow_html=True)

# --- 3. DATA LOADER ---
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
total_medicines = len(df_master) if df_master is not None else 0
total_categories = len(df_symptom) if df_symptom is not None else 0

# --- 4. BRANDING & DASHBOARD ---
st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <div class="status-badge"><span class="pulse"></span> System Online</div>
    <h1 style="margin:0; font-size: 3rem; font-weight: 700; background: linear-gradient(90deg, #10b981, #3b82f6); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">💊 NA Pharma Care AI</h1>
    <p style="color: #94a3b8; font-size: 1.1rem; margin-top: 5px;">Smart Internal Pharmacy Assistant</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f"""
    <div class="glass-card">
        <p class="text-muted" style="margin:0; text-transform:uppercase; letter-spacing:1px;">📦 Medicines</p>
        <p class="card-value">{total_medicines}</p>
        <p class="text-primary" style="margin:0; font-size:0.85rem;">Total Items Available</p>
    </div>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <div class="glass-card">
        <p class="text-muted" style="margin:0; text-transform:uppercase; letter-spacing:1px;">📚 Categories</p>
        <p class="card-value">{total_categories}</p>
        <p class="text-secondary" style="margin:0; font-size:0.85rem;">Indexed Groups</p>
    </div>
    """, unsafe_allow_html=True)
with col3:
    st.markdown("""
    <div class="glass-card">
        <p class="text-muted" style="margin:0; text-transform:uppercase; letter-spacing:1px;">🤖 AI Status</p>
        <p class="card-value" style="color:#10b981;">ONLINE</p>
        <p class="text-muted" style="margin:0; font-size:0.85rem;">Database Connected</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# --- 5. TABS NAVIGATION ---
tab1, tab2, tab3 = st.tabs(["🤖 AI Assistant", "📚 Medicine Database", "🧾 Bill Calculator"])

# --- TAB 1: AI ASSISTANT ---
with tab1:
    if not api_key:
        st.error("⚠️ GROQ_API_KEY is missing.")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Quick Lookup Categories
        st.markdown("<h4 style='color: #f8fafc; font-weight: 500;'>⚡ Quick Lookup</h4>", unsafe_allow_html=True)
        q1, q2, q3, q4, q5, q6 = st.columns(6)
        
        selected_prompt = None
        if q1.button("🩹 Pain Relief", use_container_width=True): selected_prompt = "Show me pain relief medicines."
        if q2.button("🤒 Fever", use_container_width=True): selected_prompt = "What do we have for fever?"
        if q3.button("🤧 Cold & Flu", use_container_width=True): selected_prompt = "Show cold and flu medications."
        if q4.button("💊 Antibiotics", use_container_width=True): selected_prompt = "List available antibiotics."
        if q5.button("👁️ Eye / 👂 Ear", use_container_width=True): selected_prompt = "Show eye and ear drops."
        if q6.button("🧹 Clear Chat", use_container_width=True): 
            st.session_state.messages = []
            st.rerun()

        # Chat Interface
        chat_container = st.container(height=500)
        with chat_container:
            if not st.session_state.messages:
                st.markdown("""
                <div style='text-align:center; padding: 40px; color:#94a3b8;'>
                    <h3 style='color:#e2e8f0;'>Ask anything about medicines.</h3>
                    <p>Try searching for: <br><i>Uses of Panadol • Alternative to Brufen • Medicine for sore throat</i></p>
                </div>
                """, unsafe_allow_html=True)
                
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        user_input = st.chat_input("Search medicine, generic name, symptoms, or ask AI...")
        prompt = selected_prompt or user_input

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("🔍 Reading Excel Database..."):
                        try:
                            q = prompt.lower().strip()
                            context = "--- DATABASE RESULTS ---\n"
                            
                            if df_master is not None:
                                master_matches = df_master[df_master.apply(lambda row: row.astype(str).str.lower().str.contains(q, na=False).any(), axis=1)]
                                context += master_matches.head(15).to_string(index=False) if not master_matches.empty else "No exact matches found in master list."

                            system_instruction = f"""
                            You are NA Pharma Care AI, a premium internal pharmacy assistant.
                            
                            STRICT RESPONSE FORMAT (DO NOT USE TABLES OR CODE BLOCKS):
                            Whenever you suggest a medicine, you MUST format it EXACTLY like this beautiful virtual card:
                            
                            **💊 [Medicine Name]**  
                            **Generic Name:** [Salt Name]  
                            **Category:** [Category]  
                            
                            🔹 **Uses:** [Primary uses]  
                            🔹 **Dosage:** [Standard dosage]  
                            ⚠️ **Side Effects:** [Key side effects]  
                            🛑 **Warnings / Contraindications:** [Warnings]  
                            🤰 **Pregnancy Safety:** [Safe/Unsafe]  
                            👶 **Children:** [Safe/Unsafe]  
                            📦 **Storage:** [Storage instructions]  
                            🏢 **Manufacturer:** [Company name]  
                            🔄 **Alternatives:** [List 1-2 alternatives]  
                            
                            ---
                            
                            Be concise, professional, and act as expensive medical software. Avoid long paragraphs. Base your answers on the provided database context.
                            
                            DATA INVENTORY:
                            {context}
                            """

                            messages_payload = [{"role": "system", "content": system_instruction}]
                            for m in st.session_state.messages:
                                messages_payload.append({"role": m["role"], "content": m["content"]})

                            response = client.chat.completions.create(
                                model="llama-3.1-8b-instant",
                                messages=messages_payload,
                                stream=True
                            )
                            
                            answer = st.write_stream((chunk.choices[0].delta.content for chunk in response if chunk.choices[0].delta.content))
                            st.session_state.messages.append({"role": "assistant", "content": answer})
                        
                        except Exception as e:
                            st.error(f"API Error: {e}")

# --- TAB 2: INVENTORY DATABASE ---
with tab2:
    if df_master is not None:
        st.markdown("<h3 style='color: #f8fafc;'>📦 Master Database</h3>", unsafe_allow_html=True)
        search_term = st.text_input("🔍 Search to filter database instantly:", "")
        if search_term:
            filtered_df = df_master[df_master.apply(lambda row: row.astype(str).str.lower().str.contains(search_term.lower(), na=False).any(), axis=1)]
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(df_master, use_container_width=True)
            
        csv_data = df_master.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export as CSV", csv_data, "na_pharma_inventory.csv", "text/csv")

# --- TAB 3: BILL CALCULATOR ---
with tab3:
    st.markdown("<h3 style='color: #f8fafc;'>🧾 Premium Bill Calculator</h3>", unsafe_allow_html=True)
    if df_master is not None and "Brand Name" in df_master.columns:
        medicine_list = df_master["Brand Name"].dropna().tolist()
        selected_meds = st.multiselect("Select Medicines for Invoice:", medicine_list)
        
        if selected_meds:
            bill_items = []
            total_amount = 0.0
            
            for med in selected_meds:
                st.markdown(f"**{med}**")
                col_p, col_q = st.columns([1, 1])
                with col_p:
                    price = st.number_input(f"Price (Rs)", min_value=0.0, value=100.0, step=10.0, key=f"p_{med}")
                with col_q:
                    qty = st.number_input(f"Qty", min_value=1, value=1, step=1, key=f"q_{med}")
                
                item_total = price * qty
                total_amount += item_total
                bill_items.append({"Medicine": med, "Qty": qty, "Price": price, "Total": item_total})
            
            st.markdown("<br><hr style='border-color: #334155;'>", unsafe_allow_html=True)
            st.markdown(f"<h2 style='color: #10b981;'>Grand Total: Rs. {total_amount:,.2f}</h2>", unsafe_allow_html=True)
            st.dataframe(pd.DataFrame(bill_items), use_container_width=True)

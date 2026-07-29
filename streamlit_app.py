import streamlit as st
import pandas as pd
from openai import OpenAI
import requests
from streamlit_lottie import st_lottie

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NA Pharma Care AI",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CUSTOM CSS STYLING ---
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.header-card {
    background: linear-gradient(135deg, rgba(17, 153, 142, 0.18), rgba(56, 239, 125, 0.12));
    border: 1px solid rgba(56, 239, 125, 0.35);
    border-radius: 18px;
    padding: 22px 28px;
    margin-bottom: 20px;
}

.main-title {
    background: linear-gradient(90deg, #11998e, #38ef7d);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8rem;
    font-weight: 800;
    margin: 0px;
    line-height: 1.1;
}

.sub-title {
    color: #b0b0b0;
    font-size: 1.05rem;
    font-weight: 500;
    margin-top: 6px;
    margin-bottom: 0px;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    background: rgba(46, 204, 113, 0.15);
    color: #2ecc71;
    padding: 5px 14px;
    border-radius: 50px;
    font-size: 0.82rem;
    font-weight: 600;
    border: 1px solid rgba(46, 204, 113, 0.35);
    margin-bottom: 12px;
}

.pulse-dot {
    width: 8px;
    height: 8px;
    background-color: #2ecc71;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
    box-shadow: 0 0 8px #2ecc71;
}

.kpi-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 16px;
    text-align: center;
}

.kpi-num {
    font-size: 1.9rem;
    font-weight: 800;
    color: #38ef7d;
    margin: 0;
}

.kpi-label {
    font-size: 0.8rem;
    color: #999;
    margin-top: 4px;
    margin-bottom: 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>""", unsafe_allow_html=True)

# --- 3. ANIMATION LOADER ---
@st.cache_data
def load_lottieurl(url: str):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except:
        return None
    return None

lottie_health = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_jcikwtux.json")

# --- 4. DATA LOADER ---
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

# --- 5. HEADER SECTION WITH LIVE METRICS ---
st.markdown("""
<div class="header-card">
    <div class="status-badge"><span class="pulse-dot"></span> System Live & Connected</div>
    <p class="main-title">NA Pharma Care</p>
    <p class="sub-title">AI Pharmacy Management & Automated Inventory System</p>
</div>
""", unsafe_allow_html=True)

col_stat1, col_stat2, col_stat3, col_anim = st.columns([2, 2, 2, 2])

with col_stat1:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-num">{total_medicines}</p>
        <p class="kpi-label">📦 Tracked Products</p>
    </div>
    """, unsafe_allow_html=True)

with col_stat2:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-num">{total_categories}</p>
        <p class="kpi-label">🔍 Symptom Categories</p>
    </div>
    """, unsafe_allow_html=True)

with col_stat3:
    st.markdown("""
    <div class="kpi-card">
        <p class="kpi-num" style="color:#11998e;">Active</p>
        <p class="kpi-label">⚡ Smart Substitute Engine</p>
    </div>
    """, unsafe_allow_html=True)

with col_anim:
    if lottie_health:
        st_lottie(lottie_health, height=75, key="header_lottie")

st.markdown("<br>", unsafe_allow_html=True)

# --- 6. NAVIGATION TABS ---
tab1, tab2, tab3 = st.tabs(["💬 AI Assistant", "📊 Inventory Database", "🧮 Quick Bill Estimator"])

# --- TAB 1: AI ASSISTANT ---
with tab1:
    if not api_key:
        st.error("⚠️ GROQ_API_KEY is missing in Streamlit Cloud Secrets. Please add it in Settings -> Secrets.")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Category Quick Chips
        st.markdown("**💡 Quick Category Queries:**")
        qcol1, qcol2, qcol3, qcol4, qcol5 = st.columns(5)
        
        selected_prompt = None
        if qcol1.button("👂 Ear Drops"):
            selected_prompt = "Do we have any ear drops in stock?"
        if qcol2.button("👁️ Eye Drops"):
            selected_prompt = "List all eye drop solutions available."
        if qcol3.button("💊 Antibiotics"):
            selected_prompt = "What antibiotics do we have in inventory?"
        if qcol4.button("🤒 Pain Relief"):
            selected_prompt = "Show pain relief medications and dosages."
        if qcol5.button("🧹 Clear Chat"):
            st.session_state.messages = []
            st.rerun()

        chat_container = st.container(autoscroll=True)

        with chat_container:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

        user_input = st.chat_input("Search medicine name, active salt, or symptom...")
        prompt = selected_prompt or user_input

        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            with chat_container:
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner("Searching inventory and analyzing active salts..."):
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
                            You are the professional AI pharmacy assistant for NA Pharma Care.
                            Answer customer and pharmacist queries using the retrieved inventory data below.
                            
                            INSTRUCTIONS:
                            1. Present findings clearly using bold text, bullet points, and clean formatting.
                            2. Include Brand Name, Active Salt / Generic Formula, Category, and Primary Uses when listing medicines.
                            3. GENERIC SUBSTITUTE ENGINE: If an exact requested brand is not listed or missing, check the active salt and explicitly suggest alternative brands in the database with the SAME active salt.
                            4. Keep answers concise, helpful, and professional.
                            
                            RETRIEVED INVENTORY DATA FOR THIS QUERY:
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
                            
                            def stream_generator():
                                for chunk in response:
                                    content = chunk.choices[0].delta.content
                                    if content:
                                        yield content

                            answer = st.write_stream(stream_generator())
                            st.session_state.messages.append({"role": "assistant", "content": answer})
                        
                        except Exception as e:
                            st.error(f"API Error: {e}")

# --- TAB 2: INVENTORY DATABASE ---
with tab2:
    st.subheader("📦 Master Inventory Database")
    if df_master is not None:
        search_term = st.text_input("🔍 Filter database in real-time:", "")
        if search_term:
            filtered_df = df_master[df_master.apply(lambda row: row.astype(str).str.lower().str.contains(search_term.lower(), na=False).any(), axis=1)]
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.dataframe(df_master, use_container_width=True)
            
        csv_data = df_master.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Export Inventory as CSV", csv_data, "na_pharma_inventory.csv", "text/csv")
    else:
        st.error("Could not load master inventory list.")

# --- TAB 3: QUICK BILL ESTIMATOR ---
with tab3:
    st.subheader("🧮 Walk-in Counter Bill Estimator")
    st.markdown("Quickly calculate totals for walk-in customer purchases.")
    
    if df_master is not None and "Brand Name" in df_master.columns:
        medicine_list = df_master["Brand Name"].dropna().tolist()
        selected_meds = st.multiselect("Select Medicines:", medicine_list)
        
        if selected_meds:
            bill_items = []
            total_amount = 0.0
            
            for med in selected_meds:
                col_m, col_p, col_q = st.columns([3, 2, 2])
                with col_m:
                    st.write(f"**{med}**")
                with col_p:
                    price = st.number_input(f"Unit Price for {med}", min_value=0.0, value=100.0, step=10.0, key=f"p_{med}")
                with col_q:
                    qty = st.number_input(f"Quantity for {med}", min_value=1, value=1, step=1, key=f"q_{med}")
                
                item_total = price * qty
                total_amount += item_total
                bill_items.append({"Medicine": med, "Unit Price": price, "Qty": qty, "Total": item_total})
            
            st.markdown("---")
            st.markdown(f"### 💳 Total Estimated Bill: **Rs. {total_amount:,.2f}**")
            st.dataframe(pd.DataFrame(bill_items), use_container_width=True)
    else:
        st.info("Inventory brand names column not detected. You can view full stock in Tab 2.")

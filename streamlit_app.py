import io
import os
import base64
import streamlit as st
import pandas as pd
from openai import OpenAI

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NA Pharma Care - Enterprise Neural Terminal",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ENTERPRISE CLINICAL UI DESIGN SYSTEM ---
st.markdown("""
<style>
/* --- HIDE STREAMLIT BRANDING --- */
#MainMenu {visibility: hidden !important;}
header {visibility: hidden !important; background: transparent !important;}
footer {visibility: hidden !important; display: none !important;}
.stDeployButton {display: none !important;}
[data-testid="stToolbar"] {visibility: hidden !important;}

/* --- GLOBAL APP BACKGROUND (Obsidian Slate Theme) --- */
.stApp, html, body, [data-testid="stAppViewContainer"] {
    background-color: #07090e !important;
    background-image: linear-gradient(135deg, #07090e 0%, #0d1117 100%) !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* --- SUBTLE SUB-GRID BACKGROUND --- *
.stApp::before {
    content: "";
    position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
    background-image: linear-gradient(rgba(255, 255, 255, 0.015) 1px, transparent 1px),
                      linear-gradient(90deg, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
    background-size: 32px 32px;
    z-index: 0; pointer-events: none;
}

/* --- PROFESSIONAL STATUS BADGE --- */
.live-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(56, 189, 248, 0.08);
    border: 1px solid rgba(56, 189, 248, 0.25);
    padding: 5px 12px; border-radius: 6px;
    font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1.2px;
    color: #38bdf8;
}
.pulse-dot {
    width: 6px; height: 6px; background-color: #38bdf8; border-radius: 50%;
    box-shadow: 0 0 8px rgba(56, 189, 248, 0.6);
    animation: livePulse 2s infinite ease-in-out;
}
@keyframes livePulse {
    0% { transform: scale(0.95); opacity: 0.8; }
    50% { transform: scale(1.1); opacity: 1; }
    100% { transform: scale(0.95); opacity: 0.8; }
}

/* --- ELEVATED CARD SURFACES --- */
.hud-card {
    background: rgba(15, 23, 42, 0.7) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
    padding: 20px !important;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4) !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.hud-card:hover {
    border-color: rgba(56, 189, 248, 0.3) !important;
    box-shadow: 0 6px 30px rgba(0, 0, 0, 0.6) !important;
}

/* --- PRECISION BUTTONS --- */
.stButton button {
    background: #1e293b !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 8px !important;
    color: #f8fafc !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.5px !important;
    transition: all 0.2s ease !important;
}
.stButton button:hover {
    background: #38bdf8 !important;
    border-color: #38bdf8 !important;
    color: #0f172a !important;
    box-shadow: 0 0 15px rgba(56, 189, 248, 0.3) !important;
}

/* --- INPUT FIELDS --- */
[data-testid="stTextInput"] input {
    background: #0b0f19 !important;
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 8px !important;
    color: #f8fafc !important;
    font-size: 0.95rem !important;
    padding: 12px 16px !important;
    transition: border-color 0.2s ease !important;
}
[data-testid="stTextInput"] input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2) !important;
}

/* --- HEADINGS --- */
.clean-title {
    margin: 0; font-weight: 800; font-size: 2.4rem !important; text-align: center;
    color: #f8fafc;
    letter-spacing: -0.5px;
}

/* --- DATAFRAMES --- */
[data-testid="stDataFrame"] {
    background: rgba(11, 15, 25, 0.8) !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
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
        return None

df_master = load_inventory_data()

# --- 4. SMART SEARCH ALGORITHM ---
def perform_smart_inventory_search(df, query):
    if df is None or df.empty:
        return pd.DataFrame(), "Inventory is empty or uninitialized."
    
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
        
    display_cols = [c for c in ['Brand Name', 'Active Salt / Generic Composition', 'Therapeutic Category', 'Primary Uses & Indications'] if c in df.columns]
    
    if not matches.empty:
        return matches[display_cols].head(15), matches[display_cols].head(15).to_string(index=False)
    else:
        return pd.DataFrame(), "No exact or matching medications found in current inventory records."

# --- 5. HEADER WITH SYSTEM STATUS ---
st.markdown("""
<div style="display: flex; justify-content: center; align-items: center; margin-bottom: 8px;">
    <div class="live-badge">
        <div class="pulse-dot"></div> Secure Enterprise Node • Live
    </div>
</div>
<div style="text-align: center; padding: 0 0 24px 0;">
    <h1 class="clean-title">NA Pharma Care</h1>
    <p style="color: #64748b; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 2px; margin-top: 6px;">Clinical Intelligence Matrix & Inventory Engine</p>
</div>
""", unsafe_allow_html=True)

# --- 6. TABS NAVIGATION ---
tab1, tab2 = st.tabs(["⚡ Command Center", "➕ Inventory Ingestion Hub"])

# --- TAB 1: COMMAND CENTER ---
with tab1:
    if not api_key:
        st.error("⚠️ GROQ_API_KEY missing in Streamlit secrets.")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        
        st.markdown("<p style='color: #94a3b8; font-size: 0.78rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 8px;'>Quick Filters:</p>", unsafe_allow_html=True)
        c1, c2, c3, c4, c5, c6 = st.columns([1,1,1,1,1,1.2])
        chip_query = None
        if c1.button("Pain"): chip_query = "pain"
        if c2.button("Fever"): chip_query = "fever"
        if c3.button("Cough"): chip_query = "cough"
        if c4.button("Antibiotic"): chip_query = "antibiotic"
        if c5.button("Stomach"): chip_query = "stomach"
        if c6.button("Clear Search"): chip_query = ""

        search_input = st.text_input("Search inventory by brand, generic salt, or symptom...", value=chip_query if chip_query is not None else "")
        active_query = search_input.strip()

        if active_query:
            total_meds_count = len(df_master) if df_master is not None else 0
            df_matches, context_data = perform_smart_inventory_search(df_master, active_query)

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
                with st.spinner("Analyzing matrix records..."):
                    try:
                        system_instruction = f"""
                        You are the internal clinical assistant for NA Pharma Care.
                        TOTAL INVENTORY: {total_meds_count} medications registered.
                        
                        RULES:
                        1. If medications appear in matches, they ARE IN STOCK.
                        2. Present each item clearly with clean line breaks.
                        
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
                        <div class="hud-card" style="margin-top: 10px; line-height: 1.6;">
                            {response.choices[0].message.content}
                        </div>
                        """, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"Neural Error: {e}")
        else:
            st.markdown("""
            <div class="hud-card" style="text-align: center; padding: 45px 20px; margin-top: 15px;">
                <h3 style="color: #f8fafc; margin-bottom: 8px; font-weight: 700; font-size: 1.2rem;">System Ready</h3>
                <p style="color: #64748b; font-size: 0.9rem; max-width: 500px; margin: 0 auto;">Enter a search query above or select a quick filter to query the live inventory matrix.</p>
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
            <h4 style="color: #f8fafc; margin-top: 0; font-size: 1rem;">Handwritten Document OCR</h4>
            <p style="color: #94a3b8; font-size: 0.85rem;">Upload an image of a handwritten list or prescription to automatically extract and review items.</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_handwriting_image = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
        
        if uploaded_handwriting_image is not None:
            st.image(uploaded_handwriting_image, caption="Source Document", use_container_width=True)
            
            if st.button("Extract & Process Document"):
                if api_key:
                    with st.spinner("Decoding document..."):
                        try:
                            client_vision = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
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
                        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='w') as writer:
                            combined_df.to_excel(writer, sheet_name='Full Master Medicine List', startrow=3, index=False)
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
            <h4 style="color: #f8fafc; margin-top: 0; font-size: 1rem;">Text Log Parser</h4>
            <p style="color: #94a3b8; font-size: 0.85rem;">Paste supplier lists or chat messages to parse items into structured format.</p>
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
                        parse_response = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key).chat.completions.create(
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
                        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='w') as writer:
                            combined_df.to_excel(writer, sheet_name='Full Master Medicine List', startrow=3, index=False)
                        st.success(f"Merged successfully. Total records: {len(combined_df)}")
                        st.cache_data.clear()
            except PermissionError:
                st.error("File locked. Please close 'inventory.xlsx' in Microsoft Excel.")
            except Exception as e:
                st.error(f"Error: {e}")

    # --- SUB-TAB 4: LIVE BROWSER GRID ---
    with sub_tab4:
        if df_master is not None:
            empty_template = pd.DataFrame(columns=df_master.columns)
            edited_grid_df = st.data_editor(empty_template, num_rows="dynamic", use_container_width=True, height=250)
            if st.button("Commit Grid Rows"):
                valid_new_rows = edited_grid_df.dropna(how='all')
                if not valid_new_rows.empty:
                    updated_df = pd.concat([df_master, valid_new_rows], ignore_index=True).drop_duplicates()
                    try:
                        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='w') as writer:
                            updated_df.to_excel(writer, sheet_name='Full Master Medicine List', startrow=3, index=False)
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
                        cols = list(df_master.columns)
                        new_row = {col: "" for col in cols}
                        if len(cols) > 0: new_row[cols[0]] = new_brand.strip().title()
                        if len(cols) > 1: new_row[cols[1]] = new_generic
                        if len(cols) > 2: new_row[cols[2]] = new_category
                        if len(cols) > 3: new_row[cols[3]] = new_uses
                        
                        updated_df = pd.concat([df_master, pd.DataFrame([new_row])], ignore_index=True)
                        try:
                            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='w') as writer:
                                updated_df.to_excel(writer, sheet_name='Full Master Medicine List', startrow=3, index=False)
                            st.success(f"Committed '{new_brand}'.")
                            st.cache_data.clear()
                        except PermissionError:
                            st.error("File locked. Please close 'inventory.xlsx' in Microsoft Excel.")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Brand Name is required.")

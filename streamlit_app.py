import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="NA Pharma Care AI - Spider-Man Edition",
    page_icon="🕷️",
    layout="wide"
)

# Custom Spider-Man Theme CSS Injection
st.markdown("""
    <style>
    /* Main App Background */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Sidebar Styling with Red Accent Border */
    [data-testid="stSidebar"] {
        background-color: #1E293B;
        border-right: 2px solid #E23636;
    }
    
    /* Headers with Heroic Red */
    h1, h2, h3 {
        color: #E23636 !important;
        font-family: 'Segoe UI', sans-serif;
        font-weight: 700;
    }
    
    /* Custom Spider-Man Action Buttons */
    .stButton>button {
        background-color: #E23636;
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(226, 54, 54, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #FF4D4D;
        box-shadow: 0 6px 12px rgba(255, 77, 77, 0.5);
        border: 1px solid #FFFFFF;
    }
    
    /* Metrics and Data Cards */
    [data-testid="stMetricValue"] {
        color: #38BDF8 !important; /* Tech Blue Contrast */
    }
    
    /* Input Fields & Data Editors */
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        background-color: #0B0F19;
        color: #FFFFFF;
        border: 1px solid #1E293B;
        border-radius: 4px;
    }
    .stTextInput>div>div>input:focus {
        border-color: #E23636;
    }
    
    /* Custom Alert Boxes */
    .stAlert {
        background-color: #1E293B;
        color: #F8FAFC;
        border-left: 5px solid #E23636;
    }
    </style>
""", unsafe_allow_html=True)

# Mock Data Generation for 400 Medicines Inventory Branch
@st.cache_data
def load_inventory_data():
    np.random.seed(42)
    categories = ["Analgesics", "Antibiotics", "Antiseptics", "Cardiovascular", "Respiratory", "Dermatology"]
    medicines = [
        "Paracetamol", "Ibuprofen", "Amoxicillin", "Azithromycin", "Ciprofloxacin",
        "Omeprazole", "Pantoprazole", "Metformin", "Amlodipine", "Losartan",
        "Cetirizine", "Loratadine", "Salbutamol", "Montelukast", "Diclofenac"
    ]
    
    # Scale to simulate 400 items
    data = []
    for i in range(1, 401):
        med_name = f"{np.random.choice(medicines)} {i}"
        category = np.random.choice(categories)
        stock = np.random.randint(5, 500)
        price = round(np.random.uniform(50.0, 1500.0), 2)
        status = "Low Stock" if stock < 30 else "Optimal"
        data.append({
            "ID": f"MED-{1000+i}",
            "Medicine Name": med_name,
            "Category": category,
            "Stock Quantity": stock,
            "Price (PKR)": price,
            "Status": status
        })
    return pd.DataFrame(data)

df_inventory = load_inventory_data()

# App Sidebar Navigation & Info
st.sidebar.title("🕷️ NA Pharma Control")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation Grid",
    ["Dashboard Overview", "Inventory Management", "Stock Alerts", "NA Pharma Care AI"]
)

st.sidebar.markdown("---")
st.sidebar.info("🚀 **System Status:** Online & Secured\nBranch: Family Pharmacy Unit #1")

# Main Content Routing
if page == "Dashboard Overview":
    st.title("🕷️ NA Pharma Care AI")
    st.markdown("### *Your Friendly Neighborhood Pharmacy Management System*")
    
    # Top-level metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Medicines", "400 Items", "Tracked")
    col2.metric("Low Stock Items", len(df_inventory[df_inventory["Stock Quantity"] < 30]), "-2 from yesterday", delta_color="inverse")
    col3.metric("Total Valuation", "PKR 3,450,200", "+5.4%")
    col4.metric("AI Assistant Status", "Active", "Web-Slinger v2.6")
    
    st.markdown("---")
    st.subheader("📊 Live Inventory Analytics Snapshot")
    st.dataframe(df_inventory.head(10), use_container_width=True)

elif page == "Inventory Management":
    st.title("📦 Inventory Control Panel")
    st.markdown("Manage, update, and inspect your branch inventory of ~400 medical items.")
    
    search_query = st.text_input("🔍 Search Medicine by Name or ID", "")
    
    if search_query:
        filtered_df = df_inventory[
            df_inventory["Medicine Name"].str.contains(search_query, case=False, na=False) |
            df_inventory["ID"].str.contains(search_query, case=False, na=False)
        ]
    else:
        filtered_df = df_inventory
        
    edited_df = st.data_editor(filtered_df, num_rows="fixed", use_container_width=True, key="inventory_editor")
    
    if st.button("💾 Save Database Changes"):
        st.success("Inventory updates successfully synchronized with the cloud ledger, web-slinger!")

elif page == "Stock Alerts":
    st.title("🚨 Critical Stock & Expiry Alerts")
    st.markdown("Automated monitoring for items falling below safety threshold levels (< 30 units).")
    
    low_stock_df = df_inventory[df_inventory["Stock Quantity"] < 30]
    
    if len(low_stock_df) > 0:
        st.warning(f"Attention: {len(low_stock_df)} items require immediate re-stocking!")
        st.dataframe(low_stock_df, use_container_width=True)
        if st.button("📨 Dispatch Auto-Restock Order"):
            st.success("Purchase orders successfully generated and transmitted to suppliers!")
    else:
        st.success("All inventory items are currently at safe operating levels. Great job!")

elif page == "NA Pharma Care AI":
    st.title("🤖 NA Pharma Care AI Assistant")
    st.markdown("Ask your tactical AI companion for prescription insights, inventory forecasts, and alternative drug suggestions.")
    
    # Chat Interface simulation
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello web-slinger! Your pharmacy network is secure. All 400 medicines are accounted for. How can I assist with your inventory or stock predictions today?"}
        ]
        
    for message in st.session_state.messages:
        with st.chat_message(message["role"], avatar="🕷️" if message["role"]=="assistant" else "👤"):
            st.markdown(message["content"])
            
    if prompt := st.chat_input("Ask about stock levels, drug alternatives, or supply chain reports..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
            
        with st.chat_message("assistant", avatar="🕷️"):
            # Simple contextual responses based on query
            if "low stock" in prompt.lower() or "alert" in prompt.lower():
                response = f"Scanning inventory... We currently have {len(df_inventory[df_inventory['Stock Quantity'] < 30])} items running low on stock."
            elif "paracetamol" in prompt.lower():
                response = "Paracetamol stock is optimal across all batches. Average unit price stands around PKR 75.00."
            else:
                response = f"Analyzing database for query: '{prompt}'. All metrics indicate stable branch performance. Let me know if you need specific batch lookups!"
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

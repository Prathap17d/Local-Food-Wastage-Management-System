import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from pandasql import sqldf

# 1. PAGE CONFIGURATION (FOR FULL WIDE FRAME)
st.set_page_config(
    page_title="Local Food Wastage Management System",
    page_icon="🍎",
    layout="wide"  
)

# 2. INITIALIZE MASTER RUNTIME DATA
if 'data_loaded' not in st.session_state:
    base_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else r"F:\Local_Food_Wastage_Project"
    
    st.session_state.providers = pd.read_csv(os.path.join(base_dir, "providers_data.csv"))
    st.session_state.receivers = pd.read_csv(os.path.join(base_dir, "receivers_data.csv"))
    st.session_state.food_listings = pd.read_csv(os.path.join(base_dir, "food_listings_data.csv"))
    st.session_state.claims = pd.read_csv(os.path.join(base_dir, "claims_data.csv"))
    
    # Standardize column names across datasets
    if 'Location' in st.session_state.food_listings.columns:
        st.session_state.food_listings['City'] = st.session_state.food_listings['Location']
    if 'Location' in st.session_state.providers.columns:
        st.session_state.providers['City'] = st.session_state.providers['Location']
    if 'Location' in st.session_state.receivers.columns:
        st.session_state.receivers['City'] = st.session_state.receivers['Location']
        
    st.session_state.data_loaded = True

providers = st.session_state.providers
receivers = st.session_state.receivers
food_listings = st.session_state.food_listings
claims = st.session_state.claims

def run_mysql_query(query):
    """Executes a SQL query string against local Pandas DataFrames as a cloud fallback."""
    try:
        providers = st.session_state.providers
        receivers = st.session_state.receivers
        food_listings = st.session_state.food_listings
        claims = st.session_state.claims
        
        if 'provider_type' not in food_listings.columns and 'Provider_Type' in food_listings.columns:
            food_listings = food_listings.rename(columns={'Provider_Type': 'provider_type'})
        if 'status' not in claims.columns and 'Status' in claims.columns:
            claims = claims.rename(columns={'Status': 'status'})
            
        query_processed = query.replace("DATEDIFF(f.expiry_date, c.timestamp)", "julianday(f.expiry_date) - julianday(c.timestamp)")
        
        env = {
            "providers": providers,
            "receivers": receivers,
            "food_listings": food_listings,
            "claims": claims
        }
        
        df = sqldf(query_processed, env)
        return df
        
    except Exception as e:
        st.error(f"SQL Cloud Execution Error: {e}")
        return pd.DataFrame()
    
    
    
sidebar_bg_image = "https://i.postimg.cc/gcgdz83S/2026-06-19-15-15-52.jpg"

st.markdown(
    f"""
    <style>
    /* Target the sidebar block and make its default solid background transparent */
    [data-testid="stSidebar"] {{
        position: relative;
        background-color: rgba(255, 255, 255, 0.15) !important; 
    }}

    /* Create an isolated background layer so the blur effect stays behind your dropdowns */
    [data-testid="stSidebar"]::before {{
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        background-image: url("{sidebar_bg_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        filter: blur(2px); /* 🎛️ Adjust this number to make it more or less blurry */
        z-index: -1; 
        opacity: 0.90; 
    }}
    
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
        color: #000000 !important;
        font-weight: 600;
    }}

    [data-testid="stAppViewContainer"] {{
        background-color: #FDF6ED !important;
    }}

    [data-testid="stHeader"] {{
        background-color: rgba(0, 0, 0, 0) !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)  

# 3. SIDEBAR FILTER PANE

st.sidebar.title("🔍 Global Dashboard Filters")
st.sidebar.markdown("---")

all_cities = ["All Cities"] + sorted(list(food_listings['City'].dropna().unique()))
selected_city = st.sidebar.selectbox("📍 Select City Location:", options=all_cities)

all_providers = ["All Providers"] + sorted(list(providers['Type'].dropna().unique()))
selected_provider_type = st.sidebar.selectbox("🏪 Select Provider Type:", options=all_providers)

all_receivers = ["All Receivers"] + sorted(list(receivers['Type'].dropna().unique()))
selected_receiver_type = st.sidebar.selectbox("🏠 Select Receiver Type:", options=all_receivers)

all_meals = ["All Meal Types"] + sorted(list(food_listings['Meal_Type'].dropna().unique()))
selected_meal = st.sidebar.selectbox("🍱 Select Meal Type:", options=all_meals)

all_foods = ["All Food Types"] + sorted(list(food_listings['Food_Type'].dropna().unique()))
selected_food = st.sidebar.selectbox("🥬 Select Food Type:", options=all_foods)

# 4. INTERACTIVE FILTER PROCESSING ENGINE

filtered_listings = food_listings.copy()
filtered_providers = providers.copy()
filtered_receivers = receivers.copy()
filtered_claims =claims.copy()

if selected_city != "All Cities":
    filtered_listings = filtered_listings[filtered_listings['City'] == selected_city]
    filtered_providers = filtered_providers[filtered_providers['City'] == selected_city]
    filtered_receivers = filtered_receivers[filtered_receivers['City'] == selected_city]

if selected_provider_type != "All Providers":
    filtered_listings = filtered_listings[filtered_listings['Provider_Type'] == selected_provider_type]
    filtered_providers = filtered_providers[filtered_providers['Type'] == selected_provider_type]

if selected_receiver_type != "All Receivers":
    filtered_receivers = filtered_receivers[filtered_receivers['Type'] == selected_receiver_type]

if selected_meal != "All Meal Types":
    filtered_listings = filtered_listings[filtered_listings['Meal_Type'] == selected_meal]

if selected_food != "All Food Types":
    filtered_listings = filtered_listings[filtered_listings['Food_Type'] == selected_food]

# 5. MAIN LAYOUT AND NAVIGATION TABS
st.title("🍎 Local Food Wastage Management System")
st.caption("Comprehensive data infrastructure monitoring supplier networks, contact records, queries, charts, and administration.")
st.markdown("---")

tab_dashboard, tab_charts, tab_CRUD, tab_query = st.tabs([
    "📊 Executive Analytics View", 
    "📈 Business Visuals Dashboard", 
    "🛠️ Database CRUD Management", 
    "🗃️ Business Query Hub"
])

# TAB 1: EXECUTIVE ANALYTICS VIEW
with tab_dashboard:
    kpi1, kpi2, kpi3, kpi4, kpi5= st.columns(5)
    with kpi1:
        st.metric(label="Total Providers", value=len(filtered_providers))
    with kpi2:
        st.metric(label="Total Receivers", value=len(filtered_receivers))
    with kpi3:
        st.metric(label="Total Claims", value=len(filtered_claims))
    with kpi4:
        st.metric(label="Total Units Volume", value=f"{int(filtered_listings['Quantity'].sum()):,}" if not filtered_listings.empty else "0")
    with kpi5:
        unclaimed_count = len(filtered_claims[filtered_claims['Status'].str.lower() == 'pending']) if not filtered_claims.empty else 0
        st.metric(label="Unclaimed Foods", value=unclaimed_count)    
            

    st.markdown("<br>", unsafe_allow_html=True)

    st.header("📞 Provider Contact Information")
    if filtered_providers.empty:
        st.info("No provider contacts match the current filter criteria.")
    else:
        st.dataframe(filtered_providers[['Provider_ID', 'Name', 'Type', 'City', 'Contact']].reset_index(drop=True), use_container_width=True, hide_index=True)

    st.header("📞 Receiver Contact Information")
    if filtered_receivers.empty:
        st.info("No receiver contacts match the current filter criteria.")
    else:
        st.dataframe(filtered_receivers[['Receiver_ID', 'Name', 'Type', 'City', 'Contact']].reset_index(drop=True), use_container_width=True, hide_index=True)    

# TAB 2: EDA CHARTS:  
with tab_charts:
    st.header("📈 Executive Visual Insights Studio")
    st.caption("Select a chart from the matrix below to generate real-time visual distributions from our system tables.")
    
    chart_options = [
        "1. Provider Type Distribution",
        "2. Food Quantity Breakdown by Meal Type",
        "3. Food Type Distribution",
        "4. Meal Type Distribution",
        "5. Top 10 Cities by Number of Food Listings",
        "6. Provider Type vs Quantity",
        "7. Claim Status Distribution"
    ]
    selected_chart = st.selectbox("📊 Select Chart to Generate:", options=chart_options)
    st.markdown("---")
      
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    
    # 📈 CHART 1
    if selected_chart == "1. Provider Type Distribution":
        st.subheader("🏢 Distribution of Provider Types")
        if not filtered_providers.empty:
            col1, col2, col3 = st.columns([0.15, 0.70, 0.15])
            with col2:
                              
                fig, ax = plt.subplots(figsize=(6, 4)) 
                p = sns.countplot(data=filtered_providers, x='Type', hue='Type', palette='Set2', legend=False, ax=ax)
                for container in p.containers:
                    p.bar_label(container, padding=1)
                plt.title('Distribution of Provider Types', fontsize=11)
                plt.xlabel('Provider Type', fontsize=9)
                plt.ylabel('Count', fontsize=9)
                plt.xticks(rotation=45, fontsize=8)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
        else:
            st.info("No provider data available matching current filters.")
    
   # 📈 CHART 2 
    elif selected_chart == "2. Food Quantity Breakdown by Meal Type":
        st.subheader("🍱 Food Quantity Breakdown by Meal Type and Food Type")
        if not filtered_listings.empty:
            col1, col2, col3 = st.columns([0.10, 0.80, 0.10])
            with col2:
                
                fig, ax = plt.subplots(figsize=(8, 5))
                sns.barplot(data=filtered_listings,x='Meal_Type',y='Quantity',hue='Food_Type',estimator=sum,errorbar=None, 
                    palette='muted',ax=ax
                )
                ax.set_title('Food Quantity Breakdown by Meal Type and Food Type', fontsize=11, fontweight='bold')
                ax.set_xlabel('Meal Type', fontsize=9)
                ax.set_ylabel('Total Quantity', fontsize=9)
                ax.legend(title='Food Type',
                    bbox_to_anchor=(1.05, 1),   
                    loc='upper left',
                    fontsize=8,
                    title_fontsize=9)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
        else:
            st.info("No active food listings data available matching current filters.")

    # 📈 CHART 3 
    elif selected_chart == "3. Food Type Distribution":
        st.subheader("🥬 Distribution of Food Types")
        if not filtered_listings.empty:
            col1, col2, col3 = st.columns([0.15, 0.70, 0.15])
            
            with col2:
                fig, ax = plt.subplots()
                ft = sns.countplot(data=filtered_listings, x='Food_Type', hue='Food_Type', palette='pastel', legend=False, ax=ax)
                for container in ft.containers:
                    ft.bar_label(container, padding=1)
                plt.title('Distribution of Food Types')
                plt.xlabel('Food Type')
                plt.ylabel('Count')     
                plt.xticks(rotation=0)
                st.pyplot(fig)
                plt.close(fig)
        else:
            st.info("No active food listings data available matching current filters.")

    # 📈 CHART 4 
    elif selected_chart == "4. Meal Type Distribution":
        st.subheader("🍱 Distribution of Meal Types")
        if not filtered_listings.empty:
            col1, col2, col3 = st.columns([0.15, 0.70, 0.15])
            with col2:
                fig, ax = plt.subplots()
                mt = sns.countplot(data=filtered_listings, x='Meal_Type', hue='Meal_Type', palette='deep', legend=False, ax=ax)
                for container in mt.containers:
                    mt.bar_label(container, padding=1)
                plt.title('Distribution of Meal Types')
                plt.xlabel('Meal Type')
                plt.ylabel('Count')
                plt.xticks(rotation=0)            
                st.pyplot(fig)
                plt.close(fig)
        else:
            st.info("No active food listings data available matching current filters.")

    # 📈 CHART 5
    elif selected_chart == "5. Top 10 Cities by Number of Food Listings":
        st.subheader("📍 Top 10 Cities by Food Listings Count")
        if not filtered_listings.empty:
            top_cities = filtered_listings['City'].value_counts().head(10)
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(x=top_cities.index, y=top_cities.values, ax=ax)
            plt.title('Top 10 Cities by Food Listings')
            plt.xlabel('City')
            plt.ylabel('Number of Listings')
            plt.xticks(rotation=45)
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No active food listings data available matching current filters.")

    # 📈 CHART 6 
    elif selected_chart == "6. Provider Type vs Quantity":
        st.subheader("🏢 Total Food Quantity Donated by Provider Type")
        if not filtered_listings.empty:
            fig, ax = plt.subplots()
            pt = sns.barplot(data=filtered_listings, x='Provider_Type', y='Quantity', estimator=sum, errorbar=None, palette='viridis', ax=ax)
            for container in pt.containers:
                pt.bar_label(container, padding=1)
            plt.title('Total Food Quantity Donated by Provider Type')
            plt.xlabel('Provider Type')
            plt.ylabel('Total Quantity')
            plt.xticks(rotation=0)
            st.pyplot(fig)
            plt.close(fig)
        else:
            st.info("No active food listings data available matching current filters.")

    # 📈 CHART 7 
    elif selected_chart == "7. Claim Status Distribution":
        st.subheader("📊 Ticket Exceptions & Fulfillment Status Distribution")
        if not filtered_claims.empty:
            col1, col2, col3 = st.columns([0.15, 0.70, 0.15])
            with col2:

                status_counts = filtered_claims['Status'].value_counts()
                fig, ax = plt.subplots(figsize=(6, 5))
                ax.pie(status_counts,labels=status_counts.index,autopct='%1.1f%%',colors=['#4CAF50', '#FFC107', '#F44336'],startangle=90
                )
                ax.set_title('Overall Claim Status Distribution', fontsize=11, fontweight='bold')
                ax.axis('equal')  
                plt.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
        else:
            st.info("No claim transaction records available matching current filters.")         

# TAB 3: CENTRALIZED DATABASE CRUD MANAGEMENT
with tab_CRUD:
    st.header("🛠️ Production Logs Admin Panel")
    st.caption("Perform complete operational data creation, updates, or removals safely across any core record system.")
    
    target_table = st.selectbox("🎯 Select Target Database Component:", ["Providers Registry", "Receivers Registry", "Claims Log Registry"])
    crud_action = st.radio("Database Operation Mode:", ["🟢 CREATE ENTRY", "🔵 READ MASTER LOGS", "🟡 UPDATE RECORD", "🔴 DELETE RECORD"], horizontal=True)
    st.markdown("---")
    
    if target_table == "Providers Registry":
        if crud_action == "🟢 CREATE ENTRY":
            st.subheader("➕ Add New Entry to Providers Data Layer")
            with st.form("create_provider_form", clear_on_submit=True):
                next_id = int(st.session_state.providers['Provider_ID'].max() + 1) if not st.session_state.providers.empty else 1
                in_name = st.text_input("Entity Trading Name:")
                in_type = st.selectbox("Establishment Category Type:", ["Supermarket", "Grocery Store", "Restaurant", "Catering Service"])
                in_city = st.text_input("City Location Boundary:")
                in_addr = st.text_input("Street Address Details:")
                in_cont = st.text_input("Active Phone Communication Line:")
                
                if st.form_submit_button("Commit Provider to Database"):
                    if in_name and in_city:
                        new_row = pd.DataFrame([{'Provider_ID': next_id, 'Name': in_name, 'Type': in_type, 'Address': in_addr, 'City': in_city, 'Contact': in_cont}])
                        st.session_state.providers = pd.concat([st.session_state.providers, new_row], ignore_index=True)
                        st.success(f"Registered New Provider ID {next_id} successfully.")
                        st.rerun()
                    else:
                        st.error("Name and City fields are strictly mandatory.")
        elif crud_action == "🔵 READ MASTER LOGS":
            st.dataframe(st.session_state.providers, use_container_width=True, hide_index=True)
        elif crud_action == "🟡 UPDATE RECORD":
            select_edit_id = st.selectbox("Select Target Provider ID to modify:", st.session_state.providers['Provider_ID'].tolist())
            current_row = st.session_state.providers[st.session_state.providers['Provider_ID'] == select_edit_id].iloc[0]
            with st.form("update_provider_form"):
                edit_name = st.text_input("Modify Provider Name:", value=str(current_row['Name']))
                edit_city = st.text_input("Modify Operational City:", value=str(current_row['City']))
                if st.form_submit_button("Apply Value Changes"):
                    idx = st.session_state.providers[st.session_state.providers['Provider_ID'] == select_edit_id].index[0]
                    st.session_state.providers.at[idx, 'Name'] = edit_name
                    st.session_state.providers.at[idx, 'City'] = edit_city
                    st.success("Log override saved successfully!")
                    st.rerun()
        elif crud_action == "🔴 DELETE RECORD":
            select_del_id = st.selectbox("Select Target Provider ID to remove entirely:", st.session_state.providers['Provider_ID'].tolist())
            if st.button("Confirm Atomic Deletion Process"):
                st.session_state.providers = st.session_state.providers[st.session_state.providers['Provider_ID'] != select_del_id].reset_index(drop=True)
                st.success(f"Record for Provider ID {select_del_id} has been pruned.")
                st.rerun()

    elif target_table == "Receivers Registry":
        if crud_action == "🟢 CREATE ENTRY":
            st.subheader("➕ Add New Entry to Receivers Data Layer")
            with st.form("create_receiver_form", clear_on_submit=True):
                next_id = int(st.session_state.receivers['Receiver_ID'].max() + 1) if not st.session_state.receivers.empty else 1
                in_name = st.text_input("Receiver Organization Name:")
                in_type = st.selectbox("Organization Category Type:", ["NGO", "Shelter", "Community Kitchen", "Orphanage"])
                in_city = st.text_input("City Location Boundary:")
                in_addr = st.text_input("Street Address Details:")
                in_cont = st.text_input("Active Contact Line:")
                
                if st.form_submit_button("Commit Receiver to Database"):
                    if in_name and in_city:
                        new_row = pd.DataFrame([{'Receiver_ID': next_id, 'Name': in_name, 'Type': in_type, 'Address': in_addr, 'City': in_city, 'Contact': in_cont}])
                        st.session_state.receivers = pd.concat([st.session_state.receivers, new_row], ignore_index=True)
                        st.success(f"Registered New Receiver ID {next_id} successfully.")
                        st.rerun()
                    else:
                        st.error("Name and City fields are mandatory.")
        elif crud_action == "🔵 READ MASTER LOGS":
            st.dataframe(st.session_state.receivers, use_container_width=True, hide_index=True)
        elif crud_action == "🟡 UPDATE RECORD":
            select_edit_id = st.selectbox("Select Target Receiver ID to modify:", st.session_state.receivers['Receiver_ID'].tolist())
            current_row = st.session_state.receivers[st.session_state.receivers['Receiver_ID'] == select_edit_id].iloc[0]
            with st.form("update_receiver_form"):
                edit_name = st.text_input("Modify Receiver Name:", value=str(current_row['Name']))
                edit_city = st.text_input("Modify Operational City:", value=str(current_row['City']))
                if st.form_submit_button("Apply Value Changes"):
                    idx = st.session_state.receivers[st.session_state.receivers['Receiver_ID'] == select_edit_id].index[0]
                    st.session_state.receivers.at[idx, 'Name'] = edit_name
                    st.session_state.receivers.at[idx, 'City'] = edit_city
                    st.success("Receiver log updated successfully!")
                    st.rerun()
        elif crud_action == "🔴 DELETE RECORD":
            select_del_id = st.selectbox("Select Target Receiver ID to remove entirely:", st.session_state.receivers['Receiver_ID'].tolist())
            if st.button("Confirm Atomic Deletion Process"):
                st.session_state.receivers = st.session_state.receivers[st.session_state.receivers['Receiver_ID'] != select_del_id].reset_index(drop=True)
                st.success(f"Record for Receiver ID {select_del_id} has been pruned.")
                st.rerun()

    elif target_table == "Claims Log Registry":
        if crud_action == "🟢 CREATE ENTRY":
            st.subheader("➕ File New Logistics Claim Entry")
            with st.form("create_claim_form", clear_on_submit=True):
                next_id = int(st.session_state.claims['Claim_ID'].max() + 1) if not st.session_state.claims.empty else 1
                in_food_id = st.selectbox("Link Food Asset ID:", st.session_state.food_listings['Food_ID'].tolist())
                in_rec_id = st.selectbox("Link Receiver Entity ID:", st.session_state.receivers['Receiver_ID'].tolist())
                in_status = st.selectbox("Initial Order Status State:", ["Pending", "Completed", "Cancelled"])
                
                if st.form_submit_button("Log System Claim Ticket"):
                    new_row = pd.DataFrame([{'Claim_ID': next_id, 'Food_ID': in_food_id, 'Receiver_ID': in_rec_id, 'Status': in_status}])
                    st.session_state.claims = pd.concat([st.session_state.claims, new_row], ignore_index=True)
                    st.success(f"Claim Entry Ticket {next_id} successfully mapped.")
                    st.rerun()
        elif crud_action == "🔵 READ MASTER LOGS":
            st.dataframe(st.session_state.claims, use_container_width=True, hide_index=True)
        elif crud_action == "🟡 UPDATE RECORD":
            select_edit_id = st.selectbox("Select Target Claim ID to modify status:", st.session_state.claims['Claim_ID'].tolist())
            current_row = st.session_state.claims[st.session_state.claims['Claim_ID'] == select_edit_id].iloc[0]
            with st.form("update_claim_form"):
                edit_status = st.selectbox("Modify Transaction Pipeline Status:", ["Pending", "Completed", "Cancelled"], index=["Pending", "Completed", "Cancelled"].index(current_row['Status']))
                if st.form_submit_button("Update Ticket State"):
                    idx = st.session_state.claims[st.session_state.claims['Claim_ID'] == select_edit_id].index[0]
                    st.session_state.claims.at[idx, 'Status'] = edit_status
                    st.success(f"Claim Ticket ID {select_edit_id} status updated.")
                    st.rerun()
        elif crud_action == "🔴 DELETE RECORD":
            select_del_id = st.selectbox("Select Target Claim ID to remove entirely:", st.session_state.claims['Claim_ID'].tolist())
            if st.button("Confirm Atomic Deletion Process"):
                st.session_state.claims = st.session_state.claims[st.session_state.claims['Claim_ID'] != select_del_id].reset_index(drop=True)
                st.success(f"Claim Ticket {select_del_id} has been wiped out.")
                st.rerun()

# TAB 4: BUSINESS QUERY HUB (FULLY DYNAMIC ENGINE)
with tab_query:
    st.header("🗃️ Strategic Business Query Hub")
    st.caption("Select an executive business question from the dropdown menu to compute the live MySQL relational data matrix.")
    
    query_options = [
        "1. Total Food Providers and Receivers Count by City Nodes",
        "2. Top Food Provider Segment Contribution analysis",
        "3. Specific Regional Provider Entity Contact Lines",
        "4. Top Performing Receiver Profile by Completed Transactions",
        "5. Aggregate Summary: Total Food Volume Units Available",
        "6. High Density Hub: Top City Node by Postings Frequency",
        "7. Most Common Commodities Circulating in System",
        "8. Total Claim Frequencies Logged per Individual Food Item",
        "9. Most Successful Food Provider Node (Completed Pipeline)",
        "10. Global Platform Claim Ticket Status Breakdown Metrics (%)",
        "11. Average Resource Units Safely Claimed per Active Receiver",
        "12. Peak Volume Demand: Most Claimed Meal Category Window",
        "13. Cumulative Volumetric Contribution Logged per Provider",
        "14. Risk Assessment: Avg Days Left Before Expiry at Claim Phase",
        "15. Trust Metrics Leadership: Most Reliable System Providers"
    ]
    
    selected_query = st.selectbox("📊 Choose a Business Question to Analyze:", options=query_options, key="query_hub_box")
    st.markdown("---")
    
    if selected_query.startswith("1."):
        st.subheader("📋 Food Providers & Receivers Breakdown per City")
        sql = """
            SELECT 
                City,
                SUM(Is_Provider) AS Total_Providers,
                SUM(Is_Receiver) AS Total_Receivers
            FROM (
                SELECT City, 1 AS Is_Provider, 0 AS Is_Receiver FROM providers
                UNION ALL
                SELECT City, 0 AS Is_Provider, 1 AS Is_Receiver FROM receivers
            ) AS combined_cities
            GROUP BY City
            ORDER BY Total_Providers DESC, Total_Receivers DESC;
        """
        df_q = run_mysql_query(sql)
        st.dataframe(df_q, use_container_width=True)
        
    elif selected_query.startswith("2."):
        st.subheader("🏢 Top Volume Contribution by Provider Business Model Type")
        sql = """
            SELECT provider_type, SUM(quantity) AS total_quantity_donated 
            FROM food_listings
            GROUP BY provider_type
            ORDER BY total_quantity_donated DESC;
        """
        df_q = run_mysql_query(sql)
        st.dataframe(df_q, use_container_width=True)
        
    elif selected_query.startswith("3."):
        st.subheader("📍 Target Contact Register (City: Valentineside)")
        sql = """
            SELECT name, type, address, contact 
            FROM providers
            WHERE city = 'Valentineside';
        """
        df_q = run_mysql_query(sql)
        st.dataframe(df_q, use_container_width=True)
        
    elif selected_query.startswith("4."):
        st.subheader("🏆 Leading Receiver Node by Completed Claim Volume Entries")
        sql = """
            SELECT 
                r.name AS receiver_name,
                r.type AS receiver_type,
                COUNT(c.claim_id) AS total 
            FROM receivers r
            LEFT JOIN claims c ON r.receiver_id = c.receiver_id
            WHERE c.status = 'Completed'
            GROUP BY r.receiver_id, receiver_name, receiver_type
            ORDER BY total DESC 
            LIMIT 1;
        """
        df_q = run_mysql_query(sql)
        st.dataframe(df_q, use_container_width=True)
        
    elif selected_query.startswith("5."):
        st.subheader("📊 Global Supply Availability: Total Accumulated Food Units")
        sql = "SELECT SUM(quantity) AS total_food_units FROM food_listings;"
        df_q = run_mysql_query(sql)
        if not df_q.empty:
            total_val = df_q.iloc[0, 0] or 0
            st.metric(label="Total Food Units Available Across Network", value=f"{int(total_val):,}")
        st.dataframe(df_q, use_container_width=True)
        
    elif selected_query.startswith("6."):
        st.subheader("📍 Leading Urban Node by Listing Post Density")
        sql = """
            SELECT location, COUNT(*) AS total 
            FROM food_listings
            GROUP BY location
            ORDER BY total DESC 
            LIMIT 1;
        """
        df_q = run_mysql_query(sql)
        st.dataframe(df_q, use_container_width=True)
        
    elif selected_query.startswith("7."):
        st.subheader("🍎 Top Commodity Profiles Circulated Across Network")
        sql = """
            SELECT food_type, COUNT(*) AS total, SUM(quantity) AS total_quantity 
            FROM food_listings
            GROUP BY food_type
            ORDER BY total DESC;
        """
        df_q = run_mysql_query(sql)
        st.dataframe(df_q, use_container_width=True)
        
    elif selected_query.startswith("8."):
        st.subheader("📋 Pipeline Demand: Claim Requests Made Per Individual Item Name")
        sql = """
            SELECT f.food_name AS food_name, COUNT(c.claim_id) AS total_claims 
            FROM food_listings f
            LEFT JOIN claims c ON f.food_id = c.food_id
            GROUP BY f.food_name
            ORDER BY total_claims DESC;
        """
        df_q = run_mysql_query(sql)
        st.dataframe(df_q, use_container_width=True)
        
    elif selected_query.startswith("9."):
        st.subheader("🏅 Top Performing Provider by Successful Pipeline Fulfillment Logs")
        sql = """
            SELECT p.name AS name, p.type AS provider_type, COUNT(c.claim_id) AS total_successful_claim
            FROM providers p
            INNER JOIN food_listings f ON p.provider_id = f.provider_id
            INNER JOIN claims c ON f.food_id = c.food_id
            WHERE c.Status = 'Completed'
            GROUP BY p.provider_id, p.name, p.type
            ORDER BY total_successful_claim DESC 
            LIMIT 1;
        """
        df_q = run_mysql_query(sql)
        st.dataframe(df_q, use_container_width=True)
        
    elif selected_query.startswith("10."):
        st.subheader("📊 Ticket Exceptions & Fulfillment Status Distribution (%)")
        sql = """
            SELECT 
                Status, 
                COUNT(*) AS Total_Count,
                ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims)), 2) AS Percentage
            FROM claims
            GROUP BY Status;
        """
        df_q = run_mysql_query(sql)
        st.dataframe(df_q, use_container_width=True)
        
    elif selected_query.startswith("11."):
        st.subheader("🥣 Mean Resource Unit Volumetric Capacities Allocated per Receiver Node")
        sql = """
            SELECT ROUND(AVG(avg_food_quantity), 2) AS avg_quantity_per_receiver FROM (
                SELECT r.name AS receiver_name, AVG(f.quantity) AS avg_food_quantity 
                FROM receivers r
                INNER JOIN claims c ON r.receiver_id = c.receiver_id
                INNER JOIN food_listings f ON c.food_id = f.food_id
                WHERE c.status = 'Completed'
                GROUP BY r.receiver_id, r.name
            ) t;
        """
        df_q = run_mysql_query(sql)
        st.dataframe(df_q, use_container_width=True)
        
    elif selected_query.startswith("12."):
        st.subheader("⏱️ Peak System Demand: Most Claimed Meal Window Assignment")
        sql = """
            SELECT f.meal_type, COUNT(c.claim_id) AS total_claimed 
            FROM food_listings f
            INNER JOIN claims c ON f.food_id = c.food_id
            WHERE c.status = 'Completed'
            GROUP BY f.meal_type
            ORDER BY total_claimed DESC 
            LIMIT 1;
        """
        df_q = run_mysql_query(sql)
        st.dataframe(df_q, use_container_width=True)
        
    elif selected_query.startswith("13."):
        st.subheader("🚛 Total Aggregated Volume Units Provided per Unique Entity")
        sql = """
            SELECT p.name AS provider_name, SUM(f.quantity) AS total_qty_provided 
            FROM providers p
            INNER JOIN food_listings f ON p.provider_id = f.provider_id
            GROUP BY p.provider_id, provider_name
            ORDER BY total_qty_provided DESC;
        """
        df_q = run_mysql_query(sql)
        st.dataframe(df_q, use_container_width=True)
        
    elif selected_query.startswith("14."):
        st.subheader("⏳ Quality Assurance: Mean Days Remaining Before Expiry at Claim Entry")
        sql = """
            SELECT 
                f.provider_type,
                f.food_type,
                COUNT(c.claim_id) AS total_claims,
                ROUND(AVG(DATEDIFF(f.expiry_date, c.timestamp)), 1) AS Avg_Days_Left_Before_Expiry
            FROM food_listings f
            INNER JOIN claims c ON f.food_id = c.food_id
            WHERE c.status = 'Completed'
            GROUP BY f.provider_type, f.food_type
            ORDER BY Avg_Days_Left_Before_Expiry ASC;
        """
        df_q = run_mysql_query(sql)
        st.dataframe(df_q, use_container_width=True)
        
    elif selected_query.startswith("15."):
        st.subheader("🤝 Reliability Scorecard (Entities with Min. 5 System Shipments)")
        sql = """
            SELECT 
                p.name AS provider_name,
                p.type AS provider_type,
                COUNT(c.claim_id) AS total_claims,
                SUM(CASE WHEN c.status = 'Completed' THEN 1 ELSE 0 END) AS successful_claims,
                ROUND((SUM(CASE WHEN c.status = 'Completed' THEN 1 ELSE 0 END) / COUNT(c.claim_id)) * 100, 2) AS successful_claim_pcnt
            FROM providers p
            JOIN food_listings f ON p.provider_id = f.provider_id
            JOIN claims c ON f.food_id = c.food_id
            GROUP BY p.provider_id, provider_name, provider_type 
            HAVING total_claims >= 5
            ORDER BY successful_claim_pcnt DESC;
        """
        df_q = run_mysql_query(sql)
        st.dataframe(df_q, use_container_width=True)


    
             

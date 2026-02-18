import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# --- APP CONFIG ---
st.set_page_config(page_title="WDW Dining Scout", page_icon="🏰", layout="centered")

# --- LOAD DATA ---
@st.cache_data
def load_data():
    # Load the CSV file we are going to build
    df = pd.read_csv("dining_locations.csv")
    # Clean up empty strings in discounts/happy hour
    df['disc'] = df['disc'].fillna("")
    df['hh'] = df['hh'].fillna("")
    return df

try:
    df = load_data()
except:
    st.error("Please create the dining_locations.csv file in GitHub.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Settings")
    party = st.number_input("Party Size", 1, 20, 2)
    date = st.date_input("Date", datetime.today())
    f_date = date.strftime("%Y-%m-%d")
    
    st.divider()
    loc_filter = st.selectbox("Filter by Park/Area", ["All"] + sorted(df['loc'].unique().tolist()))
    type_filter = st.multiselect("Filter by Type", df['type'].unique(), default=df['type'].unique())

# --- FILTERING LOGIC ---
filtered = df.copy()
if loc_filter != "All":
    filtered = filtered[filtered['loc'] == loc_filter]
filtered = filtered[filtered['type'].isin(type_filter)]

# Search box
search = st.text_input("Search names or food...", "")
if search:
    filtered = filtered[filtered['name'].str.contains(search, case=False)]

# --- UI ---
st.title("🏰 WDW Dining Scout")

tab_list, tab_map = st.tabs(["📋 Restaurant List", "📍 Map View"])

with tab_list:
    st.subheader(f"Found {len(filtered)} locations")
    for _, row in filtered.iterrows():
        with st.container(border=True):
            st.subheader(row['name'])
            st.caption(f"📍 {row['loc']} | {row['type']}")
            
            if row['hh']:
                st.success(f"🍸 **Happy Hour:** {row['hh']}")
            if row['disc']:
                st.warning(f"🏷️ **Discounts:** {row['disc']}")
            
            c1, c2 = st.columns(2)
            with c1:
                st.link_button("📖 Menu", f"https://disneyworld.disney.go.com/dining/{row['slug']}/menus/", use_container_width=True)
            with c2:
                if pd.notna(row['id']):
                    res_url = f"https://disneyworld.disney.go.com/dining-res/restaurant-search/booking-details/?restaurantId={int(row['id'])}&date={f_date}&partySize={party}"
                    st.link_button("📅 Disney", res_url, type="primary", use_container_width=True)
                
                # Check for OpenTable
                if pd.notna(row['ot']):
                    st.link_button("🟢 OpenTable", row['ot'], use_container_width=True)

with tab_map:
    # Filter out locations without coordinates for the map
    map_df = filtered.dropna(subset=['lat', 'lon'])
    
    if not map_df.empty:
        m = folium.Map(location=[map_df['lat'].mean(), map_df['lon'].mean()], zoom_start=13)
        for _, row in map_df.iterrows():
            folium.Marker(
                [row['lat'], row['lon']], 
                popup=row['name'],
                tooltip=row['name'],
                icon=folium.Icon(color="blue" if pd.notna(row['id']) else "green")
            ).add_to(m)
        st_folium(m, width=700, height=500, returned_objects=[])
    else:
        st.write("No locations with coordinates found for this filter.")
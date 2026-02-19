import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime
import urllib.parse

# --- APP CONFIG ---
st.set_page_config(page_title="WDW Dining Scout", page_icon="🏰", layout="centered")

# --- STYLE ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; }
    .css-1r6slb0 { padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    # 'on_bad_lines' handles the comma errors
    df = pd.read_csv("dining_locations.csv", on_bad_lines='skip')
    df.columns = df.columns.str.strip()
    
    cols = ['name', 'loc', 'type', 'id', 'ot', 'disc', 'hh', 'slug', 'lat', 'lon', 'tips']
    for col in cols:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str).str.strip()
    return df

df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Reservation Info")
    party = st.selectbox("Party Size", range(1, 11), index=1)
    # Note: We use this to show you the date, but the cleanest links work best when 
    # letting Disney's mobile site handle the calendar picker.
    res_date = st.date_input("Target Date", datetime.today())
    
    st.divider()
    loc_filter = st.selectbox("Filter Location", ["All"] + sorted(df['loc'].unique().tolist()))
    type_filter = st.multiselect("Category", df['type'].unique(), default=df['type'].unique())

# --- FILTER LOGIC ---
filtered = df.copy()
if loc_filter != "All":
    filtered = filtered[filtered['loc'] == loc_filter]
filtered = filtered[filtered['type'].isin(type_filter)]

search = st.text_input("🔍 Search (e.g. Steak, Noodles, Fireworks)", "")
if search:
    mask = filtered['name'].str.contains(search, case=False) | \
           filtered['loc'].str.contains(search, case=False) | \
           filtered['tips'].str.contains(search, case=False)
    filtered = filtered[mask]

# --- MAIN UI ---
st.title("🏰 WDW Dining Scout")

tab_list, tab_map = st.tabs(["📋 Restaurant List", "📍 Map View"])

with tab_list:
    for _, row in filtered.iterrows():
        with st.container(border=True):
            st.subheader(row['name'])
            st.caption(f"📍 {row['loc']} | {row['type']}")
            
            if row['tips']:
                st.info(f"💡 {row['tips']}")
            
            # ACTION BUTTONS
            c1, c2, c3 = st.columns(3)
            
            # 1. MENU LINK
            # The safest menu link is the search-redirect or the base URL
            with c1:
                menu_url = f"https://disneyworld.disney.go.com/dining/{row['slug']}/"
                st.link_button("📖 Menu", menu_url)

            # 2. DISNEY RESERVATION LINK
            # We use the 'Storefront' ID link which is the most stable URL Disney has
            with c2:
                if row['id'] and row['id'] != "":
                    try:
                        clean_id = str(int(float(row['id'])))
                        # This URL is the "Golden Link" - it opens the restaurant's 
                        # booking page directly and reliably.
                        disney_res_url = f"https://disneyworld.disney.go.com/dining-res/restaurant-search/results/?id={clean_id}&type=restaurant"
                        st.link_button("📅 Disney", disney_res_url, type="primary")
                    except:
                        st.write("---")
                else:
                    st.caption("Walk-up")

            # 3. OPENTABLE LINK
            with c3:
                if row['ot'] and "opentable.com" in row['ot']:
                    st.link_button("🟢 OpenTable", row['ot'])

with tab_map:
    # Ensure lat/lon are numeric
    map_df = filtered.copy()
    map_df['lat'] = pd.to_numeric(map_df['lat'], errors='coerce')
    map_df['lon'] = pd.to_numeric(map_df['lon'], errors='coerce')
    map_df = map_df.dropna(subset=['lat', 'lon'])
    
    if not map_df.empty:
        m = folium.Map(location=[map_df['lat'].mean(), map_df['lon'].mean()], zoom_start=13)
        for _, row in map_df.iterrows():
            folium.Marker(
                [row['lat'], row['lon']], 
                popup=row['name'],
                tooltip=row['name'],
                icon=folium.Icon(color="blue" if row['id'] else "green")
            ).add_to(m)
        st_folium(m, width=700, height=500, returned_objects=[])
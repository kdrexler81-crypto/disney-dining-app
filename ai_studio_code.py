import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- APP CONFIG ---
st.set_page_config(page_title="WDW Dining Scout", page_icon="🏰", layout="centered")

# --- STYLE ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold; }
    .css-1r6slb0 { padding: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    # Load CSV and skip any messy lines
    df = pd.read_csv("dining_locations.csv", on_bad_lines='skip')
    df.columns = df.columns.str.strip()
    
    # Standardize columns
    cols = ['name', 'loc', 'type', 'slug', 'has_ot', 'disc', 'tips', 'lat', 'lon']
    for col in cols:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("").astype(str).str.strip()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading CSV: {e}")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("📝 My Trip Notes")
    st.text_area("Reservations / Goals:", placeholder="Ex: 7pm Be Our Guest", height=150)
    
    st.divider()
    st.header("🔍 Filters")
    loc_filter = st.selectbox("Location", ["All"] + sorted(df['loc'].unique().tolist()))
    type_filter = st.multiselect("Category", df['type'].unique(), default=df['type'].unique())

# --- FILTER LOGIC ---
filtered = df.copy()
if loc_filter != "All":
    filtered = filtered[filtered['loc'] == loc_filter]
filtered = filtered[filtered['type'].isin(type_filter)]

search = st.text_input("🔍 Search names, food, or tips...", "")
if search:
    mask = filtered['name'].str.contains(search, case=False) | \
           filtered['loc'].str.contains(search, case=False) | \
           filtered['tips'].str.contains(search, case=False)
    filtered = filtered[mask]

# --- MAIN UI ---
st.title("🏰 WDW Dining Scout")

tab_list, tab_map = st.tabs(["📋 List View", "📍 Map View"])

with tab_list:
    st.caption(f"Showing {len(filtered)} results")
    for _, row in filtered.iterrows():
        with st.container(border=True):
            st.subheader(row['name'])
            st.caption(f"📍 {row['loc']} | {row['type']}")
            
            # Discounts & Tips
            if row['disc']:
                st.warning(f"🏷️ **Discounts:** {row['disc']}")
            if row['tips']:
                st.info(f"💡 **Tip:** {row['tips']}")
            
            # THE TWO BUTTONS
            c1, c2 = st.columns(2)
            
            with c1:
                # Direct to Disney Landing Page
                disney_url = f"https://disneyworld.disney.go.com/dining/{row['slug']}/"
                st.link_button("🏰 Disney Page", disney_url)

            with c2:
                # If marked as being on OpenTable, show generic OT button
                if row['has_ot'].lower() in ['yes', 'y', 'true']:
                    st.link_button("🟢 OpenTable", "https://www.opentable.com", type="secondary")
                else:
                    st.write("")

with tab_map:
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
                tooltip=row['name']
            ).add_to(m)
        st_folium(m, width=700, height=500, returned_objects=[])
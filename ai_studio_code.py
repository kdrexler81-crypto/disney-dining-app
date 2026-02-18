import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# --- APP CONFIG ---
st.set_page_config(page_title="WDW Dining Scout", page_icon="🏰", layout="centered")

# --- STYLE ---
st.markdown("""
    <style>
    .tip-box {
        background-color: #f0f2f6;
        border-left: 5px solid #ffca28;
        padding: 10px;
        border-radius: 5px;
        margin: 10px 0px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOAD DATA ---
@st.cache_data
def load_data():
    # 'on_bad_lines' handles the comma errors we saw earlier
    df = pd.read_csv("dining_locations.csv", on_bad_lines='skip')
    
    # Clean up column names (removes hidden spaces)
    df.columns = df.columns.str.strip()
    
    # Fill empty columns to avoid errors
    cols_to_fix = ['disc', 'hh', 'tips', 'ot', 'id']
    for col in cols_to_fix:
        if col in df.columns:
            df[col] = df[col].fillna("")
        else:
            # If the column is missing entirely from CSV, create it as empty
            df[col] = ""
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading CSV: {e}")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("📝 My Trip Notes")
    st.text_area("Save your ADR times or food goals here:", 
                 placeholder="7:15 PM - Be Our Guest\nTry the Peanut Butter Cold Brew...")
    
    st.divider()
    st.header("⚙️ Settings")
    party = st.number_input("Party Size", 1, 20, 2)
    date = st.date_input("Date", datetime.today())
    f_date = date.strftime("%Y-%m-%d")
    
    st.divider()
    loc_filter = st.selectbox("Location", ["All"] + sorted(df['loc'].unique().tolist()))
    type_filter = st.multiselect("Category", df['type'].unique(), default=df['type'].unique())

# --- FILTERING LOGIC ---
filtered = df.copy()
if loc_filter != "All":
    filtered = filtered[filtered['loc'] == loc_filter]
filtered = filtered[filtered['type'].isin(type_filter)]

search = st.text_input("🔍 Search names, locations, or food items...", "")
if search:
    # Use a safer search that handles missing 'tips' column
    mask = filtered['name'].str.contains(search, case=False) | filtered['loc'].str.contains(search, case=False)
    if 'tips' in filtered.columns:
        mask = mask | filtered['tips'].str.contains(search, case=False)
    filtered = filtered[mask]

# --- UI ---
st.title("🏰 WDW Dining Scout")

tab_list, tab_map = st.tabs(["📋 Restaurant List", "📍 Map View"])

with tab_list:
    st.caption(f"Showing {len(filtered)} results")
    for _, row in filtered.iterrows():
        with st.container(border=True):
            st.subheader(row['name'])
            st.caption(f"📍 {row['loc']} | {row['type']}")

            # INSIDER TIP BOX (Safely check if 'tips' exists and isn't empty)
            if 'tips' in row and row['tips']:
                st.info(f"💡 **Insider Tip:** {row['tips']}")

            if 'hh' in row and row['hh']:
                st.success(f"🍸 **Happy Hour:** {row['hh']}")

            if 'disc' in row and row['disc']:
                st.warning(f"🏷️ **Discounts:** {row['disc']}")
            
            # Action Buttons
            c1, c2, c3 = st.columns(3)
            with c1:
                st.link_button("📖 Menu", f"https://disneyworld.disney.go.com/dining/{row['slug']}/menus/", use_container_width=True)
            with c2:
                if row['id'] and str(row['id']).strip() != "":
                    try:
                        clean_id = int(float(row['id']))
                        res_url = f"https://disneyworld.disney.go.com/dining-res/restaurant-search/booking-details/?restaurantId={clean_id}&date={f_date}&partySize={party}"
                        st.link_button("📅 Disney", res_url, type="primary", use_container_width=True)
                    except:
                        st.caption("Res ID Error")
            with c3:
                if row['ot']:
                    st.link_button("🟢 OpenTable", row['ot'], use_container_width=True)

with tab_map:
    map_df = filtered.dropna(subset=['lat', 'lon'])
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
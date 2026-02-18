import streamlit as st
import pandas as pd
from datetime import datetime

# --- APP CONFIG ---
st.set_page_config(page_title="WDW Dining Scout", page_icon="🏰", layout="centered")

# --- EXPANDED DATASET ---
# Format: Name, Location, Type, DisneyID, OT_URL, Discounts, Happy Hour
dining_data = [
    {
        "name": "Be Our Guest", "loc": "Magic Kingdom", "type": "Table Service", 
        "id": "90002476", "ot": None, "disc": ["Disney Visa (10%)"], "hh": None,
        "slug": "be-our-guest-restaurant"
    },
    {
        "name": "The Boathouse", "loc": "Disney Springs", "type": "Table Service", 
        "id": "18395610", "ot": "https://www.opentable.com/the-boathouse-orlando", 
        "disc": ["DVC (10%)", "Annual Pass (10%)"], "hh": "Daily 11am-4pm (Bar Only)",
        "slug": "boathouse-restaurant"
    },
    {
        "name": "Jaleo by José Andrés", "loc": "Disney Springs", "type": "Table Service", 
        "id": "19238382", "ot": "https://www.opentable.com/r/jaleo-disney-springs-lake-buena-vista", 
        "disc": ["Disney Visa (10%)"], "hh": "Sangria Hour: Daily 11:30am-6pm (Bar Only)",
        "slug": "jaleo"
    },
    {
        "name": "Space 220", "loc": "Epcot", "type": "Table Service", 
        "id": "19515902", "ot": None, "disc": [], "hh": None,
        "slug": "space-220-restaurant"
    },
    {
        "name": "STK Steakhouse", "loc": "Disney Springs", "type": "Table Service", 
        "id": "18320141", "ot": "https://www.opentable.com/stk-orlando", 
        "disc": ["DVC (10%)"], "hh": "M-F 3pm-6:30pm, Weekends 3pm-5:30pm",
        "slug": "stk-orlando"
    },
    {
        "name": "Sanaa", "loc": "Resorts (AK Lodge)", "type": "Table Service", 
        "id": "14850774", "ot": "https://www.opentable.com/sanaa", 
        "disc": ["DVC (10%)", "Disney Visa (10%)"], "hh": None,
        "slug": "sanaa"
    },
    {
        "name": "Casey's Corner", "loc": "Magic Kingdom", "type": "Counter Service", 
        "id": None, "ot": None, "disc": [], "hh": None,
        "slug": "caseys-corner"
    },
    {
        "name": "Dole Whip (Aloha Isle)", "loc": "Magic Kingdom", "type": "Snack", 
        "id": None, "ot": None, "disc": [], "hh": None,
        "slug": "aloha-isle"
    }
]

df = pd.DataFrame(dining_data)

# --- UI INTERFACE ---
st.title("🏰 WDW Dining Scout")

# Floating Mobile Search Bar
search = st.text_input("Search (e.g. Steak, Epcot, HH)", "")

# Filter Tabs
tab1, tab2 = st.tabs(["Filters", "Quick Links"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        loc_filter = st.selectbox("Location", ["All", "Magic Kingdom", "Epcot", "Hollywood Studios", "Animal Kingdom", "Disney Springs", "Resorts"])
    with col_b:
        type_filter = st.selectbox("Type", ["All", "Table Service", "Counter Service", "Snack"])

# Logic for Filtering
filtered = df.copy()
if search:
    filtered = filtered[filtered['name'].str.contains(search, case=False) | filtered['loc'].str.contains(search, case=False)]
if loc_filter != "All":
    filtered = filtered[filtered['loc'].str.contains(loc_filter)]
if type_filter != "All":
    filtered = filtered[filtered['type'] == type_filter]

# --- RESERVATION SETTINGS (Global) ---
with st.sidebar:
    st.header("Reservation Settings")
    party = st.number_input("Party Size", 1, 20, 2)
    date = st.date_input("Date", datetime.today())
    f_date = date.strftime("%Y-%m-%d")
    st.info("These settings apply to all 'Reserve' buttons below.")

# --- THE LIST ---
for _, row in filtered.iterrows():
    with st.container(border=True):
        st.subheader(row['name'])
        st.caption(f"📍 {row['loc']} | {row['type']}")
        
        # Discounts & Happy Hours
        if row['hh']:
            st.success(f"🍸 **Happy Hour:** {row['hh']}")
        if row['disc']:
            st.warning(f"🏷️ **Discounts:** {', '.join(row['disc'])}")
        
        # Action Buttons
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            st.link_button("📖 Menu", f"https://disneyworld.disney.go.com/dining/{row['slug']}/menus/", use_container_width=True)
            
        with btn_col2:
            if row['id']:
                res_url = f"https://disneyworld.disney.go.com/dining-res/restaurant-search/booking-details/?restaurantId={row['id']}&date={f_date}&partySize={party}"
                st.link_button("📅 Disney", res_url, type="primary", use_container_width=True)
            else:
                st.write("Walk-up")

        if row['ot']:
            st.link_button("🟢 Check OpenTable", row['ot'], use_container_width=True)

st.markdown("---")
st.caption("Tip: Add this page to your phone's Home Screen for app-like access.")
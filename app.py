import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

#Configuration of Page Layout
st.set_page_config(
    page_title="Himalayan Expedition Data Explorer",
    layout="wide",
    initial_sidebar_state="expanded"
)

#Schema of the Tables
SCHEMA = {
    "exped": ['expid', 'peakid', 'year', 'host', 'leaders', 'nation', 'sponsor', 'highpoint', 'hdeaths'],
    "members": ['expid', 'fname', 'lname', 'status', 'death', 'deathtype'],
    "peaks": ['peakid', 'pkname', 'pkname2', 'location', 'heightm'],
    "refer": ['expid', 'refid', 'ryear', 'rauthor', 'rtitle', 'rpublisher', 'rpubdate']
}

#Def for Loading the Data
@st.cache_data
def load_data():
    data = {}
    for file in SCHEMA.keys():
        try:
            #Data is attempted to be read with utf-8 encoding first.
            try:
                df = pd.read_csv(f"DataCSV/{file}.csv", dtype=str, encoding='utf-8')
            #If that fails, it falls back to latin1 encoding
            except UnicodeDecodeError:
                df = pd.read_csv(f"DataCSV/{file}.csv", dtype=str, encoding='latin1')
            
            #Ensures that required columns exist. If not it adds them with 'N/A' values.
            for col in SCHEMA[file]:
                if col not in df.columns:
                    df[col] = 'N/A'
            data[file] = df.fillna('N/A')
            
        except Exception as e:
            st.error(f"Error loading {file}: {str(e)}")
            data[file] = pd.DataFrame(columns=SCHEMA[file]).fillna('N/A')
    return data


def main():
    #Title and Description
    st.title("Himalayan Expedition Data Explorer")
    st.markdown("Explore expedition data from the Himalayan Database")

    #Load data
    data = load_data()
    exped, members, peaks, refer = data['exped'], data['members'], data['peaks'], data['refer']

    # ===== SIDEBAR FILTERS =====
    with st.sidebar:
        st.header("Filters")

        #Year Filter
        selected_years = st.multiselect(
            "Year",
            options=sorted(exped['year'].unique(), reverse=True),
        )
        
        #Nation Filter
        all_nations = sorted(exped['nation'].unique())
        selected_nations = st.multiselect(
            "Nation",
            options=all_nations,
        )
        
        #Leader Filter
        leader_search = st.text_input("Search Leaders")

    # ===== MAIN EXPEDITION TABLE =====
    st.header("Expeditions")
    
    # Apply filters
    filtered_exped = exped.copy()
    if selected_years:
        filtered_exped = filtered_exped[filtered_exped['year'].isin(selected_years)]
    if selected_nations:
        filtered_exped = filtered_exped[filtered_exped['nation'].isin(selected_nations)]
    if leader_search:
        filtered_exped = filtered_exped[
            filtered_exped['leaders'].str.contains(leader_search, case=False, na=False)
        ]

    # Configuring the AgGrid
    gb = GridOptionsBuilder.from_dataframe(filtered_exped[SCHEMA['exped'][:6]])
    gb.configure_selection('single')
    grid_response = AgGrid(
        filtered_exped,
        gridOptions=gb.build(),
        height=300,
        theme='streamlit',
        reload_data=False
    )

if __name__ == "__main__":
    main()
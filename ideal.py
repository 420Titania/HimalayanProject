import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

# Configure page layout
st.set_page_config(
    page_title="Himalayan Expedition Data Explorer",
    layout="wide",
    initial_sidebar_state="expanded"
)

def safe_get_columns(df, possible_columns, fillna=True):
    # Safely extract available columns with optional NA filling
    available = [col for col in possible_columns if col in df.columns]
    result = df[available].copy()
    return result.fillna('N/A') if fillna else result

@st.cache_data
def load_data():
    # Load all data files with column existence checks
    try:
        exped = pd.read_csv("DataCSV/exped.csv", dtype=str)
        members = pd.read_csv("DataCSV/members.csv", dtype=str)
        peaks = pd.read_csv("DataCSV/peaks.csv", dtype=str)
        refer = pd.read_csv("DataCSV/refer.csv", dtype=str, encoding='latin1')
        
        # Ensure required columns exist in each file
        exped = safe_get_columns(exped, ['expid', 'year', 'nation', 'leaders', 'peakid'], False)
        members = safe_get_columns(members, ['expid', 'name', 'citizenship', 'sex', 'age', 'role', 'status'], False)
        peaks = safe_get_columns(peaks, ['peakid', 'pkname', 'heightm', 'firstascent', 'climbingstatus'], False)
        refer = safe_get_columns(refer, ['expid', 'reference'], False)
        
        return exped, members, peaks, refer
    except Exception as e:
        st.error(f"Data loading error: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def display_expedition_details(selected, members, peaks, refer, exped):
    # Display all details for a selected expedition
    try:
        selected_expid = selected.get('expid', '').strip().lower()
        
        # Expedition Details
        with st.expander(f"Expedition Details: {selected_expid.upper()}", expanded=True):
            cols = st.columns(3)
            cols[0].metric("Year", selected.get('year', 'N/A'))
            cols[1].metric("Nation", selected.get('nation', 'N/A'))
            cols[2].metric("Leaders", selected.get('leaders', 'N/A'))
        
        # Members Section
        filtered_members = members[
            members['expid'].str.strip().str.lower() == selected_expid
        ].copy()
        
        with st.expander(f"Members ({len(filtered_members)})", expanded=True):
            if not filtered_members.empty:
                display_data = safe_get_columns(
                    filtered_members,
                    ['name', 'citizenship', 'sex', 'age', 'role', 'status']
                )
                AgGrid(
                    display_data,
                    height=min(400, 50 + len(display_data) * 40),
                    theme='streamlit',
                    fit_columns_on_grid_load=True
                )
            else:
                st.warning("No members data found")
        
        # Peak Details
        peak_info = exped[exped['expid'].str.strip().str.lower() == selected_expid]['peakid']
        if not peak_info.empty:
            peakid = peak_info.iloc[0].strip().lower()
            filtered_peaks = peaks[peaks['peakid'].str.strip().str.lower() == peakid]
            
            with st.expander("Peak Details", expanded=True):
                if not filtered_peaks.empty:
                    peak_data = filtered_peaks.iloc[0].to_dict()
                    cols = st.columns(2)
                    cols[0].metric("Peak Name", peak_data.get('pkname', 'N/A'))
                    cols[1].metric("Height (m)", peak_data.get('heightm', 'N/A'))
                    st.write("**First Ascent:**", peak_data.get('firstascent', 'N/A'))
                    st.write("**Climbing Status:**", peak_data.get('climbingstatus', 'N/A'))
                else:
                    st.warning("No peak details found")
        
        # References
        filtered_refer = refer[
            refer['expid'].str.strip().str.lower() == selected_expid
        ].copy()
        
        with st.expander("References", expanded=False):
            if not filtered_refer.empty:
                display_data = safe_get_columns(filtered_refer, ['reference'])
                AgGrid(
                    display_data,
                    height=min(300, 50 + len(display_data) * 40),
                    theme='streamlit'
                )
            else:
                st.info("No references found")
    except Exception as e:
        st.error(f"Error displaying details: {str(e)}")

def main():
    st.title("Himalayan Expedition Data Explorer")
    st.markdown("Explore expedition data from the Himalayan Database")
    
    # Load data with all safeguards
    exped, members, peaks, refer = load_data()
    
    # Check data integrity
    if exped.empty:
        st.error("Critical error: No expedition data loaded. Check exped.csv")
        return
    
    # Sidebar filters with safe defaults
    with st.sidebar:
        st.header("Filters")
        year_options = exped['year'].dropna().unique()
        nation_options = exped['nation'].dropna().unique()
        
        year_filter = st.multiselect("Years", options=sorted(year_options))
        nation_filter = st.multiselect("Nations", options=sorted(nation_options))
        leader_filter = st.text_input("Leader Search")
    
    # Apply filters
    filtered_exped = exped.copy()
    if year_filter:
        filtered_exped = filtered_exped[filtered_exped['year'].isin(year_filter)]
    if nation_filter:
        filtered_exped = filtered_exped[filtered_exped['nation'].isin(nation_filter)]
    if leader_filter:
        filtered_exped = filtered_exped[
            filtered_exped['leaders'].str.contains(leader_filter, case=False, na=False)
        ]
    
    # Configure and display main table
    gb = GridOptionsBuilder.from_dataframe(filtered_exped)
    gb.configure_selection('single')
    grid_response = AgGrid(
        filtered_exped,
        gridOptions=gb.build(),
        height=400,
        width='100%',
        theme='streamlit'
    )
    
    # Handle selection
    selected_rows = grid_response.get('selected_rows', [])
    
    # Convert to list of dicts if it's a DataFrame
    if hasattr(selected_rows, 'to_dict'):
        selected_rows = selected_rows.to_dict('records')
    
    # Check if any rows are selected
    if len(selected_rows) > 0:
        display_expedition_details(selected_rows[0], members, peaks, refer, exped)
    else:
        st.info("ℹSelect an expedition from the table above to view details")

if __name__ == "__main__":
    main()
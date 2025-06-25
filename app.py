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
    "exped": ['expid', 'peakid', 'year', 'leaders', 'nation', 'host', 'sponsor', 'highpoint', 'hdeaths'],
    "members": ['expid', 'fname', 'lname', 'status', 'death', 'deathtype'],
    "peaks": ['peakid', 'pkname', 'pkname2', 'location', 'heightm'],
    "refer": ['expid', 'refid', 'ryear', 'rauthor', 'rtitle', 'rpublisher']
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

    # < SIDEBAR FILTERS >
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

    # < MAIN EXPEDITION TABLE >
    st.header("🗂️ Expeditions")
    
    # Applying filters
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

    # < SAFE SELECTION HANDLING >
    selected_rows = grid_response['selected_rows']
    
    # Handle both list and DataFrame return types
    if isinstance(selected_rows, list) and len(selected_rows) > 0:
        selected_exp = selected_rows[0]
    elif hasattr(selected_rows, 'to_dict'):
        selected_rows = selected_rows.to_dict('records')
        if selected_rows:
            selected_exp = selected_rows[0]
        else:
            selected_exp = None
    else:
        selected_exp = None

    # < DETAILS SECTION >
    if selected_exp:
        exp_id = selected_exp['expid']
        
        # 1. Expedition Details
        with st.expander(f"🧭 Expedition Details:", expanded=True):
            cols = st.columns(3)        
            cols[0].write(f"**Expedition ID:** {selected_exp['expid']}")
            cols[1].write(f"**Year:** {selected_exp['year']}")
            
            cols = st.columns(3)
            cols[0].write(f"**Host:** {selected_exp['host']}")
            cols[1].write(f"**Leaders:** {selected_exp['leaders']}")
            cols[2].write(f"**Nation:** {selected_exp['nation']}")

            cols = st.columns(3)
            cols[0].write(f"**Sponsor:** {selected_exp['sponsor']}")
            cols[1].write(f"**High Point:** {selected_exp['highpoint']} m")
            cols[2].write(f"**Deaths:** {selected_exp['hdeaths']}")
        
        # 2. Members Table
        with st.expander(f"🗣 Members", expanded=False):
            member_data = members[members['expid'] == exp_id][SCHEMA['members'][1:]]
            if not member_data.empty:
                col1, col2 = st.columns(2)
                with col1:
                    st.dataframe(member_data[['fname', 'lname', 'status']])
                with col2:
                    st.dataframe(member_data[['death', 'deathtype']])
            else:
                st.warning("No member records found")

        # 3. Peak Information
        peak_data = peaks[peaks['peakid'] == selected_exp['peakid']]
        with st.expander("⛰️ Peak Details", expanded=False):
            if not peak_data.empty:
                cols = st.columns(3)
                cols[0].write(f"**Peak ID:** {selected_exp['peakid']}")
                cols[1].write(f"**Height:** {peak_data['heightm'].values[0]} m")
                
                cols = st.columns(3)
                cols[0].write(f"**Location:** {peak_data['location'].values[0]}")
                cols[1].write(f"**Primary Name:** {peak_data['pkname'].values[0]}")
                cols[2].write(f"**Alternate Name:** {peak_data['pkname2'].values[0] if 'pkname2' in peak_data.columns else 'N/A'}")
            else:
                st.warning("No peak data available")

        # 4. References
        ref_data = refer[refer['expid'] == exp_id][SCHEMA['refer'][1:]]
        with st.expander("📚 References", expanded=False):
            if not ref_data.empty:
                for _, row in ref_data.iterrows():
                    st.caption(f"{row['ryear']} - {row['rauthor']}: *{row['rtitle']}* ({row['rpublisher']})")
            else:
                st.info("No references found")    

if __name__ == "__main__":
    main()
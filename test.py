import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

# Configure page layout
st.set_page_config(
    page_title="Himalayan Data Explorer - Complete View",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Master schema with ALL columns from each file
SCHEMA = {
    "exped": [
        'expid', 'peakid', 'year', 'season', 'host', 'route1', 'route2', 'route3', 'route4',
        'nation', 'leaders', 'sponsor', 'success1', 'success2', 'success3', 'success4',
        'ascent1', 'ascent2', 'ascent3', 'ascent4', 'claimed', 'disputed', 'countries',
        'approach', 'bcdate', 'smtdate', 'smttime', 'smtdays', 'totdays', 'termdate',
        'termreason', 'termnote', 'highpoint', 'traverse', 'ski', 'parapente', 'camps',
        'rope', 'totmembers', 'smtmembers', 'mdeaths', 'tothired', 'smthired', 'hdeaths',
        'nohired', 'o2used', 'o2none', 'o2climb', 'o2descent', 'o2sleep', 'o2medical',
        'o2taken', 'o2unkwn', 'othersmts', 'campsites', 'accidents', 'achievment',
        'agency', 'comrte', 'stdrte', 'primrte', 'primmem', 'primref', 'primid', 'chksum'
    ],
    "members": [
        'expid', 'membid', 'peakid', 'myear', 'mseason', 'fname', 'lname', 'sex', 'yob',
        'citizen', 'status', 'residence', 'occupation', 'leader', 'deputy', 'bconly',
        'nottobc', 'support', 'disabled', 'hired', 'sherpa', 'tibetan', 'msuccess',
        'mclaimed', 'mdisputed', 'msolo', 'mtraverse', 'mski', 'mparapente', 'mspeed',
        'mhighpt', 'mperhighpt', 'msmtdate1', 'msmtdate2', 'msmtdate3', 'msmttime1',
        'msmttime2', 'msmttime3', 'mroute1', 'mroute2', 'mroute3', 'mascent1', 'mascent2',
        'mascent3', 'mo2used', 'mo2none', 'mo2climb', 'mo2descent', 'mo2sleep', 'mo2medical',
        'mo2note', 'death', 'deathdate', 'deathtime', 'deathtype', 'deathhgtm', 'deathclass',
        'msmtbid', 'msmtterm', 'hcn', 'mchksum'
    ],
    "peaks": [
        'peakid', 'pkname', 'pkname2', 'location', 'heightm', 'heightf', 'himal', 'region',
        'open', 'unlisted', 'trekking', 'trekyear', 'restrict', 'phost', 'pstatus', 'pyear',
        'pseason', 'pmonth', 'pday', 'pexpid', 'pcountry', 'psummiters', 'psmtnote'
    ],
    "refer": [
        'expid', 'refid', 'ryear', 'rtype', 'rjrnl', 'rauthor', 'rtitle', 'rpublisher',
        'rpubdate', 'rlanguage', 'rcitation', 'ryak94'
    ]
}

@st.cache_data
def load_data():
    """Load all datasets with encoding fallback"""
    data = {}
    for file in SCHEMA.keys():
        try:
            # Try UTF-8 first, fallback to latin1 if needed
            try:
                df = pd.read_csv(f"DataCSV/{file}.csv", dtype=str, encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(f"DataCSV/{file}.csv", dtype=str, encoding='latin1')
            
            # Ensure all columns exist
            for col in SCHEMA[file]:
                if col not in df.columns:
                    df[col] = 'N/A'
            data[file] = df.fillna('N/A')
            
        except Exception as e:
            st.error(f"Error loading {file}: {str(e)}")
            # Create empty dataframe with all columns
            data[file] = pd.DataFrame(columns=SCHEMA[file]).fillna('N/A')
    return data['exped'], data['members'], data['peaks'], data['refer']

def display_full_table(df, title, height=400):
    """Display complete table with all columns"""
    st.subheader(title)
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(
        min_column_width=100,
        resizable=True,
        wrapText=True,
        autoHeight=True
    )
    AgGrid(
        df,
        gridOptions=gb.build(),
        height=height,
        theme='streamlit',
        fit_columns_on_grid_load=False,
        reload_data=False
    )

def main():
    st.title("Himalayan Data Explorer - Complete Schema View")
    exped, members, peaks, refer = load_data()
    
    # Display all tables with complete columns
    display_full_table(exped, "Expeditions Table")
    display_full_table(members, "Members Table")
    display_full_table(peaks, "Peaks Table")
    display_full_table(refer, "References Table")
    
    # Data quality checks
    st.sidebar.header("Data Quality Report")
    st.sidebar.metric("Total Expeditions", len(exped))
    st.sidebar.metric("Total Members", len(members))
    
    # Check for data issues
    if len(peaks[peaks['peakid'] == 'N/A']) > 0:
        st.sidebar.warning("⚠ Missing peakid values")
    if len(refer[refer['rcitation'] == 'N/A']) > 0:
        st.sidebar.warning("⚠ Missing citations")

if __name__ == "__main__":
    main()
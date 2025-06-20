import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder

st.set_page_config(
    page_title="Himalayan Expedition Data Explorer",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    try:
        exped = pd.read_csv("DataCSV/exped.csv", dtype=str)
        members = pd.read_csv("DataCSV/members.csv", dtype=str)
        peaks = pd.read_csv("DataCSV/peaks.csv", dtype=str)
        refer = pd.read_csv("DataCSV/refer.csv", dtype=str, encoding='latin1')
        return exped, members, peaks, refer
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def main():
    st.title("Himalayan Expedition Data Explorer")
    st.markdown("Explore expedition data from the Himalayan Database")

    # Load data with all safeguards
    exped, members, peaks, refer = load_data()

if __name__ == "__main__":
    main()
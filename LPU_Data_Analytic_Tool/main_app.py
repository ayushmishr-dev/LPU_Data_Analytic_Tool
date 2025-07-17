import streamlit as st
from yt_discovery import run_yt_discovery
from yt_classification import run_yt_classification
from ig_discovery import run_ig_discovery
from ig_classification import run_ig_classification  # Optional, if you want separate classification logic

st.set_page_config(page_title="LPU IG & YT Automation Tool", layout="wide")
st.title("LPU Instagram & YouTube Automation Tool")

col1, col2 = st.columns(2)

with col1:
    st.header("YouTube Tools")
    yt_days_back = st.number_input("How many days back? (YouTube)", min_value=1, max_value=365, value=7, step=1)
    if st.button("Run YouTube Discovery"):
        run_yt_discovery(days_back=yt_days_back)
    if st.button("Run YouTube Classification"):
        run_yt_classification(days_back=yt_days_back)

with col2:
    st.header("Instagram Tools")
    ig_days_back = st.number_input("How many days back? (Instagram)", min_value=1, max_value=365, value=7, step=1, key="ig_days")
    if st.button("Run IG Discovery"):
        run_ig_discovery(days_back=ig_days_back)
    if st.button("Run IG Classification"):
         run_ig_classification(days_back=ig_days_back)  

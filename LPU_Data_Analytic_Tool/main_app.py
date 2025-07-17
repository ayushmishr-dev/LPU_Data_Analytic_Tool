import streamlit as st
from ig_discovery import run_ig_discovery
from ig_classification import run_ig_classification
from yt_discovery import run_yt_discovery
from yt_classification import run_yt_classification

# --- Custom Styles ---
st.markdown("""
    <style>
        .bluebar {
            background: #295279;
            color: #fff;
            padding: 15px 24px;
            margin-bottom: 14px;
            border-radius: 9px;
            font-size: 1.05rem;
            font-weight: 600;
            letter-spacing: 0.02em;
        }
        .main-title {
            font-size: 2.3rem;
            font-weight: 800;
            color: #e3e9f3;
        }
        .subtitle {
            font-size: 1.05rem;
            color: #b0b8c7;
            margin-bottom: 18px;
        }
        .stRadio > div {
            flex-direction: row;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 32px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title and Subtitle ---
st.markdown('<div class="main-title">LPU Data Analytic Tool</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">For internal use – LPU marketing & analytics team</div>', unsafe_allow_html=True)

# --- Tabs ---
tabs = st.tabs(["YouTube", "Instagram"])

# --- YouTube Tab ---
with tabs[0]:
    st.header("YouTube Workflows")
    # Two blue status bars for YouTube (set to 'Never', can make dynamic if needed)
    st.markdown('<div class="bluebar">Last Discovery: Never</div>', unsafe_allow_html=True)
    st.markdown('<div class="bluebar">Last Classification: Never</div>', unsafe_allow_html=True)

    yt_task = st.radio("Task", options=["Discovery", "Classification"], horizontal=True, key="yt_task")
    yt_days_back = st.number_input("How many days back?", min_value=1, max_value=365, value=0, step=1, key="yt_days")

    # Only show the right button for task
    if yt_task == "Discovery":
        if st.button("Run YT Discovery"):
            run_yt_discovery(days_back=yt_days_back)
    else:
        if st.button("Run YT Classification"):
            run_yt_classification(days_back=yt_days_back)

# --- Instagram Tab ---
with tabs[1]:
    st.header("Instagram Workflows")
    st.markdown('<div class="bluebar">Last Discovery: Never</div>', unsafe_allow_html=True)
    st.markdown('<div class="bluebar">Last Classification: Never</div>', unsafe_allow_html=True)

    ig_task = st.radio("Task", options=["Discovery", "Classification"], horizontal=True, key="ig_task")
    ig_days_back = st.number_input("How many days back?", min_value=1, max_value=365, value=0, step=1, key="ig_days")

    # Only show the right button for task
    if ig_task == "Discovery":
        if st.button("Run IG Discovery"):
            run_ig_discovery(days_back=ig_days_back)
    else:
        if st.button("Run IG Classification"):
            run_ig_classification(days_back=ig_days_back)

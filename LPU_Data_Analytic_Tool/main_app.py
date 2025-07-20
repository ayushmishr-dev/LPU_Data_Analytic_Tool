import streamlit as st
from ig_discovery import run_ig_discovery
from ig_classification import run_ig_classification
from yt_discovery import run_yt_discovery
from yt_classification import run_yt_classification
from datetime import datetime

# --- Custom Styles & Logo ---
st.markdown(
    """
    <img src="https://gallerypng.com/wp-content/uploads/2024/08/lpu-logo-png-image-750x275.png"
         width="150" style="float:left; margin-right:18px; margin-bottom:6px;">
    """,
    unsafe_allow_html=True,
)
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
    # Blue status bars (could be made dynamic if you store last-run in session/file)
    st.markdown('<div class="bluebar">Last Discovery: Never</div>', unsafe_allow_html=True)
    st.markdown('<div class="bluebar">Last Classification: Never</div>', unsafe_allow_html=True)

    yt_task = st.radio("Task", options=["Discovery", "Classification"], horizontal=True, key="yt_task")
    yt_days_back = st.number_input("How many days back?", min_value=1, max_value=365, value=1, step=1, key="yt_days")

    if yt_task == "Discovery":
        if st.button("Run YT Discovery"):
            run_yt_discovery(days_back=yt_days_back)
            st.success("YouTube Discovery complete! 🚀\n\n**Before running Classification, open your Google Sheet and fill in the 'Assigned Type' column for the new videos.**")
    else:
        st.warning("Please ensure the 'Assigned Type' column is filled in the 'Discovered Videos' sheet before running Classification. See the guide below.")
        if st.button("Run YT Discovery"):
            run_yt_classification(days_back=yt_days_back)

# --- Instagram Tab ---
with tabs[1]:
    st.header("Instagram Workflows")
    st.markdown('<div class="bluebar">Last Discovery: Never</div>', unsafe_allow_html=True)
    st.markdown('<div class="bluebar">Last Classification: Never</div>', unsafe_allow_html=True)

    ig_task = st.radio("Task", options=["Discovery", "Classification"], horizontal=True, key="ig_task")
    ig_days_back = st.number_input("How many days back?", min_value=1, max_value=365, value=1, step=1, key="ig_days")

    if ig_task == "Discovery":
        if st.button("Run IG Discovery"):
            run_ig_discovery(days_back=ig_days_back)
            st.success("Instagram Discovery complete! 🚀\n\n**Before running Classification, open your Google Sheet and fill in the 'Assignment Type' column for the new reels.**")
    else:
        st.warning("Please ensure the 'Assignment Type' column is filled in the 'Discovered IG Reels' sheet before running Classification. See the guide below.")
        if st.button("Run IG Classification"):
            run_ig_classification(days_back=ig_days_back)

# --- Assignment Type Guide Section ---
st.markdown("---")
st.header("Assignment Type Guide")

with st.expander("📺 YouTube Assignment Types"):
    st.markdown("""
| Assignment Type            | Output Sheet Name                 |
| -------------------------- | --------------------------------- |
| `student`                  | Student Youtube Video             |
| `influencer_commercial`    | Youtube Short with Commercials    |
| `influencer_noncommercial` | Youtube Short without Commercials |
| `creatorverse`             | CreatorVerse                      |
""")

with st.expander("📸 Instagram Assignment Types"):
    st.markdown("""
| Assigned Type              | Output Sheet Name                    |
| -------------------------- | ------------------------------------ |
| `influencer_commercial`    | Influencer Reel with Commercials     |
| `influencer_noncommercial` | Influencer Reel without Commercials  |
| `chancellor_pr`            | Chancellor Sir PR                    |
| `meme_marketing`           | Meme Marketing                       |
| `campus_reel`              | Campus Reel                          |
| `student_profile`          | Student Profiles                     |
| `long_term_promotion`      | Long Term Promotion                  |
| `shoutout`                 | Shoutout                             |
| `instaconfluence`          | InstaConfluence                      |
| `diwali_competition`       | Diwali Competition                   |
| `olympics`                 | Olympics                             |
| `digital_star`             | Digital Star                         |
| `outcampus`                | Outcampus                            |
""")

import streamlit as st

st.set_page_config(page_title="FinViz Stock Snapshot", layout="wide", initial_sidebar_state="expanded")

st.title("FinViz Stock Snapshot")
st.caption("Use the sidebar to open About, Stock, or ETFs.")

st.markdown(
    """
    <style>
    .metric-label { font-size: 0.8rem; color: #6b7280; }
    .section-title { font-size: 1.05rem; font-weight: 600; margin-bottom: 0.25rem; }
    /* Move sidebar to the right */
    section[data-testid="stSidebar"] { right: 0; left: auto; }
    section[data-testid="stSidebar"] > div { right: 0; left: auto; }
    main { padding-right: 22rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("Open **About**, **Stock**, or **ETFs** from the sidebar.")

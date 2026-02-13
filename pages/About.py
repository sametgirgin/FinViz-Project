import streamlit as st

st.set_page_config(page_title="About", layout="wide")

st.title("About")

try:
    notes = open("finviz.md", "r", encoding="utf-8").read().strip()
except FileNotFoundError:
    notes = ""

if notes:
    st.markdown(notes)
else:
    st.info("finviz.md is empty or missing. Add notes to publish them here.")

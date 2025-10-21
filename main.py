import streamlit as st

# Define pages
pages = [
    st.Page("pages/fair_evaluation.py", title="FAIR Evaluation", icon="📊", default=True),
    st.Page("pages/sparql_explorer.py", title="SPARQL Explorer", icon="🔍"),
    st.Page("pages/rdi_evaluation.py", title="RDI Evaluation", icon="📈"),
    st.Page("pages/resource_uploader.py", title="Resource Uploader", icon="📁"),
    st.Page("pages/about.py", title="About", icon="ℹ️"),
]

# Configure navigation
pg = st.navigation(pages)

# Set the page configuration AFTER defining navigation
st.set_page_config(page_title="FAIR Evaluation App", page_icon="🌐", layout="wide")

# GitHub Repository Link in Sidebar
repo_url = "https://github.com/fairagro/FAIR_evaluation_repository"
st.sidebar.markdown(
    f'<a href="{repo_url}" target="_blank" style="text-decoration: none; font-weight: bold;">🔗 GitHub Repository</a>',
    unsafe_allow_html=True,
)

# Run the selected page
pg.run()

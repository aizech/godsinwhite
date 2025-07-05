import streamlit as st
import pandas as pd
import numpy as np
import datetime
from config import config

if "init" not in st.session_state:
    st.session_state.init = True

pages = [
    st.Page(
        "Home.py",
        title="Home",
        icon=":material/home:"
    ),
    st.Page(
        "pages/Medical_Image_Analysis.py",
        title="Medical Image Analysis",
        icon=":material/diagnosis:"
    ),
    st.Page(
        "pages/Generated_Images.py",
        title="Generated Images",
        icon=":material/photo_library:"
    ),
    st.Page(
        "pages/Configuration.py",
        title="Configuration",
        icon=":material/settings:"
    ),
    st.Page(
        "pages/About.py",
        title="About",
        #icon=":material/widgets:"
        icon=":material/info:"
    ),
]

page = st.navigation(pages)
page.run()


#with st.sidebar.container(height=310):
#    if page.title == "Home":
#        pass
#    elif page.title == "About":
#        pass
#    else:
#        pass

st.sidebar.markdown(" ")
st.sidebar.caption(f"©  {datetime.date.today().year} | Made with :material/favorite: by [{config.COMPANY}]({config.COMPANY_URL})")
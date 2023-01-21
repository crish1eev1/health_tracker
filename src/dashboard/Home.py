# -----------------------------------------------------------------------------
# streamlit run your_script.py
# -----------------------------------------------------------------------------
import streamlit as st
from PIL import Image

# -----------------------------------------------------------------------------
# Home page
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="crish1eev1 Garmin Dashboard",
    page_icon="👋",
)

st.write("# Welcome to my Garmin Dashboard! 👋")

st.sidebar.success("Select a dashboard page above.")

st.markdown(
    """
    This dashboard is part of a personal project where I'm extracting, cleaning and transforming Garmin Connect data before sharing my main findings interactively through this dashboard.
    
    **👈 Select a page from the sidebar** to start exploring the data.
    
    ### Want to learn more?
    - Check out my project [readme file](https://tocomplete)
    - Jump into the [documentation](https://tocomplete)
    - Contact me via [my linkedin](https://www.linkedin.com/in/christophe-level/)
      
      
"""
)

image = Image.open("/src/dashboard/health_tracking_banner.png")

st.image(image, caption="image generated with Midjourney")

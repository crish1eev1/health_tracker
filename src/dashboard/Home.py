# -----------------------------------------------------------------------------
# streamlit run your_script.py
# -----------------------------------------------------------------------------
import streamlit as st
from PIL import Image

# -----------------------------------------------------------------------------
# streamlit test
# -----------------------------------------------------------------------------
# st.title("Simple Garmin App")

# # Add empty space above image
# st.empty()

# # Add image next to the title
# st.image("https://ph.garmin.com/m/ph/g/products/cf-lg_312.jpg", width=100)

# st.write(
#     """
# ## Monitoring metrics
# """
# )

# st.sidebar.write("Side Bar")

# st.write(
#     """
# ### Stress
# """
# )
# start_dt = st.sidebar.date_input("Start date", value=df["timestamp"].min())
# end_dt = st.sidebar.date_input("End date", value=df["timestamp"].max())
# if start_dt <= end_dt:
#     filtered_df = df[
#         df["timestamp"] > datetime(start_dt.year, start_dt.month, start_dt.day)
#     ]
#     filtered_df = df[df["timestamp"] < datetime(end_dt.year, end_dt.month, end_dt.day)]
#     st.line_chart(filtered_df, x="timestamp", y="stress")
#     st.dataframe(filtered_df)
# else:
#     st.error("Start date must be > End date")


# start_dt = df["timestamp"].min()


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

image = Image.open("banner.png")

st.image(image, caption="image generated with Midjourney")

import base64
import json
import os
import pathlib
import streamlit as st

from version import __version__

# Helper Functions
def load_json(name):
    try:
        return json.load(open(os.path.join("data", f"{name}.json")))
    except FileNotFoundError:
        return []

# Must be the first Streamlit command!
st.set_page_config(
    page_title=f"Prompt Forge {__version__} - Link Page",
    layout="wide"
)

# columns for banner + content
col_left, col_center = st.columns([2, 7])

with col_left:
    banner_path = pathlib.Path("assets/robo-generate.png")
    img_b64 = base64.b64encode(banner_path.read_bytes()).decode()
    st.markdown(f"""
      <style>
        .fixed-banner {{ position:fixed; top:0; left:0; width:25%; padding:5px;
                        margin:0; border-radius:5px;
                        background:transparent; z-index:9999; text-align:center; }}
        .block-container {{ padding-top:120px; }}
      </style>
      <div class="fixed-banner">
        <img src="data:image/png;base64,{img_b64}"
                alt="Prompt Forge Banner"
                title="Created with ChatGPT (ironically!) 😁"
             style="width:300px; height:300px; margin:0 auto;">
      </div>
    """, unsafe_allow_html=True)

with col_center:
    col_left, col_center, col_right = st.columns([1, 2, 1])  # Adjust column widths for centering

    with col_center:
        st.markdown("At the request of the original \"Midjourney Prompter\" creator, this site has been renamed and moved to to:", unsafe_allow_html=True,)

        # Simple text box with a link
        link_text = "https://streamlit.io/PromptForge"

        # Display the link as clickable
        st.markdown(f"[Click here to use Prompt Forge]({link_text})", unsafe_allow_html=True)

# Footer
st.markdown(
    """
    <style>
        /* Hide streamlit's default footer */
        footer {visibility: hidden;}

        /* Custom footer */
        .custom-footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            text-align: center;
            font-size: 1.0rem;
            padding: 0.5rem 0;
            background: rgba(220, 220, 220, 0.85);
        }
    </style>

    <div class="custom-footer">
        🚀 View the project on
        <a href="https://github.com/lelandg/PromptForge" target="_blank">
            GitHub
        </a>
    </div>
    """,
    unsafe_allow_html=True,
)

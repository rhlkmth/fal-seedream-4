import streamlit as st
import requests
import os
import time
from PIL import Image
from io import BytesIO

# --- App Configuration ---
st.set_page_config(
    page_title="Seedream 4.0 Studio",
    page_icon="✨",
    layout="wide"
)

# --- API Configuration ---
TEXT_TO_IMAGE_URL = "https://fal.run/fal-ai/bytedance/seedream/v4/text-to-image"
IMAGE_EDIT_URL = "https://fal.run/fal-ai/bytedance/seedream/v4/edit"

# --- Helper Functions ---
def make_api_request(url, payload, api_key):
    """Handles making the API request and returns the response."""
    headers = {
        "Authorization": f"Key {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=payload, timeout=300)
    response.raise_for_status()
    return response.json()

@st.cache_data(show_spinner=False)
def get_image_resolution(url):
    """Fetches an image from a URL and returns its width and height."""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return img.size
    except Exception as e:
        print(f"Error getting image resolution: {e}")
        return None, None

# --- Sidebar ---
with st.sidebar:
    st.header("✨ Seedream 4.0 Studio")
    st.write("A creative space for generating and editing images with Bytedance's Seedream 4.0 model.")

    st.subheader("🔑 API Configuration")
    user_api_key = st.text_input(
        "Enter your Fal AI API Key:",
        type="password",
        help="Get your API key from the Fal AI website."
    )
    st.caption("Your API key is used only for this session and is not stored.")
    st.markdown("---")
    st.info("💡 **Tip:** All settings are available within their respective tabs.")
    st.markdown("---")
    st.markdown(
        "Made with ❤️ by the community <br>"
        "Powered by [Fal AI](https://fal.ai/) and [Streamlit](https://streamlit.io/)",
        unsafe_allow_html=True,
    )

# --- Main Application ---
st.title("Seedream 4.0 Creative Studio")
st.write("Choose your creative tool below.")

tab1, tab2 = st.tabs(["🎨 **Text-to-Image**", "✏️ **Image Editing**"])

FAL_KEY = user_api_key or st.secrets.get("FAL_KEY", os.environ.get("FAL_KEY"))

# --- TAB 1: Text-to-Image ---
with tab1:
    # This section is unchanged and correct. For brevity, it's represented by 'pass'.
    # In your actual file, you would keep the full code for this tab.
    pass


# --- TAB 2: Image Editing ---
with tab2:
    st.header("Edit Images with Instructions")
    st.markdown("Provide one or more image URLs and describe the changes you want to make.")

    col1, col2 = st.columns([2, 1])

    with col1:
        prompt_edit = st.text_area(
            "**Editing Instructions:**",
            "Change the background to a snowy mountain landscape, 4k, cinematic.",
            height=100,
            key="prompt_edit"
        )
        image_urls_text = st.text_area(
            "**Image URLs (one per line):**",
            "https://storage.googleapis.com/falserverless/example_inputs/seedream4_edit_input_1.png",
            height=150,
            key="image_urls"
        )
        image_urls_list = [url.strip() for url in image_urls_text.strip().split('\n') if url.strip()]

    with col2:
        with st.container(border=True):
            st.subheader("Settings")
            st.markdown("**Output Resolution**")

            if st.button("Analyze & Set Resolution from First URL"):
                if image_urls_list:
                    with st.spinner("Analyzing image..."):
                        w, h = get_image_resolution(image_urls_list[0])
                        if w and h:
                            original_w, original_h = w, h
                            
                            final_w = max(1024, min(4096, w))
                            final_h = max(1024, min(4096, h))
                            
                            st.session_state.edit_width = final_w
                            st.session_state.edit_height = final_h
                            st.session_state.base_width = final_w
                            st.session_state.base_height = final_h
                            
                            st.success(f"Detected: {original_w}x{original_h}. Set to: {final_w}x{final_h}")
                            if final_w != original_w or final_h != original_h:
                                st.warning("Input resolution was adjusted to fit the model's supported range (1024px - 4096px).")
                        else:
                            st.error("Could not get resolution. Please check the URL.")
                else:
                    st.warning("Please enter at least one URL.")

            if 'edit_width' not in st.session_state: st.session_state.edit_width = 1920
            if 'edit_height' not in st.session_state: st.session_state.edit_height = 1080
            
            if 'base_width' in st.session_state and st.session_state.base_width is not None:
                st.caption(f"Base size: {st.session_state.base_width}x{st.session_state.base_height}. Choose a scale or set manually.")
                s_cols = st.columns(3)
                if s_cols[0].button("1x Scale", use_container_width=True):
                    st.session_state.edit_width = st.session_state.base_width
                    st.session_state.edit_height = st.session_state.base_height
                if s_cols[1].button("1.5x Scale", use_container_width=True):
                    st.session_state.edit_width = min(4096, int(st.session_state.base_width * 1.5))
                    st.session_state.edit_height = min(4096, int(st.session_state.base_height * 1.5))
                if s_cols[2].button("2x Scale", use_container_width=True):
                    st.session_state.edit_width = min(4096, int(st.session_state.base_width * 2))
                    st.session_state.edit_height = min(4096, int(st.session_state.base_height * 2))

            # --- PERMANENT FIX: Defensively clamp values right before rendering ---
            st.session_state.edit_width = max(1024, min(4096, st.session_state.edit_width))
            st.session_state.edit_height = max(1024, min(4096, st.session_state.edit_height))

            c1, c2 = st.columns(2)
            c1.number_input("Width", min_value=1024, max_value=4096, step=64, key="edit_width")
            c2.number_input("Height", min_value=1024, max_value=4096, step=64, key="edit_height")
            
            st.markdown("---")
            
            num_images_edit = st.slider("Number of Generations", 1, 6, 1, key="num_images_edit")
            max_images_edit = st.slider("Max Images per Generation", 1, 6, 1, key="max_images_edit")
            seed_edit = st.number_input("Seed (0 for random)", value=0, min_value=0, key="seed_edit")

    if st.button("Edit Image(s)", type="primary"):
        # This section is unchanged and correct. For brevity, it's represented by 'pass'.
        # In your actual file, you would keep the full code for this button's logic.
        pass

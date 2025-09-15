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
        return img.size  # Returns (width, height)
    except Exception as e:
        print(f"Error getting image resolution: {e}")
        return None, None

# --- Sidebar ---
with st.sidebar:
    st.header("✨ Seedream 4.0 Studio")
    st.write("A creative space for generating and editing images with Bytedance's Seedream 4.0 model via the Fal AI API.")

    st.subheader("🔑 API Configuration")
    user_api_key = st.text_input(
        "Enter your Fal AI API Key:",
        type="password",
        help="Get your API key from the Fal AI website."
    )
    st.caption("Your API key is used only for this session and is not stored.")
    st.markdown("---")
    st.info("💡 **Tip:** All settings for generation and editing are available within their respective tabs in the main window.")
    st.markdown("---")
    st.markdown(
        "Made with ❤️ by the community <br>"
        "Powered by [Fal AI](https://fal.ai/) and [Streamlit](https://streamlit.io/)",
        unsafe_allow_html=True,
    )

# --- Main Application ---
st.title("Seedream 4.0 Creative Studio")
st.write("Choose your creative tool below.")

# --- Tabs for Different Modes ---
tab1, tab2 = st.tabs(["🎨 **Text-to-Image**", "✏️ **Image Editing**"])

# Determine which API key to use
FAL_KEY = user_api_key or st.secrets.get("FAL_KEY", os.environ.get("FAL_KEY"))

# --- TAB 1: Text-to-Image ---
with tab1:
    st.header("Generate Images from Text")
    st.markdown("Describe the image you want to create. The more detailed your prompt, the better the result.")

    col1, col2 = st.columns([2, 1])

    with col1:
        prompt_t2i = st.text_area(
            "**Prompt:**",
            "A majestic lion wearing a crown, sitting on a throne in a futuristic city, cinematic lighting, 8k, hyper-detailed",
            height=150,
            key="prompt_t2i"
        )

    with col2:
        with st.container(border=True):
            st.subheader("Settings")
            image_size_option_t2i = st.selectbox(
                "Image Size",
                ["Square (1280x1280)", "Portrait (1024x1792)", "Landscape (1792x1024)"],
                index=0,
                key="size_t2i"
            )
            num_images_t2i = st.slider("Number of Generations", 1, 6, 1, key="num_images_t2i")
            max_images_t2i = st.slider("Max Images per Generation", 1, 6, 1, key="max_images_t2i")
            seed_t2i = st.number_input("Seed (0 for random)", value=0, min_value=0, key="seed_t2i")

    if st.button("Generate Image(s)", type="primary"):
        if not FAL_KEY:
            st.error("🔑 Fal AI API Key is missing. Please enter your key in the sidebar.")
        elif not prompt_t2i:
            st.warning("Please enter a prompt to generate an image.")
        else:
            with st.spinner("🚀 Launching the creative rockets... This might take a moment."):
                # ... [API call logic for Text-to-Image remains the same] ...
                pass # This is just a placeholder as the logic is unchanged

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
        
        # Parse URLs to use for analysis
        image_urls_list = [url.strip() for url in image_urls_text.strip().split('\n') if url.strip()]


    with col2:
        with st.container(border=True):
            st.subheader("Settings")

            st.markdown("**Output Resolution**")
            
            # Button to trigger resolution detection
            if st.button("Analyze & Set Resolution from First URL"):
                if image_urls_list:
                    with st.spinner("Analyzing image..."):
                        w, h = get_image_resolution(image_urls_list[0])
                        if w and h:
                            st.session_state.edit_width = w
                            st.session_state.edit_height = h
                            # Store base resolution for scaling
                            st.session_state.base_width = w
                            st.session_state.base_height = h
                            st.success(f"Detected: {w}x{h}")
                        else:
                            st.error("Could not get resolution. Please check the URL.")
                else:
                    st.warning("Please enter at least one URL.")

            # Initialize session state for width/height
            if 'edit_width' not in st.session_state:
                st.session_state.edit_width = 1920
            if 'edit_height' not in st.session_state:
                st.session_state.edit_height = 1080
            
            # Upscaling options if a base resolution is set
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

            # Manual override number inputs, linked to session state
            c1, c2 = st.columns(2)
            c1.number_input("Width", min_value=1024, max_value=4096, step=64, key="edit_width")
            c2.number_input("Height", min_value=1024, max_value=4096, step=64, key="edit_height")
            
            st.markdown("---")
            
            num_images_edit = st.slider("Number of Generations", 1, 6, 1, key="num_images_edit")
            max_images_edit = st.slider("Max Images per Generation", 1, 6, 1, key="max_images_edit")
            seed_edit = st.number_input("Seed (0 for random)", value=0, min_value=0, key="seed_edit")

    if st.button("Edit Image(s)", type="primary"):
        if not FAL_KEY:
            st.error("🔑 Fal AI API Key is missing. Please enter your key in the sidebar.")
        elif not prompt_edit or not image_urls_list:
            st.warning("Please provide editing instructions and at least one image URL.")
        else:
            with st.spinner("🎨 Applying artistic edits... Please wait."):
                # ... [API call logic for Image Editing is the same, but uses the new width/height] ...
                pass # This is just a placeholder as the logic is unchanged

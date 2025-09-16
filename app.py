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

@st.cache_data(show_spinner=False, ttl=3600)
def get_image_bytes(url):
    """Fetches image bytes from a URL for downloading."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to download image for download button: {e}")
        return None

@st.cache_data(show_spinner=False, ttl=3600)
def get_image_resolution(url):
    """Fetches an image from a URL and returns its width and height."""
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        img = Image.open(BytesIO(response.content))
        return img.size
    except Exception as e:
        print(f"Error getting image resolution for URL {url}: {e}")
        return None, None

# --- Sidebar ---
with st.sidebar:
    st.header("✨ Seedream 4.0 Studio")
    st.write("A creative space for generating and editing images with Bytedance's Seedream 4.0 model.")
    st.subheader("🔑 API Configuration")
    user_api_key = st.text_input("Enter your Fal AI API Key:", type="password", help="Get your API key from the Fal AI website.")
    st.caption("Your API key is used only for this session and is not stored.")
    st.markdown("---")
    st.info("💡 **Tip:** All settings are available within their respective tabs.")
    st.markdown("---")
    st.markdown("Made with ❤️ by the community", unsafe_allow_html=True)

# --- Main Application ---
st.title("Seedream 4.0 Creative Studio")
st.write("Choose your creative tool below.")

tab1, tab2 = st.tabs(["🎨 **Text-to-Image**", "✏️ **Image Editing**"])

FAL_KEY = user_api_key or st.secrets.get("FAL_KEY", os.environ.get("FAL_KEY"))

# --- TAB 1: Text-to-Image ---
with tab1:
    st.header("Generate Images from Text")
    st.markdown("Describe the image you want to create. The more detailed your prompt, the better the result.")
    col1, col2 = st.columns([2, 1])
    with col1:
        prompt_t2i = st.text_area("**Prompt:**", "A majestic lion wearing a crown, sitting on a throne in a futuristic city, cinematic lighting, 8k, hyper-detailed", height=150, key="prompt_t2i")
    with col2:
        with st.container(border=True):
            st.subheader("Settings")
            resolution_options = ["Square (1280x1280)", "Landscape 16:9 - FHD (1920x1080)", "Portrait 9:16 - FHD (1080x1920)", "Landscape 4:3 (1440x1080)", "Portrait 3:4 (1080x1440)", "Square 2K (2048x2048)", "Landscape WQHD (2560x1440)", "Portrait WQHD (1440x2560)", "Landscape 4K UHD (3840x2160)", "Portrait 4K UHD (2160x3840)", "Square 4K (4096x4096)"]
            image_size_option_t2i = st.selectbox("Image Size", resolution_options, index=0, key="size_t2i")
            num_images_t2i = st.slider("Number of Generations", 1, 6, 1, key="num_images_t2i")
            max_images_t2i = st.slider("Max Images per Generation", 1, 6, 1, key="max_images_t2i")
            seed_t2i = st.number_input("Seed (0 for random)", value=0, min_value=0, key="seed_t2i")

    if st.button("Generate Image(s)", type="primary", key="generate_button"):
        if not FAL_KEY:
            st.error("🔑 Fal AI API Key is missing. Please enter your key in the sidebar.")
        elif not prompt_t2i:
            st.warning("Please enter a prompt to generate an image.")
        else:
            with st.spinner("🚀 Launching the creative rockets... This might take a moment."):
                try:
                    image_size_map = {"Square (1280x1280)": {"width": 1280, "height": 1280}, "Landscape 16:9 - FHD (1920x1080)": {"width": 1920, "height": 1080}, "Portrait 9:16 - FHD (1080x1920)": {"width": 1080, "height": 1920}, "Landscape 4:3 (1440x1080)": {"width": 1440, "height": 1080}, "Portrait 3:4 (1080x1440)": {"width": 1080, "height": 1440}, "Square 2K (2048x2048)": {"width": 2048, "height": 2048}, "Landscape WQHD (2560x1440)": {"width": 2560, "height": 1440}, "Portrait WQHD (1440x2560)": {"width": 1440, "height": 2560}, "Landscape 4K UHD (3840x2160)": {"width": 3840, "height": 2160}, "Portrait 4K UHD (2160x3840)": {"width": 2160, "height": 3840}, "Square 4K (4096x4096)": {"width": 4096, "height": 4096}}
                    payload = {"prompt": prompt_t2i, "image_size": image_size_map[image_size_option_t2i], "num_images": num_images_t2i, "max_images": max_images_t2i, "enable_safety_checker": False}
                    if seed_t2i > 0: payload["seed"] = seed_t2i
                    result = make_api_request(TEXT_TO_IMAGE_URL, payload, FAL_KEY)

                    if "images" in result and result["images"]:
                        st.success(f"Successfully generated {len(result['images'])} image(s)!")
                        st.info(f"**Seed used:** {result.get('seed', 'N/A')}")
                        st.markdown("---")
                        st.subheader("Results")
                        cols = st.columns(len(result["images"]))
                        for i, image in enumerate(result["images"]):
                            with cols[i]:
                                with st.container(border=True):
                                    st.image(image["url"], caption=f"Generated Image {i+1}", use_container_width=True)
                                    image_bytes = get_image_bytes(image["url"])
                                    if image_bytes:
                                        st.download_button(label="Download", data=image_bytes, file_name=f"seedream_{result.get('seed', 'random')}_{i+1}.png", mime=image.get("content_type", "image/png"), use_container_width=True)
                except requests.exceptions.HTTPError as e: st.error(f"API Request Failed: {e.response.status_code} - {e.response.text}")
                except Exception as e: st.error(f"An unexpected error occurred: {e}")

# --- TAB 2: Image Editing ---
with tab2:
    st.header("Edit Images with Instructions")
    st.markdown("Provide image URLs and editing instructions. The output will be automatically upscaled.")
    col1, col2 = st.columns([2, 1])
    with col1:
        prompt_edit = st.text_area("**Editing Instructions:**", "Change the background to a snowy mountain landscape, 4k, cinematic.", height=100, key="prompt_edit")
        image_urls_text = st.text_area("**Image URLs (one per line):**", "https://storage.googleapis.com/falserverless/example_inputs/seedream4_edit_input_1.png", height=150, key="image_urls")
        image_urls_list = [url.strip() for url in image_urls_text.strip().split('\n') if url.strip()]
    with col2:
        with st.container(border=True):
            st.subheader("Settings")
            if 'source_url_for_res' not in st.session_state: st.session_state.source_url_for_res = None; st.session_state.input_width = None; st.session_state.input_height = None
            first_url = image_urls_list[0] if image_urls_list else None
            if first_url != st.session_state.source_url_for_res:
                if first_url: w, h = get_image_resolution(first_url); st.session_state.input_width = w; st.session_state.input_height = h
                else: st.session_state.input_width = None; st.session_state.input_height = None
                st.session_state.source_url_for_res = first_url
                st.rerun()
            upscale_factor = st.radio("**Upscale Factor**", ["2x (Default)", "4x"], horizontal=True, key="upscale_factor")
            scale = 4 if upscale_factor == "4x" else 2
            if st.session_state.input_width and st.session_state.input_height:
                detected_w, detected_h = st.session_state.input_width, st.session_state.input_height; target_w, target_h = detected_w * scale, detected_h * scale
                output_w = max(1024, min(4096, target_w)); output_h = max(1024, min(4096, target_h))
                st.info(f"Detected Input: `{detected_w} x {detected_h}`"); st.success(f"Calculated Output: `{output_w} x {output_h}`")
                if (output_w != target_w) or (output_h != target_h): st.warning("Output was scaled to fit the model's supported range (1024px to 4096px).")
            else: st.info("Awaiting a valid image URL for auto-sizing..."); output_w, output_h = 1920, 1080
            st.markdown("---")
            num_images_edit = st.slider("Number of Generations", 1, 6, 1, key="num_images_edit"); max_images_edit = st.slider("Max Images per Generation", 1, 6, 1, key="max_images_edit"); seed_edit = st.number_input("Seed (0 for random)", value=0, min_value=0, key="seed_edit")

    if st.button("Edit Image(s)", type="primary", key="edit_button"):
        if not FAL_KEY: st.error("🔑 Fal AI API Key is missing. Please enter your key in the sidebar.")
        elif not prompt_edit or not image_urls_list: st.warning("Please provide editing instructions and at least one image URL.")
        else:
            with st.spinner("🎨 Applying artistic edits... Please wait."):
                try:
                    payload = {"prompt": prompt_edit, "image_urls": image_urls_list, "image_size": {"width": output_w, "height": output_h}, "num_images": num_images_edit, "max_images": max_images_edit, "enable_safety_checker": False}
                    if seed_edit > 0: payload["seed"] = seed_edit
                    
                    st.subheader("Input Preview")
                    with st.container(border=True):
                        in_cols = st.columns(min(len(image_urls_list), 4))
                        for i, url in enumerate(image_urls_list):
                            with in_cols[i % 4]:
                                st.image(url, use_container_width=True)
                    
                    result = make_api_request(IMAGE_EDIT_URL, payload, FAL_KEY)
                    
                    st.markdown("---")
                    st.subheader("Results")
                    if "images" in result and result["images"]:
                        st.success(f"Successfully edited and generated {len(result['images'])} image(s)!")
                        st.info(f"**Seed used:** {result.get('seed', 'N/A')}")
                        out_cols = st.columns(len(result["images"]))
                        for i, image in enumerate(result["images"]):
                            with out_cols[i]:
                                with st.container(border=True):
                                    st.image(image["url"], caption=f"Edited Image {i+1}", use_container_width=True)
                                    image_bytes = get_image_bytes(image["url"])
                                    if image_bytes:
                                        st.download_button(label="Download", data=image_bytes, file_name=f"seedream_{result.get('seed', 'random')}_{i+1}.png", mime=image.get("content_type", "image/png"), use_container_width=True)
                    else:
                        st.warning("The API did not return any edited images.")
                        with st.expander("Show API Response"): st.json(result)
                except requests.exceptions.HTTPError as e: st.error(f"API Request Failed: {e.response.status_code} - {e.response.text}")
                except Exception as e: st.error(f"An unexpected error occurred: {e}")

import streamlit as st
import requests
import os
import time

# --- App Configuration ---
st.set_page_config(
    page_title="Fal AI Image Factory 4.0",
    page_icon="🎨",
    layout="wide"
)

# --- API Configuration ---
API_URL = "https://fal.run/fal-ai/bytedance/seedream/v4/text-to-image"

# --- Sidebar for User Inputs ---
with st.sidebar:
    st.header("🎨 Fal AI Image Factory 4.0")
    st.write("Generate images using the Bytedance Seedream 4.0 model.")

    # User input for API Key
    st.subheader("API Configuration")
    user_api_key = st.text_input(
        "Enter your Fal AI API Key:",
        type="password",
        help="You can get your API key from the Fal AI website."
    )
    st.caption("Your API key is not stored. It is only used for the current session.")

    st.markdown("---")

    # Prompt and settings
    st.subheader("Generation Settings")
    prompt = st.text_area(
        "Enter your creative prompt:",
        "A majestic lion wearing a crown, sitting on a throne in a futuristic city, cinematic lighting",
        height=150
    )

    image_size_option = st.selectbox(
        "Image Size:",
        ["Square (1280x1280)", "Portrait (1024x1792)", "Landscape (1792x1024)"],
        index=0
    )

    num_images = st.slider("Number of Generations:", 1, 6, 1)
    max_images = st.slider("Max Images per Generation:", 1, 6, 1)

    # Advanced options
    with st.expander("Advanced Settings"):
        # Use a unique key for the number_input to allow dynamic updates
        if 'seed_value' not in st.session_state:
            st.session_state.seed_value = 0

        seed = st.number_input("Seed (0 for random):", value=st.session_state.seed_value, min_value=0)
        if st.button("Randomize Seed"):
            st.session_state.seed_value = int(time.time())
            st.rerun() # Rerun the app to update the number_input value

# --- Determine which API key to use ---
# Priority: User input > Streamlit secrets > Environment variable
FAL_KEY = user_api_key or st.secrets.get("FAL_KEY", os.environ.get("FAL_KEY"))

# --- Main Panel for Image Display ---
st.title("🖼️ Your Generated Images")

# "Generate" button
if st.button("Generate Image(s)"):
    if not FAL_KEY:
        st.error("Fal AI API Key is missing. Please enter your key in the sidebar to proceed.")
    elif not prompt:
        st.warning("Please enter a prompt to generate an image.")
    else:
        # --- Prepare API Payload ---
        image_size_map = {
            "Square (1280x1280)": {"width": 1280, "height": 1280},
            "Portrait (1024x1792)": {"width": 1024, "height": 1792},
            "Landscape (1792x1024)": {"width": 1792, "height": 1024}
        }

        payload = {
            "prompt": prompt,
            "image_size": image_size_map[image_size_option],
            "num_images": num_images,
            "max_images": max_images,
            "enable_safety_checker": False
        }
        # Only add the seed if it's not 0, as 0 means random
        if seed > 0:
            payload["seed"] = seed

        # --- API Call ---
        with st.spinner("Generating your masterpiece... This might take a moment."):
            try:
                headers = {
                    "Authorization": f"Key {FAL_KEY}",
                    "Content-Type": "application/json"
                }
                response = requests.post(API_URL, headers=headers, json=payload, timeout=300)
                response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

                result = response.json()

                # --- Display Images ---
                if "images" in result and result["images"]:
                    st.success(f"Successfully generated {len(result['images'])} image(s)!")
                    
                    # Create columns dynamically based on the number of images
                    cols = st.columns(len(result["images"]))
                    for i, image in enumerate(result["images"]):
                        with cols[i]:
                            st.image(image["url"], caption=f"Generated Image {i+1}", use_column_width=True)
                    
                    st.info(f"Seed used for generation: {result.get('seed', 'N/A')}")
                else:
                    st.warning("The API did not return any images. Please try a different prompt or settings.")
                    st.json(result) # Show the raw response for debugging

            except requests.exceptions.HTTPError as e:
                st.error(f"API Request Failed: {e.response.status_code} - {e.response.text}")
            except requests.exceptions.RequestException as e:
                st.error(f"Network or request error: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# --- Instructions for getting started ---
st.markdown("---")
st.markdown("### How to Use:")
st.markdown("1. **Enter your Fal AI API Key** in the sidebar. You can obtain one from the [Fal AI website](https://fal.ai/).")
st.markdown("2. **Enter your desired prompt** in the text area.")
st.markdown("3. **Adjust the settings** like image size and number of images.")
st.markdown("4. **Click 'Generate Image(s)'** to see the magic happen!")

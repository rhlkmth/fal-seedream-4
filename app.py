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
# It's recommended to set the FAL_KEY as a secret in Streamlit Cloud
FAL_KEY = st.secrets.get("FAL_KEY", os.environ.get("FAL_KEY"))
API_URL = "https://fal.run/fal-ai/bytedance/seedream/v4/text-to-image"

# --- Sidebar for User Inputs ---
with st.sidebar:
    st.header("🎨 Fal AI Image Factory 4.0")
    st.write("Generate images using the Bytedance Seedream 4.0 model via the Fal AI API.")

    prompt = st.text_area(
        "Enter your creative prompt:",
        "A majestic lion wearing a crown, sitting on a throne in a futuristic city, cinematic lighting",
        height=150
    )

    st.subheader("Image Settings")
    image_size_option = st.selectbox(
        "Image Size:",
        ["Square (1280x1280)", "Portrait (1024x1792)", "Landscape (1792x1024)"],
        index=0
    )

    num_images = st.slider("Number of Generations:", 1, 6, 1)
    max_images = st.slider("Max Images per Generation:", 1, 6, 1)

    # Advanced options
    with st.expander("Advanced Settings"):
        seed_placeholder = st.empty()
        seed = seed_placeholder.number_input("Seed (optional):", value=0, min_value=0)
        if st.button("Randomize Seed"):
            seed = seed_placeholder.number_input("Seed (optional):", value=int(time.time()), min_value=0)


# --- Main Panel for Image Display ---
st.title("🖼️ Your Generated Images")

# "Generate" button
if st.button("Generate Image(s)"):
    if not FAL_KEY:
        st.error("FAL_KEY is not set. Please set it as a secret in Streamlit Cloud or as an environment variable.")
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
        if seed > 0:
            payload["seed"] = seed

        # --- API Call ---
        with st.spinner("Generating your masterpiece..."):
            try:
                headers = {
                    "Authorization": f"Key {FAL_KEY}",
                    "Content-Type": "application/json"
                }
                response = requests.post(API_URL, headers=headers, json=payload)
                response.raise_for_status()  # Raise an exception for bad status codes

                result = response.json()

                # --- Display Images ---
                if "images" in result and result["images"]:
                    cols = st.columns(len(result["images"]))
                    for i, image in enumerate(result["images"]):
                        with cols[i]:
                            st.image(image["url"], caption=f"Generated Image {i+1}", use_column_width=True)
                    st.success(f"Successfully generated {len(result['images'])} image(s)!")
                    st.info(f"Seed used: {result.get('seed', 'N/A')}")
                else:
                    st.warning("The API did not return any images. Please try a different prompt or settings.")

            except requests.exceptions.RequestException as e:
                st.error(f"API Request Failed: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")

# --- Instructions for getting started ---
st.markdown("---")
st.markdown("### How to Use:")
st.markdown("1. Enter your desired prompt in the sidebar.")
st.markdown("2. Adjust the settings like image size and number of images.")
st.markdown("3. Click 'Generate Image(s)' to see the magic happen!")

import streamlit as st
import os
import base64
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Streamlit page config
st.set_page_config(page_title="AI Calorie Estimator", page_icon="🍔", layout="centered")

st.title("🍔 AI Food Calorie Estimator")
st.write("Upload a picture of your food, and our AI Nutritionist will identify the dish and estimate its calories and macronutrients!")

# Get API Key securely
api_key = os.getenv("GROQ_API_KEY")
if not api_key or api_key == "your_api_key_here":
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        pass

with st.sidebar:
    st.subheader("Configuration")
    if not api_key or api_key == "your_api_key_here":
        user_api_key = st.text_input("Groq API Key", type="password", help="Get your free API key from console.groq.com")
        if user_api_key:
            api_key = user_api_key
    else:
        st.success("API Key is securely loaded from server!")
        
    st.info("Powered by Groq's insanely fast Llama 4 Scout Vision model.")

def get_calorie_estimate(base64_image, api_key):
    """Sends the image to Groq's Vision API and requests a markdown table format."""
    client = Groq(api_key=api_key)
    
    prompt = """
    You are an expert nutritionist. Look at the image provided and:
    1. Identify the food/dish in the image.
    2. Estimate the calories and macronutrients (Protein, Carbs, Fats).
    3. Output the result STRICTLY as a clean Markdown table with the following columns:
       | Dish Name | Estimated Calories | Protein (g) | Carbs (g) | Fats (g) |
    
    If there are multiple distinct items, list them as separate rows.
    Do not add any extra conversational text before or after the table, just the markdown table.
    """
    
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",  # Updated model
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    },
                ],
            }
        ],
        temperature=0,
    )
    
    return response.choices[0].message.content

# Image Upload
uploaded_file = st.file_uploader("Upload an image of your food", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display the uploaded image
    st.image(uploaded_file, caption="Uploaded Food Image", use_container_width=True)
    
    if st.button("Analyze Food 🔍"):
        if not api_key or api_key == "your_api_key_here":
            st.error("Cannot analyze without a Groq API Key. Please provide one in the sidebar.")
        else:
            with st.spinner("Analyzing image..."):
                try:
                    # Convert uploaded image to base64
                    image_bytes = uploaded_file.getvalue()
                    base64_image = base64.b64encode(image_bytes).decode('utf-8')
                    
                    # Get result from API
                    result = get_calorie_estimate(base64_image, api_key)
                    
                    st.success("Analysis Complete!")
                    st.markdown(result)
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

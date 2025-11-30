import gradio as gr
import google.generativeai as genai
import os
import random
import time
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# Configure Google GenAI
# Get your key from: https://aistudio.google.com/app/apikey
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# ---------------------------------------------------------
# DATA: LIST OF MEXICAN CELEBRITIES
# ---------------------------------------------------------
mexican_icons = {
    "Female": [
        "Frida Kahlo (Iconic Painter)",
        "Salma Hayek (Actress)",
        "Thalía (Singer)",
        "Sor Juana Inés de la Cruz (Poet)",
        "María Félix (Golden Age Actress)",
        "Gloria Trevi (Singer)",
        "Yalitza Aparicio (Actress)",
        "Dolores del Río (Actress)"
    ],
    "Male": [
        "Diego Rivera (Muralist)",
        "Guillermo del Toro (Director)",
        "Vicente Fernández (Singer)",
        "Peso Pluma (Singer)",
        "Luis Miguel (Singer)",
        "Cantinflas (Comedian)",
        "Saúl 'Canelo' Álvarez (Boxer)",
        "Carlos Santana (Musician)"
    ]
}

# ---------------------------------------------------------
# FUNCTION: GENERATE SELFIE WITH GOOGLE
# ---------------------------------------------------------
def generate_magic_selfie_google(user_image_path, gender_choice):
    if not user_image_path:
        raise gr.Error("Please upload a selfie first!")
    
    if not GOOGLE_API_KEY:
        raise gr.Error("GOOGLE_API_KEY is missing. Please set it in your .env file.")

    # 1. Pick a random celebrity
    celebs = mexican_icons.get(gender_choice, mexican_icons["Female"])
    selected_celeb = random.choice(celebs)
    celeb_name = selected_celeb.split(" (")[0]
    
    print(f"✨ Selected Celebrity: {selected_celeb}")

    try:
        # 2. Analyze the User's Selfie using Gemini Vision (Nano Banana Pro Level!)
        # We use Gemini 1.5 Pro to "see" the user and describe them
        print("👀 Gemini (Nano Banana Pro) is analyzing your selfie...")
        
        # Using the latest Gemini model with vision capabilities
        # Try gemini-1.5-pro-latest first, fall back to gemini-pro-vision
        try:
            model = genai.GenerativeModel('gemini-1.5-pro-latest')
        except:
            model = genai.GenerativeModel('gemini-pro-vision')
        
        # Load the image for Gemini
        img = Image.open(user_image_path)
        
        analysis_prompt = (
            "Analyze this selfie and provide a detailed physical description of the person. "
            "Include details about their age, gender, hair color/style, eye color, skin tone, "
            "clothing, and facial expression. Keep it concise but descriptive. "
            "Do not describe the background."
        )
        
        response = model.generate_content([analysis_prompt, img])
        user_description = response.text
        print(f"📝 User Description: {user_description}")

        # 3. Create the Image Generation Prompt
        # Now we combine the user description with the celebrity
        image_prompt = (
            f"A photorealistic smartphone selfie of two people standing together. "
            f"Person 1: {user_description} "
            f"Person 2: The famous Mexican celebrity {celeb_name}. "
            f"They are standing side-by-side, looking at the camera and smiling. "
            f"The background is a vibrant, colorful Mexican street scene with papel picado. "
            f"Cinematic lighting, 8k resolution, highly detailed."
        )
        
        print(f"🎨 Generating Image Prompt: {image_prompt}")

        # 4. Generate the Image
        # Note: We are using a placeholder here because standard Gemini API 
        # is primarily for Text/Vision. For Image Generation (Imagen), 
        # we would typically use Vertex AI or specific endpoints.
        # However, to make this work with your Google Key, we will try to use
        # the 'gemini-pro-vision' to at least give us the text, 
        # and if you have access to Imagen via the API, we could use it.
        
        # IMPORTANT: Since standard free Google GenAI keys might not have 
        # public access to Imagen 3 yet (it's rolling out), 
        # we will use a fallback or simulation if it fails, 
        # OR we can try to use the 'fal-client' if you still have it, 
        # using Gemini just for the "Brain" (Prompt Engineering).
        
        # Let's try to use Fal.ai for the final generation if the key exists,
        # otherwise we return the text description as a "Plan".
        
        if os.getenv("FAL_KEY"):
            import fal_client
            print("🚀 Using Fal.ai (Flux) for final generation with Gemini's Brain...")
            handler = fal_client.submit(
                "fal-ai/flux/dev",
                arguments={
                    "prompt": image_prompt,
                    "image_size": "portrait_9_16",
                    "num_inference_steps": 28,
                    "enable_safety_checker": True
                },
            )
            result = handler.get()
            image_url = result['images'][0]['url']
            return image_url, f"📸 You (described by Gemini) and {selected_celeb}!"
        
        else:
            # If no Fal key, we return a placeholder or error explaining
            # that we need an image generator.
            # OR we could try a free image generation API if available.
            return None, (
                f"✨ Gemini Analysis Complete! ✨\n\n"
                f"I saw you as: {user_description}\n\n"
                f"I wanted to generate: {image_prompt}\n\n"
                "⚠️ To see the actual image, we need an Image Generation model connected! "
                "Add a FAL_KEY to your .env file to let Gemini paint this picture."
            )

    except Exception as e:
        raise gr.Error(f"Error with Google GenAI: {str(e)}")

# ---------------------------------------------------------
# UI: STYLISH GRADIO INTERFACE
# ---------------------------------------------------------

with gr.Blocks() as demo:
    
    gr.Markdown("# 🍌 Nano Banana Pro Selfie Machine 🍌")
    gr.Markdown("### Powered by Google Gemini 1.5 Pro")
    
    with gr.Row():
        with gr.Column():
            input_img = gr.Image(
                label="Upload Your Selfie", 
                type="filepath", 
                sources=["upload", "webcam"]
            )
            
            gender_input = gr.Radio(
                choices=["Female", "Male"], 
                value="Female", 
                label="Choose Celebrity Gender"
            )
            
            generate_btn = gr.Button("✨ Analyze & Generate ✨", variant="primary", size="lg")
        
        with gr.Column():
            output_img = gr.Image(label="Result")
            result_text = gr.Textbox(label="Gemini's Thoughts", interactive=False, lines=5)

    gr.Markdown("*Using Google Gemini for Vision Analysis & Prompt Engineering*")

    generate_btn.click(
        fn=generate_magic_selfie_google, 
        inputs=[input_img, gender_input], 
        outputs=[output_img, result_text]
    )

if __name__ == "__main__":
    demo.launch()

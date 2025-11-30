import gradio as gr
import fal_client
import os
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# Make sure to set your key in your environment variables 
# or uncomment the line below and paste it there:
# os.environ["FAL_KEY"] = "your-fal-ai-api-key-here"

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
# FUNCTION: GENERATE SELFIE
# ---------------------------------------------------------
def generate_magic_selfie(user_image, gender_choice):
    if not user_image:
        raise gr.Error("Please upload a selfie first!")
    
    if not os.environ.get("FAL_KEY"):
        raise gr.Error("FAL_KEY is missing. Please set your API key in the .env file.")

    # 1. Pick a random celebrity based on gender
    celebs = mexican_icons.get(gender_choice, mexican_icons["Female"])
    selected_celeb = random.choice(celebs)
    celeb_name = selected_celeb.split(" (")[0] # Extract just the name
    
    print(f"Generating selfie with: {selected_celeb}")

    # 2. Construct the Prompt
    # We use natural language to tell the AI to combine the user with the celeb
    prompt = (
        f"A realistic smartphone selfie of the person in the uploaded image standing next to {celeb_name}. "
        f"{celeb_name} is a famous Mexican celebrity. "
        "They are both looking at the camera and smiling. "
        "Background is a colorful blurred Mexican street or artistic studio. "
        "High quality, 8k, photorealistic, cinematic lighting, perfect eyes."
    )

    # 3. Call Fal.ai (Flux Dev Image-to-Image)
    # This model takes your image and transforms it based on the prompt
    try:
        handler = fal_client.submit(
            "fal-ai/flux/dev/image-to-image",
            arguments={
                "image_url": user_image,
                "prompt": prompt,
                "strength": 0.75, # Controls how much the original image is preserved (0.70-0.85 is sweet spot)
                "guidance_scale": 3.5,
                "image_size": "portrait_9_16", # 9:16 Aspect Ratio
                "num_inference_steps": 28,
                "enable_safety_checker": True
            },
        )
        
        # Get result
        result = handler.get()
        image_url = result['images'][0]['url']
        
        return image_url, f"📸 You and {selected_celeb}!"

    except Exception as e:
        raise gr.Error(f"Error generating image: {str(e)}")

# ---------------------------------------------------------
# UI: STYLISH GRADIO INTERFACE
# ---------------------------------------------------------
custom_css = """
body { background-color: #121212; color: white; }
.container { max-width: 900px; margin: auto; padding-top: 20px; }
h1 { text-align: center; font-family: 'Helvetica', sans-serif; color: #00d26a; }
.gr-button-primary { background: linear-gradient(90deg, #009c48 0%, #ce1126 100%); border: none; }
.gr-box { border-radius: 15px; border: 1px solid #333; }
#gallery { min-height: 600px; }
"""

with gr.Blocks(theme=gr.themes.Soft(), css=custom_css) as demo:
    
    with gr.Column(elem_classes="container"):
        gr.Markdown("# 🇲🇽 Viva la Selfie 🇲🇽")
        gr.Markdown("### Take a photo with a random famous Mexican Legend")
        
        with gr.Row():
            with gr.Column(scale=1):
                # Input Section
                input_img = gr.Image(
                    label="Upload Your Selfie", 
                    type="filepath", 
                    sources=["upload", "webcam"],
                    elem_classes="gr-box"
                )
                
                gender_input = gr.Radio(
                    choices=["Female", "Male"], 
                    value="Female", 
                    label="Choose Celebrity Gender",
                    info="Who do you want to meet today?"
                )
                
                generate_btn = gr.Button("✨ Generate Magic Selfie ✨", variant="primary", size="lg")
            
            with gr.Column(scale=1):
                # Output Section
                output_img = gr.Image(label="Your Selfie", elem_id="gallery", type="filepath")
                result_text = gr.Textbox(label="Celebrity Found", interactive=False)

        # Footer
        gr.Markdown("*Powered by Fal.ai Flux Dev API*")

    # Bind functions
    generate_btn.click(
        fn=generate_magic_selfie, 
        inputs=[input_img, gender_input], 
        outputs=[output_img, result_text]
    )

# Run the App
if __name__ == "__main__":
    demo.launch()

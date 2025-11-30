"""
Viva La Selfie API Server - Powered by Nano Banana Pro! 🍌
Uses Google Gemini to analyze selfies and Fal.ai to generate celebrity photos
"""

import os
import json
import base64
import io
import random
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
import fal_client

# Load environment variables
load_dotenv()

# Configure Google GenAI (Nano Banana Pro!)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

# Mexican Celebrity Database 🌟
MEXICAN_ICONS = {
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


def analyze_selfie_with_gemini(image_base64):
    """
    Use Google Gemini 1.5 Pro (Nano Banana Pro level!) to analyze the user's selfie.
    Returns a detailed description of the person in the photo.
    """
    if not GOOGLE_API_KEY:
        raise Exception("GOOGLE_API_KEY is missing! Please set it in your .env file.")

    print("👀 Nano Banana Pro (Gemini) is analyzing your selfie...")

    # Remove data:image prefix if present
    if ',' in image_base64:
        image_base64 = image_base64.split(',')[1]

    # Decode base64 to PIL Image
    try:
        image_data = base64.b64decode(image_base64)
        img = Image.open(io.BytesIO(image_data))
    except Exception as e:
        raise Exception(f"Failed to decode image: {str(e)}")

    # Use Gemini 1.5 Pro for vision analysis
    try:
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
    except:
        try:
            model = genai.GenerativeModel('gemini-pro-vision')
        except Exception as e:
            raise Exception(f"Failed to load Gemini model: {str(e)}")

    analysis_prompt = (
        "Analyze this selfie and provide a detailed physical description of the person. "
        "Include details about their age, gender, hair color/style, eye color, skin tone, "
        "clothing, and facial expression. Keep it concise but descriptive. "
        "Do not describe the background."
    )

    try:
        response = model.generate_content([analysis_prompt, img])
        user_description = response.text
        print(f"📝 Gemini's analysis: {user_description}")
        return user_description
    except Exception as e:
        raise Exception(f"Gemini analysis failed: {str(e)}")


def generate_celebrity_selfie(user_description, celebrity_name, gender):
    """
    Use Fal.ai Flux Dev to generate an image of the user with a Mexican celebrity.
    Returns base64 encoded image data.
    """
    FAL_KEY = os.getenv("FAL_KEY")
    if not FAL_KEY:
        raise Exception("FAL_KEY is missing! Please set it in your .env file.")

    print(f"🎨 Generating your photo with {celebrity_name}...")

    # Create the detailed prompt
    image_prompt = (
        f"A photorealistic smartphone selfie of two people standing together. "
        f"Person 1: {user_description} "
        f"Person 2: The famous Mexican celebrity {celebrity_name}. "
        f"They are standing side-by-side, looking at the camera and smiling. "
        f"The background is a vibrant, colorful Mexican street scene with papel picado. "
        f"Cinematic lighting, 8k resolution, highly detailed."
    )

    print(f"💭 Prompt: {image_prompt[:100]}...")

    try:
        # Call Fal.ai Flux Dev
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

        print(f"✨ Image generated! Downloading from: {image_url[:50]}...")

        # Download image and convert to base64
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()
        img_base64 = base64.b64encode(img_response.content).decode('utf-8')

        print("✅ Image downloaded and encoded!")
        return img_base64

    except Exception as e:
        raise Exception(f"Fal.ai generation failed: {str(e)}")


class handler(BaseHTTPRequestHandler):
    """
    HTTP server handler for the Viva La Selfie API.
    Receives selfie images and returns celebrity composite photos!
    """

    def do_POST(self):
        """Handle POST requests from the website."""
        try:
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            # Get image and gender from request
            image_data = data.get('image', '').strip()
            gender = data.get('gender', 'Female')

            if not image_data:
                self.send_error_response("Please provide an image!", 400)
                return

            # Validate gender
            if gender not in ['Female', 'Male']:
                gender = 'Female'

            # Check API keys
            if not os.getenv("GOOGLE_API_KEY"):
                self.send_error_response(
                    "GOOGLE_API_KEY not configured. Please add it to your .env file! Get it from: https://aistudio.google.com/app/apikey",
                    500
                )
                return

            if not os.getenv("FAL_KEY"):
                self.send_error_response(
                    "FAL_KEY not configured. Please add it to your .env file! Get it from: https://fal.ai/dashboard/keys",
                    500
                )
                return

            # Step 1: Select a random celebrity
            celebs = MEXICAN_ICONS.get(gender, MEXICAN_ICONS["Female"])
            selected_celeb = random.choice(celebs)
            celeb_name = selected_celeb.split(" (")[0]

            print(f"\n✨ Selected Celebrity: {selected_celeb}")

            # Step 2: Analyze selfie with Gemini (Nano Banana Pro!)
            user_description = analyze_selfie_with_gemini(image_data)

            # Step 3: Generate image with Fal.ai
            result_image = generate_celebrity_selfie(
                user_description,
                celeb_name,
                gender
            )

            # Send success response
            self.send_success_response({
                "image": result_image,
                "celebrity": celeb_name,
                "fullCelebrity": selected_celeb,
                "description": user_description,
                "gender": gender
            })

            print(f"🎉 Success! Generated photo with {celeb_name}\n")

        except json.JSONDecodeError:
            self.send_error_response("Invalid request format", 400)
        except Exception as e:
            error_message = str(e)
            print(f"❌ Error: {error_message}")
            self.send_error_response(f"Error: {error_message}", 500)

    def send_success_response(self, data):
        """Send a successful JSON response."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow CORS
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def send_error_response(self, message, status_code):
        """Send an error JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()


if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 3001))
    print(f"🍌 Starting Viva La Selfie API Server (Nano Banana Pro Edition!)")
    print(f"🌟 Running on http://localhost:{PORT}")
    print(f"📸 API endpoint: http://localhost:{PORT}/api/generate")
    print(f"\n🔑 Make sure you have these API keys in your .env file:")
    print(f"   - GOOGLE_API_KEY (from https://aistudio.google.com/app/apikey)")
    print(f"   - FAL_KEY (from https://fal.ai/dashboard/keys)")
    print(f"\n✨ Ready to create celebrity selfies! Press Ctrl+C to stop.\n")

    server = HTTPServer(('localhost', PORT), handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped. Adios!")
        server.server_close()

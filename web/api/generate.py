"""
Vercel Serverless Function for Maia's Mexican Art Machine
This is the "backend" that the website calls to generate art!
"""

import os
import json
import runpod
from http.server import BaseHTTPRequestHandler


# Mexican Art Style Templates (same as in art_generator.py)
MEXICAN_ART_STYLES = {
    "frida": "in the style of Frida Kahlo with vibrant colors, self-portrait elements, flowers in hair, and nature symbolism",
    "mural": "in the style of Mexican muralism with bold cultural symbols, strong social themes, and dramatic compositions",
    "folk": "in the style of Mexican folk art with bright traditional colors, intricate patterns, and festive cultural motifs"
}


def enhance_prompt_with_style(prompt, style="frida"):
    """Enhance the user's prompt with Mexican art style."""
    style_modifier = MEXICAN_ART_STYLES.get(style, MEXICAN_ART_STYLES["frida"])
    return f"{prompt}, {style_modifier}"


class handler(BaseHTTPRequestHandler):
    """
    Vercel serverless function handler.
    This receives requests from your website!
    """

    def do_POST(self):
        """Handle POST requests from the website."""
        try:
            # Read the request body (the data sent from the website)
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            # Get the prompt and style from the request
            prompt = data.get('prompt', '').strip()
            style = data.get('style', 'frida')

            if not prompt:
                self.send_error_response("Please provide a prompt!", 400)
                return

            # Get RunPod configuration from environment variables
            api_key = os.getenv("RUNPOD_API_KEY")
            endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")

            if not api_key or not endpoint_id:
                self.send_error_response(
                    "Server configuration error. Please contact Maia!",
                    500
                )
                return

            # Set up RunPod - make sure values are strings, not bytes!
            runpod.api_key = str(api_key).strip()
            endpoint = runpod.Endpoint(str(endpoint_id).strip())

            # Enhance prompt with Mexican art style
            enhanced_prompt = enhance_prompt_with_style(prompt, style)

            # Prepare the request for RunPod
            payload = {
                "input": {
                    "prompt": enhanced_prompt,
                    "num_inference_steps": 25,
                    "guidance_scale": 7.5,
                    "width": 1024,
                    "height": 1024,
                }
            }

            # Generate the art! (synchronous - wait for result)
            result = endpoint.run_sync(payload, timeout=300)

            # Extract image data
            image_data = None
            if "output" in result and "image" in result["output"]:
                image_data = result["output"]["image"]
            elif "output" in result and isinstance(result["output"], str):
                image_data = result["output"]
            else:
                self.send_error_response(
                    f"Unexpected response from AI: {result}",
                    500
                )
                return

            # Send success response back to website
            self.send_success_response({
                "image": image_data,
                "prompt": prompt,
                "enhanced_prompt": enhanced_prompt,
                "style": style
            })

        except json.JSONDecodeError:
            self.send_error_response("Invalid request format", 400)
        except Exception as e:
            self.send_error_response(f"Error generating art: {str(e)}", 500)

    def send_success_response(self, data):
        """Send a successful JSON response."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow requests from any domain
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

"""
Vercel Serverless Function for Maia's Mexican Art Machine
This is the "backend" that the website calls to generate art!
"""

import os
import json
import time
import requests
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

            # Clean up the credentials
            api_key = str(api_key).strip()
            endpoint_id = str(endpoint_id).strip()

            # Enhance prompt with Mexican art style
            enhanced_prompt = enhance_prompt_with_style(prompt, style)

            # Prepare the request for RunPod ComfyUI
            payload = {
                "input": {
                    "prompt": enhanced_prompt,
                    "num_inference_steps": 25,
                    "guidance_scale": 7.5,
                    "width": 1024,
                    "height": 1024,
                }
            }

            # Call RunPod API directly using /run endpoint
            api_url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # Send the request to start the job
            response = requests.post(api_url, json=payload, headers=headers)

            if response.status_code != 200:
                self.send_error_response(
                    f"RunPod API error: {response.status_code} - {response.text}",
                    500
                )
                return

            result_data = response.json()
            job_id = result_data.get("id")

            if not job_id:
                self.send_error_response(
                    f"No job ID returned: {result_data}",
                    500
                )
                return

            # Poll for the result (check every 2 seconds, max 5 minutes)
            status_url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{job_id}"
            max_attempts = 150  # 5 minutes / 2 seconds

            for attempt in range(max_attempts):
                time.sleep(2)  # Wait 2 seconds between checks

                status_response = requests.get(status_url, headers=headers)
                if status_response.status_code != 200:
                    continue

                status_data = status_response.json()
                status = status_data.get("status")

                if status == "COMPLETED":
                    # Extract the image from the completed job
                    output = status_data.get("output")
                    image_data = None

                    if isinstance(output, dict) and "image" in output:
                        image_data = output["image"]
                    elif isinstance(output, str):
                        image_data = output
                    elif isinstance(output, list) and len(output) > 0:
                        image_data = output[0]

                    if not image_data:
                        self.send_error_response(
                            f"No image in completed job: {output}",
                            500
                        )
                        return
                    break

                elif status in ["FAILED", "CANCELLED"]:
                    error_msg = status_data.get("error", "Unknown error")
                    self.send_error_response(
                        f"Job {status.lower()}: {error_msg}",
                        500
                    )
                    return
            else:
                # Timeout - job took too long
                self.send_error_response(
                    "Timeout: Art generation took too long. Please try again!",
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

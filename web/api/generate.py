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

            # Prepare the ComfyUI workflow for Flux Schnell
            # This is based on the official RunPod ComfyUI worker format
            payload = {
                "input": {
                    "workflow": {
                        "6": {
                            "inputs": {
                                "text": enhanced_prompt,
                                "clip": ["30", 1]
                            },
                            "class_type": "CLIPTextEncode",
                            "_meta": {
                                "title": "CLIP Text Encode (Positive Prompt)"
                            }
                        },
                        "8": {
                            "inputs": {
                                "samples": ["31", 0],
                                "vae": ["30", 2]
                            },
                            "class_type": "VAEDecode",
                            "_meta": {
                                "title": "VAE Decode"
                            }
                        },
                        "9": {
                            "inputs": {
                                "filename_prefix": "maia_art",
                                "images": ["8", 0]
                            },
                            "class_type": "SaveImage",
                            "_meta": {
                                "title": "Save Image"
                            }
                        },
                        "27": {
                            "inputs": {
                                "width": 1024,
                                "height": 1024,
                                "batch_size": 1
                            },
                            "class_type": "EmptySD3LatentImage",
                            "_meta": {
                                "title": "Empty Latent Image"
                            }
                        },
                        "30": {
                            "inputs": {
                                "ckpt_name": "flux1-dev-fp8.safetensors"
                            },
                            "class_type": "CheckpointLoaderSimple",
                            "_meta": {
                                "title": "Load Checkpoint"
                            }
                        },
                        "31": {
                            "inputs": {
                                "seed": int(time.time()),
                                "steps": 20,
                                "cfg": 1.0,
                                "sampler_name": "euler",
                                "scheduler": "simple",
                                "denoise": 1.0,
                                "model": ["30", 0],
                                "positive": ["35", 0],
                                "negative": ["33", 0],
                                "latent_image": ["27", 0]
                            },
                            "class_type": "KSampler",
                            "_meta": {
                                "title": "KSampler"
                            }
                        },
                        "33": {
                            "inputs": {
                                "text": "",
                                "clip": ["30", 1]
                            },
                            "class_type": "CLIPTextEncode",
                            "_meta": {
                                "title": "CLIP Text Encode (Negative Prompt)"
                            }
                        },
                        "35": {
                            "inputs": {
                                "guidance": 3.5,
                                "conditioning": ["6", 0]
                            },
                            "class_type": "FluxGuidance",
                            "_meta": {
                                "title": "Flux Guidance"
                            }
                        }
                    }
                }
            }

            # Use /runsync endpoint (synchronous - waits for completion)
            api_url = f"https://api.runpod.ai/v2/{endpoint_id}/runsync"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            # Send the request
            try:
                response = requests.post(
                    api_url,
                    json=payload,
                    headers=headers,
                    timeout=300  # 5 minute timeout for image generation
                )
            except requests.exceptions.Timeout:
                self.send_error_response(
                    "Request timed out. The endpoint might be cold-starting. Please try again!",
                    500
                )
                return
            except Exception as e:
                self.send_error_response(
                    f"Request failed: {str(e)}",
                    500
                )
                return

            if response.status_code != 200:
                # Try to get more details from the error
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = json.dumps(error_json, indent=2)
                except:
                    pass

                self.send_error_response(
                    f"RunPod API error {response.status_code}: {error_detail}. Endpoint ID: {endpoint_id}. Make sure your RunPod workers are running (green 'idle' status in console)!",
                    500
                )
                return

            # Parse the response
            try:
                result_data = response.json()
            except json.JSONDecodeError:
                self.send_error_response(
                    f"Invalid JSON response: {response.text[:200]}",
                    500
                )
                return

            # Extract image from ComfyUI response
            image_data = None

            # ComfyUI typically returns images in output.message or output.images
            if "output" in result_data:
                output = result_data["output"]

                # Try different ComfyUI response formats
                if isinstance(output, dict):
                    # Format 1: output.message (base64 string)
                    if "message" in output:
                        image_data = output["message"]
                    # Format 2: output.images (list of base64 strings)
                    elif "images" in output and isinstance(output["images"], list) and len(output["images"]) > 0:
                        image_data = output["images"][0]
                    # Format 3: output.image (single base64 string)
                    elif "image" in output:
                        image_data = output["image"]
                    # Format 4: Any other string value
                    else:
                        # Try to find any base64-looking string in the output
                        for key, value in output.items():
                            if isinstance(value, str) and len(value) > 100:
                                image_data = value
                                break

                # If output is a list, take first element
                elif isinstance(output, list) and len(output) > 0:
                    image_data = output[0]
                # If output is directly a string
                elif isinstance(output, str):
                    image_data = output

            if not image_data:
                self.send_error_response(
                    f"No image in response. Full response structure: {json.dumps(result_data, indent=2)[:1000]}",
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

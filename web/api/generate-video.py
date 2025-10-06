"""
Vercel Serverless Function for Video Generation
Generates animated Mexican art videos using AnimateDiff on RunPod!
"""

import os
import json
import time
import requests
from http.server import BaseHTTPRequestHandler


# Mexican Art Style Templates (same as image generation)
MEXICAN_ART_STYLES = {
    "frida": "in the style of Frida Kahlo with vibrant colors, self-portrait elements, flowers in hair, and nature symbolism",
    "mural": "in the style of Mexican muralism with bold cultural symbols, strong social themes, and dramatic compositions",
    "folk": "in the style of Mexican folk art with bright traditional colors, intricate patterns, and festive cultural motifs"
}


def enhance_prompt_with_style(prompt, style="frida"):
    """Enhance the user's prompt with Mexican art style."""
    style_modifier = MEXICAN_ART_STYLES.get(style, MEXICAN_ART_STYLES["frida"])
    # Add motion keywords for video
    return f"{prompt}, {style_modifier}, smooth animation, flowing movement, artistic motion"


def get_animatediff_workflow(enhanced_prompt):
    """Generate ComfyUI workflow for AnimateDiff (text-to-video)."""
    return {
        "6": {
            "inputs": {
                "text": enhanced_prompt,
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "CLIP Text Encode (Positive)"}
        },
        "7": {
            "inputs": {
                "text": "blurry, low quality, distorted, static, frozen",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode",
            "_meta": {"title": "CLIP Text Encode (Negative)"}
        },
        "3": {
            "inputs": {
                "seed": int(time.time()),
                "steps": 25,  # AnimateDiff needs more steps
                "cfg": 7.5,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler",
            "_meta": {"title": "KSampler"}
        },
        "4": {
            "inputs": {
                "ckpt_name": "sd_v15_mm_sd_v15.ckpt"  # AnimateDiff checkpoint
            },
            "class_type": "CheckpointLoaderSimple",
            "_meta": {"title": "Load Checkpoint"}
        },
        "5": {
            "inputs": {
                "width": 512,
                "height": 512,
                "batch_size": 16  # Number of frames
            },
            "class_type": "EmptyLatentImage",
            "_meta": {"title": "Empty Latent Image"}
        },
        "8": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            },
            "class_type": "VAEDecode",
            "_meta": {"title": "VAE Decode"}
        },
        "9": {
            "inputs": {
                "filename_prefix": "maia_video",
                "images": ["8", 0]
            },
            "class_type": "SaveImage",
            "_meta": {"title": "Save Video"}
        }
    }


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler for video generation."""

    def do_POST(self):
        """Handle POST requests for video generation."""
        try:
            # Read the request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))

            # Get parameters from request
            prompt = data.get('prompt', '').strip()
            style = data.get('style', 'frida')

            if not prompt:
                self.send_error_response("Please provide a prompt!", 400)
                return

            # Get RunPod configuration
            api_key = os.getenv("RUNPOD_API_KEY")
            # For video, we'll use a separate endpoint (or same one if it supports AnimateDiff)
            endpoint_id = os.getenv("RUNPOD_VIDEO_ENDPOINT_ID", os.getenv("RUNPOD_ENDPOINT_ID"))

            if not api_key or not endpoint_id:
                self.send_error_response(
                    "Video generation not configured yet! Coming soon!",
                    500
                )
                return

            # Clean up credentials
            api_key = str(api_key).strip()
            endpoint_id = str(endpoint_id).strip()

            # Enhance prompt for video
            enhanced_prompt = enhance_prompt_with_style(prompt, style)

            # Get AnimateDiff workflow
            workflow = get_animatediff_workflow(enhanced_prompt)

            # Prepare payload
            payload = {
                "input": {
                    "workflow": workflow
                }
            }

            # Call RunPod API
            api_url = f"https://api.runpod.ai/v2/{endpoint_id}/runsync"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            try:
                response = requests.post(
                    api_url,
                    json=payload,
                    headers=headers,
                    timeout=300  # 5 minutes for video generation
                )
            except requests.exceptions.Timeout:
                self.send_error_response(
                    "Video generation timed out. Please try again!",
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
                error_detail = response.text
                try:
                    error_json = response.json()
                    error_detail = json.dumps(error_json, indent=2)
                except:
                    pass

                self.send_error_response(
                    f"RunPod API error {response.status_code}: {error_detail}",
                    500
                )
                return

            # Parse response
            try:
                result_data = response.json()
            except json.JSONDecodeError:
                self.send_error_response(
                    f"Invalid JSON response: {response.text[:200]}",
                    500
                )
                return

            # Extract video from response
            video_data = None

            if "output" in result_data:
                output = result_data["output"]

                if isinstance(output, dict):
                    if "video" in output:
                        video_data = output["video"]
                    elif "message" in output:
                        video_data = output["message"]
                    else:
                        for key, value in output.items():
                            if isinstance(value, str) and len(value) > 100:
                                video_data = value
                                break
                elif isinstance(output, str):
                    video_data = output

            # Extract from nested dict if needed
            if isinstance(video_data, dict):
                if "data" in video_data:
                    video_data = video_data["data"]
                elif "video" in video_data:
                    video_data = video_data["video"]

            if not video_data or not isinstance(video_data, str):
                self.send_error_response(
                    f"No video in response. Response: {json.dumps(result_data, indent=2)[:1000]}",
                    500
                )
                return

            # Send success response
            self.send_success_response({
                "video": video_data,
                "prompt": prompt,
                "enhanced_prompt": enhanced_prompt,
                "style": style
            })

        except json.JSONDecodeError:
            self.send_error_response("Invalid request format", 400)
        except Exception as e:
            self.send_error_response(f"Error generating video: {str(e)}", 500)

    def send_success_response(self, data):
        """Send a successful JSON response."""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
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

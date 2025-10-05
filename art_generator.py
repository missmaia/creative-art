#!/usr/bin/env python3
"""
Maia's Mexican Art Machine - Desktop Art Generator
Creates beautiful AI art inspired by Frida Kahlo and Mexican folk art!
"""

import os
import sys
import base64
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import runpod

# Load environment variables from .env file
# This keeps your API keys safe and separate from the code!
load_dotenv()

# Mexican Art Style Templates
MEXICAN_ART_STYLES = {
    "frida": "in the style of Frida Kahlo with vibrant colors, self-portrait elements, flowers in hair, and nature symbolism",
    "mural": "in the style of Mexican muralism with bold cultural symbols, strong social themes, and dramatic compositions",
    "folk": "in the style of Mexican folk art with bright traditional colors, intricate patterns, and festive cultural motifs"
}


def get_runpod_config():
    """
    Get RunPod API configuration from environment variables.
    Returns a dictionary with api_key and endpoint_id.
    """
    api_key = os.getenv("RUNPOD_API_KEY")
    endpoint_id = os.getenv("RUNPOD_ENDPOINT_ID")

    if not api_key:
        print("❌ Error: RUNPOD_API_KEY not found in .env file!")
        print("Please create a .env file with your RunPod API key.")
        print("See .env.example for template.")
        sys.exit(1)

    if not endpoint_id:
        print("❌ Error: RUNPOD_ENDPOINT_ID not found in .env file!")
        print("Please add your RunPod endpoint ID to .env file.")
        sys.exit(1)

    return {"api_key": api_key, "endpoint_id": endpoint_id}


def enhance_prompt_with_style(prompt, style="frida"):
    """
    Enhance the user's prompt with Mexican art style.

    Args:
        prompt: The user's original art idea
        style: Which Mexican art style to use (frida, mural, or folk)

    Returns:
        Enhanced prompt with style instructions
    """
    style_modifier = MEXICAN_ART_STYLES.get(style, MEXICAN_ART_STYLES["frida"])
    return f"{prompt}, {style_modifier}"


def generate_art(prompt, style="frida"):
    """
    Generate art using RunPod's Flux model.

    Args:
        prompt: What you want to create
        style: Mexican art style to use

    Returns:
        Base64 encoded image data or None if failed
    """
    print("🎨 Starting Maia's Art Machine...")
    print(f"✨ Creating art with prompt: '{prompt}'")
    print(f"🌻 Style: {style.upper()}")

    # Get API configuration
    config = get_runpod_config()
    runpod.api_key = config["api_key"]

    # Create endpoint instance
    endpoint = runpod.Endpoint(config["endpoint_id"])

    # Enhance prompt with Mexican art style
    enhanced_prompt = enhance_prompt_with_style(prompt, style)
    print(f"📝 Enhanced prompt: '{enhanced_prompt}'")

    # Prepare the request payload
    # This is what we send to RunPod's AI brain!
    payload = {
        "input": {
            "prompt": enhanced_prompt,
            "num_inference_steps": 25,  # How many steps the AI takes (more = better quality but slower)
            "guidance_scale": 7.5,  # How closely to follow your prompt (higher = more literal)
            "width": 1024,  # Image width in pixels
            "height": 1024,  # Image height in pixels
        }
    }

    try:
        print("🚀 Sending request to RunPod...")
        print("⏳ Please wait, the AI is painting your masterpiece...")

        # Send request and wait for result (synchronous)
        result = endpoint.run_sync(payload, timeout=300)  # Wait up to 5 minutes

        print("✅ Art generated successfully!")

        # Extract the image data from the response
        if "output" in result and "image" in result["output"]:
            return result["output"]["image"]
        elif "output" in result and isinstance(result["output"], str):
            return result["output"]
        else:
            print(f"❌ Unexpected response format: {result}")
            return None

    except Exception as e:
        print(f"❌ Error generating art: {e}")
        print("💡 Tip: Make sure your RunPod endpoint is deployed and running!")
        return None


def save_image(image_data, prompt):
    """
    Save the generated image to a file.

    Args:
        image_data: Base64 encoded image string
        prompt: Original prompt (used in filename)

    Returns:
        Path to saved file or None if failed
    """
    try:
        # Decode base64 image data to bytes
        # Base64 is how images travel over the internet as text!
        image_bytes = base64.b64decode(image_data)

        # Create a unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Make prompt filename-safe (remove special characters)
        safe_prompt = "".join(c if c.isalnum() or c in " -_" else "" for c in prompt)[:30]
        filename = f"mexican_art_{safe_prompt}_{timestamp}.png"

        # Save to current directory
        output_path = Path(filename)
        output_path.write_bytes(image_bytes)

        print(f"💾 Image saved to: {output_path.absolute()}")
        return str(output_path)

    except Exception as e:
        print(f"❌ Error saving image: {e}")
        return None


def show_help():
    """Display usage instructions."""
    help_text = """
🎨 Maia's Mexican Art Machine 🌻

Usage:
    python art_generator.py "<your prompt>" [style]

Styles available:
    frida  - Frida Kahlo style with vibrant colors and nature (default)
    mural  - Mexican muralism with bold cultural symbols
    folk   - Mexican folk art with traditional patterns

Examples:
    python art_generator.py "a garden with butterflies"
    python art_generator.py "self-portrait with sunflowers" frida
    python art_generator.py "Day of the Dead celebration" folk
    python art_generator.py "workers and revolution" mural

Setup:
    1. Copy .env.example to .env
    2. Add your RUNPOD_API_KEY
    3. Add your RUNPOD_ENDPOINT_ID
    4. Run the script!

Happy creating! ✨
"""
    print(help_text)


def main():
    """Main function to run the art generator."""
    # Check if user needs help
    if len(sys.argv) < 2 or sys.argv[1] in ["-h", "--help", "help"]:
        show_help()
        sys.exit(0)

    # Get prompt from command line argument
    prompt = sys.argv[1]

    # Get style (default to "frida" if not specified)
    style = sys.argv[2] if len(sys.argv) > 2 else "frida"

    # Validate style
    if style not in MEXICAN_ART_STYLES:
        print(f"⚠️  Unknown style '{style}'. Using 'frida' instead.")
        style = "frida"

    # Generate the art!
    image_data = generate_art(prompt, style)

    if image_data:
        # Save the image
        output_file = save_image(image_data, prompt)

        if output_file:
            print("🎉 Success! Your Mexican-style art is ready!")
            print(f"📂 Open {output_file} to see your masterpiece!")
        else:
            print("😞 Failed to save the image.")
            sys.exit(1)
    else:
        print("😞 Failed to generate art. Please check your configuration.")
        sys.exit(1)


if __name__ == "__main__":
    main()

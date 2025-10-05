# 🎨 Maia's Mexican Art Machine 🌻

[![Made by](https://img.shields.io/badge/Made%20by-Maia%20(Age%208!)-FF69B4?style=for-the-badge)](https://github.com/missmaia)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![Powered by](https://img.shields.io/badge/Powered%20by-RunPod-5C6BC0?style=for-the-badge)](https://runpod.io)
[![AI Model](https://img.shields.io/badge/AI-Flux%20Schnell-FF6B9D?style=for-the-badge)](https://runpod.io)

> **Create beautiful AI art inspired by Frida Kahlo and Mexican folk art!**

Built by an 8-year-old learning to code, this project combines AI, art, and culture to generate stunning Mexican-style artwork.

## ✨ Features

- 🌺 **Three Mexican Art Styles**
  - **Frida Kahlo**: Vibrant self-portraits with nature symbolism
  - **Muralist**: Bold cultural symbols and social themes
  - **Folk Art**: Traditional colorful patterns and festive motifs

- 🖥️ **Desktop Tool**: Command-line Python script for local art generation
- 🌐 **Web Interface**: Beautiful website anyone can use (deployed on Vercel)
- 🤖 **AI-Powered**: Uses RunPod's Flux model for high-quality image generation
- 🔒 **Secure**: Proper API key management and environment variables

## 🎥 Demo

*Coming soon! Screenshots and examples of generated art!*

## 🚀 Quick Start

### Option 1: Use the Website (Easiest!)

Just visit the deployed website: `[Your Vercel URL will go here]`

1. Choose your art style (Frida, Mural, or Folk)
2. Type what you want to create
3. Click "Generate Art!"
4. Download your masterpiece!

### Option 2: Run Locally (Desktop Tool)

#### Prerequisites

- Python 3.10 or higher
- A RunPod account ([sign up here](https://runpod.io))
- RunPod API key and Endpoint ID

#### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/missmaia/creative-art.git
   cd creative-art
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your environment variables**
   ```bash
   cp .env.example .env
   ```

   Then edit `.env` and add your RunPod credentials:
   ```env
   RUNPOD_API_KEY=your_api_key_here
   RUNPOD_ENDPOINT_ID=your_endpoint_id_here
   ```

#### Usage

Generate art with a simple command:

```bash
# Basic usage (uses Frida Kahlo style by default)
python art_generator.py "a garden with butterflies"

# Specify a style
python art_generator.py "workers celebrating" mural
python art_generator.py "Day of the Dead celebration" folk
```

The generated image will be saved in the current directory with a timestamp!

## 🎨 Example Prompts

Try these creative ideas:

- `"self-portrait with sunflowers and monarch butterflies"`
- `"magical forest with jaguars and tropical birds"`
- `"traditional Mexican fiesta with papel picado"`
- `"colorful garden with hibiscus and hummingbirds"`
- `"Day of the Dead altar with marigolds and sugar skulls"`
- `"workers in a field during harvest time"`

## 🛠️ How to Set Up RunPod

1. **Create a RunPod account**
   - Go to [runpod.io](https://runpod.io) and sign up

2. **Get your API Key**
   - Go to Settings → API Keys
   - Click "Create API Key"
   - Give it a name (like "ArtMachine")
   - Choose "Restricted" permissions (safer!)
   - Copy the key and save it in your `.env` file

3. **Deploy a Serverless Endpoint**
   - Go to Serverless → Endpoints
   - Click "Create Endpoint"
   - Search for "ComfyUI + Flux Schnell" template
   - Click "Deploy"
   - Copy the Endpoint ID and save it in your `.env` file

## 📁 Project Structure

```
creative-art/
├── art_generator.py          # Desktop tool - main Python script
├── requirements.txt           # Python package dependencies
├── .env.example              # Template for environment variables
├── .gitignore                # Files to keep out of Git
├── vercel.json               # Vercel deployment configuration
├── examples/
│   └── mexican_art_prompts.txt  # Fun prompt ideas
└── web/
    ├── index.html            # Beautiful website interface
    └── api/
        └── generate.py       # Serverless function for website
```

## 🧠 What I Learned

Building this project at age 8, I learned about:

- **Python Programming**: Functions, error handling, file I/O
- **APIs**: How programs talk to each other over the internet
- **Environment Variables**: Keeping secrets safe
- **Git & GitHub**: Version control and sharing code
- **Web Development**: HTML, CSS, JavaScript
- **Serverless Functions**: Code that runs in the cloud
- **AI/ML**: How AI generates art from text descriptions
- **Mexican Art History**: Frida Kahlo, muralism, and folk art!

## 🌟 Technologies Used

- **Python 3.12**: Main programming language
- **RunPod**: GPU cloud platform for AI inference
- **Flux Schnell**: State-of-the-art text-to-image AI model
- **Vercel**: Serverless deployment platform
- **HTML/CSS/JavaScript**: Web interface
- **Git & GitHub**: Version control

## 🎓 Educational Value

This project demonstrates:

- **Full-stack development** (frontend + backend)
- **API integration** with third-party services
- **Security best practices** (environment variables, .gitignore)
- **Professional code structure** and documentation
- **Cultural awareness** (Mexican art history)
- **Problem-solving** and **creative thinking**

## 🤝 Contributing

This is my learning project, but I'd love to hear your ideas! If you have suggestions:

1. Open an Issue describing your idea
2. Be kind and encouraging (I'm still learning!)
3. Teach me something new!

## 📜 License

MIT License - Feel free to learn from this code!

## 🌻 About the Artist

Hi! I'm Maia, and I'm 8 years old. I love art, coding, and learning about different cultures. I built this project to combine my interests in technology and Mexican art, especially Frida Kahlo's amazing paintings!

### Why Frida Kahlo?

Frida Kahlo was a Mexican painter famous for:
- **Self-portraits** with bold colors and emotions
- **Nature symbolism** (flowers, animals, plants)
- **Cultural pride** in Mexican traditions
- **Overcoming challenges** with creativity and strength

She inspires me to be creative and proud of who I am!

## 🙏 Acknowledgments

- **Mom & Dad** for helping me set up accounts and teaching me
- **RunPod** for providing amazing AI tools
- **Frida Kahlo** for inspiring this project
- **The open-source community** for all the amazing Python libraries

## 📞 Contact

- GitHub: [@missmaia](https://github.com/missmaia)
- Project Link: [https://github.com/missmaia/creative-art](https://github.com/missmaia/creative-art)

---

<div align="center">

**Made with ❤️ and lots of learning by Maia**

*"I paint self-portraits because I am so often alone, because I am the person I know best." - Frida Kahlo*

🎨 **Happy Creating!** 🌻

</div>

# 🎨 Maia's Art Machine - Web App & PWA

This is the web interface for Maia's Mexican Art Machine! It's a Progressive Web App (PWA), which means you can install it on your phone! 📱

## 🚀 How to Run Locally

### 1. Setup Environment
Copy the example environment file and add your API keys:
```bash
cp .env.example .env
```
Edit `.env` and add your `RUNPOD_API_KEY` and `RUNPOD_ENDPOINT_ID`.

### 2. Install Dependencies
Install the Node.js packages:
```bash
npm install
```

Install the Python packages (if you haven't already):
```bash
pip install -r ../requirements.txt
```

### 3. Run the Backend Server
Open a new terminal and run the local API server:
```bash
python api_server.py
```
This will start the art generator on `http://localhost:3001`.

### 4. Run the Web App
Open another terminal and start the website:
```bash
npm run dev
```
Open `http://localhost:5173` in your browser.

## 📱 How to Install on Mobile (PWA)

1. **Deploy to Vercel** (or use a tunnel like ngrok for localhost).
2. Open the website on your phone.
3. Tap "Share" (iOS) or the menu (Android).
4. Tap **"Add to Home Screen"**.
5. Now it looks like a real app! 🌺

## 🛠️ Tech Stack
- **React + Vite**: Fast web framework
- **Vite PWA Plugin**: Makes it installable
- **Tailwind CSS**: For styling
- **Python**: For the backend API

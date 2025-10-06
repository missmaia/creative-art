import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, Palette, Heart, Loader2, Download } from 'lucide-react'
import './App.css'

const MEXICAN_STYLES = [
  {
    id: 'frida',
    name: 'Frida Kahlo',
    emoji: '🌺',
    description: 'Vibrant & Nature',
    color: 'from-pink-500 to-rose-500'
  },
  {
    id: 'mural',
    name: 'Muralist',
    emoji: '🎭',
    description: 'Bold & Cultural',
    color: 'from-purple-500 to-indigo-500'
  },
  {
    id: 'folk',
    name: 'Folk Art',
    emoji: '🎪',
    description: 'Traditional & Festive',
    color: 'from-yellow-500 to-orange-500'
  }
]

const EXAMPLE_PROMPTS = [
  'a garden with butterflies and monarch wings',
  'self-portrait with sunflowers',
  'Day of the Dead celebration altar',
  'magical forest with exotic animals',
  'traditional fiesta with papel picado'
]

function App() {
  const [selectedStyle, setSelectedStyle] = useState('frida')
  const [prompt, setPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedImage, setGeneratedImage] = useState(null)
  const [error, setError] = useState(null)

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      alert('Please enter what you want to create!')
      return
    }

    setIsGenerating(true)
    setError(null)
    setGeneratedImage(null)

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt,
          style: selectedStyle
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate art')
      }

      // Handle different image data formats
      let imageData = data.image

      if (Array.isArray(imageData)) {
        imageData = imageData[0]
      }

      if (typeof imageData === 'object' && imageData !== null) {
        imageData = imageData.image || imageData.data
      }

      if (typeof imageData === 'string') {
        if (imageData.startsWith('data:')) {
          setGeneratedImage(imageData)
        } else {
          setGeneratedImage(`data:image/png;base64,${imageData}`)
        }
      } else {
        throw new Error(`Unexpected image format: ${typeof imageData}`)
      }

    } catch (err) {
      setError(err.message)
      console.error('Error:', err)
    } finally {
      setIsGenerating(false)
    }
  }

  const handleDownload = () => {
    if (!generatedImage) return

    const link = document.createElement('a')
    link.href = generatedImage
    link.download = `maia-mexican-art-${Date.now()}.png`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  return (
    <div className="min-h-screen py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <motion.h1
            className="text-6xl font-bold mb-3 text-shadow"
            animate={{
              backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
            }}
            transition={{ duration: 5, repeat: Infinity }}
            style={{
              background: 'linear-gradient(90deg, #FF6B9D, #FFE66D, #4ECDC4, #FF6B9D)',
              backgroundSize: '200% 200%',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}
          >
            🎨 Maia's Art Machine 🌻
          </motion.h1>
          <p className="text-xl text-gray-700 font-medium">
            Create beautiful AI art inspired by Frida Kahlo & Mexican Folk Art!
          </p>
        </motion.div>

        {/* Style Selector */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <h2 className="text-2xl font-bold text-center mb-4 text-gray-800 flex items-center justify-center gap-2">
            <Palette className="w-6 h-6" />
            Choose Your Art Style:
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {MEXICAN_STYLES.map((style, index) => (
              <motion.button
                key={style.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + index * 0.1 }}
                whileHover={{ scale: 1.05, y: -4 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSelectedStyle(style.id)}
                className={`p-6 rounded-2xl transition-all duration-300 ${
                  selectedStyle === style.id
                    ? `bg-gradient-to-br ${style.color} text-white shadow-2xl ring-4 ring-white`
                    : 'bg-white text-gray-800 shadow-lg hover:shadow-xl'
                }`}
              >
                <div className="text-5xl mb-2">{style.emoji}</div>
                <div className="font-bold text-lg">{style.name}</div>
                <div className={`text-sm ${selectedStyle === style.id ? 'text-white' : 'text-gray-500'}`}>
                  {style.description}
                </div>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Prompt Input */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-6"
        >
          <h2 className="text-2xl font-bold mb-3 text-gray-800 flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-yellow-500" />
            What Do You Want to Create?
          </h2>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Describe your art idea... (e.g., 'a garden with butterflies and flowers')"
            className="w-full p-4 rounded-xl border-4 border-yellow-300 focus:border-pink-400 focus:outline-none focus:ring-4 focus:ring-pink-200 transition-all duration-300 text-lg resize-none h-32 shadow-lg"
          />

          {/* Example Prompts */}
          <div className="mt-4">
            <p className="text-sm font-semibold text-gray-700 mb-2">Click for inspiration:</p>
            <div className="flex flex-wrap gap-2">
              {EXAMPLE_PROMPTS.map((example, index) => (
                <motion.button
                  key={index}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setPrompt(example)}
                  className="px-4 py-2 bg-white rounded-full text-sm font-medium text-gray-700 hover:bg-gradient-to-r hover:from-pink-400 hover:to-yellow-400 hover:text-white transition-all duration-300 shadow-md hover:shadow-lg"
                >
                  {example}
                </motion.button>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Generate Button */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleGenerate}
          disabled={isGenerating}
          className="w-full py-6 rounded-2xl text-2xl font-bold text-white mexican-gradient shadow-2xl hover:shadow-3xl transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-3"
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-8 h-8 animate-spin" />
              Creating your masterpiece...
            </>
          ) : (
            <>
              <Sparkles className="w-8 h-8" />
              Generate Art!
              <Sparkles className="w-8 h-8" />
            </>
          )}
        </motion.button>

        {/* Loading State */}
        <AnimatePresence>
          {isGenerating && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="mt-8 text-center"
            >
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                className="w-20 h-20 mx-auto mb-4 border-8 border-pink-300 border-t-pink-600 rounded-full"
              />
              <h3 className="text-2xl font-bold text-gray-800 mb-2">
                🎨 Creating your masterpiece...
              </h3>
              <p className="text-gray-600">
                This may take 30-60 seconds. The AI is painting!
              </p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error State */}
        <AnimatePresence>
          {error && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="mt-8 p-6 bg-red-100 border-4 border-red-400 rounded-2xl"
            >
              <h3 className="text-xl font-bold text-red-800 mb-2">
                😞 Oops! Something went wrong.
              </h3>
              <p className="text-red-700">{error}</p>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Generated Image */}
        <AnimatePresence>
          {generatedImage && !isGenerating && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8, y: 50 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, y: 50 }}
              transition={{ type: 'spring', damping: 15 }}
              className="mt-12"
            >
              <motion.h2
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-3xl font-bold text-center mb-6 text-gray-800 flex items-center justify-center gap-3"
              >
                <Sparkles className="w-8 h-8 text-yellow-500" />
                Your Mexican Masterpiece!
                <Sparkles className="w-8 h-8 text-yellow-500" />
              </motion.h2>
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="relative rounded-3xl overflow-hidden shadow-2xl border-8 border-yellow-300 glow"
              >
                <img
                  src={generatedImage}
                  alt="Generated Mexican Art"
                  className="w-full h-auto"
                />
              </motion.div>

              {/* Download Button */}
              <motion.button
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleDownload}
                className="mt-6 px-8 py-4 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-2xl font-bold text-lg shadow-xl hover:shadow-2xl transition-all duration-300 flex items-center justify-center gap-3 mx-auto"
              >
                <Download className="w-6 h-6" />
                Save Your Masterpiece!
                <Download className="w-6 h-6" />
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Footer */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-12 text-center text-gray-600 space-y-1"
        >
          <p className="flex items-center justify-center gap-2">
            Built with <Heart className="w-4 h-4 text-red-500 fill-red-500" /> by Maia (Age 8!)
          </p>
          <p>Powered by RunPod AI & Flux Model</p>
          <p>🌟 Learning to code and create art! 🌟</p>
        </motion.div>
      </div>
    </div>
  )
}

export default App

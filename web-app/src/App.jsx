import { useState, useRef, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, Palette, Heart, Loader2, Download, Camera, Upload, RefreshCw } from 'lucide-react'
import Webcam from 'react-webcam'
import './App.css'

const CELEBRITY_GENDERS = [
  {
    id: 'Female',
    name: 'Female Icons',
    emoji: '👩',
    description: 'Meet Frida, Salma, Thalía & More!',
    color: 'from-pink-500 to-rose-500',
    examples: ['Frida Kahlo', 'Salma Hayek', 'Thalía', 'María Félix']
  },
  {
    id: 'Male',
    name: 'Male Icons',
    emoji: '👨',
    description: 'Meet Diego, Canelo, Cantinflas & More!',
    color: 'from-blue-500 to-indigo-500',
    examples: ['Diego Rivera', 'Cantinflas', 'Canelo Álvarez', 'Carlos Santana']
  }
]

function App() {
  const [selectedGender, setSelectedGender] = useState('Female')
  const [capturedImage, setCapturedImage] = useState(null)
  const [showWebcam, setShowWebcam] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generatedImage, setGeneratedImage] = useState(null)
  const [selectedCelebrity, setSelectedCelebrity] = useState(null)
  const [error, setError] = useState(null)
  const webcamRef = useRef(null)
  const fileInputRef = useRef(null)

  const capturePhoto = useCallback(() => {
    const imageSrc = webcamRef.current.getScreenshot()
    setCapturedImage(imageSrc)
    setShowWebcam(false)
  }, [webcamRef])

  const handleFileUpload = (e) => {
    const file = e.target.files[0]
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader()
      reader.onloadend = () => {
        setCapturedImage(reader.result)
      }
      reader.readAsDataURL(file)
    } else {
      alert('Please select a valid image file!')
    }
  }

  const retakeSelfie = () => {
    setCapturedImage(null)
    setGeneratedImage(null)
    setSelectedCelebrity(null)
    setError(null)
  }

  const handleGenerate = async () => {
    if (!capturedImage) {
      alert('Please take a selfie or upload a photo first!')
      return
    }

    setIsGenerating(true)
    setError(null)
    setGeneratedImage(null)
    setSelectedCelebrity(null)

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image: capturedImage,
          gender: selectedGender
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to generate image')
      }

      // Handle image response
      let imageData = data.image
      if (imageData.startsWith('data:')) {
        setGeneratedImage(imageData)
      } else {
        setGeneratedImage(`data:image/png;base64,${imageData}`)
      }

      setSelectedCelebrity(data.celebrity || data.fullCelebrity || 'a Mexican Celebrity')

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
    link.download = `viva-la-selfie-${selectedCelebrity?.replace(/\s+/g, '-')}-${Date.now()}.png`
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
            📸 Viva La Selfie! 🌟
          </motion.h1>
          <p className="text-xl text-gray-700 font-medium">
            Take a selfie and see yourself with famous Mexican celebrities!
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Powered by Nano Banana Pro 🍌 (Google Gemini + Fal.ai)
          </p>
        </motion.div>

        {/* Gender Selector */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="mb-8"
        >
          <h2 className="text-2xl font-bold text-center mb-4 text-gray-800 flex items-center justify-center gap-2">
            <Palette className="w-6 h-6" />
            Choose Celebrity Gender:
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {CELEBRITY_GENDERS.map((gender, index) => (
              <motion.button
                key={gender.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 + index * 0.1 }}
                whileHover={{ scale: 1.05, y: -4 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSelectedGender(gender.id)}
                className={`p-6 rounded-2xl transition-all duration-300 ${
                  selectedGender === gender.id
                    ? `bg-gradient-to-br ${gender.color} text-white shadow-2xl ring-4 ring-white`
                    : 'bg-white text-gray-800 shadow-lg hover:shadow-xl'
                }`}
              >
                <div className="text-5xl mb-2">{gender.emoji}</div>
                <div className="font-bold text-lg">{gender.name}</div>
                <div className={`text-sm ${selectedGender === gender.id ? 'text-white' : 'text-gray-500'}`}>
                  {gender.description}
                </div>
                <div className={`text-xs mt-2 ${selectedGender === gender.id ? 'text-white/80' : 'text-gray-400'}`}>
                  {gender.examples.slice(0, 2).join(', ')}...
                </div>
              </motion.button>
            ))}
          </div>
        </motion.div>

        {/* Selfie Capture Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-6"
        >
          <h2 className="text-2xl font-bold mb-3 text-gray-800 flex items-center gap-2">
            <Camera className="w-6 h-6 text-blue-500" />
            Take or Upload Your Selfie:
          </h2>

          {/* No image captured yet */}
          {!capturedImage && !showWebcam && (
            <div className="flex flex-col md:flex-row gap-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setShowWebcam(true)}
                className="flex-1 py-6 rounded-2xl bg-gradient-to-r from-blue-500 to-cyan-500 text-white text-xl font-bold shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-3"
              >
                <Camera className="w-8 h-8" />
                Take Selfie
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => fileInputRef.current.click()}
                className="flex-1 py-6 rounded-2xl bg-gradient-to-r from-green-500 to-emerald-500 text-white text-xl font-bold shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center gap-3"
              >
                <Upload className="w-8 h-8" />
                Upload Photo
              </motion.button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileUpload}
                className="hidden"
              />
            </div>
          )}

          {/* Webcam active */}
          {showWebcam && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="space-y-4"
            >
              <div className="rounded-2xl overflow-hidden shadow-2xl border-4 border-blue-300">
                <Webcam
                  ref={webcamRef}
                  audio={false}
                  screenshotFormat="image/jpeg"
                  videoConstraints={{
                    width: 1280,
                    height: 720,
                    facingMode: "user"
                  }}
                  className="w-full"
                />
              </div>
              <div className="flex gap-4">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={capturePhoto}
                  className="flex-1 py-4 rounded-xl bg-gradient-to-r from-pink-500 to-rose-500 text-white text-lg font-bold shadow-lg"
                >
                  📸 Capture Photo
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => setShowWebcam(false)}
                  className="flex-1 py-4 rounded-xl bg-gray-500 text-white text-lg font-bold shadow-lg"
                >
                  Cancel
                </motion.button>
              </div>
            </motion.div>
          )}

          {/* Image captured */}
          {capturedImage && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="space-y-4"
            >
              <div className="rounded-2xl overflow-hidden shadow-2xl border-4 border-green-300">
                <img src={capturedImage} alt="Your selfie" className="w-full" />
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={retakeSelfie}
                className="w-full py-4 rounded-xl bg-gradient-to-r from-yellow-500 to-orange-500 text-white text-lg font-bold shadow-lg flex items-center justify-center gap-2"
              >
                <RefreshCw className="w-6 h-6" />
                Retake Selfie
              </motion.button>
            </motion.div>
          )}
        </motion.div>

        {/* Generate Button */}
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={handleGenerate}
          disabled={isGenerating || !capturedImage}
          className="w-full py-6 rounded-2xl text-2xl font-bold text-white mexican-gradient shadow-2xl hover:shadow-3xl transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center gap-3"
        >
          {isGenerating ? (
            <>
              <Loader2 className="w-8 h-8 animate-spin" />
              Creating your celebrity selfie...
            </>
          ) : (
            <>
              <Sparkles className="w-8 h-8" />
              Generate Celebrity Selfie!
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
                🎨 Creating your celebrity selfie...
              </h3>
              <p className="text-gray-600">
                Step 1: Nano Banana Pro (Gemini) is analyzing your photo... 👀<br/>
                Step 2: Picking the perfect celebrity... 🎭<br/>
                Step 3: Generating your photo together... ✨<br/>
                This takes 30-60 seconds total!
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
              {error.includes('API') && (
                <p className="text-red-600 text-sm mt-2">
                  💡 Make sure you've added your API keys to the .env file!
                </p>
              )}
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
                You & {selectedCelebrity}! 🌟
                <Sparkles className="w-8 h-8 text-yellow-500" />
              </motion.h2>
              <motion.div
                whileHover={{ scale: 1.02 }}
                className="relative rounded-3xl overflow-hidden shadow-2xl border-8 border-yellow-300 glow"
              >
                <img
                  src={generatedImage}
                  alt={`You with ${selectedCelebrity}`}
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
                Save Your Celebrity Selfie!
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
          <p>Powered by Google Gemini (Nano Banana Pro) & Fal.ai Flux Dev</p>
          <p>🌟 Learning to code and create magic! 🌟</p>
        </motion.div>
      </div>
    </div>
  )
}

export default App

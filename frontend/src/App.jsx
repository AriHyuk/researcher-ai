import { useState, useRef } from 'react'
import ReactMarkdown from 'react-markdown'

function App() {
  const [topik, setTopik] = useState('')
  const [target, setTarget] = useState('Dosen Penguji')
  const [geminiKey, setGeminiKey] = useState('') // BYOK Mode
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('') // Pesan progres real-time
  const [streamingContent, setStreamingContent] = useState('') // Teks yang "ngetik"
  const [result, setResult] = useState(null)
  const [internalLog, setInternalLog] = useState([]) // Trace log jeroan agent

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8081"
  const SYSTEM_API_KEY = import.meta.env.VITE_API_KEY || ""

  const handleRiset = async (e) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    setStreamingContent('')
    setInternalLog([])
    setStatus('Memulai koneksi ke Agent...')

    try {
      const response = await fetch(`${API_BASE_URL}/api/riset-lengkap`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'X-API-Key': SYSTEM_API_KEY,
          'X-Gemini-API-Key': geminiKey // BYOK header
        },
        body: JSON.stringify({ topik, target_pembaca: target })
      })
      
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Terjadi kesalahan pada server")
      }
      
      // STREAM READING LOGIC
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let partialContent = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        // Split chunk by newline karena kita yield JSON line per line
        const lines = chunk.split('\n').filter(l => l.trim() !== '')

        for (const line of lines) {
          try {
            const data = JSON.parse(line)
            
            if (data.status === 'researching' || data.status === 'writing' || data.status === 'editing') {
              setStatus(data.message)
            } else if (data.status === 'writing_stream') {
              partialContent += data.chunk
              setStreamingContent(partialContent)
            } else if (data.status === 'research_done') {
              setInternalLog(prev => [...prev, { step: 'Researcher', data: data.data }])
            } else if (data.status === 'revising') {
              setStatus(data.message)
              setInternalLog(prev => [...prev, { step: 'Editor Reflection', data: data.feedback }])
            } else if (data.status === 'completed') {
              setResult({ hasil_final: data.hasil_final })
              setStatus(data.message)
            } else if (data.status === 'error') {
              throw new Error(data.message)
            }
          } catch (pE) {
            console.error("Gagal parse line:", line)
          }
        }
      }
    } catch (error) {
      alert("⚠️ Error: " + error.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 py-10 px-4 font-sans text-slate-900 flex flex-col items-center">
      <div className="w-full max-w-4xl">
        
        {/* HEADER */}
        <div className="text-center mb-10">
          <h1 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-700 to-indigo-600 mb-2 tracking-tight">
            ai-researcher <span className="text-lg align-top bg-blue-100 text-blue-600 px-2 py-1 rounded-md ml-1">V2</span>
          </h1>
          <p className="text-slate-500 font-medium italic">Powered by Gemini 3.1 & Vertex AI</p>
        </div>

        {/* FORM INPUT */}
        <div className="bg-white p-8 rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100 mb-8">
          <form onSubmit={handleRiset} className="space-y-6">
            <div>
              <label className="block text-xs font-black text-slate-400 mb-2 uppercase tracking-widest">Penelitian</label>
              <textarea 
                className="w-full p-4 border border-slate-200 rounded-2xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none transition-all duration-300 min-h-[100px]"
                placeholder="Topik risetmu..."
                value={topik}
                onChange={(e) => setTopik(e.target.value)}
                required
              />
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-xs font-black text-slate-400 mb-2 uppercase tracking-widest">Persona Reader</label>
                <select 
                  className="w-full p-4 border border-slate-200 rounded-2xl bg-slate-50 outline-none"
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                >
                  <option>Dosen Penguji</option>
                  <option>Praktisi Industri</option>
                  <option>Masyarakat Umum</option>
                </select>
              </div>
              <div>
                <label className="block text-xs font-black text-slate-400 mb-2 uppercase tracking-widest">Gemini API Key (BYOK - Opsional)</label>
                <input 
                  type="password"
                  className="w-full p-4 border border-slate-200 rounded-2xl bg-slate-50 outline-none placeholder:text-slate-300"
                  placeholder="Paste Key Gemini-mu di sini..."
                  value={geminiKey}
                  onChange={(e) => setGeminiKey(e.target.value)}
                />
              </div>
            </div>

            <button 
              type="submit" 
              disabled={loading}
              className={`w-full py-5 rounded-2xl text-white font-black text-xl shadow-xl transition-all duration-300 transform active:scale-[0.98] ${loading ? 'bg-slate-300' : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:-translate-y-1 hover:shadow-blue-500/20'}`}
            >
              {loading ? (
                <div className="flex flex-col items-center">
                  <span className="text-xl animate-pulse">Running Agents...</span>
                  <span className="text-xs font-normal mt-1 text-blue-100 uppercase tracking-widest">{status}</span>
                </div>
              ) : 'GAS RISET!'}
            </button>
          </form>
        </div>

        {/* LOADING STATE - TYPING EFFECT VIEW */}
        {loading && streamingContent && !result && (
          <div className="bg-white p-10 rounded-3xl shadow-2xl border-l-[12px] border-blue-600 animate-pulse mb-8">
            <h3 className="text-blue-600 font-black mb-4 flex items-center gap-2">
              <span className="inline-block w-2 h-4 bg-blue-600 animate-bounce"></span>
              WRITER GENERATING CONTENT...
            </h3>
            <div className="prose prose-slate max-w-none opacity-60">
              <ReactMarkdown>{streamingContent}</ReactMarkdown>
            </div>
          </div>
        )}

        {/* FINAL RESULT */}
        {result && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="bg-white p-10 rounded-3xl shadow-2xl border border-slate-100">
              <header className="flex flex-col md:flex-row md:items-center justify-between mb-8 border-b border-slate-50 pb-6 gap-4">
                <h2 className="text-4xl font-black text-slate-900 -tracking-tight italic">the final paper.</h2>
                <div className="flex gap-2">
                   <span className="px-3 py-1 bg-indigo-100 text-indigo-700 text-[10px] font-black rounded-lg uppercase tracking-tighter">Gemini 3.1 Pro Editor</span>
                   <span className="px-3 py-1 bg-green-100 text-green-700 text-[10px] font-black rounded-lg uppercase tracking-tighter">Verified Research</span>
                </div>
              </header>
              
              <div className="prose prose-slate max-w-none text-slate-800 leading-relaxed text-xl first-letter:text-5xl first-letter:font-black first-letter:text-blue-600 first-letter:mr-3 first-letter:float-left">
                <ReactMarkdown>{result.hasil_final}</ReactMarkdown>
              </div>

              {/* TRACE LOG */}
              <div className="mt-12 space-y-4">
                <h4 className="text-xs font-black text-slate-300 uppercase tracking-[0.2em] text-center">Internal Trace Log</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                   {internalLog.map((log, idx) => (
                     <div key={idx} className="bg-slate-900 text-green-400 p-4 rounded-2xl text-[10px] font-mono overflow-auto max-h-[200px] border border-slate-800">
                        <div className="mb-2 text-white font-bold border-b border-slate-700 pb-1">[{log.step}]</div>
                        <pre>{JSON.stringify(log.data, null, 2)}</pre>
                     </div>
                   ))}
                </div>
              </div>
            </div>
          </div>
        )}

      </div>
      
      <footer className="mt-20 text-slate-400 text-[10px] font-black uppercase tracking-[0.3em]">
        ai-researcher // 2026 // Vertex AI // Monorepo V2
      </footer>
    </div>
  )
}

export default App
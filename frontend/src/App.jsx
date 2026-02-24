import { useState } from 'react'
import ReactMarkdown from 'react-markdown'

// ──────────────────────────────────────────────────────────────────
// UTILITY: parse streaming JSON-lines dengan aman (buffer accumulator)
// Ini solusi untuk chunk yang keputus antar network packet
// ──────────────────────────────────────────────────────────────────
function parseSSEBuffer(buffer) {
  const results = []
  const lines = buffer.split('\n')
  // Kembalikan sisa string yang belum closed (mungkin terpotong)
  let remainder = ''

  for (const line of lines) {
    const trimmed = line.trim()
    if (!trimmed) continue
    try {
      results.push(JSON.parse(trimmed))
    } catch {
      // Baris ini belum lengkap — simpan sebagai sisa untuk digabung dengan chunk berikutnya
      remainder = trimmed
    }
  }
  return { results, remainder }
}

// ──────────────────────────────────────────────────────────────────
// COMPONENT: Kartu Sumber Riset — Representasi visual untuk data riset profesional
// ──────────────────────────────────────────────────────────────────
function ResearchSourceCard({ source, index }) {
  return (
    <div className="flex gap-4 p-4 bg-slate-50 rounded-2xl border border-slate-100 hover:border-blue-200 transition-colors">
      <div className="flex-shrink-0 w-8 h-8 bg-blue-600 text-white rounded-lg flex items-center justify-center text-xs font-black">
        {index + 1}
      </div>
      <div className="flex-1 min-w-0">
        <p className="font-bold text-slate-800 text-sm leading-snug mb-1">{source.judul}</p>
        <p className="text-xs text-slate-500 mb-2">
          <span className="font-semibold">{source.penulis}</span>
          {source.tahun && source.tahun !== 'Tidak disebutkan' && ` · ${source.tahun}`}
        </p>
        <p className="text-xs text-slate-600 leading-relaxed">{source.temuan}</p>
      </div>
    </div>
  )
}

// ──────────────────────────────────────────────────────────────────
// COMPONENT: Panel Sumber Riset
// ──────────────────────────────────────────────────────────────────
function ResearchPanel({ researchData }) {
  if (!researchData) return null
  return (
    <div className="mt-12 pt-8 border-t border-slate-100">
      <h4 className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] mb-1">
        Sumber Riset Terverifikasi
      </h4>
      {researchData.summary_data && (
        <p className="text-sm text-slate-500 italic mb-6 leading-relaxed">
          {researchData.summary_data}
        </p>
      )}
      <div className="space-y-3">
        {researchData.sources?.map((src, i) => (
          <ResearchSourceCard key={i} source={src} index={i} />
        ))}
      </div>
    </div>
  )
}

// ──────────────────────────────────────────────────────────────────
// MAIN APP
// ──────────────────────────────────────────────────────────────────
function App() {
  const [topik, setTopik] = useState('')
  const [copied, setCopied] = useState(false)
  const [target, setTarget] = useState('Dosen Penguji')
  const [geminiKey, setGeminiKey] = useState('')
  const [loading, setLoading] = useState(false)
  const [status, setStatus] = useState('')
  const [streamingContent, setStreamingContent] = useState('')
  const [result, setResult] = useState(null)
  const [researchData, setResearchData] = useState(null)

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8081"
  const SYSTEM_API_KEY = import.meta.env.VITE_API_KEY || ""

  const handleRiset = async (e) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)
    setResearchData(null)
    setStreamingContent('')
    setStatus('Menghubungkan ke sistem agen...')

    try {
      const response = await fetch(`${API_BASE_URL}/api/riset-lengkap`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': SYSTEM_API_KEY,
          'X-Gemini-API-Key': geminiKey
        },
        body: JSON.stringify({ topik, target_pembaca: target })
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Terjadi kesalahan pada server")
      }

      // ── STREAM READING dengan BUFFER ACCUMULATOR ──────────────────
      // Solusi untuk chunk SSE yang keputus antar network packet:
      // kita akumulasi sisa baris yang belum complete, gabung dengan chunk berikutnya
      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''       // Accumulator untuk partial lines
      let partialContent = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        // Tambahkan hasil decode ke buffer yang ada
        buffer += decoder.decode(value, { stream: true })

        // Parse semua baris yang sudah complete, sisakan yang terpotong
        const { results, remainder } = parseSSEBuffer(buffer)
        buffer = remainder  // simpan sisa terpotong untuk chunk berikutnya

        for (const data of results) {
          if (data.status === 'researching' || data.status === 'writing' || data.status === 'editing') {
            setStatus(data.message)
          } else if (data.status === 'writing_stream') {
            partialContent += data.chunk
            setStreamingContent(partialContent)
          } else if (data.status === 'research_done') {
            setResearchData(data.data)  // Simpan data riset untuk ditampilkan di UI
          } else if (data.status === 'revising') {
            setStatus(data.message)
          } else if (data.status === 'completed') {
            setResult({ hasil_final: data.hasil_final })
            setStatus(data.message)
          } else if (data.status === 'error') {
            throw new Error(data.message)
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
          <p className="text-slate-500 font-medium italic">Powered by Gemini 2.5 & Vertex AI</p>
        </div>

        {/* FORM INPUT */}
        <div className="bg-white p-8 rounded-3xl shadow-xl shadow-slate-200/50 border border-slate-100 mb-8">
          <form onSubmit={handleRiset} className="space-y-6">
            <div>
              <label className="block text-xs font-black text-slate-400 mb-2 uppercase tracking-widest">Penelitian</label>
              <textarea
                className="w-full p-4 border border-slate-200 rounded-2xl focus:ring-4 focus:ring-blue-500/10 focus:border-blue-500 outline-none transition-all duration-300 min-h-[100px]"
                placeholder="Masukkan topik penelitian Anda..."
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
                  placeholder="Masukkan API Key Gemini Anda di sini..."
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
              ) : 'MULAI PENELITIAN'}
            </button>
          </form>
        </div>

        {/* LOADING STATE - TYPING EFFECT VIEW */}
        {loading && streamingContent && !result && (
          <div className="bg-white p-10 rounded-3xl shadow-2xl border-l-[12px] border-blue-600 animate-pulse mb-8">
            <h3 className="text-blue-600 font-black mb-4 flex items-center gap-2">
              <span className="inline-block w-2 h-4 bg-blue-600 animate-bounce"></span>
              PENULIS SEDANG MENYUSUN KONTEN...
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
                <h2 className="text-4xl font-black text-slate-900 -tracking-tight">Laporan Penelitian Final</h2>
                <div className="flex flex-wrap gap-2 items-center">
                  <span className="px-3 py-1 bg-indigo-100 text-indigo-700 text-[10px] font-black rounded-lg uppercase tracking-tighter">Gemini 2.5 Pro Editor</span>
                  <span className="px-3 py-1 bg-green-100 text-green-700 text-[10px] font-black rounded-lg uppercase tracking-tighter">Verified Research</span>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText(result.hasil_final)
                      setCopied(true)
                      setTimeout(() => setCopied(false), 2000)
                    }}
                    className="px-3 py-1 bg-slate-100 hover:bg-slate-200 text-slate-600 text-[10px] font-black rounded-lg uppercase tracking-tighter transition-colors"
                  >
                    {copied ? '✅ Copied!' : '📋 Copy MD'}
                  </button>
                  <button
                    onClick={() => {
                      const blob = new Blob([result.hasil_final], { type: 'text/markdown' })
                      const url = URL.createObjectURL(blob)
                      const a = document.createElement('a')
                      a.href = url
                      a.download = `${topik.slice(0, 40).replace(/\s+/g, '-')}.md`
                      a.click()
                      URL.revokeObjectURL(url)
                    }}
                    className="px-3 py-1 bg-blue-100 hover:bg-blue-200 text-blue-700 text-[10px] font-black rounded-lg uppercase tracking-tighter transition-colors"
                  >
                    ⬇️ Download .md
                  </button>
                </div>
              </header>

              <div className="prose prose-slate max-w-none text-slate-800 leading-relaxed text-xl first-letter:text-5xl first-letter:font-black first-letter:text-blue-600 first-letter:mr-3 first-letter:float-left">
                <ReactMarkdown>{result.hasil_final}</ReactMarkdown>
              </div>

              {/* RESEARCH SOURCES — proper UI, bukan raw JSON */}
              <ResearchPanel researchData={researchData} />
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
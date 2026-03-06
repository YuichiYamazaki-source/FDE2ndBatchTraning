import { useState } from 'react'
import { sendChat } from '../api/client'

// Phase 1-2: direct LLM stub.
// Phase 3: replace sendChat with Orchestrator Agent call (no UI changes needed).

export default function ChatPanel({ selectedProductId }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSend(e) {
    e.preventDefault()
    if (!input.trim()) return

    const userMsg = { role: 'user', text: input.trim() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const data = await sendChat(userMsg.text, selectedProductId)
      setMessages(prev => [...prev, { role: 'assistant', text: data.response }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', text: 'Error: could not connect to chat service.' }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <section style={{ background: '#fff', borderRadius: 8, padding: 16, boxShadow: '0 1px 4px rgba(0,0,0,0.1)' }} aria-label="Chat panel">
      <h3 style={{ fontSize: 15, marginBottom: 8 }}>Product Assistant</h3>
      {selectedProductId && <p style={{ fontSize: 12, color: '#888', marginBottom: 8 }}>Asking about product: {selectedProductId}</p>}
      <div style={{ minHeight: 80, maxHeight: 200, overflowY: 'auto', fontSize: 13, marginBottom: 8, display: 'flex', flexDirection: 'column', gap: 6 }}>
        {messages.length === 0 && <p style={{ color: '#bbb', fontSize: 12 }}>Ask anything about a product…</p>}
        {messages.map((m, i) => (
          <div key={i} style={{ alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start', background: m.role === 'user' ? '#0070f3' : '#f0f0f0', color: m.role === 'user' ? '#fff' : '#333', padding: '6px 10px', borderRadius: 8, maxWidth: '80%' }}>
            {m.text}
          </div>
        ))}
      </div>
      <form onSubmit={handleSend} style={{ display: 'flex', gap: 8 }}>
        <input
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Ask about this product…"
          aria-label="Chat message"
          disabled={loading}
          style={{ flex: 1, padding: '6px 10px', borderRadius: 4, border: '1px solid #ccc', fontSize: 13 }}
        />
        <button type="submit" disabled={loading || !input.trim()} style={{ padding: '6px 14px', borderRadius: 4, background: '#0070f3', color: '#fff', border: 'none', cursor: 'pointer' }}>
          {loading ? '…' : 'Send'}
        </button>
      </form>
    </section>
  )
}

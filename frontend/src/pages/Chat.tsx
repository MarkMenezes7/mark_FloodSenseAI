import { useState } from 'react'
import './Chat.css'

interface Message { role: 'user' | 'assistant'; content: string; timestamp: Date }

const QUICK_QUESTIONS = [
  'What should I do during a flood?',
  'How do I protect my home from flooding?',
  'What are the signs of flash flooding?',
  'What emergency contacts should I know?',
  'How does heavy rainfall cause floods?',
  'How do I prepare an emergency kit?'
]

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([{
    role: 'assistant',
    content: "Hello! I'm your **FloodSenseAI Assistant**, powered by Google Gemini.\n\nI can help you with flood safety, emergency preparedness, risk information, and disaster response guidelines.\n\nAsk me anything, or tap one of the quick questions below to get started.",
    timestamp: new Date()
  }])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const API = window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://mark-floodsenseai.onrender.com'

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading) return
    setMessages(prev => [...prev, { role: 'user', content: text, timestamp: new Date() }])
    setInput('')
    setLoading(true)
    try {
      const res = await fetch(`${API}/api/rag/chat`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text })
      })
      const data = await res.json()
      setMessages(prev => [...prev, { role: 'assistant', content: data.response || 'Sorry, I could not process that.', timestamp: new Date() }])
    } catch {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Connection error. Please make sure the backend server is running.', timestamp: new Date() }])
    } finally { setLoading(false) }
  }

  const fmt = (t: string) => t.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br/>')

  return (
    <div className="page chat-page">
      <div className="container chat-wrap">

        {/* Header */}
        <div className="chat-header card">
          <div className="chat-avatar">🤖</div>
          <div className="chat-header-info">
            <h2>AI Flood Assistant</h2>
            <p>Powered by Google Gemini · Flood Safety Expert</p>
          </div>
          <div className="online-badge">🟢 Online</div>
        </div>

        {/* Quick Questions */}
        <div className="quick-qs">
          <p className="quick-qs-label">Quick questions:</p>
          <div className="quick-qs-list">
            {QUICK_QUESTIONS.map((q, i) => (
              <button key={i} className="quick-q" onClick={() => sendMessage(q)}>{q}</button>
            ))}
          </div>
        </div>

        {/* Messages */}
        <div className="messages-area card">
          {messages.map((msg, i) => (
            <div key={i} className={`msg-row ${msg.role}`}>
              {msg.role === 'assistant' && <div className="msg-avatar">🤖</div>}
              <div className={`msg-bubble ${msg.role}`}>
                <p dangerouslySetInnerHTML={{ __html: fmt(msg.content) }} />
                <span className="msg-time">{msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
              </div>
            </div>
          ))}
          {loading && (
            <div className="msg-row assistant">
              <div className="msg-avatar">🤖</div>
              <div className="msg-bubble assistant typing-bubble">
                <span className="dot" /><span className="dot" /><span className="dot" />
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <form className="chat-input-bar card" onSubmit={e => { e.preventDefault(); sendMessage(input) }}>
          <input
            id="chat-input"
            type="text"
            className="input chat-field"
            placeholder="Ask about flood safety, emergency steps, risk factors..."
            value={input}
            onChange={e => setInput(e.target.value)}
            disabled={loading}
          />
          <button type="submit" id="chat-send-btn" className="btn btn-primary send-btn" disabled={loading || !input.trim()}>
            {loading ? '⏳' : 'Send →'}
          </button>
        </form>

      </div>
    </div>
  )
}

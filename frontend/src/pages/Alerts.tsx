import { useState } from 'react'
import './Alerts.css'

const BOT_NUMBER = '+14155238886'
// Pre-fills the exact join phrase so users don't have to type it
const JOIN_TEXT = 'join young-except'
const WA_JOIN_LINK = `https://wa.me/14155238886?text=${encodeURIComponent(JOIN_TEXT)}`
const WA_HI_LINK   = `https://wa.me/14155238886?text=hi`

export default function Alerts() {
  const [phone, setPhone]             = useState('')
  const [threshold, setThreshold]     = useState(60)
  const [locationName, setLocationName] = useState('')
  const [coords, setCoords]           = useState<{ lat: number; lon: number } | null>(null)
  const [status, setStatus]           = useState<'idle' | 'loading' | 'success' | 'error'>('idle')
  const [message, setMessage]         = useState('')
  const [locLoading, setLocLoading]   = useState(false)

  const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  const detectLocation = () => {
    if (!navigator.geolocation) return
    setLocLoading(true)
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const { latitude, longitude } = pos.coords
        setCoords({ lat: latitude, lon: longitude })
        try {
          const res  = await fetch(`${API}/api/weather/current?lat=${latitude}&lon=${longitude}`)
          const data = await res.json()
          if (data.location) {
            setLocationName(`${data.location.name}, ${data.location.country}`)
          } else {
            setLocationName(`${latitude.toFixed(3)}, ${longitude.toFixed(3)}`)
          }
        } catch {
          setLocationName(`${latitude.toFixed(3)}, ${longitude.toFixed(3)}`)
        }
        setLocLoading(false)
      },
      () => setLocLoading(false)
    )
  }

  const handleSubscribe = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!phone.trim()) { setMessage('Please enter your WhatsApp number with country code.'); setStatus('error'); return }
    setStatus('loading')
    try {
      const res = await fetch(`${API}/api/alerts/subscribe`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone_number: phone,
          latitude:      coords?.lat,
          longitude:     coords?.lon,
          location_name: locationName,
          risk_threshold: threshold
        })
      })
      const data = await res.json()
      if (data.success) {
        setStatus('success')
      } else {
        setStatus('error')
        setMessage(data.detail || 'Subscription failed. Please try again.')
      }
    } catch {
      setStatus('error')
      setMessage('Cannot connect to server. Is the backend running?')
    }
  }

  const riskLabel = (t: number) => {
    if (t >= 75) return { label: 'Critical Only',  color: '#ef4444' }
    if (t >= 55) return { label: 'High & Above',   color: '#f97316' }
    if (t >= 35) return { label: 'Moderate & Up',  color: '#eab308' }
    return            { label: 'Very Sensitive',   color: '#22c55e' }
  }
  const rl = riskLabel(threshold)

  return (
    <div className="page alerts-page">
      <div className="container">

        {/* Header */}
        <div className="page-header">
          <h1>WhatsApp <span className="gradient-text">Flood Alerts</span></h1>
          <p>Get instant flood warnings directly on WhatsApp — no app, no sign-up, completely free.</p>
        </div>

        {/* ── Step 0: Sandbox join banner — MUST be seen before anything else ── */}
        <div style={{
          background: 'linear-gradient(135deg, rgba(37,211,102,0.12), rgba(37,211,102,0.04))',
          border: '1.5px solid rgba(37,211,102,0.4)',
          borderRadius: 14, padding: '1.2rem 1.5rem', marginBottom: '1.5rem',
          display: 'flex', gap: '1rem', alignItems: 'flex-start'
        }}>
          <span style={{ fontSize: '2rem', lineHeight: 1 }}>📌</span>
          <div>
            <p style={{ fontWeight: 700, fontSize: '1rem', margin: '0 0 6px', color: '#25D366' }}>
              Step 0 — Activate the WhatsApp Sandbox first (required)
            </p>
            <p style={{ margin: '0 0 10px', color: '#94a3b8', fontSize: '0.88rem', lineHeight: 1.5 }}>
              This bot runs on Twilio Sandbox. Before any message works, you must send exactly this phrase to {BOT_NUMBER}:
            </p>
            <div style={{
              background: '#075E54', borderRadius: '0px 8px 8px 8px',
              padding: '8px 14px', fontFamily: 'monospace', fontSize: '1.1rem',
              color: '#ffffff', marginBottom: 12, display: 'inline-block', boxShadow: '0 1px 0.5px rgba(0,0,0,0.13)'
            }}>
              join young-except
            </div>
            <br />
            <a href={WA_JOIN_LINK} target="_blank" rel="noopener noreferrer"
              style={{
                display: 'inline-flex', alignItems: 'center', gap: 8,
                background: '#25D366', color: '#fff', borderRadius: 8,
                padding: '8px 18px', fontWeight: 600, fontSize: '0.9rem',
                textDecoration: 'none'
              }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
              Tap to send "join young-except" on WhatsApp
            </a>
            <p style={{ margin: '8px 0 0', fontSize: '0.75rem', color: '#64748b' }}>
              ⚠️ You only need to do this once. After joining, type any city name to get a flood report.
            </p>
          </div>
        </div>

        <div className="alerts-layout">

          {/* ── Left: Subscription Form ── */}
          <div className="card sub-form-card">
            <h3>
              <svg width="22" height="22" viewBox="0 0 24 24" fill="#25D366" style={{ marginRight: 8, verticalAlign: 'middle' }}>
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
              </svg>
              Subscribe for Free Alerts
            </h3>
            <p className="card-desc">We check your location every 30 minutes and alert you the moment risk rises.</p>

            {status === 'success' ? (
              <div className="success-state">
                <div className="success-icon-big">✅</div>
                <h3>You're subscribed!</h3>
                <p>You'll receive WhatsApp alerts when flood risk exceeds <strong>{threshold}%</strong> near <em>{locationName || 'your saved location'}</em>.</p>
                <div className="activation-box">
                  <p><strong>📌 Step 1 — Join the sandbox (do this first):</strong></p>
                  <p style={{fontSize:'0.85rem',color:'#94a3b8',marginBottom:8}}>Send exactly this to {BOT_NUMBER}:</p>
                  <div style={{
                    background: '#075E54', borderRadius: '0px 8px 8px 8px',
                    padding: '8px 14px', fontFamily: 'monospace', fontSize: '1.1rem',
                    color: '#ffffff', marginBottom: 12, display: 'inline-block', boxShadow: '0 1px 0.5px rgba(0,0,0,0.13)'
                  }}>join young-except</div>
                  <br />
                  <a href={WA_JOIN_LINK} target="_blank" rel="noopener noreferrer" className="btn btn-whatsapp wa-activate-btn" id="wa-join-btn">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
                    Tap to join sandbox on WhatsApp
                  </a>
                  <p style={{margin:'12px 0 4px'}}><strong>📩 Step 2 — Then say hi:</strong></p>
                  <a href={WA_HI_LINK} target="_blank" rel="noopener noreferrer" className="btn btn-outline wa-activate-btn" id="wa-activate-btn">
                    Open WhatsApp &amp; Send "hi"
                  </a>
                </div>
              </div>
            ) : (
              <form className="sub-form" onSubmit={handleSubscribe}>
                {/* Phone */}
                <div className="form-field">
                  <label htmlFor="phone-input">WhatsApp Number <span className="req">*</span></label>
                  <div className="input-hint">Include your country code, e.g. +91 for India</div>
                  <input
                    id="phone-input"
                    type="tel"
                    className="input"
                    placeholder="+91 98765 43210"
                    value={phone}
                    onChange={e => setPhone(e.target.value)}
                  />
                </div>

                {/* Location */}
                <div className="form-field">
                  <label>Your Location</label>
                  <div className="input-hint">We monitor this location every 30 minutes</div>
                  <div className="loc-row">
                    <input
                      type="text"
                      className="input"
                      value={locationName}
                      onChange={e => setLocationName(e.target.value)}
                      placeholder="Type city or click detect..."
                    />
                    <button
                      type="button"
                      className="btn btn-outline detect-btn"
                      id="detect-loc-btn"
                      onClick={detectLocation}
                      disabled={locLoading}
                    >
                      {locLoading ? '...' : '📍 Detect'}
                    </button>
                  </div>
                  {coords && <p className="loc-confirmed">✅ Coordinates saved: {coords.lat.toFixed(3)}, {coords.lon.toFixed(3)}</p>}
                </div>

                {/* Threshold */}
                <div className="form-field">
                  <label htmlFor="threshold-slider">
                    Alert threshold: &nbsp;
                    <span className="threshold-badge" style={{ background: rl.color }}>{threshold}% — {rl.label}</span>
                  </label>
                  <div className="input-hint">You'll only get a message when risk is at or above this level</div>
                  <input
                    id="threshold-slider"
                    type="range"
                    min={20} max={90} step={5}
                    value={threshold}
                    onChange={e => setThreshold(Number(e.target.value))}
                    className="slider"
                  />
                  <div className="slider-labels">
                    <span>Very Sensitive (20%)</span>
                    <span>Critical Only (90%)</span>
                  </div>
                </div>

                {status === 'error' && <div className="form-error">⚠️ {message}</div>}

                <button
                  type="submit"
                  id="subscribe-btn"
                  className="btn btn-primary sub-btn"
                  disabled={status === 'loading'}
                >
                  {status === 'loading' ? '⏳ Subscribing...' : '🔔 Subscribe to Alerts'}
                </button>
              </form>
            )}
          </div>

          {/* ── Right column ── */}
          <div className="alerts-right">

            {/* Quick Start */}
            <div className="card wa-quick-card">
              <h4>🚀 Quick Start — Chat with the Bot Now</h4>
              <p>No subscription needed. Open WhatsApp and type any city name to get an instant flood risk report.</p>
              <a href={WA_HI_LINK} target="_blank" rel="noopener noreferrer" className="btn btn-whatsapp wa-full-btn" id="wa-quick-btn">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
                Open WhatsApp Bot
              </a>
            </div>

            {/* How it works steps */}
            <div className="steps-list">
              {[
                { n: '0', title: 'Join the sandbox first', desc: `Send "join young-except" to ${BOT_NUMBER} on WhatsApp. You only need to do this once.`, highlight: true },
                { n: '1', title: 'Subscribe above', desc: 'Enter your WhatsApp number and set your preferred risk threshold.' },
                { n: '2', title: 'Say hi to the bot', desc: `After joining, send "hi" to ${BOT_NUMBER} to activate your subscription.` },
                { n: '3', title: 'Share your location', desc: 'Type any city name or share your GPS location for an instant report.' },
                { n: '4', title: 'Receive auto-alerts', desc: 'We check every 30 minutes and send you a message when risk exceeds your threshold.' },
              ].map(s => (
                <div key={s.n} className="card step-card">
                  <div className="step-num">{s.n}</div>
                  <div>
                    <h4>{s.title}</h4>
                    <p>{s.desc}</p>
                  </div>
                </div>
              ))}
            </div>

            {/* Bot commands */}
            <div className="card commands-card">
              <h4>💬 WhatsApp Bot Commands</h4>
              <div className="commands-list">
                {[
                  ['hi',              'Start the bot & see the menu'],
                  ['Mumbai',          'Get risk for any city'],
                  ['📍 Share Location','Get risk for your exact GPS spot'],
                  ['help',            'Show all commands'],
                  ['unsubscribe',     'Stop receiving auto-alerts'],
                ].map(([cmd, desc]) => (
                  <div key={cmd} className="cmd-row">
                    <code>{cmd}</code>
                    <span>{desc}</span>
                  </div>
                ))}
              </div>
            </div>

          </div>
        </div>
      </div>
    </div>
  )
}

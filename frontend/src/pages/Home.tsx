import { Link } from 'react-router-dom'
import './Home.css'

const FEATURES = [
  { icon: '📍', title: 'Your Location, Instantly', desc: 'One tap to get real-time flood risk for exactly where you are. No sign-up needed.' },
  { icon: '🤖', title: 'AI-Powered Analysis', desc: 'Our Gemini AI analyses rainfall, humidity, wind speed and gives you a clear risk score.' },
  { icon: '📱', title: 'WhatsApp Alerts', desc: 'Get flood warnings directly on WhatsApp. Share your location in the chat for instant results.' },
  { icon: '🌍', title: 'Works Everywhere', desc: 'Search any city in the world. Works perfectly on mobile and desktop, 24/7.' },
]

const STATS = [
  { value: '24/7', label: 'Live Monitoring' },
  { value: 'Global', label: 'Coverage' },
  { value: '0', label: 'Cost to You' },
  { value: '<5s', label: 'Response Time' },
]

const HOW_IT_WORKS = [
  { step: '1', title: 'Enter Your Location', desc: 'Type any city name or tap "Detect My Location" for instant results.' },
  { step: '2', title: 'AI Analyses the Risk', desc: 'Our AI checks live rainfall, humidity, wind speed and river data in real time.' },
  { step: '3', title: 'Get Your Risk Report', desc: 'See a clear risk score, safety advice and 24-hour weather forecast.' },
  { step: '4', title: 'Stay Alerted', desc: 'Subscribe to WhatsApp alerts and get notified automatically when risk rises.' },
]

export default function Home() {
  return (
    <div className="home-page">

      {/* ── HERO ── */}
      <section className="hero-section">
        <div className="container hero-container">
          <div className="hero-content animate-fadeInUp">
            <div className="hero-tag">🌊 AI-Powered Flood Safety</div>
            <h1 className="hero-title">
              Know Your Flood Risk<br />
              <span className="gradient-text">Before It's Too Late</span>
            </h1>
            <p className="hero-desc">
              FloodSenseAI gives you real-time flood risk information for any location -
              powered by artificial intelligence. Free, instant, and available on WhatsApp.
            </p>
            <div className="hero-actions">
              <Link to="/check-risk" className="btn btn-primary hero-btn" id="check-risk-hero-btn">
                🔍 Check Flood Risk Now
              </Link>
              <a
                href="https://wa.me/14155238886?text=hi"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-whatsapp hero-btn"
                id="whatsapp-hero-btn"
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" /></svg>
                Connect on WhatsApp
              </a>
            </div>
            <p className="hero-note">✅ No sign-up · ✅ Completely free · ✅ Works on any device</p>
          </div>
          <div className="hero-image-wrap animate-float">
            <img src="/hero.png" alt="FloodSenseAI flood risk monitoring" className="hero-img" />
          </div>
        </div>
      </section>

      {/* ── STATS ── */}
      <section className="stats-strip">
        <div className="container stats-grid">
          {STATS.map((s, i) => (
            <div key={i} className="stat-item">
              <div className="stat-value gradient-text">{s.value}</div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── FEATURES ── */}
      <section className="features-section section">
        <div className="container">
          <div className="section-header">
            <h2>Everything You Need to Stay Safe</h2>
            <p>FloodSenseAI brings advanced flood monitoring technology to everyone, no technical knowledge required.</p>
          </div>
          <div className="features-grid">
            {FEATURES.map((f, i) => (
              <div key={i} className="card feature-card">
                <div className="feature-icon">{f.icon}</div>
                <h3 className="feature-title">{f.title}</h3>
                <p className="feature-desc">{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── HOW IT WORKS ── */}
      <section className="how-section section">
        <div className="container">
          <div className="section-header">
            <h2>How It Works</h2>
            <p>Get your flood risk report in under 5 seconds - it's that simple.</p>
          </div>
          <div className="how-grid">
            {HOW_IT_WORKS.map((h, i) => (
              <div key={i} className="how-card">
                <div className="how-step">{h.step}</div>
                <h3>{h.title}</h3>
                <p>{h.desc}</p>
                {i < HOW_IT_WORKS.length - 1 && <div className="how-arrow">→</div>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── WHATSAPP CTA ── */}
      <section className="wa-section section">
        <div className="container">
          <div className="wa-card card">
            <div className="wa-icon">
              <svg width="1em" height="1em" viewBox="0 0 24 24" fill="#25D366"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" /></svg>
            </div>
            <div className="wa-content">
              <h2>Get Flood Alerts on WhatsApp</h2>
              <p>
                Our WhatsApp bot works 24/7. Send your location and get an instant flood risk
                report. Subscribe for automatic alerts when risk rises in your area.
              </p>
              <div className="wa-steps">
                <div className="wa-step"><span className="wa-num">1</span>Click the button below</div>
                <div className="wa-step"><span className="wa-num">2</span>Send <strong>"hi"</strong> to start the bot</div>
                <div className="wa-step"><span className="wa-num">3</span>Share your location for instant results</div>
              </div>
              <a
                href="https://wa.me/14155238886?text=hi"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-whatsapp wa-cta-btn"
                id="whatsapp-cta-btn"
              >
                <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z" /></svg>
                Open WhatsApp Bot
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ── ABOUT ── */}
      <section className="about-section section">
        <div className="container about-grid">
          <div className="about-text">
            <div className="about-tag">About FloodSenseAI</div>
            <h2>AI That Protects Communities</h2>
            <p>
              FloodSenseAI was built with one mission - to make flood safety information
              accessible to every person, in every community, for free.
            </p>
            <p style={{ marginTop: '12px' }}>
              We combine live weather data, artificial intelligence, and instant messaging
              to deliver flood risk warnings before disaster strikes - aligned with
              <strong> UN SDG 13 (Climate Action)</strong> and <strong>SDG 11 (Sustainable Cities)</strong>.
            </p>
            <div className="sdg-badges">
              <span className="sdg-badge">🌍 SDG 13 - Climate Action</span>
              <span className="sdg-badge">🏙️ SDG 11 - Sustainable Cities</span>
              <span className="sdg-badge">❤️ SDG 3 - Good Health</span>
            </div>
          </div>
          <div className="about-cards">
            <div className="card about-stat-card">
              <div className="about-stat-icon">🤖</div>
              <h4>Google Gemini AI</h4>
              <p>Powers our intelligent flood assistant with real-time knowledge</p>
            </div>
            <div className="card about-stat-card">
              <div className="about-stat-icon">⚖️</div>
              <h4>Responsible AI</h4>
              <p>Fair, transparent, and privacy-respecting - no personal data stored</p>
            </div>
            <div className="card about-stat-card">
              <div className="about-stat-icon">🌐</div>
              <h4>Open Access</h4>
              <p>No login, no fees, no barriers - anyone can use FloodSenseAI</p>
            </div>
            <div className="card about-stat-card">
              <div className="about-stat-icon">📡</div>
              <h4>Real-Time Data</h4>
              <p>Live weather APIs updated every few minutes from around the world</p>
            </div>
          </div>
        </div>
      </section>

      {/* ── FOOTER CTA ── */}
      <section className="footer-cta-section">
        <div className="container">
          <div className="footer-cta-content">
            <h2>Ready to Check Your Risk?</h2>
            <p>It takes less than 5 seconds. No account needed.</p>
            <Link to="/check-risk" className="btn btn-white" id="footer-check-btn">
              🔍 Check Flood Risk Now
            </Link>
          </div>
        </div>
      </section>

    </div>
  )
}

import { useState, useEffect, useCallback, useRef } from 'react'
import { Link } from 'react-router-dom'
import FloodMap from '../components/FloodMap/FloodMap'
import './CheckRisk.css'

interface WeatherData {
  location: { name: string; country: string; lat: number; lon: number }
  current: {
    temperature: number; feels_like: number; humidity: number
    rainfall_1h: number; rainfall_3h: number
    wind_speed: number; description: string; icon: string
    pressure: number; visibility: number
    data_timestamp: number  // Unix epoch from OWM — for freshness display
  }
  forecast: Array<{ time: string; temperature: number; rainfall: number; description: string; icon: string }>
}
interface RiskData { risk_score: number; risk_level: string; color: string; advice: string; infrastructure_multiplier?: number; infrastructure_quality?: string }

export default function CheckRisk() {
  const [weather, setWeather] = useState<WeatherData | null>(null)
  const [risk, setRisk] = useState<RiskData | null>(null)
  const [loading, setLoading] = useState(false)
  const [locationName, setLocationName] = useState('')
  const [error, setError] = useState('')
  const [searchCity, setSearchCity] = useState('')
  const [coords, setCoords] = useState<{ lat: number; lon: number } | null>(null)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const refreshTimer = useRef<ReturnType<typeof setInterval> | null>(null)

  const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  const fetchForCoords = useCallback(async (lat: number, lon: number) => {
    setLoading(true); setError('')
    try {
      const weatherRes = await fetch(`${API}/api/weather/current?lat=${lat}&lon=${lon}`)
      const weatherData = await weatherRes.json()
      if (!weatherRes.ok) {
        setError(weatherData.detail || 'Failed to fetch weather data. Check API keys.')
        setLoading(false)
        return
      }
      setWeather(weatherData)
      setCoords({ lat, lon })
      setLocationName(`${weatherData.location.name}, ${weatherData.location.country}`)
      const riskRes = await fetch(
        `${API}/api/risk/predict?lat=${lat}&lon=${lon}` +
        `&rainfall=${weatherData.current.rainfall_3h}&humidity=${weatherData.current.humidity}` +
        `&temperature=${weatherData.current.temperature}&wind_speed=${weatherData.current.wind_speed}` +
        `&location_name=${encodeURIComponent(weatherData.location.name)}`
      )
      setRisk(await riskRes.json())
      setLastUpdated(new Date())
    } catch { setError('Could not connect. Make sure the backend server is running.') }
    finally { setLoading(false) }
  }, [API])

  // Auto-refresh every 10 minutes when coords are set
  useEffect(() => {
    if (!coords) return
    if (refreshTimer.current) clearInterval(refreshTimer.current)
    refreshTimer.current = setInterval(() => {
      fetchForCoords(coords.lat, coords.lon)
    }, 10 * 60 * 1000)
    return () => { if (refreshTimer.current) clearInterval(refreshTimer.current) }
  }, [coords, fetchForCoords])

  const handleMyLocation = () => {
    if (!navigator.geolocation) { setError('Geolocation is not supported by your browser.'); return }
    setLoading(true)
    navigator.geolocation.getCurrentPosition(
      pos => fetchForCoords(pos.coords.latitude, pos.coords.longitude),
      () => { setError('Location access denied. Please allow location access or search by city name.'); setLoading(false) }
    )
  }

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!searchCity.trim()) return
    setLoading(true); setError('')
    try {
      const res = await fetch(`${API}/api/weather/city?city=${encodeURIComponent(searchCity)}`)
      const data = await res.json()
      if (!res.ok || data.error) { 
        setError(data.detail || data.error || `City not found: "${searchCity}"`)
        setLoading(false)
        return 
      }
      setWeather(data)
      setCoords({ lat: data.location.lat, lon: data.location.lon })
      setLocationName(`${data.location.name}, ${data.location.country}`)
      const riskRes = await fetch(
        `${API}/api/risk/predict?lat=${data.location.lat}&lon=${data.location.lon}` +
        `&rainfall=${data.current.rainfall_3h}&humidity=${data.current.humidity}` +
        `&temperature=${data.current.temperature}&wind_speed=${data.current.wind_speed}` +
        `&location_name=${encodeURIComponent(data.location.name)}`
      )
      setRisk(await riskRes.json())
      setLastUpdated(new Date())
    } catch { setError('Search failed. Please check your connection.') }
    finally { setLoading(false) }
  }

  const riskClass = (level: string) => level?.toLowerCase() || 'low'

  return (
    <div className="page check-risk-page">
      <div className="container">

        {/* Page Header */}
        <div className="page-header">
          <h1>Check <span className="gradient-text">Flood Risk</span></h1>
          <p>Enter a city name or use your current location to get an instant flood risk report.</p>
        </div>

        {/* Search Card */}
        <div className="card search-card">
          <form className="search-form" onSubmit={handleSearch}>
            <div className="search-input-wrap">
              <span className="search-icon-prefix">🔍</span>
              <input
                id="city-search-input"
                type="text"
                className="input search-field"
                placeholder="Search a city - e.g. Mumbai, Chennai, Delhi..."
                value={searchCity}
                onChange={e => setSearchCity(e.target.value)}
              />
            </div>
            <button type="submit" className="btn btn-primary" id="search-submit-btn" disabled={loading}>
              {loading ? 'Searching...' : 'Search'}
            </button>
            <div className="divider-or"><span>or</span></div>
            <button type="button" className="btn btn-outline detect-btn" id="detect-location-btn" onClick={handleMyLocation} disabled={loading}>
              📍 Detect My Location
            </button>
          </form>
        </div>

        {error && <div className="error-msg">⚠️ {error}</div>}

        {loading && (
          <div className="loading-card card">
            <div className="loading-icon">🌊</div>
            <p>Analysing flood risk for your location...</p>
            <div className="loading-bar"><div className="loading-fill"></div></div>
          </div>
        )}

        {!weather && !loading && (
          <div className="empty-card card">
            <img src="/check_risk_hero.png" alt="Flood safety" className="empty-img" />
            <h3>Enter a location above to get started</h3>
            <p>We'll show you live weather data, a flood risk score, and a 24-hour forecast.</p>
          </div>
        )}

        {weather && risk && !loading && (
          <div className="results-section">

            {/* Location Title */}
            <div className="results-header">
              <h2 className="results-location">📍 {locationName}</h2>
              <span className={`badge badge-${riskClass(risk.risk_level)}`}>{risk.risk_level} RISK</span>
              {lastUpdated && (
                <span className="last-updated">🔄 Updated {lastUpdated.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} · auto-refreshes every 10 min</span>
              )}
              {weather.current.data_timestamp > 0 && (() => {
                // eslint-disable-next-line react-hooks/purity
                const ageMin = Math.round((Date.now() / 1000 - weather.current.data_timestamp) / 60)
                return (
                  <span style={{
                    fontSize: '0.72rem', color: ageMin > 30 ? '#f97316' : '#64748b',
                    background: 'rgba(255,255,255,0.05)', borderRadius: 6,
                    padding: '2px 8px', border: '1px solid #333'
                  }}>
                    📡 OWM data: {ageMin <= 1 ? 'just now' : `${ageMin} min ago`}
                  </span>
                )
              })()}
            </div>

            {/* Main Results Grid */}
            <div className="results-grid">

              {/* Risk Score */}
              <div className={`card risk-main-card risk-border-${riskClass(risk.risk_level)}`}>
                <p className="risk-card-label">Flood Risk Score</p>
                <div className="risk-score-big" style={{ color: risk.color }}>{risk.risk_score.toFixed(0)}%</div>
                <div className="risk-bar-track">
                  <div className="risk-bar-fill" style={{ width: `${risk.risk_score}%`, background: risk.color }}></div>
                </div>
                <p className="risk-advice-text">{risk.advice}</p>
                <Link to="/assistant" className="btn btn-primary ask-ai-btn">💬 Ask AI for Advice</Link>
              </div>

              {/* Weather Stats */}
              <div className="weather-stats-col">
                <div className="card weather-stat">
                  <span className="ws-icon">🌡️</span>
                  <div><p className="ws-label">Temperature</p><p className="ws-val">{weather.current.temperature.toFixed(1)}°C</p><p className="ws-sub">Feels like {weather.current.feels_like.toFixed(1)}°C</p></div>
                </div>
                <div className="card weather-stat">
                  <span className="ws-icon">🌧️</span>
                  <div><p className="ws-label">Rainfall</p><p className="ws-val">{weather.current.rainfall_3h.toFixed(1)} mm</p><p className="ws-sub">Last 3 hours</p></div>
                </div>
                <div className="card weather-stat">
                  <span className="ws-icon">💧</span>
                  <div><p className="ws-label">Humidity</p><p className="ws-val">{weather.current.humidity}%</p><p className="ws-sub">Relative humidity</p></div>
                </div>
                <div className="card weather-stat">
                  <span className="ws-icon">💨</span>
                  <div><p className="ws-label">Wind Speed</p><p className="ws-val">{weather.current.wind_speed.toFixed(1)} m/s</p><p className="ws-sub">{weather.current.description}</p></div>
                </div>
                <div className="card weather-stat">
                  <span className="ws-icon">👁️</span>
                  <div><p className="ws-label">Visibility</p><p className="ws-val">{(weather.current.visibility/1000).toFixed(1)} km</p><p className="ws-sub">Pressure: {weather.current.pressure} hPa</p></div>
                </div>
              </div>
            </div>

            {/* 24h Forecast */}
            {weather.forecast.length > 0 && (
              <div className="card forecast-card">
                <h3 className="forecast-title">⏰ 24-Hour Weather Forecast</h3>
                <div className="forecast-row">
                  {weather.forecast.map((item, i) => (
                    <div key={i} className="forecast-chip">
                      <p className="fc-time">{new Date(item.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                      <img src={`https://openweathermap.org/img/wn/${item.icon}.png`} alt={item.description} className="fc-icon" />
                      <p className="fc-temp">{item.temperature.toFixed(0)}°C</p>
                      <p className="fc-rain">🌧 {item.rainfall.toFixed(1)}mm</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Interactive Flood Map */}
            {coords && (
              <FloodMap
                lat={coords.lat}
                lon={coords.lon}
                locationName={locationName}
                riskScore={risk.risk_score}
                riskLevel={risk.risk_level}
                riskColor={risk.color}
                infrastructureMultiplier={risk.infrastructure_multiplier}
                infrastructureQuality={risk.infrastructure_quality}
              />
            )}

            <div className="results-actions">
              <Link to="/alerts" className="btn btn-outline">🔔 Set Up WhatsApp Alerts</Link>
              <Link to="/assistant" className="btn btn-primary">💬 Chat with AI Assistant</Link>
              <a href="https://wa.me/14155238886?text=hi" target="_blank" rel="noopener noreferrer" className="btn btn-whatsapp">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
                Get on WhatsApp
              </a>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

import { useEffect, useState } from 'react'
import { MapContainer, TileLayer } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import './GlobalMap.css'

export default function GlobalMap() {
  const [apiKey, setApiKey] = useState<string>('')
  const [error, setError] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  const API = window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'https://mark-floodsenseai.onrender.com'

  useEffect(() => {
    // Fetch the OpenWeather API key from our backend config
    const fetchConfig = async () => {
      try {
        const res = await fetch(`${API}/api/weather/config`)
        const data = await res.json()
        if (data.openweather_key) {
          setApiKey(data.openweather_key)
        } else {
          setError(true)
        }
      } catch (err) {
        setError(true)
      }
    }

    fetchConfig()

    // Auto-refresh the timestamp every 10 minutes (OpenWeather updates tiles roughly every 10-30 min)
    const interval = setInterval(() => {
      setLastUpdate(new Date())
    }, 10 * 60 * 1000)

    return () => clearInterval(interval)
  }, [API])

  // Render a nice timestamp
  const ageMins = Math.floor((new Date().getTime() - lastUpdate.getTime()) / 60000)
  const timeText = ageMins === 0 ? 'just now' : `${ageMins} min ago`

  return (
    <div className="global-map-page">
      <div className="map-container-full">
        {/* Overlay Panel */}
        <div className="map-overlay-panel">
          <h1>🌍 Global Live Radar</h1>
          <p>Real-time precipitation and rainfall intensity across the entire world, down to street-level neighborhoods.</p>
          
          <div className="map-legend">
            <div className="legend-item"><div className="legend-color color-extreme"></div> Extreme / Hail (Purple)</div>
            <div className="legend-item"><div className="legend-color color-heavy"></div> Heavy Rain (Red)</div>
            <div className="legend-item"><div className="legend-color color-mod"></div> Moderate Rain (Yellow)</div>
            <div className="legend-item"><div className="legend-color color-light"></div> Light Rain (Green)</div>
          </div>

          <div className="timestamp-badge">
            🔄 Live satellite feed — updated {timeText}
          </div>
        </div>

        {/* Map */}
        {apiKey ? (
          <MapContainer 
            center={[20, 0]} 
            zoom={3} 
            style={{ width: '100%', height: '100%', background: '#0f172a' }}
            zoomControl={false} // Hide default to place it better if needed, or keep default
          >
            {/* Dark theme basemap (CartoDB Dark Matter) */}
            <TileLayer
              attribution='&copy; <a href="https://carto.com/">CartoDB</a>'
              url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />
            
            {/* OpenWeatherMap Precipitation Layer */}
            <TileLayer
              attribution='&copy; <a href="https://openweathermap.org/">OpenWeather</a>'
              url={`https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=${apiKey}`}
              opacity={0.85}
            />
          </MapContainer>
        ) : error ? (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#ef4444' }}>
            Failed to load weather radar configuration.
          </div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: '#94a3b8' }}>
            Connecting to weather satellites...
          </div>
        )}
      </div>
    </div>
  )
}

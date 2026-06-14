import { useEffect, useRef, useState, useCallback } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import './GlobalMap.css'

// Token is stored in Vercel environment variable VITE_MAPBOX_TOKEN
const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN as string
mapboxgl.accessToken = MAPBOX_TOKEN

export default function GlobalMap() {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<mapboxgl.Map | null>(null)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())
  const [mapLoaded, setMapLoaded] = useState(false)

  const API = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://mark-floodsenseai.onrender.com'

  const addWeatherLayer = useCallback(async (mapInstance: mapboxgl.Map) => {
    try {
      const res = await fetch(`${API}/api/weather/config`)
      const data = await res.json()
      const owmKey = data.openweather_key
      if (!owmKey) return

      // Add OpenWeatherMap precipitation as a raster source
      mapInstance.addSource('owm-precipitation', {
        type: 'raster',
        tiles: [`https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=${owmKey}`],
        tileSize: 256,
        attribution: '© OpenWeatherMap',
        maxzoom: 10,
      })

      mapInstance.addLayer({
        id: 'precipitation-layer',
        type: 'raster',
        source: 'owm-precipitation',
        paint: {
          'raster-opacity': 0.80,
          'raster-fade-duration': 300,
        },
      })
    } catch (err) {
      console.error('Failed to load weather layer:', err)
    }
  }, [API])

  useEffect(() => {
    if (map.current || !mapContainer.current) return

    const mapInstance = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/light-v11',
      center: [20, 20],
      zoom: 3,
      minZoom: 2,
      projection: 'mercator',
    })

    mapInstance.addControl(new mapboxgl.NavigationControl(), 'bottom-right')
    mapInstance.addControl(new mapboxgl.ScaleControl({ maxWidth: 120, unit: 'metric' }), 'bottom-left')

    mapInstance.on('load', () => {
      setMapLoaded(true)
      addWeatherLayer(mapInstance)
    })

    map.current = mapInstance

    // Refresh weather layer every 10 minutes
    const interval = setInterval(() => {
      setLastUpdate(new Date())
      if (map.current && map.current.isStyleLoaded()) {
        // Remove and re-add to force fresh tiles
        if (map.current.getLayer('precipitation-layer')) {
          map.current.removeLayer('precipitation-layer')
        }
        if (map.current.getSource('owm-precipitation')) {
          map.current.removeSource('owm-precipitation')
        }
        addWeatherLayer(map.current)
      }
    }, 10 * 60 * 1000)

    return () => {
      clearInterval(interval)
      mapInstance.remove()
      map.current = null
    }
  }, [addWeatherLayer])

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
            <div className="legend-item"><div className="legend-color color-light"></div> Light Rain (Blue)</div>
          </div>

          <div className="timestamp-badge">
            🔄 Live satellite feed — updated {timeText}
          </div>

          {!mapLoaded && (
            <div style={{ marginTop: 12, color: '#94a3b8', fontSize: '0.78rem' }}>
              ⏳ Loading map...
            </div>
          )}
        </div>

        {/* Mapbox Map */}
        <div ref={mapContainer} style={{ width: '100%', height: '100%' }} />
      </div>
    </div>
  )
}

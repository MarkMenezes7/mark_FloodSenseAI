import { useEffect, useRef, useCallback } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import './FloodMap.css'

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN as string
mapboxgl.accessToken = MAPBOX_TOKEN

interface FloodMapProps {
  lat: number
  lon: number
  locationName: string
  riskScore: number
  riskLevel: string
  riskColor: string
  infrastructureMultiplier?: number
  infrastructureQuality?: string
}

export default function FloodMap({
  lat, lon, locationName, riskScore, riskLevel, riskColor,
  infrastructureMultiplier, infrastructureQuality,
}: FloodMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<mapboxgl.Map | null>(null)
  const markerRef = useRef<mapboxgl.Marker | null>(null)
  const popupRef = useRef<mapboxgl.Popup | null>(null)

  const API = window.location.hostname === 'localhost'
    ? 'http://localhost:8000'
    : 'https://mark-floodsenseai.onrender.com'

  const addWeatherLayer = useCallback(async (mapInstance: mapboxgl.Map) => {
    try {
      const res = await fetch(`${API}/api/weather/config`)
      const data = await res.json()
      const owmKey = data.openweather_key
      if (!owmKey) return

      if (!mapInstance.getSource('owm-precipitation')) {
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
          paint: { 'raster-opacity': 0.75, 'raster-fade-duration': 300 },
        })
      }
    } catch (err) {
      console.error('Failed to load weather layer:', err)
    }
  }, [API])

  // Build the risk popup HTML
  const buildPopupHTML = () => {
    const infraLine = infrastructureQuality
      ? `<div class="fm-row"><span class="fm-label">🏗️ Infrastructure</span><span class="fm-val" style="color:#f97316">${infrastructureQuality.replace(/_/g, ' ')}</span></div>`
      : ''
    const multLine = infrastructureMultiplier
      ? `<div class="fm-row"><span class="fm-label">⚡ Risk multiplier</span><span class="fm-val">${infrastructureMultiplier.toFixed(1)}×</span></div>`
      : ''
    return `
      <div class="fm-card">
        <div class="fm-title">📍 ${locationName}</div>
        <div class="fm-score" style="color:${riskColor}">${riskScore.toFixed(0)}% <span class="fm-level">${riskLevel} RISK</span></div>
        <div class="fm-divider"></div>
        ${infraLine}
        ${multLine}
        <div class="fm-tip">Click anywhere on map for live weather</div>
      </div>
    `
  }

  // Handle any map click → show live weather popup
  const fetchWeatherPopup = useCallback(async (
    mapInstance: mapboxgl.Map,
    lngLat: mapboxgl.LngLat
  ) => {
    const clickPopup = new mapboxgl.Popup({ closeButton: true, maxWidth: '260px', className: 'wx-popup' })
      .setLngLat(lngLat)
      .setHTML(`<div class="wx-loading">⏳ Fetching weather...</div>`)
      .addTo(mapInstance)

    try {
      const res = await fetch(`${API}/api/weather/current?lat=${lngLat.lat.toFixed(4)}&lon=${lngLat.lng.toFixed(4)}`)
      const data = await res.json()
      const loc = data.location
      const cur = data.current
      if (!cur) { clickPopup.setHTML(`<div class="wx-error">❌ No data for this location</div>`); return }

      const rain = cur.rainfall_1h ?? 0
      const rainLabel = rain === 0 ? 'None' : `${rain} mm/hr`
      const riskEmoji = rain > 10 ? '🔴' : rain > 2 ? '🟡' : '🟢'

      clickPopup.setHTML(`
        <div class="wx-card">
          <div class="wx-title">📍 ${loc?.name ?? 'Unknown'}, ${loc?.country ?? ''}</div>
          <div class="wx-grid">
            <div class="wx-row"><span class="wx-label">🌧️ Rainfall</span><span class="wx-val ${rain > 5 ? 'wx-danger' : ''}">${rainLabel} ${riskEmoji}</span></div>
            <div class="wx-row"><span class="wx-label">💧 Humidity</span><span class="wx-val">${cur.humidity}%</span></div>
            <div class="wx-row"><span class="wx-label">💨 Wind</span><span class="wx-val">${cur.wind_speed} m/s</span></div>
            <div class="wx-row"><span class="wx-label">🌡️ Temp</span><span class="wx-val">${cur.temperature}°C</span></div>
            <div class="wx-row"><span class="wx-label">☁️ Conditions</span><span class="wx-val">${cur.description ?? '-'}</span></div>
          </div>
          <div class="wx-coords">${lngLat.lat.toFixed(3)}°, ${lngLat.lng.toFixed(3)}°</div>
        </div>
      `)
    } catch {
      clickPopup.setHTML(`<div class="wx-error">❌ Failed to load weather data</div>`)
    }
  }, [API])

  // Init map once
  useEffect(() => {
    if (map.current || !mapContainer.current) return

    const mapInstance = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/light-v11',
      center: [lon, lat],
      zoom: 8,
      minZoom: 2,
      projection: 'mercator',
      renderWorldCopies: false,
    })

    mapInstance.addControl(new mapboxgl.NavigationControl(), 'bottom-right')
    mapInstance.addControl(new mapboxgl.ScaleControl({ maxWidth: 100, unit: 'metric' }), 'bottom-left')

    mapInstance.on('load', () => {
      addWeatherLayer(mapInstance)

      // Pulsing risk marker
      const el = document.createElement('div')
      el.className = 'fm-marker'
      el.style.borderColor = riskColor
      el.style.setProperty('--risk-color', riskColor)

      popupRef.current = new mapboxgl.Popup({
        offset: 20, closeButton: false, className: 'fm-popup', maxWidth: '280px',
      })
        .setHTML(buildPopupHTML())

      markerRef.current = new mapboxgl.Marker({ element: el, anchor: 'bottom' })
        .setLngLat([lon, lat])
        .setPopup(popupRef.current)
        .addTo(mapInstance)

      // Open popup by default
      markerRef.current.togglePopup()
    })

    mapInstance.on('click', (e) => {
      // Don't re-trigger if clicking the marker popup area
      fetchWeatherPopup(mapInstance, e.lngLat)
    })

    mapInstance.on('mousemove', () => {
      mapInstance.getCanvas().style.cursor = 'crosshair'
    })

    map.current = mapInstance

    return () => {
      mapInstance.remove()
      map.current = null
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // When location changes, fly to new coords and update marker
  useEffect(() => {
    if (!map.current) return
    map.current.flyTo({ center: [lon, lat], zoom: 9, speed: 1.4, curve: 1.2 })

    if (markerRef.current) {
      markerRef.current.setLngLat([lon, lat])
      const el = markerRef.current.getElement()
      el.style.borderColor = riskColor
      el.style.setProperty('--risk-color', riskColor)
    }

    if (popupRef.current) {
      popupRef.current.setLngLat([lon, lat]).setHTML(buildPopupHTML())
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lat, lon, riskScore, riskLevel, riskColor, locationName])

  return (
    <div className="flood-map-section">
      <div className="flood-map-header">
        <h3 className="flood-map-title">🗺️ Interactive Flood Risk Map</h3>
        <span className="flood-map-hint">💡 Click anywhere on the map for live weather data</span>
      </div>
      <div className="flood-map-wrapper">
        <div ref={mapContainer} className="flood-map-canvas" />
      </div>
    </div>
  )
}

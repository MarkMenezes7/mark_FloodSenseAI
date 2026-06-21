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
  // Weather data to show in the risk popup
  rainfall?: number
  humidity?: number
  windSpeed?: number
  temperature?: number
  weatherDescription?: string
}

export default function FloodMap({
  lat, lon, locationName, riskScore, riskLevel, riskColor,
  infrastructureMultiplier, infrastructureQuality,
  rainfall = 0, humidity = 0, windSpeed = 0, temperature = 0, weatherDescription = '',
}: FloodMapProps) {
  const mapContainer = useRef<HTMLDivElement>(null)
  const map = useRef<mapboxgl.Map | null>(null)
  const markerRef = useRef<mapboxgl.Marker | null>(null)
  const riskPopupRef = useRef<mapboxgl.Popup | null>(null)
  const clickPopupRef = useRef<mapboxgl.Popup | null>(null)

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

  // Build the FULL risk popup HTML — now includes all weather data
  const buildPopupHTML = (
    _lat: number, _lon: number,
    _locationName: string, _riskScore: number, _riskLevel: string, _riskColor: string,
    _rainfall: number, _humidity: number, _windSpeed: number, _temperature: number, _weatherDescription: string,
    _infraQuality?: string, _infraMultiplier?: number,
  ) => {
    const rainLabel = _rainfall === 0 ? 'None' : `${_rainfall.toFixed(1)} mm`
    const riskEmoji = _rainfall > 10 ? '🔴' : _rainfall > 2 ? '🟡' : '🟢'
    const rainColor = _rainfall > 5 ? '#ef4444' : '#0f172a'

    const infraLine = _infraQuality
      ? `<div class="fm-row"><span class="fm-label">🏗️ Infrastructure</span><span class="fm-val" style="color:#f97316">${_infraQuality.replace(/_/g, ' ')}</span></div>`
      : ''
    const multLine = _infraMultiplier
      ? `<div class="fm-row"><span class="fm-label">⚡ Risk multiplier</span><span class="fm-val">${_infraMultiplier.toFixed(1)}×</span></div>`
      : ''

    return `
      <div class="fm-card">
        <div class="fm-title">📍 ${_locationName}</div>
        <div class="fm-score" style="color:${_riskColor}">${_riskScore.toFixed(0)}% <span class="fm-level">${_riskLevel} RISK</span></div>
        <div class="fm-divider"></div>
        <div class="fm-row"><span class="fm-label">🌧️ Rainfall</span><span class="fm-val" style="color:${rainColor}">${rainLabel} ${riskEmoji}</span></div>
        <div class="fm-row"><span class="fm-label">💧 Humidity</span><span class="fm-val">${_humidity}%</span></div>
        <div class="fm-row"><span class="fm-label">💨 Wind</span><span class="fm-val">${_windSpeed.toFixed(1)} m/s</span></div>
        <div class="fm-row"><span class="fm-label">🌡️ Temp</span><span class="fm-val">${_temperature.toFixed(1)}°C</span></div>
        <div class="fm-row"><span class="fm-label">☁️ Conditions</span><span class="fm-val">${_weatherDescription || '-'}</span></div>
        ${infraLine}
        ${multLine}
        <div class="fm-tip">Click anywhere on map for another location's weather</div>
      </div>
    `
  }

  // Handle map click → show live weather popup for clicked spot (closes marker popup first)
  const fetchWeatherPopup = useCallback(async (
    mapInstance: mapboxgl.Map,
    lngLat: mapboxgl.LngLat
  ) => {
    // Close the risk marker popup so they don't stack
    if (riskPopupRef.current && riskPopupRef.current.isOpen()) {
      riskPopupRef.current.remove()
    }
    // Remove any previous click popup
    if (clickPopupRef.current) {
      clickPopupRef.current.remove()
    }

    const newPopup = new mapboxgl.Popup({ closeButton: true, maxWidth: '260px', className: 'wx-popup' })
      .setLngLat(lngLat)
      .setHTML(`<div class="wx-loading">⏳ Fetching weather...</div>`)
      .addTo(mapInstance)

    clickPopupRef.current = newPopup

    try {
      const res = await fetch(`${API}/api/weather/current?lat=${lngLat.lat.toFixed(4)}&lon=${lngLat.lng.toFixed(4)}`)
      const data = await res.json()
      const loc = data.location
      const cur = data.current
      if (!cur) { newPopup.setHTML(`<div class="wx-error">❌ No data for this location</div>`); return }

      const rain = cur.rainfall_1h ?? 0
      const rainLabel = rain === 0 ? 'None' : `${rain} mm/hr`
      const riskEmoji = rain > 10 ? '🔴' : rain > 2 ? '🟡' : '🟢'

      newPopup.setHTML(`
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
      newPopup.setHTML(`<div class="wx-error">❌ Failed to load weather data</div>`)
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

      // Pulsing risk marker element
      const el = document.createElement('div')
      el.className = 'fm-marker'
      el.style.borderColor = riskColor
      el.style.setProperty('--risk-color', riskColor)

      const riskPopup = new mapboxgl.Popup({
        offset: 20, closeButton: true, className: 'fm-popup', maxWidth: '300px',
      }).setHTML(buildPopupHTML(
        lat, lon, locationName, riskScore, riskLevel, riskColor,
        rainfall, humidity, windSpeed, temperature, weatherDescription,
        infrastructureQuality, infrastructureMultiplier,
      ))

      riskPopupRef.current = riskPopup

      markerRef.current = new mapboxgl.Marker({ element: el, anchor: 'bottom' })
        .setLngLat([lon, lat])
        .setPopup(riskPopup)
        .addTo(mapInstance)

      // When the risk popup is opened from the marker, close any stray click popup
      riskPopup.on('open', () => {
        if (clickPopupRef.current) {
          clickPopupRef.current.remove()
          clickPopupRef.current = null
        }
      })

      // Open risk popup by default
      markerRef.current.togglePopup()
    })

    // Map click → weather popup for that spot
    mapInstance.on('click', (e) => {
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

  // When location/weather changes, fly there and update the risk popup content
  useEffect(() => {
    if (!map.current) return
    map.current.flyTo({ center: [lon, lat], zoom: 9, speed: 1.4, curve: 1.2 })

    if (markerRef.current) {
      markerRef.current.setLngLat([lon, lat])
      const el = markerRef.current.getElement()
      el.style.borderColor = riskColor
      el.style.setProperty('--risk-color', riskColor)
    }

    if (riskPopupRef.current) {
      riskPopupRef.current
        .setLngLat([lon, lat])
        .setHTML(buildPopupHTML(
          lat, lon, locationName, riskScore, riskLevel, riskColor,
          rainfall, humidity, windSpeed, temperature, weatherDescription,
          infrastructureQuality, infrastructureMultiplier,
        ))
    }

    // Close stray click popup when a new city is searched
    if (clickPopupRef.current) {
      clickPopupRef.current.remove()
      clickPopupRef.current = null
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lat, lon, riskScore, riskLevel, riskColor, locationName, rainfall, humidity, windSpeed, temperature, weatherDescription])

  return (
    <div className="flood-map-section">
      <div className="flood-map-header">
        <h3 className="flood-map-title">🗺️ Interactive Flood Risk Map</h3>
        <span className="flood-map-hint">💡 Click the marker for risk details · Click anywhere else for live weather</span>
      </div>
      <div className="flood-map-wrapper">
        <div ref={mapContainer} className="flood-map-canvas" />
      </div>
    </div>
  )
}

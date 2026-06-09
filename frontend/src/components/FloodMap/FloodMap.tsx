import { useEffect, useRef } from 'react'
import L from 'leaflet'
import './FloodMap.css'

// Fix Leaflet default marker icon broken in Vite
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

interface FloodMapProps {
  lat: number
  lon: number
  locationName: string
  riskScore: number
  riskLevel: string
  riskColor: string
}

const getRiskRadius = (score: number) => {
  if (score >= 75) return 8000
  if (score >= 55) return 6000
  if (score >= 35) return 4000
  return 2500
}

export default function FloodMap({ lat, lon, locationName, riskScore, riskLevel, riskColor }: FloodMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstance = useRef<L.Map | null>(null)

  useEffect(() => {
    if (!mapRef.current) return

    // Remove existing map if re-rendering
    if (mapInstance.current) {
      mapInstance.current.remove()
      mapInstance.current = null
    }

    // Init map
    const map = L.map(mapRef.current, {
      center: [lat, lon],
      zoom: 11,
      zoomControl: true,
      scrollWheelZoom: true,
    })
    mapInstance.current = map

    // Tile layer — clean OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map)

    // Risk zone circle (color-coded)
    L.circle([lat, lon], {
      radius: getRiskRadius(riskScore),
      color: riskColor,
      fillColor: riskColor,
      fillOpacity: 0.15,
      weight: 2,
    }).addTo(map)

    // Location marker with popup
    const marker = L.marker([lat, lon]).addTo(map)
    marker.bindPopup(`
      <div style="font-family: Inter, sans-serif; padding: 4px 0; min-width: 180px;">
        <p style="font-weight: 700; font-size: 0.95rem; margin: 0 0 6px 0;">📍 ${locationName}</p>
        <div style="display:flex; align-items:center; gap:8px; background:${riskColor}22; border:1px solid ${riskColor}44; border-radius:8px; padding: 6px 10px;">
          <span style="font-size:1.4rem; font-weight:900; color:${riskColor};">${riskScore.toFixed(0)}%</span>
          <span style="font-size:0.8rem; font-weight:600; color:${riskColor};">${riskLevel} RISK</span>
        </div>
      </div>
    `, { maxWidth: 220 }).openPopup()

    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove()
        mapInstance.current = null
      }
    }
  }, [lat, lon, riskScore, riskLevel, riskColor, locationName])

  return (
    <div className="flood-map-wrapper">
      <div className="flood-map-header">
        <span className="map-label">📍 Risk Zone Map</span>
        <span className="map-hint">Coloured zone shows estimated flood risk area</span>
      </div>
      <div ref={mapRef} className="flood-map-container" id="flood-map" />
    </div>
  )
}

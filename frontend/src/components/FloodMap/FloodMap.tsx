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
  infrastructureMultiplier?: number
  infrastructureQuality?: string
}

// Known flood-prone hotspots — shown as warning markers on the map
// These are shown near the searched location if within ~50km
const FLOOD_HOTSPOTS = [
  // Mumbai Region
  { lat: 19.4561, lon: 72.8090, name: "Nalasopara", multiplier: 2.0, reason: "Zero drainage capacity, lowest elevation in MMR" },
  { lat: 19.4855, lon: 72.8095, name: "Virar", multiplier: 2.0, reason: "Worst drainage in MMR, floods 6-8 hrs every monsoon" },
  { lat: 19.3000, lon: 72.8527, name: "Mira Road", multiplier: 1.7, reason: "Unplanned development, drainage never upgraded" },
  { lat: 19.0759, lon: 72.8777, name: "Kurla", multiplier: 1.8, reason: "Multiple underpasses flood, very low elevation" },
  { lat: 19.0176, lon: 72.8561, name: "Dharavi", multiplier: 1.8, reason: "Very low-lying, inadequate drainage" },
  { lat: 19.1186, lon: 72.8694, name: "Malwani", multiplier: 1.7, reason: "Extremely low-lying, poor drainage" },
  { lat: 19.1724, lon: 72.8574, name: "Malad", multiplier: 1.5, reason: "Mahim Creek flooding, low areas" },
  { lat: 19.1196, lon: 72.8468, name: "Andheri (Low Areas)", multiplier: 1.5, reason: "Mithi River flooding risk" },
  { lat: 19.2183, lon: 72.9781, name: "Ulhasnagar", multiplier: 1.6, reason: "Poor drainage, annual flooding" },
  { lat: 19.2437, lon: 73.1355, name: "Badlapur", multiplier: 1.7, reason: "Severe flooding 2021-2024" },
  { lat: 19.2403, lon: 73.0508, name: "Kalyan", multiplier: 1.6, reason: "Ulhas River flooding" },
  { lat: 19.0605, lon: 72.8862, name: "Sion", multiplier: 1.6, reason: "Frequently floods in heavy rain" },
  { lat: 19.0154, lon: 72.8553, name: "Lower Parel", multiplier: 1.5, reason: "Mill land redevelopment, drainage issues" },
  // Delhi Region
  { lat: 28.6692, lon: 77.2088, name: "Old Delhi", multiplier: 1.7, reason: "Ancient narrow drains, severe waterlogging" },
  { lat: 28.5921, lon: 77.0460, name: "Dwarka", multiplier: 1.6, reason: "Famous for waterlogging after rain" },
  { lat: 28.4595, lon: 77.0266, name: "Gurgaon", multiplier: 1.8, reason: "Infamous flooding despite being a new city" },
  // Other cities
  { lat: 26.1197, lon: 91.7362, name: "Guwahati", multiplier: 1.8, reason: "Annual Brahmaputra flooding" },
  { lat: 25.5941, lon: 85.1376, name: "Patna", multiplier: 1.7, reason: "Ganga River flooding" },
  { lat: 13.0827, lon: 80.2707, name: "Velachery, Chennai", multiplier: 1.7, reason: "Built on lake, notorious flooding" },
  { lat: 22.5726, lon: 88.3639, name: "Kolkata Low Areas", multiplier: 1.6, reason: "Low elevation, tidal flooding" },
  { lat: 6.5244, lon: 3.3792, name: "Lagos", multiplier: 1.8, reason: "Very poor drainage infrastructure" },
  { lat: -6.2088, lon: 106.8456, name: "Jakarta", multiplier: 1.9, reason: "Sinking city, extreme flood risk" },
  { lat: 29.7604, lon: -95.3698, name: "Houston", multiplier: 1.6, reason: "Poor drainage (Hurricane Harvey 2017)" },
  { lat: 29.9511, lon: -90.0715, name: "New Orleans", multiplier: 1.9, reason: "Below sea level, levee-dependent" },
]

const getRiskRadius = (score: number) => {
  if (score >= 70) return 9000
  if (score >= 50) return 7000
  if (score >= 30) return 5000
  return 3000
}

const getHotspotColor = (multiplier: number): string => {
  if (multiplier >= 1.8) return '#ef4444'   // red — extreme
  if (multiplier >= 1.6) return '#f97316'   // orange — severe
  if (multiplier >= 1.4) return '#eab308'   // yellow — poor
  return '#22c55e'                           // green — ok
}

// Distance between two lat/lon points in km
const distanceKm = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
  const R = 6371
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

export default function FloodMap({
  lat, lon, locationName, riskScore, riskLevel, riskColor,
  infrastructureMultiplier = 1.2,
  infrastructureQuality = 'average drainage'
}: FloodMapProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const mapInstance = useRef<L.Map | null>(null)

  useEffect(() => {
    if (!mapRef.current) return

    if (mapInstance.current) {
      mapInstance.current.remove()
      mapInstance.current = null
    }

    const map = L.map(mapRef.current, {
      center: [lat, lon],
      zoom: 11,
      zoomControl: true,
      scrollWheelZoom: true,
    })
    mapInstance.current = map

    // Base tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map)

    // Main risk zone circle
    L.circle([lat, lon], {
      radius: getRiskRadius(riskScore),
      color: riskColor,
      fillColor: riskColor,
      fillOpacity: riskScore >= 50 ? 0.20 : 0.10,
      weight: 2,
      dashArray: riskScore >= 70 ? '6,4' : undefined,
    }).addTo(map)

    // Infrastructure quality indicator — inner circle
    const infraColor = infrastructureMultiplier >= 1.6 ? '#ef4444'
      : infrastructureMultiplier >= 1.4 ? '#f97316'
      : infrastructureMultiplier >= 1.2 ? '#eab308'
      : '#22c55e'

    // Main location marker
    const marker = L.marker([lat, lon]).addTo(map)
    marker.bindPopup(`
      <div style="font-family: Inter, sans-serif; padding: 4px 0; min-width: 210px;">
        <p style="font-weight: 700; font-size: 0.95rem; margin: 0 0 8px 0;">📍 ${locationName}</p>
        <div style="display:flex; align-items:center; gap:8px; background:${riskColor}22; border:1px solid ${riskColor}44; border-radius:8px; padding: 6px 10px; margin-bottom: 8px;">
          <span style="font-size:1.4rem; font-weight:900; color:${riskColor};">${riskScore.toFixed(0)}%</span>
          <span style="font-size:0.8rem; font-weight:600; color:${riskColor};">${riskLevel} RISK</span>
        </div>
        <div style="font-size:0.75rem; color:#888; background:#f8f8f8; border-radius:6px; padding:5px 8px;">
          🏗️ Drainage: <strong style="color:${infraColor}">${infrastructureQuality}</strong>
        </div>
      </div>
    `, { maxWidth: 240 }).openPopup()

    // Show nearby flood hotspots within 60km
    const nearbyHotspots = FLOOD_HOTSPOTS.filter(h =>
      distanceKm(lat, lon, h.lat, h.lon) < 60
    )

    nearbyHotspots.forEach(hotspot => {
      const color = getHotspotColor(hotspot.multiplier)
      const isCurrentLocation = distanceKm(lat, lon, hotspot.lat, hotspot.lon) < 2

      if (!isCurrentLocation) {
        // Hotspot circle marker
        L.circleMarker([hotspot.lat, hotspot.lon], {
          radius: 8,
          color,
          fillColor: color,
          fillOpacity: 0.7,
          weight: 2,
        }).addTo(map).bindPopup(`
          <div style="font-family: Inter, sans-serif; min-width: 190px;">
            <p style="font-weight:700; margin:0 0 6px; font-size:0.9rem;">⚠️ ${hotspot.name}</p>
            <div style="background:${color}22; border:1px solid ${color}55; border-radius:6px; padding:5px 8px; font-size:0.78rem;">
              <strong>Drainage multiplier: ${hotspot.multiplier}x</strong><br/>
              ${hotspot.reason}
            </div>
          </div>
        `, { maxWidth: 220 })
      }
    })

    // Add map legend
    const legend = new (L.Control.extend({
      onAdd: () => {
        const div = L.DomUtil.create('div', 'flood-map-legend')
        div.innerHTML = `
          <div style="background:rgba(15,17,25,0.92);border:1px solid #333;border-radius:10px;padding:10px 12px;font-family:Inter,sans-serif;font-size:0.72rem;color:#ccc;min-width:140px;">
            <p style="font-weight:700;color:#fff;margin:0 0 8px;font-size:0.78rem;">🗺️ Map Legend</p>
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;"><span style="width:12px;height:12px;border-radius:50%;background:#ef4444;display:inline-block;"></span> Extreme flood risk</div>
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;"><span style="width:12px;height:12px;border-radius:50%;background:#f97316;display:inline-block;"></span> Severe drainage</div>
            <div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;"><span style="width:12px;height:12px;border-radius:50%;background:#eab308;display:inline-block;"></span> Poor drainage</div>
            <div style="display:flex;align-items:center;gap:6px;"><span style="width:12px;height:12px;border-radius:50%;background:#22c55e;display:inline-block;"></span> Good drainage</div>
            <p style="color:#666;margin:8px 0 0;font-size:0.65rem;">Dots = known flood hotspots</p>
          </div>
        `
        return div
      }
    }))({ position: 'bottomright' })
    legend.addTo(map)

    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove()
        mapInstance.current = null
      }
    }
  }, [lat, lon, riskScore, riskLevel, riskColor, locationName, infrastructureMultiplier, infrastructureQuality])

  return (
    <div className="flood-map-wrapper">
      <div className="flood-map-header">
        <span className="map-label">📍 Flood Risk Zone Map</span>
        <span className="map-hint">Dots show known flood-prone hotspots nearby</span>
      </div>
      <div ref={mapRef} className="flood-map-container" id="flood-map" />
    </div>
  )
}

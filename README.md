# 🌊 FloodSenseAI

A real-time flood risk monitoring and early warning system powered by Machine Learning and Google Gemini AI.

🌐 **Live Demo:** https://floodsenseai-frontend.vercel.app/

---

## 📌 About the Project

FloodSenseAI is a full-stack platform that provides hyper-local, real-time flood risk assessments to users via a web interface and WhatsApp. It bridges the gap between raw meteorological data and actionable public safety by combining live weather data, a trained ML model, and Agentic AI.

---

## ✨ Features

- 🔍 **Real-Time Risk Checker** — Enter any city or use GPS to get an instant flood risk score (0–100%)
- 🌍 **Global Live Radar** — Interactive world map with real-time precipitation data
- 🤖 **AI Assistant** — RAG-powered chatbot (Google Gemini) for flood preparedness Q&A
- 📲 **WhatsApp Bot** — Get flood risk reports and subscribe to automated alerts via WhatsApp
- ⏰ **Automated Alerts** — Background scheduler sends WhatsApp warnings hourly when risk exceeds 60%

---

## 🧠 How the ML Model Works

1. Live weather data (rainfall, humidity, temperature, wind) is fetched from OpenWeatherMap
2. Data is fed into a trained **XGBoost Regressor** model
3. A city-specific **infrastructure multiplier** adjusts the score for local drainage quality
4. A **rule-based safety net** enforces minimum risk thresholds for extreme rainfall events
5. Final score is categorised as **Low / Moderate / High / Critical**

---

## 🛠️ Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React, TypeScript, Vite, CSS, Mapbox GL JS |
| Backend | Python, FastAPI, Uvicorn |
| Database | PostgreSQL (Neon) |
| AI / ML | Google Gemini 2.5 Flash-Lite (RAG), XGBoost |
| APIs | OpenWeatherMap, Twilio WhatsApp API |
| Deployment | Vercel (Frontend), Render (Backend) |

---

## 🚀 Getting Started

### Prerequisites
- Node.js 18+
- Python 3.10+
- PostgreSQL database

### Frontend Setup
```bash
cd frontend
npm install
npm run dev

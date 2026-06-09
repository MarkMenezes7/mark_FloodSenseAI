import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar/Navbar'
import Footer from './components/Footer/Footer'
import Home from './pages/Home'
import CheckRisk from './pages/CheckRisk'
import Chat from './pages/Chat'
import Alerts from './pages/Alerts'
import './index.css'

function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Navbar />
        <main style={{ flex: 1 }}>
          <Routes>
            <Route path="/"           element={<Home />} />
            <Route path="/check-risk" element={<CheckRisk />} />
            <Route path="/assistant"  element={<Chat />} />
            <Route path="/alerts"     element={<Alerts />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  )
}

export default App

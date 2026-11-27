import { Route, Routes } from 'react-router-dom'
import Painel from './pages/Painel'
import Totem from './pages/Totem'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Totem />} />
      <Route path="/painel" element={<Painel />} />
      <Route path="*" element={<p>Página não encontrada.</p>} />
    </Routes>
  )
}
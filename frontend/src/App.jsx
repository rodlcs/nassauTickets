import { Route, Routes } from 'react-router-dom'
import RotaProtegida from './components/RotaProtegida'
import Guiche from './pages/Guiche'
import Login from './pages/Login'
import Painel from './pages/Painel'
import Totem from './pages/Totem'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Totem />} />
      <Route path="/painel" element={<Painel />} />
      <Route path="/login" element={<Login />} />
      <Route
        path="/guiche"
        element={
          <RotaProtegida>
            <Guiche />
          </RotaProtegida>
        }
      />
      <Route path="*" element={<p>Página não encontrada.</p>} />
    </Routes>
  )
}
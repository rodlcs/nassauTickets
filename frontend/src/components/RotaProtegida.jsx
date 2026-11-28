import { Navigate } from 'react-router-dom'
import { useAuth } from '../auth/contexto'

// Só deixa passar quem fez login; os demais vão para a tela de login.
export default function RotaProtegida({ children }) {
  const { sessao } = useAuth()
  if (!sessao) return <Navigate to="/login" replace />
  return children
}
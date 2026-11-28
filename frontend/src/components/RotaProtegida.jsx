import { Navigate } from 'react-router-dom'
import { useAuth } from '../auth/contexto'

// Só deixa passar quem fez login. Com `perfil`, exige também esse perfil.
export default function RotaProtegida({ perfil, children }) {
  const { sessao } = useAuth()
  if (!sessao) return <Navigate to="/login" replace />
  if (perfil && sessao.usuario.perfil !== perfil) return <Navigate to="/guiche" replace />
  return children
}
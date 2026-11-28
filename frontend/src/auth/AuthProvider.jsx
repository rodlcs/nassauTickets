import { useCallback, useMemo, useState } from 'react'
import { api } from '../services/api'
import { AuthContext } from './contexto'

const CHAVE = 'nassautickets.sessao'

function lerSessao() {
  try {
    return JSON.parse(sessionStorage.getItem(CHAVE))
  } catch {
    return null
  }
}

// Guarda o token do login. O sessionStorage some quando a aba é fechada.
export default function AuthProvider({ children }) {
  const [sessao, setSessao] = useState(lerSessao)

  const entrar = useCallback(async (login, senha) => {
    const dados = await api('/login', { metodo: 'POST', corpo: { login, senha } })
    const nova = { token: dados.token, usuario: dados.usuario }
    sessionStorage.setItem(CHAVE, JSON.stringify(nova))
    setSessao(nova)
  }, [])

  const sair = useCallback(() => {
    sessionStorage.removeItem(CHAVE)
    setSessao(null)
  }, [])

  const valor = useMemo(() => ({ sessao, entrar, sair }), [sessao, entrar, sair])

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>
}
import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/contexto'
import './Login.css'

export default function Login() {
  const { sessao, entrar } = useAuth()
  const navigate = useNavigate()
  const [login, setLogin] = useState('')
  const [senha, setSenha] = useState('')
  const [erro, setErro] = useState('')
  const [enviando, setEnviando] = useState(false)

  if (sessao) return <Navigate to="/guiche" replace />

  async function enviar(evento) {
    evento.preventDefault()
    setErro('')
    setEnviando(true)
    try {
      await entrar(login.trim(), senha)
      navigate('/guiche', { replace: true })
    } catch (e) {
      setErro(e.message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <main className="login">
      <form className="login__form" onSubmit={enviar}>
        <h1>Acesso do atendente</h1>

        {erro && (
          <p className="login__erro" role="alert">
            {erro}
          </p>
        )}

        <label htmlFor="login">Login</label>
        <input
          id="login"
          type="text"
          autoComplete="username"
          value={login}
          onChange={(e) => setLogin(e.target.value)}
          required
        />

        <label htmlFor="senha">Senha</label>
        <input
          id="senha"
          type="password"
          autoComplete="current-password"
          value={senha}
          onChange={(e) => setSenha(e.target.value)}
          required
        />

        <button type="submit" disabled={enviando}>
          {enviando ? 'Entrando...' : 'Entrar'}
        </button>
      </form>
    </main>
  )
}
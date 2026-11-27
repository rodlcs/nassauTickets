import { useEffect, useState } from 'react'
import { api } from '../services/api'
import './Totem.css'

const TIPOS = [
  { sigla: 'SP', titulo: 'Prioritária' },
  { sigla: 'SG', titulo: 'Atendimento geral' },
  { sigla: 'SE', titulo: 'Retirada de exames' },
]

const SEGUNDOS_NA_TELA = 10

export default function Totem() {
  const [senha, setSenha] = useState(null)
  const [erro, setErro] = useState('')
  const [carregando, setCarregando] = useState(false)

  // Depois de mostrar a senha, a tela volta sozinha para o início.
  useEffect(() => {
    if (!senha) return undefined
    const temporizador = setTimeout(() => setSenha(null), SEGUNDOS_NA_TELA * 1000)
    return () => clearTimeout(temporizador)
  }, [senha])

  async function emitir(sigla) {
    setErro('')
    setCarregando(true)
    try {
      const nova = await api('/senhas', { metodo: 'POST', corpo: { tipo: sigla } })
      setSenha(nova)
    } catch (e) {
      setErro(e.message)
    } finally {
      setCarregando(false)
    }
  }

  if (senha) {
    return (
      <main className="totem">
        <section className="totem__senha" aria-live="polite">
          <p>Sua senha é</p>
          <strong className="totem__numero">{senha.numero}</strong>
          <p>Aguarde a chamada no painel.</p>
          <button className="totem__voltar" onClick={() => setSenha(null)}>
            Nova senha
          </button>
        </section>
      </main>
    )
  }

  return (
    <main className="totem">
      <h1>Laboratório nassauTickets</h1>
      <p className="totem__instrucao">Toque no tipo de atendimento para retirar sua senha.</p>

      {erro && (
        <p className="totem__erro" role="alert">
          {erro}
        </p>
      )}

      <div className="totem__botoes">
        {TIPOS.map((tipo) => (
          <button
            key={tipo.sigla}
            className="totem__botao"
            onClick={() => emitir(tipo.sigla)}
            disabled={carregando}
          >
            <span className="totem__sigla">{tipo.sigla}</span>
            <span>{tipo.titulo}</span>
          </button>
        ))}
      </div>
    </main>
  )
}
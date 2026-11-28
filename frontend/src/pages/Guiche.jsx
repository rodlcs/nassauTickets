import { useCallback, useEffect, useState } from 'react'
import { useAuth } from '../auth/contexto'
import { api } from '../services/api'
import './Guiche.css'

// Mesma quantidade criada pelo seed.py (proposta; o número real é um ponto em aberto).
const GUICHES = [1, 2, 3]

const ESTADOS = {
  CHAMADA: 'Chamada',
  CHAMADA_NOVAMENTE: 'Chamada novamente (última chamada)',
  EM_ATENDIMENTO: 'Em atendimento',
}

export default function Guiche() {
  const { sessao, sair } = useAuth()
  const token = sessao?.token

  const [guiche, setGuiche] = useState(GUICHES[0])
  const [atual, setAtual] = useState(null)
  const [carregando, setCarregando] = useState(true)
  const [ocupado, setOcupado] = useState(false)
  const [erro, setErro] = useState('')
  const [aviso, setAviso] = useState('')

  // Sessão vencida: volta para o login.
  const tratarErro = useCallback(
    (e) => {
      if (e.status === 401) sair()
      else setErro(e.message)
    },
    [sair],
  )

  // Ao abrir (ou recarregar), recupera a senha que o atendente deixou em aberto.
  useEffect(() => {
    let ativo = true
    api('/atendimentos/atual', { token })
      .then((dados) => {
        if (!ativo || !dados.senha) return
        setAtual(dados.senha)
        setGuiche(dados.senha.guiche)
      })
      .catch((e) => {
        if (ativo) tratarErro(e)
      })
      .finally(() => {
        if (ativo) setCarregando(false)
      })
    return () => {
      ativo = false
    }
  }, [token, tratarErro])

  async function executar(acao) {
    setErro('')
    setAviso('')
    setOcupado(true)
    try {
      await acao()
    } catch (e) {
      tratarErro(e)
    } finally {
      setOcupado(false)
    }
  }

  function chamarProxima() {
    return executar(async () => {
      const senha = await api('/chamadas/proxima', {
        metodo: 'POST',
        corpo: { guiche },
        token,
      })
      setAtual(senha)
    })
  }

  function mudar(caminho, mensagemFinal) {
    return executar(async () => {
      const resultado = await api(`/atendimentos/${atual.id}/${caminho}`, {
        metodo: 'POST',
        token,
      })
      if (mensagemFinal) {
        setAviso(`${atual.numero}: ${mensagemFinal}`)
        setAtual(null)
      } else {
        setAtual({ ...atual, estado: resultado.estado })
      }
    })
  }

  if (carregando) return <main className="guiche"><p>Carregando...</p></main>

  return (
    <main className="guiche">
      <header className="guiche__topo">
        <div>
          <h1>Guichê de atendimento</h1>
          <p>
            {sessao.usuario.nome} ({sessao.usuario.perfil === 'GESTOR' ? 'gestor' : 'atendente'})
          </p>
        </div>
        <button className="guiche__sair" onClick={sair}>
          Sair
        </button>
      </header>

      {erro && (
        <p className="guiche__erro" role="alert">
          {erro}
        </p>
      )}
      {aviso && (
        <p className="guiche__aviso" role="status">
          {aviso}
        </p>
      )}

      <label className="guiche__campo" htmlFor="guiche">
        Meu guichê
        <select
          id="guiche"
          value={guiche}
          onChange={(e) => setGuiche(Number(e.target.value))}
          disabled={Boolean(atual)}
        >
          {GUICHES.map((numero) => (
            <option key={numero} value={numero}>
              Guichê {numero}
            </option>
          ))}
        </select>
      </label>

      {!atual ? (
        <button className="guiche__principal" onClick={chamarProxima} disabled={ocupado}>
          Chamar próxima senha
        </button>
      ) : (
        <section className="guiche__atual" aria-live="polite">
          <p className="guiche__estado">{ESTADOS[atual.estado]}</p>
          <strong className="guiche__numero">{atual.numero}</strong>

          <div className="guiche__acoes">
            {atual.estado !== 'EM_ATENDIMENTO' && (
              <button onClick={() => mudar('iniciar')} disabled={ocupado}>
                Iniciar atendimento
              </button>
            )}
            {atual.estado === 'CHAMADA' && (
              <button onClick={() => mudar('rechamar')} disabled={ocupado}>
                Chamar novamente
              </button>
            )}
            {atual.estado === 'CHAMADA_NOVAMENTE' && (
              <button
                onClick={() => mudar('nao-compareceu', 'cliente não compareceu.')}
                disabled={ocupado}
              >
                Cliente não compareceu
              </button>
            )}
            {atual.estado === 'EM_ATENDIMENTO' && (
              <button
                onClick={() => mudar('finalizar', 'atendimento finalizado.')}
                disabled={ocupado}
              >
                Finalizar atendimento
              </button>
            )}
          </div>
        </section>
      )}
    </main>
  )
}
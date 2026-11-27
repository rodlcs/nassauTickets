import { useEffect, useRef, useState } from 'react'
import { api } from '../services/api'
import { audioDisponivel, falar } from '../services/audio'
import './Painel.css'

const INTERVALO_MS = 3000

const NOMES = {
  SP: 'prioritária',
  SG: 'geral',
  SE: 'retirada de exames',
}

// Frase falada: prioridade, senha e guichê (e "última chamada", quando for o caso).
function textoDaChamada(senha) {
  const sequencia = Number(senha.numero.slice(-3))
  const prefixo = senha.ultima_chamada ? 'Última chamada. ' : ''
  const letras = senha.tipo.split('').join(' ')
  return `${prefixo}Senha ${NOMES[senha.tipo]}. ${letras}, ${sequencia}. Guichê ${senha.guiche}.`
}

export default function Painel() {
  const [senhas, setSenhas] = useState([])
  const [carregado, setCarregado] = useState(false)
  const [offline, setOffline] = useState(false)
  const [audioAtivo, setAudioAtivo] = useState(false)

  const inicializado = useRef(false)
  const ultimaChave = useRef(null)

  // Consulta o backend de tempos em tempos.
  useEffect(() => {
    let ativo = true

    async function atualizar() {
      try {
        const dados = await api('/painel')
        if (!ativo) return
        setSenhas(dados.senhas)
        setOffline(false)
        setCarregado(true)
      } catch {
        // Mantém o que já está na tela e avisa que a conexão caiu.
        if (ativo) setOffline(true)
      }
    }

    atualizar()
    const id = setInterval(atualizar, INTERVALO_MS)
    return () => {
      ativo = false
      clearInterval(id)
    }
  }, [])

  const atual = senhas[0]
  const chave = atual ? `${atual.numero}|${atual.estado}|${atual.chamada_em}` : null

  // Fala quando uma chamada nova chega (inclusive "chamar novamente").
  useEffect(() => {
    if (!carregado) return
    if (!inicializado.current) {
      // Primeira carga: não anuncia chamadas antigas.
      inicializado.current = true
      ultimaChave.current = chave
      return
    }
    if (chave === null || chave === ultimaChave.current) return
    ultimaChave.current = chave
    if (audioAtivo) falar(textoDaChamada(atual))
  }, [carregado, chave, audioAtivo, atual])

  function ativarAudio() {
    // O navegador só libera o som depois de um clique do usuário.
    setAudioAtivo(true)
    falar('Áudio do painel ativado.')
  }

  return (
    <main className="painel">
      <header className="painel__topo">
        <h1>Painel de chamadas</h1>
        {audioDisponivel() &&
          (audioAtivo ? (
            <span className="painel__audio">Áudio ativado</span>
          ) : (
            <button className="painel__ativar" onClick={ativarAudio}>
              Ativar áudio
            </button>
          ))}
      </header>

      {offline && (
        <p className="painel__aviso" role="alert">
          Sem conexão com o sistema. Tentando reconectar...
        </p>
      )}

      {!atual ? (
        <p className="painel__vazio">Aguardando a primeira chamada.</p>
      ) : (
        <>
          <section className="painel__atual" aria-live="polite">
            {atual.ultima_chamada && (
              <p className="painel__ultima">Última chamada</p>
            )}
            <strong className="painel__numero">{atual.numero}</strong>
            <p className="painel__guiche">Guichê {atual.guiche}</p>
          </section>

          <section>
            <h2>Chamadas anteriores</h2>
            <ul className="painel__lista">
              {senhas.slice(1).map((senha) => (
                <li key={senha.numero}>
                  <span>{senha.numero}</span>
                  <span>Guichê {senha.guiche}</span>
                </li>
              ))}
            </ul>
          </section>
        </>
      )}
    </main>
  )
}
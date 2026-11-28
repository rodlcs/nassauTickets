import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../auth/contexto'
import { api } from '../services/api'
import './Relatorios.css'

const ESTADOS = {
  EMITIDA: 'Emitida',
  AGUARDANDO: 'Aguardando',
  CHAMADA: 'Chamada',
  CHAMADA_NOVAMENTE: 'Chamada novamente',
  EM_ATENDIMENTO: 'Em atendimento',
  ATENDIDA: 'Atendida',
  NAO_COMPARECEU: 'Não compareceu',
}

function hojeISO() {
  const agora = new Date()
  const mes = String(agora.getMonth() + 1).padStart(2, '0')
  const dia = String(agora.getDate()).padStart(2, '0')
  return `${agora.getFullYear()}-${mes}-${dia}`
}

// Campos sem valor ficam em branco, como o relatório exige.
function formatar(iso) {
  if (!iso) return ''
  return `${iso.slice(8, 10)}/${iso.slice(5, 7)}/${iso.slice(0, 4)} ${iso.slice(11, 19)}`
}

export default function Relatorios() {
  const { sessao, sair } = useAuth()
  const token = sessao?.token

  const [modo, setModo] = useState('diario')
  const [dia, setDia] = useState(hojeISO)
  const [mes, setMes] = useState(() => hojeISO().slice(0, 7))
  const [resultado, setResultado] = useState({ caminho: null, dados: null, erro: '' })

  const valido = modo === 'diario' ? Boolean(dia) : Boolean(mes)
  const caminho =
    modo === 'diario' ? `/relatorios/diario?data=${dia}` : `/relatorios/mensal?mes=${mes}`

  useEffect(() => {
    if (!valido) return undefined
    let ativo = true

    api(caminho, { token })
      .then((dados) => {
        if (ativo) setResultado({ caminho, dados, erro: '' })
      })
      .catch((e) => {
        if (!ativo) return
        if (e.status === 401) sair()
        else setResultado({ caminho, dados: null, erro: e.message })
      })

    return () => {
      ativo = false
    }
  }, [caminho, valido, token, sair])

  const atualizado = resultado.caminho === caminho
  const carregando = valido && !atualizado
  const dados = atualizado ? resultado.dados : null
  const erro = atualizado ? resultado.erro : ''

  return (
    <main className="relatorios">
      <header className="relatorios__topo">
        <h1>Relatórios</h1>
        <nav className="relatorios__menu">
          <Link className="relatorios__link" to="/guiche">
            Voltar ao guichê
          </Link>
          <button className="relatorios__sair" onClick={sair}>
            Sair
          </button>
        </nav>
      </header>

      <section className="relatorios__filtros" aria-label="Período do relatório">
        <label>
          Tipo
          <select value={modo} onChange={(e) => setModo(e.target.value)}>
            <option value="diario">Diário</option>
            <option value="mensal">Mensal</option>
          </select>
        </label>

        {modo === 'diario' ? (
          <label>
            Dia
            <input type="date" value={dia} onChange={(e) => setDia(e.target.value)} />
          </label>
        ) : (
          <label>
            Mês
            <input type="month" value={mes} onChange={(e) => setMes(e.target.value)} />
          </label>
        )}
      </section>

      {carregando && <p className="relatorios__estado">Carregando...</p>}

      {erro && (
        <p className="relatorios__erro" role="alert">
          {erro}
        </p>
      )}

      {dados && (
        <>
          <section className="relatorios__bloco">
            <h2>Resumo ({dados.periodo.rotulo})</h2>
            <dl className="relatorios__resumo">
              <div>
                <dt>Emitidas</dt>
                <dd>{dados.resumo.emitidas}</dd>
              </div>
              <div>
                <dt>Atendidas</dt>
                <dd>{dados.resumo.atendidas}</dd>
              </div>
              <div>
                <dt>Não compareceram</dt>
                <dd>{dados.resumo.nao_compareceu}</dd>
              </div>
              <div>
                <dt>Descartadas</dt>
                <dd>{dados.resumo.descartadas}</dd>
              </div>
              <div>
                <dt>Tempo médio de atendimento</dt>
                <dd>{dados.resumo.tempo_medio ?? 'Sem atendimentos'}</dd>
              </div>
            </dl>
          </section>

          <section className="relatorios__bloco">
            <h2>Por prioridade</h2>
            <div className="relatorios__tabela">
              <table>
                <thead>
                  <tr>
                    <th scope="col">Tipo</th>
                    <th scope="col">Emitidas</th>
                    <th scope="col">Atendidas</th>
                  </tr>
                </thead>
                <tbody>
                  {dados.por_tipo.map((linha) => (
                    <tr key={linha.tipo}>
                      <td>{linha.tipo}</td>
                      <td>{linha.emitidas}</td>
                      <td>{linha.atendidas}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          <section className="relatorios__bloco">
            <h2>Relatório detalhado</h2>
            {dados.detalhado.length === 0 ? (
              <p>Nenhuma senha no período.</p>
            ) : (
              <div className="relatorios__tabela">
                <table>
                  <thead>
                    <tr>
                      <th scope="col">Senha</th>
                      <th scope="col">Tipo</th>
                      <th scope="col">Situação</th>
                      <th scope="col">Emissão</th>
                      <th scope="col">Atendimento</th>
                      <th scope="col">Guichê</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dados.detalhado.map((linha) => (
                      <tr key={linha.numero}>
                        <td>{linha.numero}</td>
                        <td>{linha.tipo}</td>
                        <td>{ESTADOS[linha.estado] ?? linha.estado}</td>
                        <td>{formatar(linha.emitida_em)}</td>
                        <td>{formatar(linha.atendida_em)}</td>
                        <td>{linha.guiche}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>

          <section className="relatorios__bloco">
            <h2>Auditoria</h2>
            {dados.auditoria.length === 0 ? (
              <p>Nenhuma chamada no período.</p>
            ) : (
              <div className="relatorios__tabela">
                <table>
                  <thead>
                    <tr>
                      <th scope="col">Atendente</th>
                      <th scope="col">Guichê</th>
                      <th scope="col">Senha</th>
                      <th scope="col">1ª chamada</th>
                      <th scope="col">2ª chamada</th>
                      <th scope="col">Início</th>
                      <th scope="col">Fim</th>
                    </tr>
                  </thead>
                  <tbody>
                    {dados.auditoria.map((linha) => (
                      <tr key={linha.senha}>
                        <td>{linha.atendente}</td>
                        <td>{linha.guiche}</td>
                        <td>{linha.senha}</td>
                        <td>{formatar(linha.primeira_chamada_em)}</td>
                        <td>{formatar(linha.segunda_chamada_em)}</td>
                        <td>{formatar(linha.inicio_em)}</td>
                        <td>{formatar(linha.fim_em)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </>
      )}
    </main>
  )
}
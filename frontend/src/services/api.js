const BASE = '/api'

const MENSAGEM_SEM_CONEXAO = 'Sem conexão com o sistema. Tente novamente em instantes.'

export class ApiError extends Error {
  constructor(mensagem, status) {
    super(mensagem)
    this.status = status
  }
}

// Cliente único para falar com o backend. Traduz falhas em mensagens para o usuário.
export async function api(caminho, { metodo = 'GET', corpo, token } = {}) {
  const headers = {}
  if (corpo) headers['Content-Type'] = 'application/json'
  if (token) headers.Authorization = `Bearer ${token}`

  let resposta
  try {
    resposta = await fetch(`${BASE}${caminho}`, {
      method: metodo,
      headers,
      body: corpo ? JSON.stringify(corpo) : undefined,
    })
  } catch {
    throw new ApiError(MENSAGEM_SEM_CONEXAO, 0)
  }

  let dados = null
  try {
    dados = await resposta.json()
  } catch {
    // resposta sem corpo JSON
  }

  if (!resposta.ok) {
    if (dados?.erro) throw new ApiError(dados.erro, resposta.status)
    // Erro de servidor sem mensagem (ex.: o proxy não alcançou o backend).
    if (resposta.status >= 500) throw new ApiError(MENSAGEM_SEM_CONEXAO, resposta.status)
    throw new ApiError('Não foi possível concluir a operação.', resposta.status)
  }
  return dados
}
const CHAVE_TOKEN = 'oraculo-token'

export function lerToken() {
  try {
    return localStorage.getItem(CHAVE_TOKEN)
  } catch {
    return null
  }
}

export function guardarToken(token) {
  try {
    if (token) localStorage.setItem(CHAVE_TOKEN, token)
    else localStorage.removeItem(CHAVE_TOKEN)
  } catch {
    // Sem acesso ao armazenamento: a sessão dura até a página ser recarregada
  }
}

// Avisado quando o servidor recusa a sessão (expirada ou encerrada)
let aoPerderSessao = () => {}
export function quandoPerderSessao(funcao) {
  aoPerderSessao = funcao
}

export class ErroApi extends Error {
  constructor(mensagem, status) {
    super(mensagem)
    this.status = status
  }
}

async function requisitar(caminho, { metodo = 'GET', corpo, mensagemPadrao } = {}) {
  const cabecalhos = {}
  const token = lerToken()
  if (token) cabecalhos.Authorization = `Bearer ${token}`
  if (corpo !== undefined) cabecalhos['Content-Type'] = 'application/json'

  let resposta
  try {
    resposta = await fetch(caminho, {
      method: metodo,
      headers: cabecalhos,
      body: corpo === undefined ? undefined : JSON.stringify(corpo),
    })
  } catch {
    throw new ErroApi('Sem conexão com o servidor. Verifique sua internet e tente novamente.', 0)
  }

  if (resposta.status === 204) return null
  const dados = await resposta.json().catch(() => ({}))
  if (!resposta.ok) {
    if (resposta.status === 401 && token) aoPerderSessao()
    // O servidor já devolve mensagens prontas para mostrar ao usuário
    const detalhe = typeof dados.detail === 'string' ? dados.detail : mensagemPadrao || 'Algo deu errado. Tente novamente.'
    throw new ErroApi(detalhe, resposta.status)
  }
  return dados
}

// Consulta pública

export const buscarSugestoes = () => requisitar('/api/sugestoes')

export const enviarPergunta = (texto) =>
  requisitar('/api/perguntas', {
    metodo: 'POST',
    corpo: { texto },
    mensagemPadrao: 'Não foi possível enviar sua pergunta agora. Tente novamente em instantes.',
  })


// A resposta, 2 sites e 2 vídeos vão para o e-mail informado
export const pedirSaibaMais = (perguntaId, { nome, email, consentimento }) =>
  requisitar('/api/saiba-mais', {
    metodo: 'POST',
    corpo: { pergunta_id: perguntaId, nome, email, consentimento },
    mensagemPadrao: 'Não foi possível registrar seu pedido agora.',
  })

export const consultarPedido = (id) => requisitar(`/api/saiba-mais/${id}`)

// Autenticação

export const entrar = (email, senha) => requisitar('/api/auth/login', { metodo: 'POST', corpo: { email, senha } })

export const cadastrar = ({ nome, email, senha, consentimento }) =>
  requisitar('/api/auth/cadastro', { metodo: 'POST', corpo: { nome, email, senha, consentimento } })

export const sair = () => requisitar('/api/auth/sair', { metodo: 'POST' })

export const buscarUsuarioAtual = () => requisitar('/api/auth/eu')

// Base de conhecimento

export const listarTemas = () => requisitar('/api/temas')

export function listarTrechos({ temaId, busca, pagina }) {
  const parametros = new URLSearchParams({ pagina: String(pagina || 1) })
  if (temaId) parametros.set('tema_id', temaId)
  if (busca) parametros.set('busca', busca)
  return requisitar(`/api/base/trechos?${parametros}`)
}

export const obterTrecho = (id) => requisitar(`/api/base/trechos/${id}`)

export const salvarTrecho = (id, dados) =>
  requisitar(id ? `/api/base/trechos/${id}` : '/api/base/trechos', { metodo: id ? 'PUT' : 'POST', corpo: dados })

export const excluirTrecho = (id) => requisitar(`/api/base/trechos/${id}`, { metodo: 'DELETE' })


// Usuários

export const listarUsuarios = () => requisitar('/api/usuarios')

export const salvarUsuario = (id, dados) =>
  requisitar(id ? `/api/usuarios/${id}` : '/api/usuarios', { metodo: id ? 'PUT' : 'POST', corpo: dados })

export const excluirUsuario = (id) => requisitar(`/api/usuarios/${id}`, { metodo: 'DELETE' })

// Acompanhamento de temas

export const listarInscricoes = () => requisitar('/api/inscricoes')

export const criarInscricao = (temaId) => requisitar('/api/inscricoes', { metodo: 'POST', corpo: { tema_id: temaId } })

export const excluirInscricao = (id) => requisitar(`/api/inscricoes/${id}`, { metodo: 'DELETE' })

// Atualizações de temas (Módulo 2)

export function listarAtualizacoes(temaId) {
  return requisitar(temaId ? `/api/atualizacoes?tema_id=${temaId}` : '/api/atualizacoes')
}

export const publicarAtualizacao = (dados) => requisitar('/api/atualizacoes', { metodo: 'POST', corpo: dados })

export const reenviarAtualizacao = (id) => requisitar(`/api/atualizacoes/${id}/reenviar`, { metodo: 'POST' })

export const excluirAtualizacao = (id) => requisitar(`/api/atualizacoes/${id}`, { metodo: 'DELETE' })

export const listarMinhasAtualizacoes = () => requisitar('/api/minhas-atualizacoes')

// Dashboard e relatórios

export const buscarIndicadores = (dias) => requisitar(`/api/painel/indicadores?dias=${dias}`)

function parametros(filtros) {
  const busca = new URLSearchParams()
  for (const [chave, valor] of Object.entries(filtros)) if (valor) busca.set(chave, valor)
  return busca.toString()
}

export const relatorioPerguntas = (filtros) => requisitar(`/api/relatorios/perguntas?${parametros(filtros)}`)

export const relatorioHistorico = (filtros) => requisitar(`/api/relatorios/historico?${parametros(filtros)}`)

// Baixa o relatório em CSV (a rota exige o token, por isso não basta um link)
export async function baixarCsv(caminho, filtros) {
  const resposta = await fetch(`${caminho}?${parametros({ ...filtros, formato: 'csv' })}`, {
    headers: { Authorization: `Bearer ${lerToken()}` },
  })
  if (!resposta.ok) {
    const dados = await resposta.json().catch(() => ({}))
    throw new ErroApi(dados.detail || 'Não foi possível exportar o relatório.', resposta.status)
  }
  const nome = /filename="([^"]+)"/.exec(resposta.headers.get('Content-Disposition') || '')?.[1] || 'relatorio.csv'
  const endereco = URL.createObjectURL(await resposta.blob())
  const link = Object.assign(document.createElement('a'), { href: endereco, download: nome })
  link.click()
  URL.revokeObjectURL(endereco)
}

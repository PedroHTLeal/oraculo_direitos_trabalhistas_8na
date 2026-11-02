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

export const buscarInstrucoesWhatsApp = () => requisitar('/api/whatsapp')

export const pedirSaibaMais = (perguntaId, telefone, consentimento) =>
  requisitar('/api/saiba-mais', {
    metodo: 'POST',
    corpo: { pergunta_id: perguntaId, telefone, consentimento },
    mensagemPadrao: 'Não foi possível registrar seu pedido agora.',
  })

export const consultarPedido = (id) => requisitar(`/api/saiba-mais/${id}`)

// Autenticação

export const entrar = (email, senha) => requisitar('/api/auth/login', { metodo: 'POST', corpo: { email, senha } })

export const cadastrar = (nome, email, senha) =>
  requisitar('/api/auth/cadastro', { metodo: 'POST', corpo: { nome, email, senha } })

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

export const listarPerguntas = () => requisitar('/api/base/perguntas')

// Usuários

export const listarUsuarios = () => requisitar('/api/usuarios')

export const salvarUsuario = (id, dados) =>
  requisitar(id ? `/api/usuarios/${id}` : '/api/usuarios', { metodo: id ? 'PUT' : 'POST', corpo: dados })

export const excluirUsuario = (id) => requisitar(`/api/usuarios/${id}`, { metodo: 'DELETE' })

// Acompanhamento de temas

export const listarInscricoes = () => requisitar('/api/inscricoes')

export const criarInscricao = (temaId, telefone, consentimento) =>
  requisitar('/api/inscricoes', { metodo: 'POST', corpo: { tema_id: temaId, telefone, consentimento } })

export const excluirInscricao = (id) => requisitar(`/api/inscricoes/${id}`, { metodo: 'DELETE' })

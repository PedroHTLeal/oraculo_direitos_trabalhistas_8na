async function requisitar(caminho, opcoes, mensagemPadrao) {
  const resposta = await fetch(caminho, opcoes)
  const dados = await resposta.json().catch(() => ({}))
  if (!resposta.ok) {
    // Erros de validação trazem uma mensagem pronta para mostrar ao usuário
    const detalhe = typeof dados.detail === 'string' ? dados.detail : mensagemPadrao
    throw new Error(detalhe)
  }
  return dados
}

function enviarJson(corpo) {
  return {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(corpo),
  }
}

export function buscarSugestoes() {
  return requisitar('/api/sugestoes', undefined, 'Falha ao carregar sugestões')
}

export function enviarPergunta(texto) {
  return requisitar(
    '/api/perguntas',
    enviarJson({ texto }),
    'Não foi possível enviar sua pergunta agora. Tente novamente em instantes.',
  )
}

export function buscarInstrucoesWhatsApp() {
  return requisitar('/api/whatsapp', undefined, 'Falha ao carregar instruções do WhatsApp')
}

export function pedirSaibaMais(perguntaId, telefone, consentimento) {
  return requisitar(
    '/api/saiba-mais',
    enviarJson({ pergunta_id: perguntaId, telefone, consentimento }),
    'Não foi possível registrar seu pedido agora.',
  )
}

export function consultarPedido(id) {
  return requisitar(`/api/saiba-mais/${id}`, undefined, 'Falha ao consultar o pedido')
}

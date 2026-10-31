export async function buscarSugestoes() {
  const resposta = await fetch('/api/sugestoes')
  if (!resposta.ok) throw new Error('Falha ao carregar sugestões')
  return resposta.json()
}

export async function enviarPergunta(texto) {
  const resposta = await fetch('/api/perguntas', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ texto }),
  })
  if (!resposta.ok) throw new Error('Falha ao enviar pergunta')
  return resposta.json()
}

import { useEffect, useRef, useState } from 'react'
import { buscarInstrucoesWhatsApp, consultarPedido, pedirSaibaMais } from '../api'
import { formatarTelefone } from '../telefone'

const INTERVALO_CONSULTA = 2500
const TEMPO_MAXIMO = 90000

function linkWhatsApp(numero, codigo) {
  return `https://wa.me/${numero.replace(/\D/g, '')}?text=${encodeURIComponent(codigo)}`
}

function ModalSaibaMais({ perguntaId, aoFechar }) {
  const dialogo = useRef(null)
  const [telefone, setTelefone] = useState('')
  const [consentimento, setConsentimento] = useState(false)
  const [etapa, setEtapa] = useState('formulario') // formulario | enviando | enviado | erro
  const [erro, setErro] = useState(null)
  const [sandbox, setSandbox] = useState(null)

  useEffect(() => {
    dialogo.current?.showModal()
    buscarInstrucoesWhatsApp()
      .then((dados) => dados.codigo && setSandbox(dados))
      .catch(() => setSandbox(null))
  }, [])

  // Acompanha o envio, que roda em segundo plano no servidor
  async function acompanhar(id) {
    const inicio = Date.now()
    while (Date.now() - inicio < TEMPO_MAXIMO) {
      await new Promise((resolver) => setTimeout(resolver, INTERVALO_CONSULTA))
      const { status } = await consultarPedido(id)
      if (status === 'enviado') return setEtapa('enviado')
      if (status === 'erro') break
    }
    setErro('Não conseguimos enviar a mensagem. Tente novamente mais tarde.')
    setEtapa('erro')
  }

  async function enviar(evento) {
    evento.preventDefault()
    setErro(null)
    setEtapa('enviando')
    try {
      const pedido = await pedirSaibaMais(perguntaId, telefone, consentimento)
      await acompanhar(pedido.id)
    } catch (falha) {
      setErro(falha.message)
      setEtapa('formulario')
    }
  }

  const digitos = telefone.replace(/\D/g, '').length
  const podeEnviar = digitos >= 10 && consentimento

  return (
    <dialog ref={dialogo} className="modal" onClose={aoFechar} aria-labelledby="titulo-modal">
      <button type="button" className="modal-fechar" onClick={() => dialogo.current.close()} aria-label="Fechar">
        ×
      </button>

      {etapa === 'enviado' ? (
        <div className="modal-sucesso" role="status">
          <span className="modal-icone" aria-hidden="true">
            ✓
          </span>
          <h2 id="titulo-modal">Pronto! Confira seu WhatsApp</h2>
          <p>Enviamos a resposta, 2 sites e 2 vídeos sobre o assunto para {telefone}.</p>
          <button type="button" className="botao-principal" onClick={() => dialogo.current.close()}>
            Fechar
          </button>
        </div>
      ) : (
        <form onSubmit={enviar}>
          <p className="chamada">Saiba mais</p>
          <h2 id="titulo-modal">Receba mais conteúdo no seu WhatsApp</h2>
          <p className="modal-texto">
            Vamos enviar a resposta junto com <strong>2 sites</strong> e <strong>2 vídeos do YouTube</strong> que
            explicam o assunto.
          </p>

          {sandbox && (
            <div className="modal-aviso">
              <strong>Antes de continuar (ambiente de teste):</strong> envie a mensagem{' '}
              <code>{sandbox.codigo}</code> para o WhatsApp <strong>{sandbox.numero}</strong>.{' '}
              <a href={linkWhatsApp(sandbox.numero, sandbox.codigo)} target="_blank" rel="noreferrer">
                Abrir no WhatsApp ↗
              </a>
            </div>
          )}

          <label htmlFor="telefone" className="campo-rotulo">
            Seu WhatsApp com DDD
          </label>
          <input
            id="telefone"
            type="tel"
            inputMode="numeric"
            autoComplete="tel-national"
            placeholder="(51) 99999-8888"
            value={telefone}
            onChange={(evento) => setTelefone(formatarTelefone(evento.target.value))}
            disabled={etapa === 'enviando'}
          />

          <label className="consentimento">
            <input
              type="checkbox"
              checked={consentimento}
              onChange={(evento) => setConsentimento(evento.target.checked)}
              disabled={etapa === 'enviando'}
            />
            <span>
              Autorizo o uso do meu telefone apenas para receber este conteúdo, conforme a Lei Geral de Proteção de
              Dados (LGPD).
            </span>
          </label>

          {erro && (
            <p className="erro" role="alert">
              {erro}
            </p>
          )}

          <button type="submit" className="botao-principal" disabled={!podeEnviar || etapa === 'enviando'}>
            {etapa === 'enviando' ? 'Buscando conteúdos e enviando...' : 'Receber no WhatsApp'}
          </button>
        </form>
      )}
    </dialog>
  )
}

export default ModalSaibaMais

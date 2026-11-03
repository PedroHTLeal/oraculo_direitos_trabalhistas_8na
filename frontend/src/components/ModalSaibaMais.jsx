import { useEffect, useRef, useState } from 'react'
import { consultarPedido, pedirSaibaMais } from '../api'
import { useAutenticacao } from '../autenticacao/contexto'
import { regras, validar } from '../validacao'
import Campo from './Campo'

const INTERVALO_CONSULTA = 2500
const TEMPO_MAXIMO = 90000

const ESQUEMA = {
  nome: [regras.obrigatorio('nome'), regras.minimo('nome', 2), regras.maximo('nome', 100)],
  email: [regras.obrigatorio('e-mail'), regras.email()],
  consentimento: [(valor) => (valor ? null : 'É preciso autorizar o envio do conteúdo para o seu e-mail.')],
}

// "Quer saber mais?": a pessoa informa nome e e-mail e recebe a resposta com sites e vídeos sobre o assunto.
// Não precisa de conta; quem já entrou tem os campos preenchidos.
function ModalSaibaMais({ perguntaId, aoFechar }) {
  const dialogo = useRef(null)
  const { usuario } = useAutenticacao()
  const [dados, setDados] = useState({ nome: usuario?.nome || '', email: usuario?.email || '', consentimento: false })
  const [erros, setErros] = useState({})
  const [etapa, setEtapa] = useState('formulario') // formulario | enviando | enviado
  const [erro, setErro] = useState(null)

  useEffect(() => {
    dialogo.current?.showModal()
  }, [])

  const mudar = (campo) => (evento) => setDados({ ...dados, [campo]: evento.target.value })

  // Acompanha o envio, que roda em segundo plano no servidor
  async function acompanhar(id) {
    const inicio = Date.now()
    while (Date.now() - inicio < TEMPO_MAXIMO) {
      await new Promise((resolver) => setTimeout(resolver, INTERVALO_CONSULTA))
      const { status } = await consultarPedido(id)
      if (status === 'enviado') return setEtapa('enviado')
      if (status === 'erro') break
    }
    setErro('Não conseguimos enviar o e-mail agora. Tente novamente em alguns minutos.')
    setEtapa('formulario')
  }

  async function enviar(evento) {
    evento.preventDefault()
    const encontrados = validar(dados, ESQUEMA)
    setErros(encontrados)
    setErro(null)
    if (Object.keys(encontrados).length) return

    setEtapa('enviando')
    try {
      const pedido = await pedirSaibaMais(perguntaId, {
        nome: dados.nome.trim(),
        email: dados.email.trim(),
        consentimento: dados.consentimento,
      })
      await acompanhar(pedido.id)
    } catch (falha) {
      setErro(falha.message)
      setEtapa('formulario')
    }
  }

  const fechar = () => dialogo.current.close()

  return (
    <dialog ref={dialogo} className="modal" onClose={aoFechar} aria-labelledby="titulo-modal">
      <button type="button" className="modal-fechar" onClick={fechar} aria-label="Fechar">
        ×
      </button>

      {etapa === 'enviado' ? (
        <div className="modal-sucesso" role="status">
          <span className="modal-icone" aria-hidden="true">
            ✓
          </span>
          <h2 id="titulo-modal">Pronto! Confira seu e-mail</h2>
          <p>
            Enviamos a resposta, sites e vídeos sobre o assunto para <strong>{dados.email.trim()}</strong>. Se não
            encontrar na caixa de entrada, olhe também a pasta de spam.
          </p>
          <button type="button" className="botao-principal" onClick={fechar}>
            Fechar
          </button>
        </div>
      ) : (
        <form className="modal-conteudo" onSubmit={enviar} noValidate>
          <p className="chamada">Saber mais</p>
          <h2 id="titulo-modal">Receba mais no seu e-mail</h2>
          <p className="modal-texto">
            Informe seu nome e seu e-mail. Vamos enviar esta resposta junto com <strong>sites</strong> e{' '}
            <strong>vídeos do YouTube</strong> que explicam bem o assunto.
          </p>

          <Campo id="saiba-nome" rotulo="Nome" autoComplete="name" value={dados.nome} onChange={mudar('nome')} erro={erros.nome} />
          <Campo
            id="saiba-email"
            rotulo="E-mail"
            type="email"
            autoComplete="email"
            placeholder="nome@exemplo.com"
            value={dados.email}
            onChange={mudar('email')}
            erro={erros.email}
          />
          <label className={erros.consentimento ? 'consentimento com-erro' : 'consentimento'}>
            <input
              type="checkbox"
              checked={dados.consentimento}
              onChange={(evento) => setDados({ ...dados, consentimento: evento.target.checked })}
            />
            <span>
              Autorizo o uso do meu nome e e-mail apenas para receber este conteúdo do Oráculo, conforme a Lei Geral de
              Proteção de Dados (LGPD).
            </span>
          </label>
          {erros.consentimento && (
            <p className="campo-erro" role="alert">
              {erros.consentimento}
            </p>
          )}
          {erro && (
            <p className="erro" role="alert">
              {erro}
            </p>
          )}
          <button type="submit" className="botao-principal" disabled={etapa === 'enviando'}>
            {etapa === 'enviando' ? 'Buscando conteúdos e enviando...' : 'Receber por e-mail'}
          </button>
        </form>
      )}
    </dialog>
  )
}

export default ModalSaibaMais

import { useEffect, useRef, useState } from 'react'
import { buscarInstrucoesWhatsApp, consultarPedido, pedirSaibaMais } from '../api'
import { telefoneLegivel, useAutenticacao } from '../autenticacao/contexto'
import FormularioCadastro from './FormularioCadastro'
import FormularioEntrar from './FormularioEntrar'

const INTERVALO_CONSULTA = 2500
const TEMPO_MAXIMO = 90000

function linkWhatsApp(numero, codigo) {
  return `https://wa.me/${numero.replace(/\D/g, '')}?text=${encodeURIComponent(codigo)}`
}

// "Quer saber mais?": envia resposta, 2 sites e 2 vídeos para o WhatsApp da conta.
// Sem login, explica o que acontece e oferece criar a conta ou entrar, sem perder a resposta.
function ModalSaibaMais({ perguntaId, aoFechar }) {
  const dialogo = useRef(null)
  const { usuario } = useAutenticacao()
  const [aba, setAba] = useState('cadastro')
  // Antes do formulário, quem não tem conta vê o que acontece ao informar nome e WhatsApp
  const [explicado, setExplicado] = useState(false)
  const [etapa, setEtapa] = useState('confirmar') // confirmar | enviando | enviado
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
    setErro('Não conseguimos enviar a mensagem agora. Confira as instruções acima e tente novamente mais tarde.')
    setEtapa('confirmar')
  }

  async function enviar() {
    setErro(null)
    setEtapa('enviando')
    try {
      const pedido = await pedirSaibaMais(perguntaId)
      await acompanhar(pedido.id)
    } catch (falha) {
      setErro(falha.message)
      setEtapa('confirmar')
    }
  }

  const fechar = () => dialogo.current.close()
  const podeReceber = usuario?.telefone

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
          <h2 id="titulo-modal">Pronto! Confira seu WhatsApp</h2>
          <p>Enviamos a resposta, 2 sites e 2 vídeos sobre o assunto para {telefoneLegivel(usuario.telefone)}.</p>
          <button type="button" className="botao-principal" onClick={fechar}>
            Fechar
          </button>
        </div>
      ) : (
        <div className="modal-conteudo">
          <p className="chamada">Saiba mais</p>
          <h2 id="titulo-modal">Receba mais sobre o assunto no seu WhatsApp</h2>

          {!usuario && !explicado && (
            <>
              <p className="modal-texto">Veja o que acontece se você informar seu nome e seu WhatsApp:</p>
              <ol className="passos">
                <li>
                  <strong>Criamos sua conta no Oráculo</strong> com seu nome, seu WhatsApp e uma senha que você escolhe, para
                  entrar de novo depois.
                </li>
                <li>
                  <strong>Enviamos no seu WhatsApp</strong> esta resposta, <strong>2 sites</strong> e{' '}
                  <strong>2 vídeos do YouTube</strong> que explicam o assunto.
                </li>
                <li>
                  <strong>Se quiser</strong>, você escolhe temas para acompanhar e recebe as novidades deles no WhatsApp.
                </li>
              </ol>
              <p className="modal-aviso">
                Seu telefone é usado <strong>somente</strong> para enviar os conteúdos do Oráculo, conforme a Lei Geral de
                Proteção de Dados (LGPD). Nada é enviado sem a sua autorização.
              </p>
              <div className="acoes">
                <button type="button" className="botao-secundario" onClick={fechar}>
                  Agora não
                </button>
                <button type="button" className="botao-principal botao-compacto" onClick={() => setExplicado(true)}>
                  Quero receber
                </button>
              </div>
            </>
          )}

          {usuario && (
            <p className="modal-texto">
              Vamos enviar a resposta junto com <strong>2 sites</strong> e <strong>2 vídeos do YouTube</strong> que explicam
              o assunto.
            </p>
          )}

          {!usuario && explicado && (
            <>
              <p className="modal-texto">Informe seu nome e seu WhatsApp, ou entre se já tiver uma conta.</p>
              <div className="abas" role="tablist">
                <button type="button" role="tab" aria-selected={aba === 'cadastro'} onClick={() => setAba('cadastro')}>
                  Criar conta
                </button>
                <button type="button" role="tab" aria-selected={aba === 'entrar'} onClick={() => setAba('entrar')}>
                  Já tenho conta
                </button>
              </div>
              {aba === 'cadastro' ? <FormularioCadastro prefixo="modal-cadastro" /> : <FormularioEntrar prefixo="modal-entrar" />}
            </>
          )}

          {usuario && !podeReceber && (
            <p className="alerta alerta-erro" role="alert">
              Sua conta não tem um telefone cadastrado. Entre com uma conta de WhatsApp para receber o conteúdo.
            </p>
          )}

          {podeReceber && (
            <>
              {sandbox && (
                <div className="modal-aviso">
                  <strong>Ambiente de teste:</strong> antes, envie a mensagem <code>{sandbox.codigo}</code> para o WhatsApp{' '}
                  <strong>{sandbox.numero}</strong>. O WhatsApp só libera o envio até 24 horas depois da sua última
                  mensagem para esse número.{' '}
                  <a href={linkWhatsApp(sandbox.numero, sandbox.codigo)} target="_blank" rel="noreferrer">
                    Abrir no WhatsApp ↗
                  </a>
                </div>
              )}
              <p className="destino-envio">
                Enviar para <strong>{telefoneLegivel(usuario.telefone)}</strong> ({usuario.nome})
              </p>
              {erro && (
                <p className="erro" role="alert">
                  {erro}
                </p>
              )}
              <button type="button" className="botao-principal" onClick={enviar} disabled={etapa === 'enviando'}>
                {etapa === 'enviando' ? 'Buscando conteúdos e enviando...' : 'Receber no WhatsApp'}
              </button>
            </>
          )}
        </div>
      )}
    </dialog>
  )
}

export default ModalSaibaMais

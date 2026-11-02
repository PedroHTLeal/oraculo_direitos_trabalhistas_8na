import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { criarInscricao, excluirInscricao, listarInscricoes, listarTemas } from '../../api'
import Campo from '../../components/Campo'
import { formatarTelefone } from '../../telefone'
import { regras, validar } from '../../validacao'

const ESQUEMA = {
  tema_id: [regras.obrigatorio('tema')],
  telefone: [regras.obrigatorio('telefone'), regras.telefone()],
  consentimento: [(valor) => (valor ? null : 'É preciso autorizar o envio de atualizações pelo WhatsApp.')],
}

// Acompanhamento de temas (UC06, RF12)
function MeusTemas() {
  const boasVindas = useLocation().state?.boasVindas
  const [temas, setTemas] = useState([])
  const [inscricoes, setInscricoes] = useState(null)
  const [dados, setDados] = useState({ tema_id: '', telefone: '', consentimento: false })
  const [erros, setErros] = useState({})
  const [erroGeral, setErroGeral] = useState(null)
  const [mensagem, setMensagem] = useState(boasVindas ? 'Conta criada! Escolha abaixo os temas que quer acompanhar.' : null)
  const [salvando, setSalvando] = useState(false)

  useEffect(() => {
    listarTemas()
      .then(setTemas)
      .catch(() => setTemas([]))
    listarInscricoes()
      .then(setInscricoes)
      .catch((falha) => setErroGeral(falha.message))
  }, [])

  async function enviar(evento) {
    evento.preventDefault()
    const encontrados = validar(dados, ESQUEMA)
    setErros(encontrados)
    setErroGeral(null)
    if (Object.keys(encontrados).length) return

    setSalvando(true)
    try {
      const nova = await criarInscricao(Number(dados.tema_id), dados.telefone, dados.consentimento)
      setInscricoes([...inscricoes, nova])
      setDados({ ...dados, tema_id: '' })
      setMensagem(`Pronto! Você vai receber as novidades sobre ${nova.tema}.`)
    } catch (falha) {
      setErroGeral(falha.message)
    } finally {
      setSalvando(false)
    }
  }

  async function cancelar(inscricao) {
    try {
      await excluirInscricao(inscricao.id)
      setInscricoes(inscricoes.filter((i) => i.id !== inscricao.id))
      setMensagem(`Você deixou de acompanhar ${inscricao.tema}.`)
    } catch (falha) {
      setErroGeral(falha.message)
    }
  }

  const acompanhados = new Set((inscricoes || []).map((i) => i.tema_id))

  return (
    <section>
      <h1>Meus temas</h1>
      <p className="subtitulo">Escolha os assuntos sobre os quais quer receber novidades no seu WhatsApp.</p>

      {mensagem && (
        <p className="alerta alerta-sucesso" role="status">
          {mensagem}
        </p>
      )}
      {erroGeral && (
        <p className="alerta alerta-erro" role="alert">
          {erroGeral}
        </p>
      )}

      <form className="cartao-formulario formulario-largo" onSubmit={enviar} noValidate>
        <h2>Acompanhar um tema</h2>
        <Campo id="tema" rotulo="Tema" erro={erros.tema_id}>
          <select
            id="tema"
            value={dados.tema_id}
            onChange={(evento) => setDados({ ...dados, tema_id: evento.target.value })}
            aria-invalid={Boolean(erros.tema_id)}
          >
            <option value="">Escolha um tema</option>
            {temas.map((tema) => (
              <option key={tema.id} value={tema.id} disabled={acompanhados.has(tema.id)}>
                {tema.nome}
                {acompanhados.has(tema.id) ? ' (já acompanha)' : ''}
              </option>
            ))}
          </select>
        </Campo>
        <Campo
          id="telefone"
          rotulo="WhatsApp com DDD"
          type="tel"
          inputMode="numeric"
          placeholder="(51) 99999-8888"
          value={dados.telefone}
          onChange={(evento) => setDados({ ...dados, telefone: formatarTelefone(evento.target.value) })}
          erro={erros.telefone}
        />
        <label className={erros.consentimento ? 'consentimento com-erro' : 'consentimento'}>
          <input
            type="checkbox"
            checked={dados.consentimento}
            onChange={(evento) => setDados({ ...dados, consentimento: evento.target.checked })}
          />
          <span>Autorizo o uso do meu telefone apenas para receber atualizações deste tema (LGPD).</span>
        </label>
        {erros.consentimento && (
          <p className="campo-erro" role="alert">
            {erros.consentimento}
          </p>
        )}
        <button type="submit" className="botao-principal botao-compacto" disabled={salvando}>
          {salvando ? 'Salvando...' : 'Acompanhar tema'}
        </button>
      </form>

      <h2>Temas que você acompanha</h2>
      {inscricoes && inscricoes.length === 0 && (
        <div className="estado-vazio">
          <p>Você ainda não acompanha nenhum tema.</p>
        </div>
      )}
      {inscricoes && inscricoes.length > 0 && (
        <ul className="lista-inscricoes">
          {inscricoes.map((inscricao) => (
            <li key={inscricao.id}>
              <div>
                <strong>{inscricao.tema}</strong>
                <span className="texto-apoio"> · {inscricao.telefone}</span>
              </div>
              <button type="button" className="botao-texto-perigo" onClick={() => cancelar(inscricao)}>
                Deixar de acompanhar
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export default MeusTemas

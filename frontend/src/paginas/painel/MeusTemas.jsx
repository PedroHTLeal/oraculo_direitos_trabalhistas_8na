import { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { criarInscricao, excluirInscricao, listarInscricoes, listarMinhasAtualizacoes, listarTemas } from '../../api'
import { telefoneLegivel, useAutenticacao } from '../../autenticacao/contexto'
import Campo from '../../components/Campo'
import { regras, validar } from '../../validacao'

const ESQUEMA = {
  tema_id: [regras.obrigatorio('tema')],
}

// Acompanhamento de temas (UC06, RF12)
function MeusTemas() {
  const { usuario } = useAutenticacao()
  const boasVindas = useLocation().state?.boasVindas
  const [temas, setTemas] = useState([])
  const [inscricoes, setInscricoes] = useState(null)
  const [dados, setDados] = useState({ tema_id: '' })
  const [erros, setErros] = useState({})
  const [erroGeral, setErroGeral] = useState(null)
  const [mensagem, setMensagem] = useState(boasVindas ? 'Conta criada! Escolha abaixo os temas que quer acompanhar.' : null)
  const [salvando, setSalvando] = useState(false)
  const [novidades, setNovidades] = useState([])

  useEffect(() => {
    listarTemas()
      .then(setTemas)
      .catch(() => setTemas([]))
    listarInscricoes()
      .then(setInscricoes)
      .catch((falha) => setErroGeral(falha.message))
    listarMinhasAtualizacoes()
      .then(setNovidades)
      .catch(() => setNovidades([]))
  }, [])

  async function enviar(evento) {
    evento.preventDefault()
    const encontrados = validar(dados, ESQUEMA)
    setErros(encontrados)
    setErroGeral(null)
    if (Object.keys(encontrados).length) return

    setSalvando(true)
    try {
      const nova = await criarInscricao(Number(dados.tema_id))
      setInscricoes([...inscricoes, nova])
      setDados({ tema_id: '' })
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
      <p className="subtitulo">
        Escolha os assuntos sobre os quais quer receber novidades. Elas chegam no WhatsApp{' '}
        <strong>{telefoneLegivel(usuario?.telefone)}</strong>.
      </p>

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
            onChange={(evento) => setDados({ tema_id: evento.target.value })}
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
              <strong>{inscricao.tema}</strong>
              <button type="button" className="botao-texto-perigo" onClick={() => cancelar(inscricao)}>
                Deixar de acompanhar
              </button>
            </li>
          ))}
        </ul>
      )}

      <h2>Novidades dos seus temas</h2>
      {novidades.length === 0 ? (
        <div className="estado-vazio">
          <p>Nenhuma novidade publicada nos temas que você acompanha.</p>
        </div>
      ) : (
        <ul className="lista-trechos">
          {novidades.map((n) => (
            <li key={n.id} className="item-trecho">
              <div>
                <p className="item-tema">
                  {n.tema} · {new Date(n.publicado_em).toLocaleDateString('pt-BR')}
                </p>
                <h2>{n.titulo}</h2>
                <p className="novidade-texto">{n.conteudo}</p>
                {n.url && (
                  <a href={n.url} target="_blank" rel="noreferrer" className="link-acao">
                    Saiba mais ↗
                  </a>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export default MeusTemas

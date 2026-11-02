import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { listarTemas, obterTrecho, salvarTrecho } from '../../api'
import Campo from '../../components/Campo'
import { regras, validar } from '../../validacao'

const ESQUEMA = {
  tema_id: [regras.obrigatorio('tema')],
  secao: [regras.obrigatorio('subtítulo'), regras.minimo('subtítulo', 2), regras.maximo('subtítulo', 200)],
  texto: [regras.obrigatorio('texto'), regras.minimo('texto', 10), regras.maximo('texto', 5000)],
}

// Cadastro e edição de um trecho (rotas /painel/base/novo e /painel/base/:id)
function FormularioTrecho() {
  const { id } = useParams()
  const editando = id !== 'novo'
  const perguntaDeOrigem = useSearchParams()[0].get('pergunta')
  const navegar = useNavigate()
  const [temas, setTemas] = useState([])
  const [dados, setDados] = useState({ tema_id: '', secao: '', texto: '' })
  const [erros, setErros] = useState({})
  const [erroGeral, setErroGeral] = useState(null)
  const [carregando, setCarregando] = useState(editando)
  const [salvando, setSalvando] = useState(false)

  useEffect(() => {
    listarTemas()
      .then(setTemas)
      .catch((falha) => setErroGeral(falha.message))
    if (!editando) return
    obterTrecho(id)
      .then((trecho) => setDados({ tema_id: String(trecho.tema_id), secao: trecho.secao, texto: trecho.texto }))
      .catch((falha) => setErroGeral(falha.message))
      .finally(() => setCarregando(false))
  }, [id, editando])

  const mudar = (campo) => (evento) => setDados({ ...dados, [campo]: evento.target.value })

  async function enviar(evento) {
    evento.preventDefault()
    const encontrados = validar(dados, ESQUEMA)
    setErros(encontrados)
    setErroGeral(null)
    if (Object.keys(encontrados).length) return

    setSalvando(true)
    try {
      await salvarTrecho(editando ? id : null, {
        tema_id: Number(dados.tema_id),
        secao: dados.secao.trim(),
        texto: dados.texto.trim(),
      })
      navegar('/painel/base', { state: { mensagem: editando ? 'Trecho atualizado.' : 'Trecho cadastrado.' } })
    } catch (falha) {
      setErroGeral(falha.message)
      setSalvando(false)
    }
  }

  return (
    <section>
      <p className="trilha">
        <Link to="/painel/base">Base de conhecimento</Link> / {editando ? 'Editar trecho' : 'Novo trecho'}
      </p>
      <h1>{editando ? 'Editar trecho' : 'Novo trecho'}</h1>

      {perguntaDeOrigem && !editando && (
        <p className="alerta alerta-info">
          Pergunta sem resposta: <strong>{perguntaDeOrigem}</strong>
          <br />
          Cadastre o conteúdo da cartilha que responde a ela; a IA passa a usá-lo nas próximas perguntas.
        </p>
      )}

      {erroGeral && (
        <p className="alerta alerta-erro" role="alert">
          {erroGeral}
        </p>
      )}

      {carregando ? (
        <p>Carregando...</p>
      ) : (
        <form className="cartao-formulario formulario-largo" onSubmit={enviar} noValidate>
          <Campo id="tema" rotulo="Tema" erro={erros.tema_id}>
            <select
              id="tema"
              value={dados.tema_id}
              onChange={mudar('tema_id')}
              aria-invalid={Boolean(erros.tema_id)}
              aria-describedby={erros.tema_id ? 'tema-erro' : undefined}
            >
              <option value="">Escolha um tema</option>
              {temas.map((tema) => (
                <option key={tema.id} value={tema.id}>
                  {tema.nome}
                </option>
              ))}
            </select>
          </Campo>
          <Campo
            id="secao"
            rotulo="Subtítulo"
            value={dados.secao}
            onChange={mudar('secao')}
            erro={erros.secao}
            ajuda="Exemplo: Pagamento das férias"
            maxLength={200}
          />
          <Campo
            id="texto"
            rotulo="Texto"
            erro={erros.texto}
            ajuda={`${dados.texto.length}/5000 caracteres. Use a linguagem da cartilha.`}
          >
            <textarea
              id="texto"
              rows={10}
              value={dados.texto}
              onChange={mudar('texto')}
              maxLength={5000}
              aria-invalid={Boolean(erros.texto)}
              aria-describedby={erros.texto ? 'texto-erro' : 'texto-ajuda'}
            />
          </Campo>
          <div className="acoes">
            <Link to="/painel/base" className="botao-secundario">
              Cancelar
            </Link>
            <button type="submit" className="botao-principal botao-compacto" disabled={salvando}>
              {salvando ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </form>
      )}
    </section>
  )
}

export default FormularioTrecho

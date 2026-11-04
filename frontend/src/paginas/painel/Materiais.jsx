import { useEffect, useRef, useState } from 'react'
import { excluirMaterial, listarMateriais, listarTemas, salvarMaterial } from '../../api'
import Campo from '../../components/Campo'
import ConfirmarExclusao from '../../components/ConfirmarExclusao'
import { regras, validar } from '../../validacao'

const TIPOS = { site: 'Site', video: 'Vídeo do YouTube' }
const LINK = /^https?:\/\/\S+$/

const ESQUEMA = {
  tema_id: [regras.obrigatorio('tema')],
  assunto: [regras.obrigatorio('assunto'), regras.minimo('assunto', 2), regras.maximo('assunto', 80)],
  palavras: [regras.obrigatorio('palavras-chave')],
  titulo: [regras.obrigatorio('título'), regras.minimo('título', 3), regras.maximo('título', 200)],
  url: [
    regras.obrigatorio('link'),
    (valor) => (LINK.test(String(valor).trim()) ? null : 'O link precisa começar com http:// ou https://.'),
    (valor, dados) =>
      dados.tipo !== 'video' || /youtube\.com\/watch|youtu\.be\//.test(valor) ? null : 'Para vídeos, use o link de um vídeo do YouTube.',
  ],
}

// Janela de cadastro e edição de um site ou vídeo
function FormularioMaterial({ material, temas, assuntos, aoSalvar, aoFechar }) {
  const dialogo = useRef(null)
  const [dados, setDados] = useState({
    tema_id: material?.tema_id ? String(material.tema_id) : '',
    assunto: material?.assunto || '',
    palavras: (material?.palavras_chave || []).join(', '),
    tipo: material?.tipo || 'video',
    titulo: material?.titulo || '',
    url: material?.url || '',
    ordem: String(material?.ordem || 1),
  })
  const [erros, setErros] = useState({})
  const [erroGeral, setErroGeral] = useState(null)
  const [salvando, setSalvando] = useState(false)

  useEffect(() => {
    dialogo.current?.showModal()
  }, [])

  const mudar = (campo) => (evento) => setDados({ ...dados, [campo]: evento.target.value })

  async function enviar(evento) {
    evento.preventDefault()
    const encontrados = validar(dados, ESQUEMA)
    setErros(encontrados)
    setErroGeral(null)
    if (Object.keys(encontrados).length) return

    setSalvando(true)
    try {
      await salvarMaterial(material?.id, {
        tema_id: Number(dados.tema_id),
        assunto: dados.assunto.trim(),
        palavras_chave: dados.palavras.split(',').map((p) => p.trim()).filter(Boolean),
        tipo: dados.tipo,
        titulo: dados.titulo.trim(),
        url: dados.url.trim(),
        ordem: Number(dados.ordem),
      })
      aoSalvar(material ? 'Link atualizado.' : 'Link cadastrado.')
      dialogo.current.close()
    } catch (falha) {
      setErroGeral(falha.message)
      setSalvando(false)
    }
  }

  return (
    <dialog ref={dialogo} className="modal" onClose={aoFechar} aria-labelledby="titulo-material">
      <button type="button" className="modal-fechar" onClick={() => dialogo.current.close()} aria-label="Fechar">
        ×
      </button>
      <form onSubmit={enviar} noValidate>
        <h2 id="titulo-material">{material ? 'Editar link' : 'Novo site ou vídeo'}</h2>
        {erroGeral && (
          <p className="alerta alerta-erro" role="alert">
            {erroGeral}
          </p>
        )}
        <Campo id="material-tema" rotulo="Tema da cartilha" erro={erros.tema_id}>
          <select id="material-tema" value={dados.tema_id} onChange={mudar('tema_id')} aria-invalid={Boolean(erros.tema_id)}>
            <option value="">Escolha o tema</option>
            {temas.map((tema) => (
              <option key={tema.id} value={tema.id}>
                {tema.nome}
              </option>
            ))}
          </select>
        </Campo>
        <Campo
          id="material-assunto"
          rotulo="Assunto"
          placeholder="Ex.: Férias"
          list="assuntos-cadastrados"
          value={dados.assunto}
          onChange={mudar('assunto')}
          erro={erros.assunto}
          ajuda="Links do mesmo assunto são enviados juntos. Use o mesmo nome para agrupar."
        />
        <datalist id="assuntos-cadastrados">
          {assuntos.map((assunto) => (
            <option key={assunto} value={assunto} />
          ))}
        </datalist>
        <Campo
          id="material-palavras"
          rotulo="Palavras-chave"
          placeholder="Ex.: ferias, descanso anual"
          value={dados.palavras}
          onChange={mudar('palavras')}
          erro={erros.palavras}
          ajuda="Separadas por vírgula. Se uma delas aparecer na pergunta, a pessoa recebe os links deste assunto."
        />
        <Campo id="material-tipo" rotulo="Tipo">
          <select id="material-tipo" value={dados.tipo} onChange={mudar('tipo')}>
            {Object.entries(TIPOS).map(([valor, nome]) => (
              <option key={valor} value={valor}>
                {nome}
              </option>
            ))}
          </select>
        </Campo>
        <Campo id="material-titulo" rotulo="Título" value={dados.titulo} onChange={mudar('titulo')} erro={erros.titulo} />
        <Campo
          id="material-url"
          rotulo="Link"
          type="url"
          placeholder="https://"
          value={dados.url}
          onChange={mudar('url')}
          erro={erros.url}
        />
        <Campo id="material-ordem" rotulo="Ordem no e-mail" ajuda="1 aparece primeiro.">
          <select id="material-ordem" value={dados.ordem} onChange={mudar('ordem')}>
            {[1, 2, 3, 4, 5].map((n) => (
              <option key={n} value={n}>
                {n}
              </option>
            ))}
          </select>
        </Campo>
        <button type="submit" className="botao-principal" disabled={salvando}>
          {salvando ? 'Salvando...' : 'Salvar'}
        </button>
      </form>
    </dialog>
  )
}

// Sites e vídeos enviados no "Saber mais", escolhidos pela equipe por assunto
function Materiais() {
  const [materiais, setMateriais] = useState(null)
  const [temas, setTemas] = useState([])
  const [erro, setErro] = useState(null)
  const [mensagem, setMensagem] = useState(null)
  const [editando, setEditando] = useState(undefined) // undefined: fechado; null: novo
  const [paraExcluir, setParaExcluir] = useState(null)
  const [recarregar, setRecarregar] = useState(0)

  useEffect(() => {
    Promise.all([listarMateriais(), listarTemas()])
      .then(([lista, todosTemas]) => {
        setMateriais(lista)
        setTemas(todosTemas)
      })
      .catch((falha) => setErro(falha.message))
  }, [recarregar])

  const atualizar = (texto) => {
    setMensagem(texto)
    setRecarregar((n) => n + 1)
  }

  // Agrupa por assunto, como os links seguem no e-mail
  const porAssunto = {}
  for (const material of materiais || []) (porAssunto[material.assunto] ||= []).push(material)
  const assuntos = Object.keys(porAssunto)

  return (
    <section>
      <div className="cabecalho-secao">
        <div>
          <h1>Sites e vídeos do Saber mais</h1>
          <p className="subtitulo">
            Links enviados por e-mail a quem pede para saber mais. O assunto é escolhido pelas palavras-chave da pergunta; sem
            assunto cadastrado, a pessoa recebe a página da cartilha e o texto da lei.
          </p>
        </div>
        <button type="button" className="botao-principal botao-compacto" onClick={() => setEditando(null)}>
          + Novo link
        </button>
      </div>

      {mensagem && (
        <p className="alerta alerta-sucesso" role="status">
          {mensagem}
          <button type="button" className="alerta-fechar" onClick={() => setMensagem(null)} aria-label="Fechar aviso">
            ×
          </button>
        </p>
      )}
      {erro && (
        <p className="alerta alerta-erro" role="alert">
          {erro}
        </p>
      )}

      {materiais && !assuntos.length && <p className="texto-apoio">Nenhum link cadastrado ainda.</p>}

      {assuntos.map((assunto) => (
        <div key={assunto} className="grupo-materiais">
          <h2>{assunto}</h2>
          <p className="texto-apoio">
            Tema: {porAssunto[assunto][0].tema} · Palavras-chave: {porAssunto[assunto][0].palavras_chave.join(', ')}
          </p>
          <div className="tabela-rolagem">
            <table className="tabela">
              <thead>
                <tr>
                  <th>Tipo</th>
                  <th>Título</th>
                  <th>Ordem</th>
                  <th>
                    <span className="somente-leitor">Ações</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {porAssunto[assunto].map((material) => (
                  <tr key={material.id}>
                    <td>
                      <span className={`selo ${material.tipo === 'video' ? 'selo-aviso' : 'selo-sucesso'}`}>{material.tipo === 'video' ? 'Vídeo' : 'Site'}</span>
                    </td>
                    <td>
                      <a href={material.url} target="_blank" rel="noreferrer">
                        {material.titulo}
                      </a>
                    </td>
                    <td>{material.ordem}</td>
                    <td className="celula-acoes">
                      <button type="button" className="botao-secundario botao-compacto" onClick={() => setEditando(material)}>
                        Editar
                      </button>
                      <button type="button" className="botao-texto-perigo" onClick={() => setParaExcluir(material)}>
                        Excluir
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}

      {editando !== undefined && (
        <FormularioMaterial
          material={editando}
          temas={temas}
          assuntos={assuntos}
          aoSalvar={atualizar}
          aoFechar={() => setEditando(undefined)}
        />
      )}
      {paraExcluir && (
        <ConfirmarExclusao
          titulo="Excluir link?"
          descricao={`"${paraExcluir.titulo}" deixa de ser enviado no assunto ${paraExcluir.assunto}.`}
          aoConfirmar={async () => {
            await excluirMaterial(paraExcluir.id)
            atualizar('Link excluído.')
          }}
          aoFechar={() => setParaExcluir(null)}
        />
      )}
    </section>
  )
}

export default Materiais

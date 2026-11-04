import { useEffect, useRef, useState } from 'react'
import { excluirSinonimo, listarSinonimos, salvarSinonimo } from '../../api'
import Campo from '../../components/Campo'
import ConfirmarExclusao from '../../components/ConfirmarExclusao'
import { regras, validar } from '../../validacao'

const ESQUEMA = {
  termo: [regras.obrigatorio('palavra'), regras.minimo('palavra', 2), regras.maximo('palavra', 60)],
  equivalentes: [regras.obrigatorio('palavras da cartilha'), regras.minimo('palavras da cartilha', 2), regras.maximo('palavras da cartilha', 200)],
}

// Janela de cadastro e edição de um sinônimo
function FormularioSinonimo({ sinonimo, aoSalvar, aoFechar }) {
  const dialogo = useRef(null)
  const [dados, setDados] = useState({ termo: sinonimo?.termo || '', equivalentes: sinonimo?.equivalentes || '' })
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
      await salvarSinonimo(sinonimo?.termo, { termo: dados.termo.trim(), equivalentes: dados.equivalentes.trim() })
      aoSalvar(sinonimo ? 'Sinônimo atualizado.' : 'Sinônimo cadastrado.')
      dialogo.current.close()
    } catch (falha) {
      setErroGeral(falha.message)
      setSalvando(false)
    }
  }

  return (
    <dialog ref={dialogo} className="modal" onClose={aoFechar} aria-labelledby="titulo-sinonimo">
      <button type="button" className="modal-fechar" onClick={() => dialogo.current.close()} aria-label="Fechar">
        ×
      </button>
      <form onSubmit={enviar} noValidate>
        <h2 id="titulo-sinonimo">{sinonimo ? 'Editar sinônimo' : 'Novo sinônimo'}</h2>
        {erroGeral && (
          <p className="alerta alerta-erro" role="alert">
            {erroGeral}
          </p>
        )}
        <Campo
          id="sinonimo-termo"
          rotulo="Palavra que as pessoas usam"
          placeholder="Ex.: patrão"
          value={dados.termo}
          onChange={mudar('termo')}
          erro={erros.termo}
        />
        <Campo
          id="sinonimo-equivalentes"
          rotulo="Palavras da cartilha"
          placeholder="Ex.: empregador"
          value={dados.equivalentes}
          onChange={mudar('equivalentes')}
          erro={erros.equivalentes}
          ajuda="Separe por espaço se houver mais de uma. Acentos e maiúsculas são ignorados."
        />
        <button type="submit" className="botao-principal" disabled={salvando}>
          {salvando ? 'Salvando...' : 'Salvar'}
        </button>
      </form>
    </dialog>
  )
}

// Palavras do dia a dia que a busca traduz para os termos da cartilha
function Sinonimos() {
  const [sinonimos, setSinonimos] = useState(null)
  const [filtro, setFiltro] = useState('')
  const [erro, setErro] = useState(null)
  const [mensagem, setMensagem] = useState(null)
  const [editando, setEditando] = useState(undefined) // undefined: fechado; null: novo
  const [paraExcluir, setParaExcluir] = useState(null)
  const [recarregar, setRecarregar] = useState(0)

  useEffect(() => {
    listarSinonimos()
      .then(setSinonimos)
      .catch((falha) => setErro(falha.message))
  }, [recarregar])

  const atualizar = (texto) => {
    setMensagem(texto)
    setRecarregar((n) => n + 1)
  }

  const busca = filtro.trim().toLowerCase()
  const visiveis = (sinonimos || []).filter((s) => !busca || `${s.termo} ${s.equivalentes}`.includes(busca))

  return (
    <section>
      <div className="cabecalho-secao">
        <div>
          <h1>Sinônimos da busca</h1>
          <p className="subtitulo">
            Palavras do dia a dia que a busca traduz para os termos da cartilha. Ex.: quem pergunta sobre o “patrão” encontra
            os trechos sobre o “empregador”.
          </p>
        </div>
        <button type="button" className="botao-principal botao-compacto" onClick={() => setEditando(null)}>
          + Novo sinônimo
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

      {sinonimos && (
        <>
          <div className="filtro-sinonimos">
            <Campo id="filtro-sinonimos" rotulo="Procurar" placeholder="Ex.: demitido" value={filtro} onChange={(e) => setFiltro(e.target.value)} />
          </div>
          <p className="texto-apoio">
            {visiveis.length} de {sinonimos.length} sinônimos
          </p>
          <div className="tabela-rolagem">
            <table className="tabela">
              <thead>
                <tr>
                  <th>Palavra que as pessoas usam</th>
                  <th>Palavras da cartilha</th>
                  <th>
                    <span className="somente-leitor">Ações</span>
                  </th>
                </tr>
              </thead>
              <tbody>
                {visiveis.map((sinonimo) => (
                  <tr key={sinonimo.termo}>
                    <td>{sinonimo.termo}</td>
                    <td>{sinonimo.equivalentes}</td>
                    <td className="celula-acoes">
                      <button type="button" className="botao-secundario botao-compacto" onClick={() => setEditando(sinonimo)}>
                        Editar
                      </button>
                      <button type="button" className="botao-texto-perigo" onClick={() => setParaExcluir(sinonimo)}>
                        Excluir
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {editando !== undefined && (
        <FormularioSinonimo sinonimo={editando} aoSalvar={atualizar} aoFechar={() => setEditando(undefined)} />
      )}
      {paraExcluir && (
        <ConfirmarExclusao
          titulo="Excluir sinônimo?"
          descricao={`A busca deixa de traduzir "${paraExcluir.termo}" para "${paraExcluir.equivalentes}".`}
          aoConfirmar={async () => {
            await excluirSinonimo(paraExcluir.termo)
            atualizar('Sinônimo excluído.')
          }}
          aoFechar={() => setParaExcluir(null)}
        />
      )}
    </section>
  )
}

export default Sinonimos

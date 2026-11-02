import { useEffect, useState } from 'react'
import { Link, useLocation, useSearchParams } from 'react-router-dom'
import { excluirTrecho, listarTemas, listarTrechos } from '../../api'
import ConfirmarExclusao from '../../components/ConfirmarExclusao'

// Consulta do CRUD principal: lista, filtros e exclusão dos trechos da cartilha
function BaseConhecimento() {
  const [parametros, setParametros] = useSearchParams()
  const temaId = parametros.get('tema') || ''
  const busca = parametros.get('busca') || ''
  const pagina = Number(parametros.get('pagina') || 1)

  const [temas, setTemas] = useState([])
  const [resultado, setResultado] = useState(null)
  const [erro, setErro] = useState(null)
  const [termo, setTermo] = useState(busca)
  const [paraExcluir, setParaExcluir] = useState(null)
  const [mensagem, setMensagem] = useState(useLocation().state?.mensagem || null)
  const [recarregar, setRecarregar] = useState(0)

  useEffect(() => {
    listarTemas()
      .then(setTemas)
      .catch(() => setTemas([]))
  }, [])

  useEffect(() => {
    setErro(null)
    listarTrechos({ temaId, busca, pagina })
      .then(setResultado)
      .catch((falha) => setErro(falha.message))
  }, [temaId, busca, pagina, recarregar])

  function filtrar(mudancas) {
    const novos = { tema: temaId, busca, ...mudancas, pagina: mudancas.pagina || 1 }
    setParametros(Object.fromEntries(Object.entries(novos).filter(([, valor]) => valor)))
  }

  const totalPaginas = resultado ? Math.max(1, Math.ceil(resultado.total / resultado.por_pagina)) : 1

  return (
    <section>
      <div className="cabecalho-secao">
        <div>
          <h1>Base de conhecimento</h1>
          <p className="subtitulo">Trechos da cartilha do TRT4 que a IA usa para responder às perguntas.</p>
        </div>
        <Link to="/painel/base/novo" className="botao-principal botao-compacto">
          + Novo trecho
        </Link>
      </div>

      {mensagem && (
        <p className="alerta alerta-sucesso" role="status">
          {mensagem}
          <button type="button" className="alerta-fechar" onClick={() => setMensagem(null)} aria-label="Fechar aviso">
            ×
          </button>
        </p>
      )}

      <form
        className="filtros"
        onSubmit={(evento) => {
          evento.preventDefault()
          filtrar({ busca: termo.trim() })
        }}
      >
        <label className="filtro">
          <span>Tema</span>
          <select value={temaId} onChange={(evento) => filtrar({ tema: evento.target.value })}>
            <option value="">Todos os temas</option>
            {temas.map((tema) => (
              <option key={tema.id} value={tema.id}>
                {tema.nome}
              </option>
            ))}
          </select>
        </label>
        <label className="filtro filtro-busca">
          <span>Buscar no texto</span>
          <input type="search" value={termo} maxLength={100} onChange={(evento) => setTermo(evento.target.value)} />
        </label>
        <button type="submit" className="botao-secundario">
          Buscar
        </button>
      </form>

      {erro && (
        <p className="alerta alerta-erro" role="alert">
          {erro}
        </p>
      )}

      {resultado && resultado.itens.length === 0 && (
        <div className="estado-vazio">
          <p>Nenhum trecho encontrado com esses filtros.</p>
        </div>
      )}

      {resultado && resultado.itens.length > 0 && (
        <>
          <p className="contagem">{resultado.total} trechos encontrados</p>
          <ul className="lista-trechos">
            {resultado.itens.map((trecho) => (
              <li key={trecho.id} className="item-trecho">
                <div>
                  <p className="item-tema">{trecho.tema}</p>
                  <h2>{trecho.secao}</h2>
                  <p className="item-texto">{trecho.texto}</p>
                </div>
                <div className="item-acoes">
                  <Link to={`/painel/base/${trecho.id}`} className="botao-secundario botao-compacto">
                    Editar
                  </Link>
                  <button type="button" className="botao-texto-perigo" onClick={() => setParaExcluir(trecho)}>
                    Excluir
                  </button>
                </div>
              </li>
            ))}
          </ul>

          {totalPaginas > 1 && (
            <nav className="paginacao" aria-label="Páginas">
              <button type="button" disabled={pagina <= 1} onClick={() => filtrar({ pagina: pagina - 1 })}>
                ← Anterior
              </button>
              <span>
                Página {pagina} de {totalPaginas}
              </span>
              <button type="button" disabled={pagina >= totalPaginas} onClick={() => filtrar({ pagina: pagina + 1 })}>
                Próxima →
              </button>
            </nav>
          )}
        </>
      )}

      {paraExcluir && (
        <ConfirmarExclusao
          titulo="Excluir trecho?"
          descricao={`"${paraExcluir.secao}" (${paraExcluir.tema}) deixará de ser usado nas respostas. Essa ação não pode ser desfeita.`}
          aoConfirmar={async () => {
            await excluirTrecho(paraExcluir.id)
            setMensagem('Trecho excluído.')
            setRecarregar((n) => n + 1)
          }}
          aoFechar={() => setParaExcluir(null)}
        />
      )}
    </section>
  )
}

export default BaseConhecimento

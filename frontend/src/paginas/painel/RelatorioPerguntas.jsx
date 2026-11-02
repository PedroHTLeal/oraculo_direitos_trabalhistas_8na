import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { baixarCsv, listarTemas, relatorioPerguntas } from '../../api'

const formatarData = (texto) => new Date(texto).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })
const FILTROS = ['inicio', 'fim', 'resultado', 'tema_id', 'busca']

// Relatório de perguntas (Sprint 07): filtros por período, resultado, tema e texto, com exportação em CSV
function RelatorioPerguntas() {
  const [parametros, setParametros] = useSearchParams()
  const filtros = Object.fromEntries(FILTROS.map((f) => [f, parametros.get(f) || '']))
  const [rascunho, setRascunho] = useState(filtros)
  const [temas, setTemas] = useState([])
  const [relatorio, setRelatorio] = useState(null)
  const [erro, setErro] = useState(null)
  const chave = parametros.toString()

  useEffect(() => {
    listarTemas()
      .then(setTemas)
      .catch(() => setTemas([]))
  }, [])

  useEffect(() => {
    setErro(null)
    relatorioPerguntas(Object.fromEntries(new URLSearchParams(chave)))
      .then(setRelatorio)
      .catch((falha) => setErro(falha.message))
  }, [chave])

  function aplicar(evento) {
    evento.preventDefault()
    setParametros(Object.fromEntries(Object.entries(rascunho).filter(([, valor]) => valor)))
  }

  function limpar() {
    setRascunho(Object.fromEntries(FILTROS.map((f) => [f, ''])))
    setParametros({})
  }

  async function exportar() {
    setErro(null)
    try {
      await baixarCsv('/api/relatorios/perguntas', filtros)
    } catch (falha) {
      setErro(falha.message)
    }
  }

  const mudar = (campo) => (evento) => setRascunho({ ...rascunho, [campo]: evento.target.value })

  return (
    <section>
      <div className="cabecalho-secao">
        <div>
          <h1>Relatório de perguntas</h1>
          <p className="subtitulo">Tudo o que foi perguntado ao Oráculo, sem dados pessoais (UC08).</p>
        </div>
        <button type="button" className="botao-secundario" onClick={exportar}>
          Exportar CSV
        </button>
      </div>

      <form className="filtros" onSubmit={aplicar}>
        <label className="filtro filtro-data">
          <span>De</span>
          <input type="date" value={rascunho.inicio} onChange={mudar('inicio')} />
        </label>
        <label className="filtro filtro-data">
          <span>Até</span>
          <input type="date" value={rascunho.fim} onChange={mudar('fim')} />
        </label>
        <label className="filtro">
          <span>Resultado</span>
          <select value={rascunho.resultado} onChange={mudar('resultado')}>
            <option value="">Todos</option>
            <option value="respondida">Respondidas</option>
            <option value="sem_resposta">Sem informação</option>
          </select>
        </label>
        <label className="filtro">
          <span>Tema</span>
          <select value={rascunho.tema_id} onChange={mudar('tema_id')}>
            <option value="">Todos os temas</option>
            {temas.map((tema) => (
              <option key={tema.id} value={tema.id}>
                {tema.nome}
              </option>
            ))}
          </select>
        </label>
        <label className="filtro filtro-busca">
          <span>Pesquisar no texto</span>
          <input type="search" maxLength={100} value={rascunho.busca} onChange={mudar('busca')} />
        </label>
        <div className="filtros-acoes">
          <button type="submit" className="botao-principal botao-compacto">
            Filtrar
          </button>
          <button type="button" className="botao-secundario" onClick={limpar}>
            Limpar
          </button>
        </div>
      </form>

      {erro && (
        <p className="alerta alerta-erro" role="alert">
          {erro}
        </p>
      )}

      {relatorio && (
        <>
          <p className="contagem">{relatorio.total} pergunta(s) encontrada(s)</p>
          {relatorio.total === 0 ? (
            <div className="estado-vazio">
              <p>Nenhuma pergunta com esses filtros.</p>
            </div>
          ) : (
            <div className="tabela-rolagem">
              <table className="tabela">
                <thead>
                  <tr>
                    <th>Data</th>
                    <th>Pergunta</th>
                    <th>Resultado</th>
                    <th>Temas</th>
                    <th>
                      <span className="somente-leitor">Ações</span>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {relatorio.itens.map((p) => (
                    <tr key={p.id}>
                      <td className="celula-data">{formatarData(p.criado_em)}</td>
                      <td>{p.texto}</td>
                      <td>
                        <span className={p.encontrou ? 'selo selo-sucesso' : 'selo selo-aviso'}>
                          {p.encontrou ? 'Respondida' : 'Sem informação'}
                        </span>
                      </td>
                      <td>{p.temas.join(', ') || '—'}</td>
                      <td>
                        {!p.encontrou && (
                          <Link to={`/painel/base/novo?pergunta=${encodeURIComponent(p.texto)}`} className="link-acao">
                            Incluir na base
                          </Link>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </section>
  )
}

export default RelatorioPerguntas

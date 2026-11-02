import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { baixarCsv, relatorioHistorico } from '../../api'

const formatarData = (texto) => new Date(texto).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'medium' })
const FILTROS = ['inicio', 'fim', 'acao', 'entidade', 'busca']

// Histórico de operações (Sprint 07): quem fez o quê e quando. Somente administradores.
function Historico() {
  const [parametros, setParametros] = useSearchParams()
  const filtros = Object.fromEntries(FILTROS.map((f) => [f, parametros.get(f) || '']))
  const [rascunho, setRascunho] = useState(filtros)
  const [historico, setHistorico] = useState(null)
  const [erro, setErro] = useState(null)
  const chave = parametros.toString()

  useEffect(() => {
    setErro(null)
    relatorioHistorico(Object.fromEntries(new URLSearchParams(chave)))
      .then(setHistorico)
      .catch((falha) => setErro(falha.message))
  }, [chave])

  function aplicar(evento) {
    evento.preventDefault()
    setParametros(Object.fromEntries(Object.entries(rascunho).filter(([, valor]) => valor)))
  }

  async function exportar() {
    setErro(null)
    try {
      await baixarCsv('/api/relatorios/historico', filtros)
    } catch (falha) {
      setErro(falha.message)
    }
  }

  const mudar = (campo) => (evento) => setRascunho({ ...rascunho, [campo]: evento.target.value })
  const acoes = historico?.acoes || {}
  const entidades = historico?.entidades || {}

  return (
    <section>
      <div className="cabecalho-secao">
        <div>
          <h1>Histórico de operações</h1>
          <p className="subtitulo">Registro das ações feitas no sistema: logins, cadastros, alterações e envios.</p>
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
          <span>Ação</span>
          <select value={rascunho.acao} onChange={mudar('acao')}>
            <option value="">Todas</option>
            {Object.entries(acoes).map(([valor, nome]) => (
              <option key={valor} value={valor}>
                {nome}
              </option>
            ))}
          </select>
        </label>
        <label className="filtro">
          <span>Área</span>
          <select value={rascunho.entidade} onChange={mudar('entidade')}>
            <option value="">Todas</option>
            {Object.entries(entidades).map(([valor, nome]) => (
              <option key={valor} value={valor}>
                {nome}
              </option>
            ))}
          </select>
        </label>
        <label className="filtro filtro-busca">
          <span>Pesquisar (pessoa ou descrição)</span>
          <input type="search" maxLength={100} value={rascunho.busca} onChange={mudar('busca')} />
        </label>
        <div className="filtros-acoes">
          <button type="submit" className="botao-principal botao-compacto">
            Filtrar
          </button>
        </div>
      </form>

      {erro && (
        <p className="alerta alerta-erro" role="alert">
          {erro}
        </p>
      )}

      {historico && (
        <>
          <p className="contagem">{historico.total} registro(s)</p>
          {historico.total === 0 ? (
            <div className="estado-vazio">
              <p>Nenhum registro com esses filtros.</p>
            </div>
          ) : (
            <div className="tabela-rolagem">
              <table className="tabela">
                <thead>
                  <tr>
                    <th>Data</th>
                    <th>Pessoa</th>
                    <th>Ação</th>
                    <th>Área</th>
                    <th>Descrição</th>
                  </tr>
                </thead>
                <tbody>
                  {historico.itens.map((r) => (
                    <tr key={r.id}>
                      <td className="celula-data">{formatarData(r.criado_em)}</td>
                      <td>{r.usuario_nome || 'Visitante'}</td>
                      <td>{acoes[r.acao] || r.acao}</td>
                      <td>{entidades[r.entidade] || r.entidade}</td>
                      <td>{r.descricao}</td>
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

export default Historico

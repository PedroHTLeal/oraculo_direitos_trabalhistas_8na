import { useState } from 'react'

// Paleta validada (contraste e daltonismo): azul para respondidas, dourado escuro para sem resposta
const CORES = { respondidas: '#3557B7', semResposta: '#A87A08' }

// Dica que aparece ao passar o mouse (ou focar pelo teclado) sobre uma barra
function useDica() {
  const [dica, setDica] = useState(null)
  const mostrar = (texto) => (evento) => {
    const caixa = evento.currentTarget.closest('.grafico').getBoundingClientRect()
    const alvo = evento.currentTarget.getBoundingClientRect()
    setDica({ texto, x: alvo.left - caixa.left + alvo.width / 2, y: alvo.top - caixa.top })
  }
  return { dica, mostrar, esconder: () => setDica(null) }
}

function Dica({ dica }) {
  if (!dica) return null
  return (
    <div className="grafico-dica" style={{ left: dica.x, top: dica.y }} role="status">
      {dica.texto}
    </div>
  )
}

// Perguntas por data: barras empilhadas (respondidas + sem resposta)
export function BarrasPorData({ dados }) {
  const { dica, mostrar, esconder } = useDica()
  const maximo = Math.max(1, ...dados.map((d) => d.total))
  const mostrarRotulo = (indice) => dados.length <= 12 || indice % Math.ceil(dados.length / 8) === 0

  return (
    <figure className="grafico">
      <div className="grafico-legenda" aria-hidden="true">
        <span>
          <i style={{ background: CORES.respondidas }} /> Respondidas
        </span>
        <span>
          <i style={{ background: CORES.semResposta }} /> Sem informação
        </span>
      </div>
      <div className="barras-verticais" aria-hidden="true">
        {dados.map((d, indice) => {
          const sem = d.total - d.respondidas
          return (
            <div
              key={d.rotulo}
              className="coluna"
              tabIndex={0}
              onMouseEnter={mostrar(`${d.rotulo}: ${d.total} pergunta(s), ${d.respondidas} respondida(s)`)}
              onFocus={mostrar(`${d.rotulo}: ${d.total} pergunta(s), ${d.respondidas} respondida(s)`)}
              onMouseLeave={esconder}
              onBlur={esconder}
            >
              <div className="coluna-pilha" style={{ height: `${(100 * d.total) / maximo}%` }}>
                {sem > 0 && <span style={{ flexGrow: sem, background: CORES.semResposta }} />}
                {d.respondidas > 0 && <span style={{ flexGrow: d.respondidas, background: CORES.respondidas }} />}
              </div>
              <small>{mostrarRotulo(indice) ? d.rotulo : ''}</small>
            </div>
          )
        })}
      </div>
      <Dica dica={dica} />
      <details className="grafico-tabela">
        <summary>Ver dados em tabela</summary>
        <table className="tabela">
          <thead>
            <tr>
              <th>Período</th>
              <th>Perguntas</th>
              <th>Respondidas</th>
            </tr>
          </thead>
          <tbody>
            {dados.map((d) => (
              <tr key={d.rotulo}>
                <td>{d.rotulo}</td>
                <td>{d.total}</td>
                <td>{d.respondidas}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </figure>
  )
}

// Ranking (temas mais consultados, inscrições por tema): barras horizontais com o valor ao lado
export function BarrasHorizontais({ dados, unidade, vazio }) {
  if (!dados.length) return <p className="texto-apoio">{vazio}</p>
  const maximo = Math.max(...dados.map((d) => d.total))
  return (
    <ul className="barras-horizontais">
      {dados.map((d) => (
        <li key={d.tema}>
          <span className="barra-rotulo">{d.tema}</span>
          <span className="barra-trilho">
            <span className="barra" style={{ width: `${(100 * d.total) / maximo}%`, background: CORES.respondidas }} />
          </span>
          <span className="barra-valor">
            {d.total} <span className="somente-leitor">{unidade}</span>
          </span>
        </li>
      ))}
    </ul>
  )
}

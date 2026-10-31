import { useState } from 'react'

function Sugestoes({ temas, aoEscolher }) {
  const [temaAberto, setTemaAberto] = useState(null)

  if (temas.length === 0) return null

  const tema = temas.find((item) => item.tema === temaAberto)

  return (
    <section className="sugestoes" aria-labelledby="titulo-sugestoes">
      <p className="chamada" id="titulo-sugestoes">
        Temas mais procurados
      </p>
      <div className="temas">
        {temas.map((item) => (
          <button
            key={item.tema}
            type="button"
            className={item.tema === temaAberto ? 'tema ativo' : 'tema'}
            aria-pressed={item.tema === temaAberto}
            onClick={() => setTemaAberto(item.tema === temaAberto ? null : item.tema)}
          >
            <span className="tema-nome">{item.tema}</span>
            <span className="tema-total">{item.perguntas.length} perguntas</span>
          </button>
        ))}
      </div>
      {tema && (
        <ul className="perguntas-sugeridas">
          {tema.perguntas.map((pergunta) => (
            <li key={pergunta}>
              <button type="button" onClick={() => aoEscolher(pergunta)}>
                <span>{pergunta}</span>
                <span className="seta" aria-hidden="true">
                  →
                </span>
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export default Sugestoes

import { useState } from 'react'

function Sugestoes({ temas, aoEscolher }) {
  const [temaAberto, setTemaAberto] = useState(null)

  if (temas.length === 0) return null

  const tema = temas.find((item) => item.tema === temaAberto)

  return (
    <section className="sugestoes" aria-labelledby="titulo-sugestoes">
      <h2 id="titulo-sugestoes">Temas mais procurados</h2>
      <div className="temas">
        {temas.map((item) => (
          <button
            key={item.tema}
            type="button"
            className={item.tema === temaAberto ? 'tema ativo' : 'tema'}
            aria-pressed={item.tema === temaAberto}
            onClick={() => setTemaAberto(item.tema === temaAberto ? null : item.tema)}
          >
            {item.tema}
          </button>
        ))}
      </div>
      {tema && (
        <ul className="perguntas-sugeridas">
          {tema.perguntas.map((pergunta) => (
            <li key={pergunta}>
              <button type="button" onClick={() => aoEscolher(pergunta)}>
                {pergunta}
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export default Sugestoes

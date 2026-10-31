function CartaoResposta({ dados }) {
  return (
    <article className={dados.encontrou ? 'resposta' : 'resposta sem-informacao'} aria-live="polite">
      <p className="resposta-pergunta">{dados.pergunta}</p>
      <p className="resposta-texto">{dados.resposta}</p>

      {dados.fontes.length > 0 && (
        <div className="fontes">
          <h3>Fonte{dados.fontes.length > 1 ? 's' : ''}</h3>
          <ul>
            {dados.fontes.map((fonte) => (
              <li key={fonte.titulo + fonte.trecho}>
                <strong>{fonte.titulo}</strong>
                <blockquote>{fonte.trecho}</blockquote>
                {fonte.url && (
                  <a href={fonte.url} target="_blank" rel="noreferrer">
                    Ver conteúdo original
                  </a>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </article>
  )
}

export default CartaoResposta

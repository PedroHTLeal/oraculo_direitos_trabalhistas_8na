// Pergunta, resposta, fontes e botão "Saiba mais"; usado no painel azul e no celular
function ConteudoResposta({ dados, aoSaberMais }) {
  return (
    <>
      <p className="resposta-pergunta">{dados.pergunta}</p>
      {dados.resposta.split('\n').filter(Boolean).map((paragrafo, indice) => (
        <p key={indice} className="resposta-texto">
          {paragrafo}
        </p>
      ))}

      {dados.fontes.length > 0 && (
        <div className="fontes">
          <h3>Fonte: Cartilha de Direitos e Obrigações no Trabalho (TRT4)</h3>
          <ul>
            {dados.fontes.map((fonte) => (
              <li key={fonte.titulo + fonte.trecho}>
                <details>
                  <summary>{fonte.titulo}</summary>
                  <blockquote>{fonte.trecho}</blockquote>
                </details>
                {fonte.url && (
                  <a href={fonte.url} target="_blank" rel="noreferrer">
                    Ver na cartilha ↗
                  </a>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {dados.encontrou && dados.id && (
        <button type="button" className="botao-saiba-mais" onClick={aoSaberMais}>
          Saiba mais pelo WhatsApp
        </button>
      )}
    </>
  )
}

export default ConteudoResposta

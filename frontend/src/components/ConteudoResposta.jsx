// Pergunta, resposta, fontes e o convite "Quer saber mais?"; usado no painel azul e no celular
function ConteudoResposta({ dados, aoSaberMais }) {
  // Uma linha por seção da cartilha, mesmo que a resposta use mais de um trecho dela
  const fontes = dados.fontes.filter((fonte, indice, todas) => todas.findIndex((f) => f.titulo === fonte.titulo) === indice)

  return (
    <>
      <p className="resposta-pergunta">{dados.pergunta}</p>
      {dados.resposta.split('\n').filter(Boolean).map((paragrafo, indice) => (
        <p key={indice} className="resposta-texto">
          {paragrafo}
        </p>
      ))}

      {fontes.length > 0 && (
        <div className="fontes">
          <h3>Fonte: Cartilha de Direitos e Obrigações no Trabalho (TRT4)</h3>
          <ul>
            {fontes.map((fonte) => (
              <li key={fonte.titulo}>
                <span className="fonte-titulo">{fonte.titulo}</span>
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
        <div className="saiba-mais">
          <p>Quer saber mais sobre o assunto?</p>
          <button type="button" className="botao-saiba-mais" onClick={aoSaberMais}>
            Sim
          </button>
        </div>
      )}
    </>
  )
}

export default ConteudoResposta

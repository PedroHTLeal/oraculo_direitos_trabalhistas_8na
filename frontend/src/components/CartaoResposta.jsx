import ConteudoResposta from './ConteudoResposta'

// Resposta exibida na coluna principal; em telas grandes ela aparece no painel azul
function CartaoResposta({ dados, aoSaberMais }) {
  return (
    <article
      className={dados.encontrou ? 'resposta somente-celular' : 'resposta sem-informacao somente-celular'}
      aria-live="polite"
    >
      <ConteudoResposta dados={dados} aoSaberMais={aoSaberMais} />
    </article>
  )
}

export default CartaoResposta

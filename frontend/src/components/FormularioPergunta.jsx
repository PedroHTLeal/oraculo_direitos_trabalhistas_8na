const TAMANHO_MINIMO = 3
const TAMANHO_MAXIMO = 500

function FormularioPergunta({ texto, aoMudarTexto, aoEnviar, carregando }) {
  const textoLimpo = texto.trim()
  const podeEnviar = textoLimpo.length >= TAMANHO_MINIMO && !carregando

  function enviar(evento) {
    evento.preventDefault()
    if (podeEnviar) aoEnviar(textoLimpo)
  }

  function aoPressionarTecla(evento) {
    // Enter envia; Shift+Enter quebra a linha
    if (evento.key === 'Enter' && !evento.shiftKey) enviar(evento)
  }

  return (
    <form className="formulario" onSubmit={enviar}>
      <label htmlFor="pergunta" className="formulario-rotulo">
        Qual é a sua dúvida?
      </label>
      <textarea
        id="pergunta"
        value={texto}
        onChange={(evento) => aoMudarTexto(evento.target.value)}
        onKeyDown={aoPressionarTecla}
        maxLength={TAMANHO_MAXIMO}
        rows={3}
        placeholder="Ex.: Quantos dias de férias eu tenho direito?"
      />
      <div className="formulario-rodape">
        <span className="contador">
          {texto.length}/{TAMANHO_MAXIMO}
        </span>
        <button type="submit" disabled={!podeEnviar}>
          {carregando ? 'Buscando...' : 'Perguntar'}
        </button>
      </div>
    </form>
  )
}

export default FormularioPergunta

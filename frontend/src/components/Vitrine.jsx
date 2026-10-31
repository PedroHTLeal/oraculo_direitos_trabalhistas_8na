const TEMAS_EM_ORBITA = ['Férias', '13º salário', 'Rescisão', 'Jornada']

// Painel decorativo exibido ao lado da tela de perguntas em telas grandes
function Vitrine() {
  return (
    <aside className="vitrine" aria-hidden="true">
      <div className="orbita">
        <span className="anel anel-1" />
        <span className="anel anel-2" />
        <span className="anel anel-3" />

        <div className="anel-rotativo">
          {TEMAS_EM_ORBITA.map((tema, indice) => (
            <span key={tema} className={`orbita-rotulo posicao-${indice}`}>
              {tema}
            </span>
          ))}
        </div>

        <span className="orbita-nucleo">
          <svg viewBox="0 0 48 48">
            {/* Balança da justiça */}
            <path
              d="M24 9v29M15 38h18M11 15h26M24 9l0 6M11 15l-6 12a6 6 0 0 0 12 0zM37 15l-6 12a6 6 0 0 0 12 0z"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.6"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </span>
      </div>

      <div className="vitrine-citacao">
        <p className="citacao">“Seus direitos no trabalho, explicados em linguagem simples.”</p>
        <p>Respostas baseadas na Cartilha de Direitos e Obrigações no Trabalho do TRT4, sempre com a fonte.</p>
      </div>
    </aside>
  )
}

export default Vitrine

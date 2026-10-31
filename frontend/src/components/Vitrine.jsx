import ConteudoResposta from './ConteudoResposta'

const TEMAS_EM_ORBITA = ['Férias', '13º salário', 'Rescisão', 'Jornada']

function Orbita({ carregando }) {
  return (
    <div className={carregando ? 'orbita carregando' : 'orbita'} aria-hidden="true">
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
  )
}

// Painel azul exibido ao lado da tela de perguntas em telas grandes.
// Mostra a órbita de temas e, depois da pergunta, a resposta.
function Vitrine({ resposta, carregando, aoSaberMais }) {
  if (resposta && !carregando) {
    return (
      <aside className="vitrine com-resposta" aria-label="Resposta">
        <div className="vitrine-resposta" aria-live="polite">
          <p className="chamada">{resposta.encontrou ? 'Resposta' : 'Não encontrei'}</p>
          <ConteudoResposta dados={resposta} aoSaberMais={aoSaberMais} />
        </div>
      </aside>
    )
  }

  return (
    <aside className="vitrine" aria-hidden={!carregando}>
      <Orbita carregando={carregando} />
      <div className="vitrine-citacao">
        {carregando ? (
          <p className="citacao" role="status">
            Consultando a cartilha...
          </p>
        ) : (
          <>
            <p className="citacao">“Seus direitos no trabalho, explicados em linguagem simples.”</p>
            <p>Respostas baseadas na Cartilha de Direitos e Obrigações no Trabalho do TRT4, sempre com a fonte.</p>
          </>
        )}
      </div>
    </aside>
  )
}

export default Vitrine

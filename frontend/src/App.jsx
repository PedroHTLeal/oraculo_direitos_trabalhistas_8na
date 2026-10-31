import { useEffect, useState } from 'react'
import { buscarSugestoes, enviarPergunta } from './api'
import CartaoResposta from './components/CartaoResposta'
import FormularioPergunta from './components/FormularioPergunta'
import Logo from './components/Logo'
import ModalSaibaMais from './components/ModalSaibaMais'
import Sugestoes from './components/Sugestoes'
import Vitrine from './components/Vitrine'

function App() {
  const [texto, setTexto] = useState('')
  const [temas, setTemas] = useState([])
  const [resposta, setResposta] = useState(null)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState(null)
  const [saibaMaisAberto, setSaibaMaisAberto] = useState(false)

  useEffect(() => {
    buscarSugestoes()
      .then(setTemas)
      .catch(() => setTemas([]))
  }, [])

  async function perguntar(pergunta) {
    setTexto(pergunta)
    setCarregando(true)
    setErro(null)
    try {
      setResposta(await enviarPergunta(pergunta))
    } catch (falha) {
      setResposta(null)
      setErro(falha.message)
    } finally {
      setCarregando(false)
    }
  }

  const abrirSaibaMais = () => setSaibaMaisAberto(true)

  return (
    <div className="pagina">
      <div className="painel">
        <header>
          <Logo />
        </header>

        <main>
          <div className="apresentacao">
            <p className="chamada">Tire sua dúvida</p>
            <h1>O que você quer saber sobre o seu trabalho?</h1>
            <p className="subtitulo">
              Pergunte do seu jeito. A resposta vem em linguagem simples e com a fonte consultada.
            </p>
          </div>

          <FormularioPergunta
            texto={texto}
            aoMudarTexto={setTexto}
            aoEnviar={perguntar}
            carregando={carregando}
          />

          {erro && (
            <p className="erro" role="alert">
              {erro}
            </p>
          )}

          {resposta && !erro && !carregando && <CartaoResposta dados={resposta} aoSaberMais={abrirSaibaMais} />}

          <Sugestoes temas={temas} aoEscolher={perguntar} />
        </main>

        <footer className="rodape">
          Oráculo · Respostas informativas, que não substituem a orientação de um advogado, sindicato ou
          da Justiça do Trabalho.
        </footer>
      </div>

      <Vitrine resposta={erro ? null : resposta} carregando={carregando} aoSaberMais={abrirSaibaMais} />

      {saibaMaisAberto && resposta && (
        <ModalSaibaMais perguntaId={resposta.id} aoFechar={() => setSaibaMaisAberto(false)} />
      )}
    </div>
  )
}

export default App

import { useEffect, useState } from 'react'
import { buscarSugestoes, enviarPergunta } from './api'
import CartaoResposta from './components/CartaoResposta'
import FormularioPergunta from './components/FormularioPergunta'
import Sugestoes from './components/Sugestoes'

function App() {
  const [texto, setTexto] = useState('')
  const [temas, setTemas] = useState([])
  const [resposta, setResposta] = useState(null)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState(null)

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
    } catch {
      setErro('Não foi possível enviar sua pergunta agora. Tente novamente em instantes.')
    } finally {
      setCarregando(false)
    }
  }

  return (
    <>
      <header className="cabecalho">
        <h1>Oráculo dos Direitos Trabalhistas</h1>
        <p>Tire suas dúvidas sobre direitos e obrigações no trabalho, em linguagem simples.</p>
      </header>

      <main>
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

        {resposta && !erro && <CartaoResposta dados={resposta} />}

        <Sugestoes temas={temas} aoEscolher={perguntar} />
      </main>

      <footer className="rodape">
        As respostas têm caráter informativo e não substituem a orientação de um advogado, sindicato
        ou da Justiça do Trabalho.
      </footer>
    </>
  )
}

export default App

import { useEffect, useState } from 'react'

function App() {
  const [statusApi, setStatusApi] = useState('verificando...')

  useEffect(() => {
    fetch('/api/saude')
      .then((resposta) => resposta.json())
      .then((dados) => setStatusApi(dados.status))
      .catch(() => setStatusApi('indisponível'))
  }, [])

  return (
    <main>
      <h1>Oráculo dos Direitos Trabalhistas</h1>
      <p>Tire suas dúvidas sobre direitos e obrigações no trabalho.</p>
      <p className="status">API: {statusApi}</p>
    </main>
  )
}

export default App

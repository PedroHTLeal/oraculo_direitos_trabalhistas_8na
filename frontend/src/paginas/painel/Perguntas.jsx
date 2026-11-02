import { useEffect, useState } from 'react'
import { listarPerguntas } from '../../api'

const formatarData = (texto) =>
  new Date(texto).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })

// Auditoria das perguntas (UC08): só o texto e o resultado, sem dados pessoais
function Perguntas() {
  const [perguntas, setPerguntas] = useState(null)
  const [erro, setErro] = useState(null)

  useEffect(() => {
    listarPerguntas()
      .then(setPerguntas)
      .catch((falha) => setErro(falha.message))
  }, [])

  return (
    <section>
      <h1>Perguntas recebidas</h1>
      <p className="subtitulo">
        As 50 perguntas mais recentes. Perguntas sem resposta indicam assuntos que podem entrar na base de conhecimento.
      </p>

      {erro && (
        <p className="alerta alerta-erro" role="alert">
          {erro}
        </p>
      )}

      {perguntas && perguntas.length === 0 && (
        <div className="estado-vazio">
          <p>Nenhuma pergunta registrada ainda.</p>
        </div>
      )}

      {perguntas && perguntas.length > 0 && (
        <div className="tabela-rolagem">
          <table className="tabela">
            <thead>
              <tr>
                <th>Pergunta</th>
                <th>Resultado</th>
                <th>Data</th>
              </tr>
            </thead>
            <tbody>
              {perguntas.map((pergunta) => (
                <tr key={pergunta.id}>
                  <td>{pergunta.texto}</td>
                  <td>
                    <span className={pergunta.encontrou ? 'selo selo-sucesso' : 'selo selo-aviso'}>
                      {pergunta.encontrou ? 'Respondida' : 'Sem informação'}
                    </span>
                  </td>
                  <td className="celula-data">{formatarData(pergunta.criado_em)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}

export default Perguntas

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { buscarIndicadores } from '../../api'
import { BarrasHorizontais, BarrasPorData } from '../../components/Graficos'

const PERIODOS = [
  { dias: 7, rotulo: '7 dias' },
  { dias: 30, rotulo: '30 dias' },
  { dias: 90, rotulo: '90 dias' },
  { dias: 365, rotulo: '12 meses' },
]

function Indicador({ titulo, valor, detalhe }) {
  return (
    <div className="indicador">
      <p className="indicador-titulo">{titulo}</p>
      <p className="indicador-valor">{valor}</p>
      {detalhe && <p className="indicador-detalhe">{detalhe}</p>}
    </div>
  )
}

// Dashboard (Sprint 07): uso do sistema com dados reais do banco
function Dashboard() {
  const [dias, setDias] = useState(30)
  const [dados, setDados] = useState(null)
  const [erro, setErro] = useState(null)

  useEffect(() => {
    setErro(null)
    buscarIndicadores(dias)
      .then(setDados)
      .catch((falha) => setErro(falha.message))
  }, [dias])

  const p = dados?.perguntas

  return (
    <section>
      <div className="cabecalho-secao">
        <div>
          <h1>Dashboard</h1>
          <p className="subtitulo">Como o Oráculo está sendo usado e o que falta na base de conhecimento.</p>
        </div>
        <div className="seletor-periodo" role="group" aria-label="Período">
          {PERIODOS.map((opcao) => (
            <button key={opcao.dias} type="button" aria-pressed={dias === opcao.dias} onClick={() => setDias(opcao.dias)}>
              {opcao.rotulo}
            </button>
          ))}
        </div>
      </div>

      {erro && (
        <p className="alerta alerta-erro" role="alert">
          {erro}
        </p>
      )}

      {dados && (
        <>
          <div className="indicadores">
            <Indicador titulo="Perguntas" valor={p.total} detalhe={`nos últimos ${PERIODOS.find((o) => o.dias === dias).rotulo}`} />
            <Indicador
              titulo="Taxa de resposta"
              valor={p.taxa_resposta === null ? '—' : `${p.taxa_resposta}%`}
              detalhe={`${p.respondidas} respondidas · ${p.sem_resposta} sem informação`}
            />
            <Indicador
              titulo="Pedidos de WhatsApp"
              valor={dados.whatsapp.enviado + dados.whatsapp.pendente + dados.whatsapp.erro}
              detalhe={`${dados.whatsapp.enviado} enviados · ${dados.whatsapp.erro} com erro`}
            />
            <Indicador
              titulo="Pessoas acompanhando temas"
              valor={dados.inscricoes.total}
              detalhe={`${dados.atualizacoes.publicadas} atualizações publicadas no período`}
            />
          </div>

          <div className="grade-cartoes">
            <article className="cartao cartao-largo">
              <h2>Perguntas por {dias <= 30 ? 'dia' : dias <= 90 ? 'semana' : 'mês'}</h2>
              <BarrasPorData dados={dados.perguntas_por_data} />
            </article>

            <article className="cartao">
              <h2>Temas mais consultados</h2>
              <BarrasHorizontais dados={dados.temas_mais_consultados} unidade="perguntas" vazio="Nenhuma pergunta respondida no período." />
            </article>

            <article className="cartao">
              <h2>Temas acompanhados</h2>
              <BarrasHorizontais dados={dados.inscricoes.por_tema} unidade="pessoas" vazio="Ninguém acompanha temas ainda." />
            </article>

            <article className="cartao cartao-largo">
              <div className="cartao-cabecalho">
                <h2>Perguntas sem resposta</h2>
                <Link to="/painel/relatorios?resultado=sem_resposta">Ver todas</Link>
              </div>
              <p className="texto-apoio">Assuntos que a cartilha não cobre. Inclua um trecho para a IA passar a responder.</p>
              {dados.sem_resposta_recentes.length === 0 ? (
                <p className="texto-apoio">Nenhuma no período.</p>
              ) : (
                <ul className="lista-simples">
                  {dados.sem_resposta_recentes.map((pergunta) => (
                    <li key={pergunta.id}>
                      <span>{pergunta.texto}</span>
                      <Link
                        to={`/painel/base/novo?pergunta=${encodeURIComponent(pergunta.texto)}`}
                        className="botao-secundario botao-compacto"
                      >
                        Incluir na base
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </article>

            <article className="cartao">
              <h2>Usuários ativos</h2>
              <ul className="lista-numeros">
                <li>
                  <span>Administradores</span> <strong>{dados.usuarios.administrador}</strong>
                </li>
                <li>
                  <span>Curadores</span> <strong>{dados.usuarios.curador}</strong>
                </li>
                <li>
                  <span>Contas com WhatsApp</span> <strong>{dados.usuarios.usuario}</strong>
                </li>
              </ul>
            </article>
          </div>
        </>
      )}
    </section>
  )
}

export default Dashboard

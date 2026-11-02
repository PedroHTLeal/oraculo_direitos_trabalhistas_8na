import { useEffect, useState } from 'react'
import { excluirAtualizacao, listarAtualizacoes, listarTemas, publicarAtualizacao, reenviarAtualizacao } from '../../api'
import { useAutenticacao } from '../../autenticacao/contexto'
import Campo from '../../components/Campo'
import ConfirmarExclusao from '../../components/ConfirmarExclusao'
import { regras, validar } from '../../validacao'

const ESQUEMA = {
  tema_id: [regras.obrigatorio('tema')],
  titulo: [regras.obrigatorio('título'), regras.minimo('título', 5), regras.maximo('título', 120)],
  conteudo: [regras.obrigatorio('conteúdo'), regras.minimo('conteúdo', 20), regras.maximo('conteúdo', 1000)],
  url: [(valor) => (!valor || /^https?:\/\/\S+$/.test(valor.trim()) ? null : 'O link precisa começar com http:// ou https://.')],
}

const VAZIO = { tema_id: '', titulo: '', conteudo: '', url: '' }

const formatarData = (texto) => new Date(texto).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })

// Módulo 2: a equipe publica novidades de um tema e o sistema avisa quem o acompanha
function Atualizacoes() {
  const { usuario } = useAutenticacao()
  const [temas, setTemas] = useState([])
  const [atualizacoes, setAtualizacoes] = useState(null)
  const [dados, setDados] = useState(VAZIO)
  const [erros, setErros] = useState({})
  const [erroGeral, setErroGeral] = useState(null)
  const [mensagem, setMensagem] = useState(null)
  const [publicando, setPublicando] = useState(false)
  const [paraExcluir, setParaExcluir] = useState(null)

  function carregar() {
    listarAtualizacoes()
      .then(setAtualizacoes)
      .catch((falha) => setErroGeral(falha.message))
  }

  useEffect(() => {
    listarTemas()
      .then(setTemas)
      .catch(() => setTemas([]))
    carregar()
  }, [])

  const mudar = (campo) => (evento) => setDados({ ...dados, [campo]: evento.target.value })

  async function publicar(evento) {
    evento.preventDefault()
    const encontrados = validar(dados, ESQUEMA)
    setErros(encontrados)
    setErroGeral(null)
    setMensagem(null)
    if (Object.keys(encontrados).length) return

    setPublicando(true)
    try {
      const nova = await publicarAtualizacao({
        tema_id: Number(dados.tema_id),
        titulo: dados.titulo.trim(),
        conteudo: dados.conteudo.trim(),
        url: dados.url.trim() || null,
      })
      const pessoas = nova.envios.pendente
      setMensagem(
        pessoas
          ? `Atualização publicada. Enviando para ${pessoas} pessoa(s) que acompanham ${nova.tema}.`
          : `Atualização publicada. Ninguém acompanha ${nova.tema} ainda, então nenhuma mensagem foi enviada.`,
      )
      setDados(VAZIO)
      // Os envios acontecem em segundo plano: atualiza a lista em seguida
      setTimeout(carregar, 2500)
      carregar()
    } catch (falha) {
      setErroGeral(falha.message)
    } finally {
      setPublicando(false)
    }
  }

  async function reenviar(atualizacao) {
    try {
      await reenviarAtualizacao(atualizacao.id)
      setMensagem(`Reenviando "${atualizacao.titulo}" para quem não recebeu.`)
      setTimeout(carregar, 2500)
    } catch (falha) {
      setErroGeral(falha.message)
    }
  }

  const podeExcluir = (atualizacao) => usuario.perfil === 'administrador' || atualizacao.autor_id === usuario.id

  return (
    <section>
      <h1>Atualizações</h1>
      <p className="subtitulo">Publique novidades de um tema. Quem acompanha o tema recebe a mensagem no WhatsApp.</p>

      {mensagem && (
        <p className="alerta alerta-sucesso" role="status">
          {mensagem}
        </p>
      )}
      {erroGeral && (
        <p className="alerta alerta-erro" role="alert">
          {erroGeral}
        </p>
      )}

      <form className="cartao-formulario formulario-largo" onSubmit={publicar} noValidate>
        <h2>Nova atualização</h2>
        <Campo id="atualizacao-tema" rotulo="Tema" erro={erros.tema_id}>
          <select id="atualizacao-tema" value={dados.tema_id} onChange={mudar('tema_id')} aria-invalid={Boolean(erros.tema_id)}>
            <option value="">Escolha um tema</option>
            {temas.map((tema) => (
              <option key={tema.id} value={tema.id}>
                {tema.nome}
              </option>
            ))}
          </select>
        </Campo>
        <Campo id="atualizacao-titulo" rotulo="Título" value={dados.titulo} onChange={mudar('titulo')} erro={erros.titulo} maxLength={120} />
        <Campo
          id="atualizacao-conteudo"
          rotulo="Conteúdo"
          erro={erros.conteudo}
          ajuda={`${dados.conteudo.length}/1000 caracteres. Escreva em linguagem simples.`}
        >
          <textarea
            id="atualizacao-conteudo"
            rows={5}
            maxLength={1000}
            value={dados.conteudo}
            onChange={mudar('conteudo')}
            aria-invalid={Boolean(erros.conteudo)}
          />
        </Campo>
        <Campo
          id="atualizacao-url"
          rotulo="Link para saber mais (opcional)"
          type="url"
          placeholder="https://"
          value={dados.url}
          onChange={mudar('url')}
          erro={erros.url}
        />
        <button type="submit" className="botao-principal botao-compacto" disabled={publicando}>
          {publicando ? 'Publicando...' : 'Publicar e enviar'}
        </button>
      </form>

      <h2>Publicadas</h2>
      {atualizacoes && atualizacoes.length === 0 && (
        <div className="estado-vazio">
          <p>Nenhuma atualização publicada ainda.</p>
        </div>
      )}
      {atualizacoes && atualizacoes.length > 0 && (
        <ul className="lista-trechos">
          {atualizacoes.map((a) => (
            <li key={a.id} className="item-trecho">
              <div>
                <p className="item-tema">
                  {a.tema} · {formatarData(a.publicado_em)} · {a.autor || 'Autor removido'}
                </p>
                <h2>{a.titulo}</h2>
                <p className="item-texto">{a.conteudo}</p>
                <p className="envios">
                  <span className="selo selo-sucesso">{a.envios.enviado} enviados</span>
                  {a.envios.pendente > 0 && <span className="selo">{a.envios.pendente} enviando</span>}
                  {a.envios.erro > 0 && <span className="selo selo-aviso">{a.envios.erro} com erro</span>}
                </p>
              </div>
              <div className="item-acoes">
                {a.envios.erro > 0 && (
                  <button type="button" className="botao-secundario botao-compacto" onClick={() => reenviar(a)}>
                    Reenviar
                  </button>
                )}
                {podeExcluir(a) && (
                  <button type="button" className="botao-texto-perigo" onClick={() => setParaExcluir(a)}>
                    Excluir
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}

      {paraExcluir && (
        <ConfirmarExclusao
          titulo="Excluir atualização?"
          descricao={`"${paraExcluir.titulo}" sairá do histórico. As mensagens já enviadas não são apagadas do WhatsApp das pessoas.`}
          aoConfirmar={async () => {
            await excluirAtualizacao(paraExcluir.id)
            setMensagem('Atualização excluída.')
            carregar()
          }}
          aoFechar={() => setParaExcluir(null)}
        />
      )}
    </section>
  )
}

export default Atualizacoes

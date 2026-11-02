import { useEffect, useRef, useState } from 'react'
import { excluirUsuario, listarUsuarios, salvarUsuario } from '../../api'
import { NOMES_DOS_PERFIS, useAutenticacao } from '../../autenticacao/contexto'
import Campo from '../../components/Campo'
import ConfirmarExclusao from '../../components/ConfirmarExclusao'
import { regras, validar } from '../../validacao'

const ESQUEMA_BASE = {
  nome: [regras.obrigatorio('nome'), regras.minimo('nome', 2), regras.maximo('nome', 100)],
  email: [regras.obrigatorio('e-mail'), regras.email()],
}

// Janela de cadastro e edição de usuário
function FormularioUsuario({ usuario, aoSalvar, aoFechar }) {
  const dialogo = useRef(null)
  const editando = Boolean(usuario)
  const [dados, setDados] = useState({
    nome: usuario?.nome || '',
    email: usuario?.email || '',
    perfil: usuario?.perfil || 'curador',
    ativo: usuario?.ativo ?? true,
    senha: '',
  })
  const [erros, setErros] = useState({})
  const [erroGeral, setErroGeral] = useState(null)
  const [salvando, setSalvando] = useState(false)

  useEffect(() => {
    dialogo.current?.showModal()
  }, [])

  const mudar = (campo) => (evento) => setDados({ ...dados, [campo]: evento.target.value })

  async function enviar(evento) {
    evento.preventDefault()
    // Na edição, a senha é opcional: só é trocada se for preenchida
    const esquema = {
      ...ESQUEMA_BASE,
      senha: editando && !dados.senha ? [] : [regras.obrigatorio('senha'), regras.minimo('senha', 8)],
    }
    const encontrados = validar(dados, esquema)
    setErros(encontrados)
    setErroGeral(null)
    if (Object.keys(encontrados).length) return

    const corpo = { nome: dados.nome.trim(), email: dados.email.trim(), perfil: dados.perfil }
    if (editando) corpo.ativo = dados.ativo
    if (dados.senha) corpo.senha = dados.senha

    setSalvando(true)
    try {
      await salvarUsuario(usuario?.id, corpo)
      aoSalvar(editando ? 'Usuário atualizado.' : 'Usuário cadastrado.')
      dialogo.current.close()
    } catch (falha) {
      setErroGeral(falha.message)
      setSalvando(false)
    }
  }

  return (
    <dialog ref={dialogo} className="modal" onClose={aoFechar} aria-labelledby="titulo-usuario">
      <button type="button" className="modal-fechar" onClick={() => dialogo.current.close()} aria-label="Fechar">
        ×
      </button>
      <form onSubmit={enviar} noValidate>
        <h2 id="titulo-usuario">{editando ? 'Editar usuário' : 'Novo usuário'}</h2>
        {erroGeral && (
          <p className="alerta alerta-erro" role="alert">
            {erroGeral}
          </p>
        )}
        <Campo id="usuario-nome" rotulo="Nome" value={dados.nome} onChange={mudar('nome')} erro={erros.nome} />
        <Campo
          id="usuario-email"
          rotulo="E-mail"
          type="email"
          value={dados.email}
          onChange={mudar('email')}
          erro={erros.email}
        />
        <Campo id="usuario-perfil" rotulo="Perfil" ajuda="Curadores cuidam da base; administradores também gerenciam usuários.">
          <select id="usuario-perfil" value={dados.perfil} onChange={mudar('perfil')} aria-describedby="usuario-perfil-ajuda">
            {Object.entries(NOMES_DOS_PERFIS).map(([valor, nome]) => (
              <option key={valor} value={valor}>
                {nome}
              </option>
            ))}
          </select>
        </Campo>
        <Campo
          id="usuario-senha"
          rotulo={editando ? 'Nova senha (opcional)' : 'Senha'}
          type="password"
          autoComplete="new-password"
          value={dados.senha}
          onChange={mudar('senha')}
          erro={erros.senha}
          ajuda={editando ? 'Deixe em branco para manter a senha atual.' : 'Mínimo de 8 caracteres.'}
        />
        {editando && (
          <label className="consentimento">
            <input
              type="checkbox"
              checked={dados.ativo}
              onChange={(evento) => setDados({ ...dados, ativo: evento.target.checked })}
            />
            <span>Acesso ativo (desmarque para bloquear o login deste usuário)</span>
          </label>
        )}
        <button type="submit" className="botao-principal" disabled={salvando}>
          {salvando ? 'Salvando...' : 'Salvar'}
        </button>
      </form>
    </dialog>
  )
}

function Usuarios() {
  const { usuario: eu } = useAutenticacao()
  const [usuarios, setUsuarios] = useState(null)
  const [erro, setErro] = useState(null)
  const [mensagem, setMensagem] = useState(null)
  const [editando, setEditando] = useState(undefined) // undefined: fechado; null: novo; objeto: edição
  const [paraExcluir, setParaExcluir] = useState(null)
  const [recarregar, setRecarregar] = useState(0)

  useEffect(() => {
    listarUsuarios()
      .then(setUsuarios)
      .catch((falha) => setErro(falha.message))
  }, [recarregar])

  const atualizar = (texto) => {
    setMensagem(texto)
    setRecarregar((n) => n + 1)
  }

  return (
    <section>
      <div className="cabecalho-secao">
        <div>
          <h1>Usuários</h1>
          <p className="subtitulo">Quem pode entrar no sistema e o que cada um pode fazer.</p>
        </div>
        <button type="button" className="botao-principal botao-compacto" onClick={() => setEditando(null)}>
          + Novo usuário
        </button>
      </div>

      {mensagem && (
        <p className="alerta alerta-sucesso" role="status">
          {mensagem}
          <button type="button" className="alerta-fechar" onClick={() => setMensagem(null)} aria-label="Fechar aviso">
            ×
          </button>
        </p>
      )}
      {erro && (
        <p className="alerta alerta-erro" role="alert">
          {erro}
        </p>
      )}

      {usuarios && (
        <div className="tabela-rolagem">
          <table className="tabela">
            <thead>
              <tr>
                <th>Nome</th>
                <th>E-mail</th>
                <th>Perfil</th>
                <th>Situação</th>
                <th>
                  <span className="somente-leitor">Ações</span>
                </th>
              </tr>
            </thead>
            <tbody>
              {usuarios.map((usuario) => (
                <tr key={usuario.id}>
                  <td>
                    {usuario.nome}
                    {usuario.id === eu.id && <span className="texto-apoio"> (você)</span>}
                  </td>
                  <td>{usuario.email}</td>
                  <td>
                    <span className={`selo selo-${usuario.perfil}`}>{NOMES_DOS_PERFIS[usuario.perfil]}</span>
                  </td>
                  <td>{usuario.ativo ? 'Ativo' : 'Bloqueado'}</td>
                  <td className="celula-acoes">
                    <button type="button" className="botao-secundario botao-compacto" onClick={() => setEditando(usuario)}>
                      Editar
                    </button>
                    {usuario.id !== eu.id && (
                      <button type="button" className="botao-texto-perigo" onClick={() => setParaExcluir(usuario)}>
                        Excluir
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {editando !== undefined && (
        <FormularioUsuario usuario={editando} aoSalvar={atualizar} aoFechar={() => setEditando(undefined)} />
      )}
      {paraExcluir && (
        <ConfirmarExclusao
          titulo="Excluir usuário?"
          descricao={`${paraExcluir.nome} (${paraExcluir.email}) perderá o acesso ao sistema. Essa ação não pode ser desfeita.`}
          aoConfirmar={async () => {
            await excluirUsuario(paraExcluir.id)
            atualizar('Usuário excluído.')
          }}
          aoFechar={() => setParaExcluir(null)}
        />
      )}
    </section>
  )
}

export default Usuarios

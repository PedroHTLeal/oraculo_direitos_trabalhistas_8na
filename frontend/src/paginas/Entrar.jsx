import { useState } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAutenticacao } from '../autenticacao/contexto'
import Campo from '../components/Campo'
import MenuConta from '../components/MenuConta'
import Vitrine from '../components/Vitrine'
import { regras, validar } from '../validacao'

const ESQUEMA = {
  email: [regras.obrigatorio('e-mail'), regras.email()],
  senha: [regras.obrigatorio('senha')],
}

function Entrar() {
  const { usuario, entrar, aviso } = useAutenticacao()
  const navegar = useNavigate()
  const destino = useLocation().state?.de || '/painel'
  const [dados, setDados] = useState({ email: '', senha: '' })
  const [erros, setErros] = useState({})
  const [erroGeral, setErroGeral] = useState(null)
  const [enviando, setEnviando] = useState(false)

  if (usuario) return <Navigate to={destino} replace />

  const mudar = (campo) => (evento) => setDados({ ...dados, [campo]: evento.target.value })

  async function enviar(evento) {
    evento.preventDefault()
    const encontrados = validar(dados, ESQUEMA)
    setErros(encontrados)
    setErroGeral(null)
    if (Object.keys(encontrados).length) return

    setEnviando(true)
    try {
      await entrar(dados.email.trim(), dados.senha)
      navegar(destino, { replace: true })
    } catch (falha) {
      setErroGeral(falha.message)
    } finally {
      setEnviando(false)
    }
  }

  return (
    <div className="pagina">
      <div className="painel">
        <MenuConta />
        <main>
          <div className="apresentacao">
            <p className="chamada">Área restrita</p>
            <h1>Entrar</h1>
            <p className="subtitulo">
              Para administrar a base de conhecimento ou acompanhar temas. Para tirar dúvidas não é preciso conta.
            </p>
          </div>

          {(erroGeral || aviso) && (
            <p className="alerta alerta-erro" role="alert">
              {erroGeral || aviso}
            </p>
          )}

          <form className="cartao-formulario" onSubmit={enviar} noValidate>
            <Campo
              id="email"
              rotulo="E-mail"
              type="email"
              autoComplete="email"
              value={dados.email}
              onChange={mudar('email')}
              erro={erros.email}
            />
            <Campo
              id="senha"
              rotulo="Senha"
              type="password"
              autoComplete="current-password"
              value={dados.senha}
              onChange={mudar('senha')}
              erro={erros.senha}
            />
            <button type="submit" className="botao-principal" disabled={enviando}>
              {enviando ? 'Entrando...' : 'Entrar'}
            </button>
          </form>

          <p className="texto-apoio">
            Ainda não tem conta? <Link to="/cadastro">Cadastre-se</Link> · <Link to="/">Voltar para a consulta</Link>
          </p>
        </main>
      </div>
      <Vitrine />
    </div>
  )
}

export default Entrar

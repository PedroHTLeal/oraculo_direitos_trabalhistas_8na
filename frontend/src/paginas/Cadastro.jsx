import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAutenticacao } from '../autenticacao/contexto'
import Campo from '../components/Campo'
import MenuConta from '../components/MenuConta'
import Vitrine from '../components/Vitrine'
import { regras, validar } from '../validacao'

const ESQUEMA = {
  nome: [regras.obrigatorio('nome'), regras.minimo('nome', 2), regras.maximo('nome', 100)],
  email: [regras.obrigatorio('e-mail'), regras.email()],
  senha: [regras.obrigatorio('senha'), regras.minimo('senha', 8), regras.maximo('senha', 128)],
  confirmacao: [regras.igual('senha', 'As senhas não conferem.')],
}

function Cadastro() {
  const { usuario, cadastrar } = useAutenticacao()
  const navegar = useNavigate()
  const [dados, setDados] = useState({ nome: '', email: '', senha: '', confirmacao: '' })
  const [erros, setErros] = useState({})
  const [erroGeral, setErroGeral] = useState(null)
  const [enviando, setEnviando] = useState(false)

  if (usuario) return <Navigate to="/painel" replace />

  const mudar = (campo) => (evento) => setDados({ ...dados, [campo]: evento.target.value })

  async function enviar(evento) {
    evento.preventDefault()
    const encontrados = validar(dados, ESQUEMA)
    setErros(encontrados)
    setErroGeral(null)
    if (Object.keys(encontrados).length) return

    setEnviando(true)
    try {
      await cadastrar(dados.nome.trim(), dados.email.trim(), dados.senha)
      navegar('/painel/temas', { replace: true, state: { boasVindas: true } })
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
            <p className="chamada">Criar conta</p>
            <h1>Cadastre-se</h1>
            <p className="subtitulo">
              Com uma conta você escolhe temas para acompanhar e recebe as novidades no seu WhatsApp.
            </p>
          </div>

          {erroGeral && (
            <p className="alerta alerta-erro" role="alert">
              {erroGeral}
            </p>
          )}

          <form className="cartao-formulario" onSubmit={enviar} noValidate>
            <Campo id="nome" rotulo="Nome" autoComplete="name" value={dados.nome} onChange={mudar('nome')} erro={erros.nome} />
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
              autoComplete="new-password"
              value={dados.senha}
              onChange={mudar('senha')}
              erro={erros.senha}
              ajuda="Mínimo de 8 caracteres."
            />
            <Campo
              id="confirmacao"
              rotulo="Confirme a senha"
              type="password"
              autoComplete="new-password"
              value={dados.confirmacao}
              onChange={mudar('confirmacao')}
              erro={erros.confirmacao}
            />
            <button type="submit" className="botao-principal" disabled={enviando}>
              {enviando ? 'Criando conta...' : 'Criar conta'}
            </button>
          </form>

          <p className="texto-apoio">
            Já tem conta? <Link to="/entrar">Entrar</Link> · <Link to="/">Voltar para a consulta</Link>
          </p>
        </main>
      </div>
      <Vitrine />
    </div>
  )
}

export default Cadastro

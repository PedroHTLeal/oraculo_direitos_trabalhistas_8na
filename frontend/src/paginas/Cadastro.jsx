import { Link, Navigate, useNavigate } from 'react-router-dom'
import { paginaInicial, useAutenticacao } from '../autenticacao/contexto'
import FormularioCadastro from '../components/FormularioCadastro'
import MenuConta from '../components/MenuConta'
import Vitrine from '../components/Vitrine'

function Cadastro() {
  const { usuario } = useAutenticacao()
  const navegar = useNavigate()

  if (usuario) return <Navigate to={paginaInicial(usuario)} replace />

  return (
    <div className="pagina">
      <div className="painel">
        <MenuConta />
        <main>
          <div className="apresentacao">
            <p className="chamada">Receba por e-mail</p>
            <h1>Crie sua conta</h1>
            <p className="subtitulo">
              Com a conta você escolhe temas para acompanhar e recebe as novidades deles no seu e-mail.
            </p>
          </div>

          <FormularioCadastro aoCadastrar={() => navegar('/painel/temas', { replace: true, state: { boasVindas: true } })} />

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

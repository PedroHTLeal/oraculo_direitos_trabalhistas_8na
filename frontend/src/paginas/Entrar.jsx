import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { paginaInicial, useAutenticacao } from '../autenticacao/contexto'
import FormularioEntrar from '../components/FormularioEntrar'
import MenuConta from '../components/MenuConta'
import Vitrine from '../components/Vitrine'

function Entrar() {
  const { usuario, aviso } = useAutenticacao()
  const navegar = useNavigate()
  const destino = useLocation().state?.de

  if (usuario) return <Navigate to={destino || paginaInicial(usuario)} replace />

  return (
    <div className="pagina">
      <div className="painel">
        <MenuConta />
        <main>
          <div className="apresentacao">
            <p className="chamada">Sua conta</p>
            <h1>Entrar</h1>
            <p className="subtitulo">
              Entre para acompanhar temas e receber as novidades deles no seu e-mail. Para fazer perguntas, não é preciso
              conta.
            </p>
          </div>

          {aviso && (
            <p className="alerta alerta-erro" role="alert">
              {aviso}
            </p>
          )}

          <FormularioEntrar aoEntrar={(conta) => navegar(destino || paginaInicial(conta), { replace: true })} />

          <p className="texto-apoio">
            Ainda não tem conta? <Link to="/cadastro">Crie sua conta</Link> · <Link to="/">Voltar para a consulta</Link>
          </p>
        </main>
      </div>
      <Vitrine />
    </div>
  )
}

export default Entrar

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
            <p className="chamada">Receba pelo WhatsApp</p>
            <h1>Cadastre seu WhatsApp</h1>
            <p className="subtitulo">
              Com a conta você recebe no WhatsApp sites e vídeos sobre as suas dúvidas e escolhe temas para receber
              novidades.
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

import { Link } from 'react-router-dom'
import { paginaInicial, useAutenticacao } from '../autenticacao/contexto'
import Logo from './Logo'

// Topo da página pública: logotipo e acesso à conta.
// Na consulta, quem não entrou não vê o botão "Entrar": basta perguntar e usar o "Saber mais".
function MenuConta({ mostrarEntrar = true }) {
  const { usuario } = useAutenticacao()

  return (
    <header className="topo">
      <Link to="/" className="topo-logo" aria-label="Oráculo - página inicial">
        <Logo />
      </Link>
      {usuario ? (
        <Link to={paginaInicial(usuario)} className="botao-secundario">
          Olá, {usuario.nome.split(' ')[0]} · {usuario.perfil === 'usuario' ? 'Meus temas' : 'Painel'}
        </Link>
      ) : (
        mostrarEntrar && (
          <Link to="/entrar" className="botao-secundario">
            Entrar
          </Link>
        )
      )}
    </header>
  )
}

export default MenuConta

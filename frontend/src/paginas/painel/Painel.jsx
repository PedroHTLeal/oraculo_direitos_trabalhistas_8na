import { Link, NavLink, Navigate, Outlet, useLocation } from 'react-router-dom'
import { NOMES_DOS_PERFIS, paginaInicial, useAutenticacao } from '../../autenticacao/contexto'
import Logo from '../../components/Logo'

// Itens do menu e perfis que podem ver cada um
const EQUIPE = ['administrador', 'curador']
const MENU = [
  { para: '/painel/dashboard', rotulo: 'Dashboard', perfis: EQUIPE },
  { para: '/painel/base', rotulo: 'Base de conhecimento', perfis: EQUIPE },
  { para: '/painel/sinonimos', rotulo: 'Sinônimos da busca', perfis: EQUIPE },
  { para: '/painel/materiais', rotulo: 'Sites e vídeos', perfis: EQUIPE },
  { para: '/painel/atualizacoes', rotulo: 'Atualizações', perfis: EQUIPE },
  { para: '/painel/relatorios', rotulo: 'Relatório de perguntas', perfis: EQUIPE },
  { para: '/painel/historico', rotulo: 'Histórico de operações', perfis: ['administrador'] },
  { para: '/painel/usuarios', rotulo: 'Usuários', perfis: ['administrador'] },
  { para: '/painel/temas', rotulo: 'Meus temas', perfis: ['usuario'] },
]

// Só exibe o conteúdo para quem está logado e tem um dos perfis exigidos
export function RotaProtegida({ perfis, children }) {
  const { usuario, carregando, saiuAgora } = useAutenticacao()
  const local = useLocation()

  if (carregando) return <p className="carregando-pagina">Carregando...</p>
  // Guarda a página pedida para voltar a ela depois do login, exceto quando a pessoa clicou em Sair
  if (!usuario) return <Navigate to="/entrar" replace state={saiuAgora ? null : { de: local.pathname }} />
  if (perfis && !perfis.includes(usuario.perfil)) {
    return (
      <div className="estado-vazio" role="alert">
        <h2>Acesso não permitido</h2>
        <p>O seu perfil ({NOMES_DOS_PERFIS[usuario.perfil]}) não tem acesso a esta área.</p>
        <Link to={paginaInicial(usuario)}>Ir para o início do painel</Link>
      </div>
    )
  }
  return children
}

function Painel() {
  const { usuario, sair } = useAutenticacao()

  return (
    <RotaProtegida>
      <div className="painel-admin">
        <header className="painel-topo">
          <Link to="/" aria-label="Oráculo - página inicial">
            <Logo />
          </Link>
          <div className="painel-conta">
            <span>
              {usuario?.nome} <span className={`selo selo-${usuario?.perfil}`}>{NOMES_DOS_PERFIS[usuario?.perfil]}</span>
            </span>
            <button type="button" className="botao-secundario" onClick={sair}>
              Sair
            </button>
          </div>
        </header>

        <div className="painel-corpo">
          <nav className="painel-menu" aria-label="Menu do painel">
            {MENU.filter((item) => item.perfis.includes(usuario?.perfil)).map((item) => (
              <NavLink key={item.para} to={item.para}>
                {item.rotulo}
              </NavLink>
            ))}
            <Link to="/" className="painel-menu-site">
              ← Fazer uma pergunta
            </Link>
          </nav>
          <main className="painel-conteudo">
            <Outlet />
          </main>
        </div>
      </div>
    </RotaProtegida>
  )
}

export function InicioPainel() {
  const { usuario } = useAutenticacao()
  return <Navigate to={paginaInicial(usuario)} replace />
}

export default Painel

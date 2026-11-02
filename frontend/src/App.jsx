import { Link, Route, Routes } from 'react-router-dom'
import ProvedorAutenticacao from './autenticacao/ProvedorAutenticacao'
import Cadastro from './paginas/Cadastro'
import Consulta from './paginas/Consulta'
import Entrar from './paginas/Entrar'
import Atualizacoes from './paginas/painel/Atualizacoes'
import BaseConhecimento from './paginas/painel/BaseConhecimento'
import Dashboard from './paginas/painel/Dashboard'
import FormularioTrecho from './paginas/painel/FormularioTrecho'
import MeusTemas from './paginas/painel/MeusTemas'
import Historico from './paginas/painel/Historico'
import Painel, { InicioPainel, RotaProtegida } from './paginas/painel/Painel'
import RelatorioPerguntas from './paginas/painel/RelatorioPerguntas'
import Usuarios from './paginas/painel/Usuarios'

const EQUIPE_DE_CONTEUDO = ['administrador', 'curador']

function PaginaNaoEncontrada() {
  return (
    <div className="estado-vazio pagina-erro">
      <h1>Página não encontrada</h1>
      <p>O endereço acessado não existe.</p>
      <Link to="/">Voltar para a página inicial</Link>
    </div>
  )
}

function App() {
  return (
    <ProvedorAutenticacao>
      <Routes>
        <Route path="/" element={<Consulta />} />
        <Route path="/entrar" element={<Entrar />} />
        <Route path="/cadastro" element={<Cadastro />} />
        <Route path="/painel" element={<Painel />}>
          <Route index element={<InicioPainel />} />
          <Route
            path="base"
            element={
              <RotaProtegida perfis={EQUIPE_DE_CONTEUDO}>
                <BaseConhecimento />
              </RotaProtegida>
            }
          />
          <Route
            path="base/:id"
            element={
              <RotaProtegida perfis={EQUIPE_DE_CONTEUDO}>
                <FormularioTrecho />
              </RotaProtegida>
            }
          />
          <Route
            path="dashboard"
            element={
              <RotaProtegida perfis={EQUIPE_DE_CONTEUDO}>
                <Dashboard />
              </RotaProtegida>
            }
          />
          <Route
            path="atualizacoes"
            element={
              <RotaProtegida perfis={EQUIPE_DE_CONTEUDO}>
                <Atualizacoes />
              </RotaProtegida>
            }
          />
          <Route
            path="relatorios"
            element={
              <RotaProtegida perfis={EQUIPE_DE_CONTEUDO}>
                <RelatorioPerguntas />
              </RotaProtegida>
            }
          />
          <Route
            path="historico"
            element={
              <RotaProtegida perfis={['administrador']}>
                <Historico />
              </RotaProtegida>
            }
          />
          <Route
            path="usuarios"
            element={
              <RotaProtegida perfis={['administrador']}>
                <Usuarios />
              </RotaProtegida>
            }
          />
          <Route
            path="temas"
            element={
              <RotaProtegida perfis={['usuario']}>
                <MeusTemas />
              </RotaProtegida>
            }
          />
        </Route>
        <Route path="*" element={<PaginaNaoEncontrada />} />
      </Routes>
    </ProvedorAutenticacao>
  )
}

export default App

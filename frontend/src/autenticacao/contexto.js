import { createContext, useContext } from 'react'

export const ContextoAutenticacao = createContext(null)

export function useAutenticacao() {
  return useContext(ContextoAutenticacao)
}

export const NOMES_DOS_PERFIS = {
  administrador: 'Administrador',
  curador: 'Curador',
  usuario: 'Usuário',
}

export const podeGerenciarConteudo = (usuario) => ['administrador', 'curador'].includes(usuario?.perfil)

export const paginaInicial = (usuario) => (podeGerenciarConteudo(usuario) ? '/painel/dashboard' : '/painel/temas')

// (51) 99999-8888 a partir de +5551999998888
export function telefoneLegivel(telefone) {
  const d = (telefone || '').replace(/^\+55/, '')
  if (d.length < 10) return telefone || ''
  return `(${d.slice(0, 2)}) ${d.slice(2, d.length - 4)}-${d.slice(-4)}`
}

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

export const paginaInicial = (usuario) => (podeGerenciarConteudo(usuario) ? '/painel/base' : '/painel/temas')

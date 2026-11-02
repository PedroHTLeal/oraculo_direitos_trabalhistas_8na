import { useCallback, useEffect, useMemo, useState } from 'react'
import * as api from '../api'
import { ContextoAutenticacao } from './contexto'

function ProvedorAutenticacao({ children }) {
  const [usuario, setUsuario] = useState(null)
  const [carregando, setCarregando] = useState(Boolean(api.lerToken()))
  const [aviso, setAviso] = useState(null)

  const encerrar = useCallback((mensagem) => {
    api.guardarToken(null)
    setUsuario(null)
    setAviso(mensagem || null)
  }, [])

  // Recupera a sessão salva ao abrir o site
  useEffect(() => {
    api.quandoPerderSessao(() => encerrar('Sua sessão expirou. Faça login novamente.'))
    if (!api.lerToken()) return
    api
      .buscarUsuarioAtual()
      .then(setUsuario)
      .catch(() => encerrar())
      .finally(() => setCarregando(false))
  }, [encerrar])

  const valor = useMemo(() => {
    async function abrirSessao(promessa) {
      const sessao = await promessa
      api.guardarToken(sessao.token)
      setUsuario(sessao.usuario)
      setAviso(null)
      return sessao.usuario
    }

    return {
      usuario,
      carregando,
      aviso,
      entrar: (identificador, senha) => abrirSessao(api.entrar(identificador, senha)),
      cadastrar: (dados) => abrirSessao(api.cadastrar(dados)),
      sair: async () => {
        await api.sair().catch(() => {})
        encerrar()
      },
    }
  }, [usuario, carregando, aviso, encerrar])

  return <ContextoAutenticacao.Provider value={valor}>{children}</ContextoAutenticacao.Provider>
}

export default ProvedorAutenticacao

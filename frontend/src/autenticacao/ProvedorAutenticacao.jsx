import { useCallback, useEffect, useMemo, useState } from 'react'
import * as api from '../api'
import { ContextoAutenticacao } from './contexto'

function ProvedorAutenticacao({ children }) {
  const [usuario, setUsuario] = useState(null)
  const [carregando, setCarregando] = useState(Boolean(api.lerToken()))
  const [aviso, setAviso] = useState(null)
  // Saída pelo botão Sair: o próximo login não deve voltar à página da pessoa anterior
  const [saiuAgora, setSaiuAgora] = useState(false)

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
      setSaiuAgora(false)
      return sessao.usuario
    }

    return {
      usuario,
      carregando,
      aviso,
      entrar: (email, senha) => abrirSessao(api.entrar(email, senha)),
      cadastrar: (dados) => abrirSessao(api.cadastrar(dados)),
      saiuAgora,
      sair: async () => {
        await api.sair().catch(() => {})
        setSaiuAgora(true)
        encerrar()
      },
    }
  }, [usuario, carregando, aviso, saiuAgora, encerrar])

  return <ContextoAutenticacao.Provider value={valor}>{children}</ContextoAutenticacao.Provider>
}

export default ProvedorAutenticacao

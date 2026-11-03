import { useState } from 'react'
import { useAutenticacao } from '../autenticacao/contexto'
import { regras, validar } from '../validacao'
import Campo from './Campo'

const ESQUEMA = {
  email: [regras.obrigatorio('e-mail'), regras.email()],
  senha: [regras.obrigatorio('senha')],
}

// Login com e-mail e senha (usuários e equipe do Oráculo)
function FormularioEntrar({ aoEntrar, prefixo = 'entrar' }) {
  const { entrar } = useAutenticacao()
  const [dados, setDados] = useState({ email: '', senha: '' })
  const [erros, setErros] = useState({})
  const [erroGeral, setErroGeral] = useState(null)
  const [enviando, setEnviando] = useState(false)

  const mudar = (campo) => (evento) => setDados({ ...dados, [campo]: evento.target.value })

  async function enviar(evento) {
    evento.preventDefault()
    const encontrados = validar(dados, ESQUEMA)
    setErros(encontrados)
    setErroGeral(null)
    if (Object.keys(encontrados).length) return

    setEnviando(true)
    try {
      const usuario = await entrar(dados.email.trim(), dados.senha)
      aoEntrar?.(usuario)
    } catch (falha) {
      setErroGeral(falha.message)
      setEnviando(false)
    }
  }

  return (
    <form className="cartao-formulario" onSubmit={enviar} noValidate>
      {erroGeral && (
        <p className="alerta alerta-erro" role="alert">
          {erroGeral}
        </p>
      )}
      <Campo
        id={`${prefixo}-email`}
        rotulo="E-mail"
        type="email"
        autoComplete="username"
        placeholder="nome@exemplo.com"
        value={dados.email}
        onChange={mudar('email')}
        erro={erros.email}
      />
      <Campo
        id={`${prefixo}-senha`}
        rotulo="Senha"
        type="password"
        autoComplete="current-password"
        value={dados.senha}
        onChange={mudar('senha')}
        erro={erros.senha}
      />
      <button type="submit" className="botao-principal" disabled={enviando}>
        {enviando ? 'Entrando...' : 'Entrar'}
      </button>
    </form>
  )
}

export default FormularioEntrar

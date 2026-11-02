import { useState } from 'react'
import { useAutenticacao } from '../autenticacao/contexto'
import { regras, validar } from '../validacao'
import Campo from './Campo'

const ESQUEMA = {
  identificador: [regras.obrigatorio('WhatsApp ou e-mail')],
  senha: [regras.obrigatorio('senha')],
}

// Login por telefone (quem recebe pelo WhatsApp) ou e-mail (equipe do Oráculo)
function FormularioEntrar({ aoEntrar, prefixo = 'entrar' }) {
  const { entrar } = useAutenticacao()
  const [dados, setDados] = useState({ identificador: '', senha: '' })
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
      const usuario = await entrar(dados.identificador.trim(), dados.senha)
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
        id={`${prefixo}-identificador`}
        rotulo="WhatsApp ou e-mail"
        autoComplete="username"
        placeholder="(51) 99999-8888"
        value={dados.identificador}
        onChange={mudar('identificador')}
        erro={erros.identificador}
        ajuda="Use o WhatsApp do cadastro. A equipe do Oráculo entra com o e-mail."
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

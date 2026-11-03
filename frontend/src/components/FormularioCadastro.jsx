import { useState } from 'react'
import { useAutenticacao } from '../autenticacao/contexto'
import { regras, validar } from '../validacao'
import Campo from './Campo'

const ESQUEMA = {
  nome: [regras.obrigatorio('nome'), regras.minimo('nome', 2), regras.maximo('nome', 100)],
  email: [regras.obrigatorio('e-mail'), regras.email()],
  senha: [regras.obrigatorio('senha'), regras.minimo('senha', 8), regras.maximo('senha', 128)],
  confirmacao: [regras.igual('senha', 'As senhas não conferem.')],
  consentimento: [(valor) => (valor ? null : 'É preciso autorizar o envio de e-mails.')],
}

// Conta de quem quer acompanhar temas e receber as novidades por e-mail: nome, e-mail e senha
function FormularioCadastro({ aoCadastrar, prefixo = 'cadastro' }) {
  const { cadastrar } = useAutenticacao()
  const [dados, setDados] = useState({ nome: '', email: '', senha: '', confirmacao: '', consentimento: false })
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
      const usuario = await cadastrar({
        nome: dados.nome.trim(),
        email: dados.email.trim(),
        senha: dados.senha,
        consentimento: dados.consentimento,
      })
      aoCadastrar?.(usuario)
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
      <Campo id={`${prefixo}-nome`} rotulo="Nome" autoComplete="name" value={dados.nome} onChange={mudar('nome')} erro={erros.nome} />
      <Campo
        id={`${prefixo}-email`}
        rotulo="E-mail"
        type="email"
        autoComplete="email"
        placeholder="nome@exemplo.com"
        value={dados.email}
        onChange={mudar('email')}
        erro={erros.email}
        ajuda="É para este e-mail que enviaremos as novidades."
      />
      <Campo
        id={`${prefixo}-senha`}
        rotulo="Senha"
        type="password"
        autoComplete="new-password"
        value={dados.senha}
        onChange={mudar('senha')}
        erro={erros.senha}
        ajuda="Mínimo de 8 caracteres."
      />
      <Campo
        id={`${prefixo}-confirmacao`}
        rotulo="Confirme a senha"
        type="password"
        autoComplete="new-password"
        value={dados.confirmacao}
        onChange={mudar('confirmacao')}
        erro={erros.confirmacao}
      />
      <label className={erros.consentimento ? 'consentimento com-erro' : 'consentimento'}>
        <input
          type="checkbox"
          checked={dados.consentimento}
          onChange={(evento) => setDados({ ...dados, consentimento: evento.target.checked })}
        />
        <span>
          Autorizo o uso do meu e-mail apenas para receber conteúdos do Oráculo, conforme a Lei Geral de Proteção de Dados
          (LGPD).
        </span>
      </label>
      {erros.consentimento && (
        <p className="campo-erro" role="alert">
          {erros.consentimento}
        </p>
      )}
      <button type="submit" className="botao-principal" disabled={enviando}>
        {enviando ? 'Criando conta...' : 'Criar conta'}
      </button>
    </form>
  )
}

export default FormularioCadastro

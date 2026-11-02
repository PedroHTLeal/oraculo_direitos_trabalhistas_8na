import { useState } from 'react'
import { useAutenticacao } from '../autenticacao/contexto'
import { formatarTelefone } from '../telefone'
import { regras, validar } from '../validacao'
import Campo from './Campo'

const ESQUEMA = {
  nome: [regras.obrigatorio('nome'), regras.minimo('nome', 2), regras.maximo('nome', 100)],
  telefone: [regras.obrigatorio('WhatsApp'), regras.telefone()],
  senha: [regras.obrigatorio('senha'), regras.minimo('senha', 8), regras.maximo('senha', 128)],
  confirmacao: [regras.igual('senha', 'As senhas não conferem.')],
  consentimento: [(valor) => (valor ? null : 'É preciso autorizar o envio de mensagens pelo WhatsApp.')],
}

// Conta de quem quer receber conteúdos pelo WhatsApp: nome, telefone e senha
function FormularioCadastro({ aoCadastrar, prefixo = 'cadastro' }) {
  const { cadastrar } = useAutenticacao()
  const [dados, setDados] = useState({ nome: '', telefone: '', senha: '', confirmacao: '', consentimento: false })
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
        telefone: dados.telefone,
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
        id={`${prefixo}-telefone`}
        rotulo="WhatsApp com DDD"
        type="tel"
        inputMode="numeric"
        autoComplete="tel-national"
        placeholder="(51) 99999-8888"
        value={dados.telefone}
        onChange={(evento) => setDados({ ...dados, telefone: formatarTelefone(evento.target.value) })}
        erro={erros.telefone}
        ajuda="É para este número que enviaremos os conteúdos."
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
          Autorizo o uso do meu telefone apenas para receber conteúdos do Oráculo pelo WhatsApp, conforme a Lei Geral de
          Proteção de Dados (LGPD).
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

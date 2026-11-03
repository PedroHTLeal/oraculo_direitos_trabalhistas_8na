// Regras iguais às do servidor, para avisar o usuário antes de enviar o formulário

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/

export const regras = {
  obrigatorio: (rotulo) => (valor) => (String(valor ?? '').trim() ? null : `Preencha o campo ${rotulo}.`),
  minimo: (rotulo, tamanho) => (valor) =>
    String(valor ?? '').trim().length >= tamanho ? null : `O campo ${rotulo} precisa ter pelo menos ${tamanho} caracteres.`,
  maximo: (rotulo, tamanho) => (valor) =>
    String(valor ?? '').trim().length <= tamanho ? null : `O campo ${rotulo} pode ter no máximo ${tamanho} caracteres.`,
  email: () => (valor) => (EMAIL.test(String(valor ?? '').trim()) ? null : 'Informe um e-mail válido, por exemplo nome@exemplo.com.'),
  igual: (outro, mensagem) => (valor, dados) => (valor === dados[outro] ? null : mensagem),
}

// Devolve { campo: mensagem } apenas para os campos com erro
export function validar(dados, esquema) {
  const erros = {}
  for (const [campo, verificacoes] of Object.entries(esquema)) {
    for (const verificar of verificacoes) {
      const erro = verificar(dados[campo], dados)
      if (erro) {
        erros[campo] = erro
        break
      }
    }
  }
  return erros
}

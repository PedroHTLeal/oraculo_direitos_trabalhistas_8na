// Campo de formulário com rótulo, ajuda e mensagem de erro ligada ao campo (acessível).
// Sem "children", desenha um <input>; com "children", usa o controle recebido (select, textarea).
function Campo({ id, rotulo, erro, ajuda, children, ...propriedades }) {
  const idDescricao = erro ? `${id}-erro` : ajuda ? `${id}-ajuda` : undefined

  return (
    <div className={erro ? 'campo com-erro' : 'campo'}>
      <label htmlFor={id}>{rotulo}</label>
      {children || <input id={id} aria-invalid={Boolean(erro)} aria-describedby={idDescricao} {...propriedades} />}
      {erro ? (
        <span id={idDescricao} className="campo-erro" role="alert">
          {erro}
        </span>
      ) : (
        ajuda && (
          <span id={idDescricao} className="campo-ajuda">
            {ajuda}
          </span>
        )
      )}
    </div>
  )
}

export default Campo

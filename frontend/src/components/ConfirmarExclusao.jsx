import { useEffect, useRef, useState } from 'react'

// Janela de confirmação antes de excluir; mostra o erro do servidor, se houver
function ConfirmarExclusao({ titulo, descricao, aoConfirmar, aoFechar }) {
  const dialogo = useRef(null)
  const [excluindo, setExcluindo] = useState(false)
  const [erro, setErro] = useState(null)

  useEffect(() => {
    dialogo.current?.showModal()
  }, [])

  async function confirmar() {
    setExcluindo(true)
    setErro(null)
    try {
      await aoConfirmar()
      dialogo.current.close()
    } catch (falha) {
      setErro(falha.message)
      setExcluindo(false)
    }
  }

  return (
    <dialog ref={dialogo} className="modal" onClose={aoFechar} aria-labelledby="titulo-exclusao">
      <h2 id="titulo-exclusao">{titulo}</h2>
      <p className="modal-texto">{descricao}</p>
      {erro && (
        <p className="erro" role="alert">
          {erro}
        </p>
      )}
      <div className="acoes">
        <button type="button" className="botao-secundario" onClick={() => dialogo.current.close()}>
          Cancelar
        </button>
        <button type="button" className="botao-perigo" onClick={confirmar} disabled={excluindo}>
          {excluindo ? 'Excluindo...' : 'Excluir'}
        </button>
      </div>
    </dialog>
  )
}

export default ConfirmarExclusao

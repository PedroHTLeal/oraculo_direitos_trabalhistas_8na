function Logo() {
  return (
    <div className="logo">
      <svg className="logo-simbolo" viewBox="0 0 40 40" aria-hidden="true">
        <circle cx="20" cy="20" r="15" fill="none" stroke="currentColor" strokeWidth="5" />
        <circle cx="31" cy="9" r="5.5" fill="var(--cor-destaque)" stroke="var(--cor-fundo)" strokeWidth="2.5" />
      </svg>
      <span className="logo-nome">Oráculo</span>
      <span className="logo-divisor" aria-hidden="true" />
      <span className="logo-complemento">
        Direitos
        <br />
        Trabalhistas
      </span>
    </div>
  )
}

export default Logo

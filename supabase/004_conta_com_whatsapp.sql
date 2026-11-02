-- Oráculo dos Direitos Trabalhistas - conta com WhatsApp
-- Execute este arquivo inteiro no SQL Editor do Supabase (depois do 003).
--
-- O cadastro público passa a ser feito com nome, telefone (WhatsApp) e senha:
-- a conta existe para a pessoa receber conteúdos pelo WhatsApp.
-- A equipe (administradores e curadores) continua entrando com e-mail.

alter table public.usuarios alter column email drop not null;
alter table public.usuarios add column if not exists telefone text;
alter table public.usuarios add column if not exists consentimento_whatsapp boolean not null default false;

create unique index if not exists usuarios_telefone_idx on public.usuarios (telefone);

-- Contas de usuário comum criadas antes desta mudança não têm telefone e não
-- conseguiriam entrar; elas eram contas de teste e são removidas
delete from public.usuarios where perfil = 'usuario' and telefone is null;

-- Toda conta precisa de um meio de login; usuários comuns precisam do telefone
alter table public.usuarios drop constraint if exists usuarios_login_check;
alter table public.usuarios add constraint usuarios_login_check check (
  (perfil = 'usuario' and telefone is not null)
  or (perfil in ('administrador', 'curador') and email is not null)
);

-- Cada pedido de "Saiba mais" fica ligado à conta de quem pediu
alter table public.solicitacoes_whatsapp
  add column if not exists usuario_id uuid references public.usuarios (id) on delete set null;

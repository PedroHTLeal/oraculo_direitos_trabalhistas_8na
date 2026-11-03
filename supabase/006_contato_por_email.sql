-- Oráculo dos Direitos Trabalhistas - contato por e-mail
-- Execute este arquivo inteiro no SQL Editor do Supabase (depois do 005).
--
-- O conteúdo complementar ("Quer saber mais?") e as novidades dos temas
-- acompanhados passam a ser enviados por e-mail. Todas as contas entram com
-- e-mail e senha, e o pedido de "Saber mais" guarda o nome e o e-mail informados.

-- Pedidos de "Saber mais": nome e e-mail de quem pediu
alter table if exists public.solicitacoes_whatsapp rename to solicitacoes_conteudo;
alter table public.solicitacoes_conteudo add column if not exists nome text;
alter table public.solicitacoes_conteudo add column if not exists email text;
alter table public.solicitacoes_conteudo drop column if exists telefone;

-- Contas de usuário comum criadas com telefone eram contas de teste e são
-- removidas (as inscrições delas saem junto)
delete from public.usuarios where email is null;

alter table public.usuarios drop constraint if exists usuarios_login_check;
alter table public.usuarios alter column email set not null;
drop index if exists public.usuarios_telefone_idx;
alter table public.usuarios drop column if exists telefone;
alter table public.usuarios drop column if exists consentimento_whatsapp;
alter table public.usuarios add column if not exists consentimento_email boolean not null default false;

-- Inscrições em temas: as novidades vão para o e-mail da conta
alter table public.inscricoes_tema add column if not exists email text;
update public.inscricoes_tema i set email = u.email from public.usuarios u where u.id = i.usuario_id;
delete from public.inscricoes_tema where email is null;
alter table public.inscricoes_tema alter column email set not null;
alter table public.inscricoes_tema drop constraint if exists inscricoes_tema_tema_id_telefone_key;
alter table public.inscricoes_tema drop column if exists telefone;
create unique index if not exists inscricoes_tema_email_idx on public.inscricoes_tema (tema_id, lower(email));

-- Histórico: o pedido de conteúdo passa a ser por e-mail
update public.historico_operacoes set acao = 'pedir_conteudo' where acao = 'pedir_whatsapp';

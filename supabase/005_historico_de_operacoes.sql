-- Oráculo dos Direitos Trabalhistas - histórico de operações (Sprint 07)
-- Execute este arquivo inteiro no SQL Editor do Supabase (depois do 004).
--
-- Registra as principais ações feitas no sistema (logins, cadastros, alterações
-- na base de conhecimento, usuários, atualizações e pedidos de WhatsApp), para
-- consulta pela administração. Não guarda senhas nem o conteúdo das mensagens.

create table if not exists public.historico_operacoes (
  id bigint generated always as identity primary key,
  usuario_id uuid references public.usuarios (id) on delete set null,
  -- Nome guardado no momento da ação, para o registro continuar legível
  -- mesmo se o usuário for excluído depois
  usuario_nome text,
  acao text not null,
  entidade text not null,
  entidade_id text,
  descricao text not null,
  criado_em timestamptz not null default now()
);

create index if not exists historico_criado_em_idx on public.historico_operacoes (criado_em desc);
create index if not exists historico_usuario_idx on public.historico_operacoes (usuario_id);

alter table public.historico_operacoes enable row level security;

-- Consultas do dashboard por período
create index if not exists perguntas_criado_em_idx on public.perguntas (criado_em desc);
create index if not exists solicitacoes_criado_em_idx on public.solicitacoes_whatsapp (criado_em desc);

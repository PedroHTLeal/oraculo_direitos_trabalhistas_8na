-- Oráculo dos Direitos Trabalhistas - estrutura inicial do banco
-- Execute este arquivo inteiro no SQL Editor do Supabase.

-- Busca em português que ignora acentos ("ferias" encontra "férias")
create extension if not exists unaccent with schema extensions;

do $$
begin
  if not exists (select 1 from pg_ts_config where cfgname = 'pt_sem_acento') then
    create text search configuration public.pt_sem_acento (copy = pg_catalog.portuguese);
    alter text search configuration public.pt_sem_acento
      alter mapping for hword, hword_part, word with extensions.unaccent, portuguese_stem;
  end if;
end
$$;

-- Trechos da Cartilha de Direitos e Obrigações no Trabalho (TRT4)
create table if not exists public.trechos (
  id bigint generated always as identity primary key,
  tema text not null,
  secao text not null,
  ordem int not null,
  texto text not null,
  url text not null,
  busca tsvector generated always as (
    setweight(to_tsvector('public.pt_sem_acento', tema || ' ' || secao), 'A') ||
    setweight(to_tsvector('public.pt_sem_acento', texto), 'B')
  ) stored,
  atualizado_em timestamptz not null default now(),
  unique (url, ordem)
);

create index if not exists trechos_busca_idx on public.trechos using gin (busca);

-- Perguntas feitas no sistema, para auditoria (UC08). Não guarda dados pessoais.
create table if not exists public.perguntas (
  id uuid primary key default gen_random_uuid(),
  texto text not null,
  resposta text not null,
  encontrou boolean not null,
  trechos_ids bigint[] not null default '{}',
  criado_em timestamptz not null default now()
);

-- Pedidos de conteúdo complementar pelo WhatsApp (UC04, UC05)
create table if not exists public.solicitacoes_whatsapp (
  id uuid primary key default gen_random_uuid(),
  pergunta_id uuid not null references public.perguntas (id),
  telefone text not null,
  consentimento boolean not null check (consentimento),
  status text not null default 'pendente' check (status in ('pendente', 'enviado', 'erro')),
  materiais jsonb,
  erro text,
  criado_em timestamptz not null default now(),
  enviado_em timestamptz
);

-- Segurança (RNF03): só o backend, com a chave de serviço, acessa as tabelas.
-- Sem políticas, o acesso público (chave anon) fica bloqueado.
alter table public.trechos enable row level security;
alter table public.perguntas enable row level security;
alter table public.solicitacoes_whatsapp enable row level security;

-- Busca os trechos mais relevantes para uma pergunta em linguagem natural.
-- As palavras da pergunta são combinadas com "OU" e os resultados ordenados
-- pela relevância (palavras no tema e no subtítulo pesam mais).
create or replace function public.buscar_trechos(consulta text, limite int default 6)
returns table (id bigint, tema text, secao text, texto text, url text, relevancia real)
language sql
stable
set search_path = public, extensions
as $$
  with termos as (
    select to_tsquery(
      'public.pt_sem_acento',
      replace(plainto_tsquery('public.pt_sem_acento', consulta)::text, ' & ', ' | ')
    ) as consulta
  )
  select t.id, t.tema, t.secao, t.texto, t.url, ts_rank_cd(t.busca, termos.consulta) as relevancia
  from public.trechos t, termos
  where t.busca @@ termos.consulta
  order by relevancia desc
  limit limite;
$$;

revoke execute on function public.buscar_trechos(text, int) from anon, authenticated;

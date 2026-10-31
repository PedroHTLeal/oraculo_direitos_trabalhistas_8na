-- Oráculo dos Direitos Trabalhistas - modelo relacional (Sprints 02 e 03)
-- Execute este arquivo inteiro no SQL Editor do Supabase (depois do 001 e do 002).
--
-- Evolução do banco para o modelo relacional completo:
-- - temas passam a ser uma tabela própria (antes eram texto repetido em cada trecho);
-- - trechos usados em cada pergunta e materiais enviados ganham tabelas de ligação
--   (antes eram uma lista e um JSON dentro da linha);
-- - usuários com perfis de acesso e sessões de login (RF14, RNF04 - Sprint 03);
-- - inscrições em temas (RF12) e atualizações enviadas aos inscritos (RF13).
--
-- As tabelas antigas não guardam dados que não possam ser recriados: a cartilha é
-- carregada de novo com "python scripts/carregar_cartilha.py".

-- Pode ser executado de novo: recria as tabelas do zero
drop function if exists public.buscar_trechos(text, int);
drop table if exists public.envios_atualizacao cascade;
drop table if exists public.atualizacoes cascade;
drop table if exists public.inscricoes_tema cascade;
drop table if exists public.materiais_enviados cascade;
drop table if exists public.solicitacoes_whatsapp cascade;
drop table if exists public.pergunta_trechos cascade;
drop table if exists public.perguntas cascade;
drop table if exists public.trechos cascade;
drop table if exists public.temas cascade;
drop table if exists public.sessoes cascade;
drop table if exists public.usuarios cascade;

-- Usuários cadastrados e seus perfis de acesso (RF14, RNF04).
-- A consulta pública não exige conta (RF01); o login dá acesso à área
-- administrativa e ao acompanhamento de temas.
--   administrador: gerencia usuários, a base de conhecimento e as auditorias
--   curador: gerencia a base de conhecimento e consulta as perguntas
--   usuario: acompanha temas e recebe atualizações
create table public.usuarios (
  id uuid primary key default gen_random_uuid(),
  nome text not null,
  email text not null,
  senha_hash text not null,
  perfil text not null default 'usuario' check (perfil in ('administrador', 'curador', 'usuario')),
  ativo boolean not null default true,
  criado_em timestamptz not null default now(),
  atualizado_em timestamptz not null default now()
);

create unique index usuarios_email_idx on public.usuarios (lower(email));

-- Sessões de login: guarda só o hash do token entregue ao navegador
create table public.sessoes (
  token_hash text primary key,
  usuario_id uuid not null references public.usuarios (id) on delete cascade,
  criada_em timestamptz not null default now(),
  expira_em timestamptz not null
);

create index sessoes_usuario_idx on public.sessoes (usuario_id);

-- Temas da cartilha (as 25 páginas do TRT4)
create table public.temas (
  id smallint generated always as identity primary key,
  nome text not null unique,
  slug text not null unique,
  url text not null,
  criado_em timestamptz not null default now()
);

-- Trechos da cartilha, um por subtítulo
create table public.trechos (
  id bigint generated always as identity primary key,
  tema_id smallint not null references public.temas (id) on delete cascade,
  secao text not null,
  ordem int not null,
  texto text not null,
  busca tsvector,
  atualizado_por uuid references public.usuarios (id) on delete set null,
  atualizado_em timestamptz not null default now(),
  unique (tema_id, ordem)
);

create index trechos_busca_idx on public.trechos using gin (busca);
create index trechos_tema_idx on public.trechos (tema_id);

-- O índice de busca usa o nome do tema (de outra tabela), por isso é mantido por gatilho
create or replace function public.atualizar_busca_trecho()
returns trigger
language plpgsql
set search_path = public, extensions
as $$
begin
  new.busca :=
    setweight(to_tsvector('public.pt_sem_acento',
      (select nome from public.temas where id = new.tema_id) || ' ' || new.secao), 'A') ||
    setweight(to_tsvector('public.pt_sem_acento', new.texto), 'B');
  new.atualizado_em := now();
  return new;
end;
$$;

create trigger trechos_atualizar_busca
  before insert or update of tema_id, secao, texto on public.trechos
  for each row execute function public.atualizar_busca_trecho();

-- Perguntas feitas no sistema, para auditoria (UC08). Não guardam dados pessoais.
create table public.perguntas (
  id uuid primary key default gen_random_uuid(),
  texto text not null,
  resposta text not null,
  encontrou boolean not null,
  criado_em timestamptz not null default now()
);

-- Trechos da cartilha usados como fonte de cada resposta (relacionamento N:N)
create table public.pergunta_trechos (
  pergunta_id uuid not null references public.perguntas (id) on delete cascade,
  trecho_id bigint not null references public.trechos (id) on delete cascade,
  primary key (pergunta_id, trecho_id)
);

-- Pedidos de conteúdo complementar pelo WhatsApp (UC04, UC05)
create table public.solicitacoes_whatsapp (
  id uuid primary key default gen_random_uuid(),
  pergunta_id uuid not null references public.perguntas (id) on delete cascade,
  telefone text not null,
  consentimento boolean not null check (consentimento),
  status text not null default 'pendente' check (status in ('pendente', 'enviado', 'erro')),
  erro text,
  criado_em timestamptz not null default now(),
  enviado_em timestamptz
);

-- Sites e vídeos enviados em cada pedido
create table public.materiais_enviados (
  id bigint generated always as identity primary key,
  solicitacao_id uuid not null references public.solicitacoes_whatsapp (id) on delete cascade,
  tipo text not null check (tipo in ('site', 'video')),
  titulo text not null,
  url text not null
);

-- Inscrições para acompanhar um tema pelo WhatsApp (UC06, RF12)
create table public.inscricoes_tema (
  id uuid primary key default gen_random_uuid(),
  tema_id smallint not null references public.temas (id) on delete cascade,
  usuario_id uuid references public.usuarios (id) on delete cascade,
  telefone text not null,
  consentimento boolean not null check (consentimento),
  ativa boolean not null default true,
  criado_em timestamptz not null default now(),
  cancelado_em timestamptz,
  unique (tema_id, telefone)
);

-- Atualizações publicadas pelo administrador sobre um tema (UC07, RF13)
create table public.atualizacoes (
  id bigint generated always as identity primary key,
  tema_id smallint not null references public.temas (id) on delete cascade,
  autor_id uuid references public.usuarios (id) on delete set null,
  titulo text not null,
  conteudo text not null,
  url text,
  publicado_em timestamptz not null default now()
);

-- Envio de cada atualização a cada inscrito (relacionamento N:N)
create table public.envios_atualizacao (
  atualizacao_id bigint not null references public.atualizacoes (id) on delete cascade,
  inscricao_id uuid not null references public.inscricoes_tema (id) on delete cascade,
  status text not null default 'pendente' check (status in ('pendente', 'enviado', 'erro')),
  enviado_em timestamptz,
  primary key (atualizacao_id, inscricao_id)
);

-- Segurança (RNF03): sem políticas, o acesso público fica bloqueado;
-- só o backend, com a chave de serviço, lê e grava os dados.
alter table public.usuarios enable row level security;
alter table public.sessoes enable row level security;
alter table public.temas enable row level security;
alter table public.trechos enable row level security;
alter table public.perguntas enable row level security;
alter table public.pergunta_trechos enable row level security;
alter table public.solicitacoes_whatsapp enable row level security;
alter table public.materiais_enviados enable row level security;
alter table public.inscricoes_tema enable row level security;
alter table public.atualizacoes enable row level security;
alter table public.envios_atualizacao enable row level security;

-- Busca os trechos mais relevantes para uma pergunta em linguagem natural.
-- 1. Acrescenta os sinônimos dos termos encontrados na pergunta.
-- 2. Combina as palavras com "OU" e ordena pela relevância
--    (palavras no tema e no subtítulo pesam mais).
create or replace function public.buscar_trechos(consulta text, limite int default 6)
returns table (id bigint, tema text, secao text, texto text, url text, relevancia real)
language sql
stable
set search_path = public, extensions
as $$
  with normalizada as (
    select lower(extensions.unaccent(consulta)) as texto
  ),
  expandida as (
    select normalizada.texto || ' ' || coalesce(string_agg(s.equivalentes, ' '), '') as texto
    from normalizada
    left join public.sinonimos s on normalizada.texto ~ ('\m' || s.termo || '\M')
    group by normalizada.texto
  ),
  termos as (
    -- O resultado do plainto_tsquery já está normalizado: é convertido direto
    -- para tsquery, sem passar de novo pelo dicionário (o que alteraria as palavras)
    select replace(plainto_tsquery('public.pt_sem_acento', expandida.texto)::text, ' & ', ' | ')::tsquery as consulta
    from expandida
  )
  select t.id, tm.nome, t.secao, t.texto, tm.url, ts_rank_cd(t.busca, termos.consulta) as relevancia
  from public.trechos t
  join public.temas tm on tm.id = t.tema_id
  cross join termos
  where t.busca @@ termos.consulta
  order by relevancia desc
  limit limite;
$$;

revoke execute on function public.buscar_trechos(text, int) from anon, authenticated;

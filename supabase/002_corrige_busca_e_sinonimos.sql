-- Oráculo dos Direitos Trabalhistas - correção da busca e sinônimos
-- Execute este arquivo inteiro no SQL Editor do Supabase (depois do 001).

-- Palavras do dia a dia que a cartilha escreve de outro jeito.
-- Quando a pergunta contém o "termo", as palavras de "equivalentes" também são buscadas.
-- O administrador pode incluir, alterar ou remover linhas (UC07).
create table if not exists public.sinonimos (
  termo text primary key,
  equivalentes text not null
);

alter table public.sinonimos enable row level security;

insert into public.sinonimos (termo, equivalentes) values
  ('estagiario', 'estagio'),
  ('estagiaria', 'estagio'),
  ('demitido', 'dispensa rescisao'),
  ('demitida', 'dispensa rescisao'),
  ('demissao', 'dispensa rescisao'),
  ('mandado embora', 'dispensa rescisao'),
  ('mandada embora', 'dispensa rescisao'),
  ('pedir as contas', 'pedido demissao rescisao'),
  ('justa causa', 'rescisao'),
  ('patrao', 'empregador'),
  ('patroa', 'empregadora'),
  ('chefe', 'empregador superior'),
  ('empresa', 'empregador'),
  ('domestica', 'domestico'),
  ('diarista', 'domestico diarista'),
  ('carteira assinada', 'registro carteira trabalho'),
  ('registro', 'carteira trabalho'),
  ('fgts', 'fundo garantia'),
  ('decimo terceiro', '13 gratificacao natalina'),
  ('13o', 'decimo terceiro gratificacao natalina'),
  ('hora extra', 'horas extras jornada'),
  ('horas extras', 'jornada'),
  ('gravida', 'gestante maternidade'),
  ('gravidez', 'gestante maternidade'),
  ('licenca maternidade', 'salario maternidade gestante'),
  ('assedio', 'assedio moral danos morais'),
  ('humilhado', 'assedio moral danos morais'),
  ('humilhada', 'assedio moral danos morais'),
  ('acidente', 'acidente trabalho seguranca'),
  ('aplicativo', 'relacao emprego autonomo'),
  ('motorista de aplicativo', 'relacao emprego autonomo'),
  ('entregador', 'relacao emprego autonomo'),
  ('menor de idade', 'trabalho infantil jovem aprendiz'),
  ('primeiro emprego', 'jovem aprendiz'),
  ('deficiente', 'pessoas deficiencia'),
  ('vale refeicao', 'vale alimentacao'),
  ('passagem', 'vale transporte'),
  ('processar', 'justica trabalho acao'),
  ('processo', 'justica trabalho acao'),
  ('advogado', 'advogado gratuito'),
  ('salario minimo', 'salario minimo remuneracao')
on conflict (termo) do nothing;

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
  select t.id, t.tema, t.secao, t.texto, t.url, ts_rank_cd(t.busca, termos.consulta) as relevancia
  from public.trechos t, termos
  where t.busca @@ termos.consulta
  order by relevancia desc
  limit limite;
$$;

revoke execute on function public.buscar_trechos(text, int) from anon, authenticated;

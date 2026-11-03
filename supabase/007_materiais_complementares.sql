-- Oráculo dos Direitos Trabalhistas - materiais complementares escolhidos pela equipe
-- Execute este arquivo inteiro no SQL Editor do Supabase (depois do 006).
--
-- Os sites e vídeos enviados no "Saber mais" são escolhidos e conferidos pela
-- equipe, por assunto. O sistema escolhe o assunto pelas palavras-chave da pergunta.

create table if not exists public.materiais_complementares (
  id bigint generated always as identity primary key,
  tema_id smallint not null references public.temas (id) on delete cascade,
  assunto text not null,
  -- Palavras que identificam o assunto na pergunta, sem acento e em minúsculas
  palavras_chave text[] not null,
  tipo text not null check (tipo in ('site', 'video')),
  titulo text not null,
  url text not null,
  ordem smallint not null default 1,
  criado_em timestamptz not null default now(),
  unique (assunto, url)
);

alter table public.materiais_complementares enable row level security;

-- Primeira versão: férias e 13º salário
insert into public.materiais_complementares (tema_id, assunto, palavras_chave, tipo, titulo, url, ordem)
select t.id, m.assunto, m.palavras_chave, m.tipo, m.titulo, m.url, m.ordem
from (values
  ('Férias', 'Férias', array['ferias'], 'video',
   'Férias trabalhistas: como funciona? (CEISC)', 'https://www.youtube.com/watch?v=QuyDtU-92W8', 1),
  ('Férias', 'Férias', array['ferias'], 'video',
   'Férias CLT precisam ser 30 dias seguidos? Veja o que a lei permite (Contas Online)', 'https://www.youtube.com/watch?v=ZEsaeJE6VmM', 2),
  ('Férias', 'Férias', array['ferias'], 'site',
   'Férias trabalhistas: como funciona e quais são os direitos do empregado (Jusbrasil)',
   'https://www.jusbrasil.com.br/artigos/ferias-trabalhistas-como-funciona-e-quais-sao-os-direitos-do-empregado/1162566612', 1),
  ('Salário e Remuneração', '13º salário', array['13', 'decimo terceiro', 'gratificacao natalina'], 'video',
   'O que é Décimo Terceiro Salário, quem tem direito e como calcular? (Conube)', 'https://www.youtube.com/watch?v=WNVyiShMdvU', 1),
  ('Salário e Remuneração', '13º salário', array['13', 'decimo terceiro', 'gratificacao natalina'], 'video',
   'Como calcular o 13º salário (Acordo Certo)', 'https://www.youtube.com/watch?v=5bc1mYovje0', 2),
  ('Salário e Remuneração', '13º salário', array['13', 'decimo terceiro', 'gratificacao natalina'], 'site',
   '13º salário: datas de pagamento, antecipação e prazos (Quero Bolsa)', 'https://querobolsa.com.br/revista/13-salario-data-de-pagamento', 1)
) as m (tema, assunto, palavras_chave, tipo, titulo, url, ordem)
join public.temas t on t.nome = m.tema
on conflict (assunto, url) do nothing;

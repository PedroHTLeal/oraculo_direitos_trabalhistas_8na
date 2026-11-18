-- Oráculo dos Direitos Trabalhistas - ajustes da versão final do banco (Sprint 10)
-- Execute este arquivo inteiro no SQL Editor do Supabase (depois do 007).
--
-- Remove a única coluna que ficou sem uso e descreve cada tabela no próprio banco,
-- para quem abrir o Supabase entender a estrutura sem precisar do código.

-- O pedido de "Saber mais" não exige mais conta: o vínculo com o usuário deixou de ser usado
alter table public.solicitacoes_conteudo drop column if exists usuario_id;

comment on table public.temas is 'As 25 páginas (temas) da Cartilha de Direitos e Obrigações no Trabalho do TRT4.';
comment on table public.trechos is 'Trechos da cartilha, um por subtítulo, usados pela IA como fonte das respostas.';
comment on table public.sinonimos is 'Palavras do dia a dia e os termos da cartilha que a busca usa no lugar delas.';
comment on table public.perguntas is 'Perguntas feitas na consulta e as respostas geradas, sem dados pessoais (auditoria).';
comment on table public.pergunta_trechos is 'Trechos da cartilha usados como fonte de cada resposta (N:N).';
comment on table public.solicitacoes_conteudo is 'Pedidos de "Saber mais": nome, e-mail, autorização (LGPD) e situação do envio.';
comment on table public.materiais_enviados is 'Sites e vídeos enviados em cada pedido de "Saber mais".';
comment on table public.materiais_complementares is 'Sites e vídeos escolhidos pela equipe para cada assunto do "Saber mais".';
comment on table public.usuarios is 'Contas: administrador, curador ou usuário. Senhas guardadas só como hash (scrypt).';
comment on table public.sessoes is 'Sessões de login; guarda só o hash do token entregue ao navegador.';
comment on table public.inscricoes_tema is 'Temas que cada usuário acompanha, com o e-mail que recebe as novidades.';
comment on table public.atualizacoes is 'Novidades publicadas pela equipe sobre um tema.';
comment on table public.envios_atualizacao is 'Situação do envio de cada novidade para cada inscrito (N:N).';
comment on table public.historico_operacoes is 'Quem fez o quê e quando no sistema (logins, cadastros, alterações, exclusões, publicações).';

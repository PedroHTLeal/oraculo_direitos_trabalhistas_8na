import functools
import logging
from datetime import datetime, timezone

import httpx
from postgrest.exceptions import APIError
from supabase import create_client

logger = logging.getLogger(__name__)

CANDIDATOS = 20
MAXIMO_POR_TEMA = 3
TENTATIVAS = 3

# O Supabase às vezes encerra conexões que ficaram paradas; nesses casos basta repetir a operação
ERROS_DE_CONEXAO = (httpx.RemoteProtocolError, httpx.ConnectError, httpx.ReadError, httpx.WriteError, httpx.PoolTimeout)


def _repetir_se_a_conexao_cair(metodo):
    @functools.wraps(metodo)
    def executar(*args, **kwargs):
        for tentativa in range(1, TENTATIVAS + 1):
            try:
                return metodo(*args, **kwargs)
            except ERROS_DE_CONEXAO:
                if tentativa == TENTATIVAS:
                    raise
                logger.warning("Conexão com o banco caiu em %s; tentando de novo", metodo.__name__)

    return executar


def _com_novas_tentativas(classe):
    for nome, valor in list(vars(classe).items()):
        if callable(valor) and not nome.startswith("_"):
            setattr(classe, nome, _repetir_se_a_conexao_cair(valor))
    return classe


def diversificar(trechos, limite, maximo_por_tema=MAXIMO_POR_TEMA):
    """Mantém a ordem de relevância, mas evita que um só tema ocupe todas as vagas."""
    por_tema, escolhidos = {}, []
    for trecho in trechos:
        if por_tema.get(trecho["tema"], 0) < maximo_por_tema:
            por_tema[trecho["tema"]] = por_tema.get(trecho["tema"], 0) + 1
            escolhidos.append(trecho)
        if len(escolhidos) == limite:
            break
    return escolhidos


@_com_novas_tentativas
class RepositorioSupabase:
    """Acesso às tabelas do Supabase usadas pelo Oráculo."""

    def __init__(self, url, chave_servico):
        self.cliente = create_client(url, chave_servico)

    def buscar_trechos(self, consulta, limite=6):
        resultado = self.cliente.rpc("buscar_trechos", {"consulta": consulta, "limite": CANDIDATOS}).execute()
        return diversificar(resultado.data, limite)

    def salvar_pergunta(self, texto, resposta, encontrou, trechos_ids):
        registro = {"texto": texto, "resposta": resposta, "encontrou": encontrou}
        pergunta_id = self.cliente.table("perguntas").insert(registro).execute().data[0]["id"]
        if trechos_ids:
            self.cliente.table("pergunta_trechos").insert(
                [{"pergunta_id": pergunta_id, "trecho_id": trecho_id} for trecho_id in trechos_ids]
            ).execute()
        return pergunta_id

    def obter_pergunta(self, pergunta_id):
        dados = (
            self.cliente.table("perguntas")
            .select("id,texto,resposta,encontrou,pergunta_trechos(trecho_id)")
            .eq("id", pergunta_id)
            .execute()
            .data
        )
        if not dados:
            return None
        pergunta = dados[0]
        pergunta["trechos_ids"] = [ligacao["trecho_id"] for ligacao in pergunta.pop("pergunta_trechos")]
        return pergunta

    def obter_trechos(self, ids):
        if not ids:
            return []
        dados = self.cliente.table("trechos").select("id,secao,temas(nome,url)").in_("id", ids).execute().data
        return [
            {"id": t["id"], "secao": t["secao"], "tema": t["temas"]["nome"], "url": t["temas"]["url"]} for t in dados
        ]

    def criar_solicitacao(self, pergunta_id, telefone, usuario_id=None):
        registro = {"pergunta_id": pergunta_id, "telefone": telefone, "consentimento": True, "usuario_id": usuario_id}
        return self.cliente.table("solicitacoes_whatsapp").insert(registro).execute().data[0]["id"]

    def obter_solicitacao(self, solicitacao_id):
        dados = (
            self.cliente.table("solicitacoes_whatsapp")
            .select("id,status,erro")
            .eq("id", solicitacao_id)
            .execute()
            .data
        )
        return dados[0] if dados else None

    def concluir_solicitacao(self, solicitacao_id, materiais):
        enviados = [
            {"solicitacao_id": solicitacao_id, "tipo": tipo, "titulo": item["titulo"], "url": item["url"]}
            for tipo, chave in (("site", "sites"), ("video", "videos"))
            for item in materiais[chave]
        ]
        if enviados:
            self.cliente.table("materiais_enviados").insert(enviados).execute()
        self.cliente.table("solicitacoes_whatsapp").update(
            {"status": "enviado", "enviado_em": datetime.now(timezone.utc).isoformat()}
        ).eq("id", solicitacao_id).execute()

    def registrar_erro_solicitacao(self, solicitacao_id, erro):
        self.cliente.table("solicitacoes_whatsapp").update({"status": "erro", "erro": erro}).eq(
            "id", solicitacao_id
        ).execute()

    # Usuários e sessões

    def criar_usuario(self, nome, email, telefone, senha_hash, perfil, consentimento_whatsapp=False):
        registro = {
            "nome": nome,
            "email": email.lower() if email else None,
            "telefone": telefone,
            "senha_hash": senha_hash,
            "perfil": perfil,
            "consentimento_whatsapp": consentimento_whatsapp,
        }
        try:
            dados = self.cliente.table("usuarios").insert(registro).execute().data[0]
        except APIError as erro:
            raise _traduzir_duplicidade(erro) from erro
        return {k: v for k, v in dados.items() if k in CAMPOS_USUARIO.split(",")}

    def obter_usuario_por_email(self, email):
        dados = self.cliente.table("usuarios").select("*").eq("email", email.lower()).execute().data
        return dados[0] if dados else None

    def obter_usuario_por_telefone(self, telefone):
        dados = self.cliente.table("usuarios").select("*").eq("telefone", telefone).execute().data
        return dados[0] if dados else None

    def obter_usuario(self, usuario_id):
        dados = self.cliente.table("usuarios").select(CAMPOS_USUARIO).eq("id", usuario_id).execute().data
        return dados[0] if dados else None

    def listar_usuarios(self):
        return self.cliente.table("usuarios").select(CAMPOS_USUARIO).order("nome").execute().data

    def contar_administradores_ativos(self):
        resultado = (
            self.cliente.table("usuarios")
            .select("id", count="exact")
            .eq("perfil", "administrador")
            .eq("ativo", True)
            .execute()
        )
        return resultado.count

    def atualizar_usuario(self, usuario_id, campos):
        campos = {**campos, "atualizado_em": datetime.now(timezone.utc).isoformat()}
        if "email" in campos:
            campos["email"] = campos["email"].lower()
        try:
            dados = self.cliente.table("usuarios").update(campos).eq("id", usuario_id).execute().data
        except APIError as erro:
            raise _traduzir_duplicidade(erro) from erro
        return {k: v for k, v in dados[0].items() if k in CAMPOS_USUARIO.split(",")} if dados else None

    def excluir_usuario(self, usuario_id):
        return bool(self.cliente.table("usuarios").delete().eq("id", usuario_id).execute().data)

    def criar_sessao(self, token_hash, usuario_id, expira_em):
        self.cliente.table("sessoes").insert(
            {"token_hash": token_hash, "usuario_id": usuario_id, "expira_em": expira_em.isoformat()}
        ).execute()

    def obter_sessao(self, token_hash):
        dados = (
            self.cliente.table("sessoes")
            .select(f"expira_em,usuario:usuarios({CAMPOS_USUARIO})")
            .eq("token_hash", token_hash)
            .execute()
            .data
        )
        return dados[0] if dados else None

    def excluir_sessao(self, token_hash):
        self.cliente.table("sessoes").delete().eq("token_hash", token_hash).execute()

    def excluir_sessoes_do_usuario(self, usuario_id):
        self.cliente.table("sessoes").delete().eq("usuario_id", usuario_id).execute()

    # Base de conhecimento (CRUD principal)

    def listar_temas(self):
        return self.cliente.table("temas").select("id,nome,url").order("nome").execute().data

    def listar_trechos(self, tema_id=None, busca=None, pagina=1, por_pagina=20):
        consulta = self.cliente.table("trechos").select(CAMPOS_TRECHO, count="exact")
        if tema_id:
            consulta = consulta.eq("tema_id", tema_id)
        if busca:
            termo = _termo_seguro(busca)
            consulta = consulta.or_(f"secao.ilike.%{termo}%,texto.ilike.%{termo}%")
        inicio = (pagina - 1) * por_pagina
        resultado = consulta.order("tema_id").order("ordem").range(inicio, inicio + por_pagina - 1).execute()
        return [_achatar_trecho(t) for t in resultado.data], resultado.count or 0

    def obter_trecho(self, trecho_id):
        dados = self.cliente.table("trechos").select(CAMPOS_TRECHO).eq("id", trecho_id).execute().data
        return _achatar_trecho(dados[0]) if dados else None

    def criar_trecho(self, tema_id, secao, texto, usuario_id):
        # O novo trecho entra no fim do tema
        ultimo = (
            self.cliente.table("trechos")
            .select("ordem")
            .eq("tema_id", tema_id)
            .order("ordem", desc=True)
            .limit(1)
            .execute()
            .data
        )
        registro = {
            "tema_id": tema_id,
            "secao": secao,
            "texto": texto,
            "ordem": (ultimo[0]["ordem"] + 1) if ultimo else 1,
            "atualizado_por": usuario_id,
        }
        trecho_id = self.cliente.table("trechos").insert(registro).execute().data[0]["id"]
        return self.obter_trecho(trecho_id)

    def atualizar_trecho(self, trecho_id, tema_id, secao, texto, usuario_id):
        campos = {"tema_id": tema_id, "secao": secao, "texto": texto, "atualizado_por": usuario_id}
        dados = self.cliente.table("trechos").update(campos).eq("id", trecho_id).execute().data
        return self.obter_trecho(trecho_id) if dados else None

    def excluir_trecho(self, trecho_id):
        return bool(self.cliente.table("trechos").delete().eq("id", trecho_id).execute().data)

    def listar_perguntas(self, limite=50):
        return (
            self.cliente.table("perguntas")
            .select("id,texto,encontrou,criado_em")
            .order("criado_em", desc=True)
            .limit(limite)
            .execute()
            .data
        )

    # Acompanhamento de temas (perfil usuário)

    def listar_inscricoes(self, usuario_id):
        dados = (
            self.cliente.table("inscricoes_tema")
            .select("id,tema_id,telefone,criado_em,temas(nome)")
            .eq("usuario_id", usuario_id)
            .eq("ativa", True)
            .order("criado_em")
            .execute()
            .data
        )
        return [{**{k: v for k, v in i.items() if k != "temas"}, "tema": i["temas"]["nome"]} for i in dados]

    def criar_inscricao(self, usuario_id, tema_id, telefone):
        registro = {"usuario_id": usuario_id, "tema_id": tema_id, "telefone": telefone, "consentimento": True}
        try:
            inscricao_id = self.cliente.table("inscricoes_tema").insert(registro).execute().data[0]["id"]
        except APIError as erro:
            if erro.code == "23505":
                raise RegistroDuplicado("Você já acompanha este tema com este telefone.") from erro
            raise
        return next(i for i in self.listar_inscricoes(usuario_id) if i["id"] == inscricao_id)

    def excluir_inscricao(self, usuario_id, inscricao_id):
        resultado = (
            self.cliente.table("inscricoes_tema")
            .delete()
            .eq("id", inscricao_id)
            .eq("usuario_id", usuario_id)
            .execute()
        )
        return bool(resultado.data)

    # Atualizações de temas e envios aos inscritos (Módulo 2)

    def criar_atualizacao(self, tema_id, titulo, conteudo, url, autor_id):
        registro = {"tema_id": tema_id, "titulo": titulo, "conteudo": conteudo, "url": url, "autor_id": autor_id}
        atualizacao_id = self.cliente.table("atualizacoes").insert(registro).execute().data[0]["id"]
        return self.obter_atualizacao(atualizacao_id)

    def listar_atualizacoes(self, tema_id=None):
        consulta = self.cliente.table("atualizacoes").select(CAMPOS_ATUALIZACAO)
        if tema_id:
            consulta = consulta.eq("tema_id", tema_id)
        return [_achatar_atualizacao(a) for a in consulta.order("publicado_em", desc=True).limit(100).execute().data]

    def obter_atualizacao(self, atualizacao_id):
        dados = self.cliente.table("atualizacoes").select(CAMPOS_ATUALIZACAO).eq("id", atualizacao_id).execute().data
        return _achatar_atualizacao(dados[0]) if dados else None

    def excluir_atualizacao(self, atualizacao_id):
        return bool(self.cliente.table("atualizacoes").delete().eq("id", atualizacao_id).execute().data)

    def listar_inscricoes_ativas(self, tema_id):
        return (
            self.cliente.table("inscricoes_tema")
            .select("id,telefone")
            .eq("tema_id", tema_id)
            .eq("ativa", True)
            .execute()
            .data
        )

    def criar_envios(self, atualizacao_id, inscricoes_ids):
        if inscricoes_ids:
            self.cliente.table("envios_atualizacao").insert(
                [{"atualizacao_id": atualizacao_id, "inscricao_id": i} for i in inscricoes_ids]
            ).execute()

    def listar_envios(self, atualizacao_id, status=None):
        consulta = (
            self.cliente.table("envios_atualizacao")
            .select("inscricao_id,status,enviado_em,inscricoes_tema(telefone)")
            .eq("atualizacao_id", atualizacao_id)
        )
        if status:
            consulta = consulta.eq("status", status)
        return [
            {"inscricao_id": e["inscricao_id"], "status": e["status"], "telefone": e["inscricoes_tema"]["telefone"]}
            for e in consulta.execute().data
        ]

    def registrar_envio(self, atualizacao_id, inscricao_id, status):
        campos = {"status": status}
        if status == "enviado":
            campos["enviado_em"] = datetime.now(timezone.utc).isoformat()
        self.cliente.table("envios_atualizacao").update(campos).eq("atualizacao_id", atualizacao_id).eq(
            "inscricao_id", inscricao_id
        ).execute()

    def atualizacoes_do_usuario(self, usuario_id, limite=20):
        temas = [i["tema_id"] for i in self.listar_inscricoes(usuario_id)]
        if not temas:
            return []
        dados = (
            self.cliente.table("atualizacoes")
            .select(CAMPOS_ATUALIZACAO)
            .in_("tema_id", temas)
            .order("publicado_em", desc=True)
            .limit(limite)
            .execute()
            .data
        )
        return [_achatar_atualizacao(a) for a in dados]

    # Histórico de operações (Sprint 07)

    def registrar_operacao(self, usuario, acao, entidade, entidade_id, descricao):
        self.cliente.table("historico_operacoes").insert(
            {
                "usuario_id": usuario["id"] if usuario else None,
                "usuario_nome": usuario["nome"] if usuario else None,
                "acao": acao,
                "entidade": entidade,
                "entidade_id": str(entidade_id) if entidade_id is not None else None,
                "descricao": descricao,
            }
        ).execute()

    def listar_historico(self, inicio=None, fim=None, acao=None, entidade=None, busca=None, limite=500):
        consulta = self.cliente.table("historico_operacoes").select("*")
        if inicio:
            consulta = consulta.gte("criado_em", inicio)
        if fim:
            consulta = consulta.lt("criado_em", fim)
        if acao:
            consulta = consulta.eq("acao", acao)
        if entidade:
            consulta = consulta.eq("entidade", entidade)
        if busca:
            termo = _termo_seguro(busca)
            consulta = consulta.or_(f"descricao.ilike.%{termo}%,usuario_nome.ilike.%{termo}%")
        return consulta.order("criado_em", desc=True).limit(limite).execute().data

    # Dashboard e relatórios (Sprint 07)

    def perguntas_no_periodo(self, inicio=None, fim=None, encontrou=None, busca=None, tema_id=None, limite=1000):
        consulta = self.cliente.table("perguntas").select(
            "id,texto,encontrou,criado_em,pergunta_trechos(trechos(tema_id,temas(nome)))"
        )
        if inicio:
            consulta = consulta.gte("criado_em", inicio)
        if fim:
            consulta = consulta.lt("criado_em", fim)
        if encontrou is not None:
            consulta = consulta.eq("encontrou", encontrou)
        if busca:
            consulta = consulta.ilike("texto", f"%{_termo_seguro(busca)}%")
        dados = consulta.order("criado_em", desc=True).limit(limite).execute().data
        perguntas = []
        for p in dados:
            temas = {}
            for ligacao in p.pop("pergunta_trechos"):
                trecho = ligacao["trechos"]
                if trecho:
                    temas[trecho["tema_id"]] = trecho["temas"]["nome"]
            if tema_id and tema_id not in temas:
                continue
            perguntas.append({**p, "temas": sorted(temas.values())})
        return perguntas

    def solicitacoes_no_periodo(self, inicio=None, fim=None):
        consulta = self.cliente.table("solicitacoes_whatsapp").select("status,criado_em")
        if inicio:
            consulta = consulta.gte("criado_em", inicio)
        if fim:
            consulta = consulta.lt("criado_em", fim)
        return consulta.limit(5000).execute().data

    def resumo_inscricoes(self):
        return self.cliente.table("inscricoes_tema").select("tema_id,temas(nome)").eq("ativa", True).limit(5000).execute().data


CAMPOS_ATUALIZACAO = (
    "id,tema_id,titulo,conteudo,url,autor_id,publicado_em,temas(nome),usuarios(nome),envios_atualizacao(status)"
)
CAMPOS_USUARIO = "id,nome,email,telefone,perfil,ativo,criado_em"
CAMPOS_TRECHO = "id,tema_id,secao,ordem,texto,atualizado_em,temas(nome,url)"


class RegistroDuplicado(ValueError):
    pass


def _traduzir_duplicidade(erro):
    """Converte a violação de unicidade do banco em uma mensagem para o usuário."""
    if erro.code != "23505":
        return erro
    if "telefone" in (erro.message or ""):
        return RegistroDuplicado("Já existe uma conta com este telefone.")
    return RegistroDuplicado("Já existe um usuário com este e-mail.")


def _termo_seguro(texto):
    # Vírgulas e parênteses têm significado nos filtros do Supabase
    return texto.replace(",", " ").replace("(", " ").replace(")", " ").replace("%", " ").strip()


def _achatar_atualizacao(atualizacao):
    envios = atualizacao.pop("envios_atualizacao") or []
    contagem = {status: sum(1 for e in envios if e["status"] == status) for status in ("pendente", "enviado", "erro")}
    return {
        **{k: v for k, v in atualizacao.items() if k not in ("temas", "usuarios")},
        "tema": atualizacao["temas"]["nome"],
        "autor": (atualizacao.get("usuarios") or {}).get("nome"),
        "envios": contagem,
    }


def _achatar_trecho(trecho):
    tema = trecho.pop("temas")
    return {**trecho, "tema": tema["nome"], "url": tema["url"]}

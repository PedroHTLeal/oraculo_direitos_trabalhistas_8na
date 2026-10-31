from datetime import datetime, timezone

from supabase import create_client


class RepositorioSupabase:
    """Acesso às tabelas do Supabase usadas pelo Oráculo."""

    def __init__(self, url, chave_servico):
        self.cliente = create_client(url, chave_servico)

    def buscar_trechos(self, consulta, limite=6):
        resultado = self.cliente.rpc("buscar_trechos", {"consulta": consulta, "limite": limite}).execute()
        return resultado.data

    def salvar_pergunta(self, texto, resposta, encontrou, trechos_ids):
        registro = {
            "texto": texto,
            "resposta": resposta,
            "encontrou": encontrou,
            "trechos_ids": trechos_ids,
        }
        return self.cliente.table("perguntas").insert(registro).execute().data[0]["id"]

    def obter_pergunta(self, pergunta_id):
        dados = self.cliente.table("perguntas").select("*").eq("id", pergunta_id).execute().data
        return dados[0] if dados else None

    def obter_trechos(self, ids):
        if not ids:
            return []
        return self.cliente.table("trechos").select("id,tema,secao,url").in_("id", ids).execute().data

    def criar_solicitacao(self, pergunta_id, telefone):
        registro = {"pergunta_id": pergunta_id, "telefone": telefone, "consentimento": True}
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
        self.cliente.table("solicitacoes_whatsapp").update(
            {
                "status": "enviado",
                "materiais": materiais,
                "enviado_em": datetime.now(timezone.utc).isoformat(),
            }
        ).eq("id", solicitacao_id).execute()

    def registrar_erro_solicitacao(self, solicitacao_id, erro):
        self.cliente.table("solicitacoes_whatsapp").update({"status": "erro", "erro": erro}).eq(
            "id", solicitacao_id
        ).execute()

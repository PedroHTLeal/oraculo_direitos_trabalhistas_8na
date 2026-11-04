"""Sinônimos da busca e sites e vídeos do "Saber mais" (parte do UC07).

A equipe mantém pelo painel as palavras do dia a dia que a busca traduz para os
termos da cartilha e os links enviados por e-mail em cada assunto.
Acesso: administradores e curadores.
"""

from fastapi import APIRouter, Depends, HTTPException, Response

from app.dependencias import equipe_de_conteudo, obter_repositorio
from app.esquemas import DadosMaterial, DadosSinonimo, Material, Sinonimo
from app.historico import registrar
from app.materiais import normalizar
from app.repositorio import RegistroDuplicado
from app.rotas.base_conhecimento import validar_tema

rotas = APIRouter(prefix="/api", tags=["Conteúdo complementar"])


def limpar_palavras(texto):
    # A busca compara sem acentos e em minúsculas
    return " ".join(normalizar(texto).split())


# Sinônimos da busca


@rotas.get("/sinonimos", response_model=list[Sinonimo])
def listar_sinonimos(_=Depends(equipe_de_conteudo), repositorio=Depends(obter_repositorio)):
    return repositorio.listar_sinonimos()


@rotas.post("/sinonimos", response_model=Sinonimo, status_code=201)
def criar_sinonimo(dados: DadosSinonimo, usuario=Depends(equipe_de_conteudo), repositorio=Depends(obter_repositorio)):
    termo, equivalentes = limpar_palavras(dados.termo), limpar_palavras(dados.equivalentes)
    try:
        sinonimo = repositorio.criar_sinonimo(termo, equivalentes)
    except RegistroDuplicado:
        raise HTTPException(status_code=409, detail=f'A palavra "{termo}" já está cadastrada.')
    registrar(repositorio, usuario, "criar", "sinonimo", termo, f'Incluiu o sinônimo "{termo}" → "{equivalentes}"')
    return sinonimo


@rotas.put("/sinonimos/{termo}", response_model=Sinonimo)
def alterar_sinonimo(
    termo: str, dados: DadosSinonimo, usuario=Depends(equipe_de_conteudo), repositorio=Depends(obter_repositorio)
):
    novo_termo, equivalentes = limpar_palavras(dados.termo), limpar_palavras(dados.equivalentes)
    try:
        sinonimo = repositorio.atualizar_sinonimo(termo, novo_termo, equivalentes)
    except RegistroDuplicado:
        raise HTTPException(status_code=409, detail=f'A palavra "{novo_termo}" já está cadastrada.')
    if not sinonimo:
        raise HTTPException(status_code=404, detail="Sinônimo não encontrado.")
    registrar(repositorio, usuario, "alterar", "sinonimo", novo_termo, f'Alterou o sinônimo "{novo_termo}" → "{equivalentes}"')
    return sinonimo


@rotas.delete("/sinonimos/{termo}", status_code=204)
def excluir_sinonimo(termo: str, usuario=Depends(equipe_de_conteudo), repositorio=Depends(obter_repositorio)):
    if not repositorio.excluir_sinonimo(termo):
        raise HTTPException(status_code=404, detail="Sinônimo não encontrado.")
    registrar(repositorio, usuario, "excluir", "sinonimo", termo, f'Excluiu o sinônimo "{termo}"')
    return Response(status_code=204)


# Sites e vídeos do "Saber mais"


def preparar_material(dados, repositorio):
    validar_tema(repositorio, dados.tema_id)
    palavras = list(dict.fromkeys(limpar_palavras(p) for p in dados.palavras_chave if p.strip()))
    if not palavras:
        raise HTTPException(status_code=422, detail="Informe pelo menos uma palavra-chave.")
    if dados.tipo == "video" and not any(d in dados.url for d in ("youtube.com/watch", "youtu.be/")):
        raise HTTPException(status_code=422, detail="Para vídeos, use o link de um vídeo do YouTube.")
    return {**dados.model_dump(), "palavras_chave": palavras}


@rotas.get("/materiais", response_model=list[Material])
def listar_materiais(_=Depends(equipe_de_conteudo), repositorio=Depends(obter_repositorio)):
    return repositorio.listar_materiais()


@rotas.post("/materiais", response_model=Material, status_code=201)
def criar_material(dados: DadosMaterial, usuario=Depends(equipe_de_conteudo), repositorio=Depends(obter_repositorio)):
    try:
        material = repositorio.criar_material(preparar_material(dados, repositorio))
    except RegistroDuplicado:
        raise HTTPException(status_code=409, detail="Este link já está cadastrado neste assunto.")
    registrar(repositorio, usuario, "criar", "material", material["id"], f'Incluiu "{dados.titulo}" em {dados.assunto}')
    return material


@rotas.put("/materiais/{material_id}", response_model=Material)
def alterar_material(
    material_id: int, dados: DadosMaterial, usuario=Depends(equipe_de_conteudo), repositorio=Depends(obter_repositorio)
):
    try:
        material = repositorio.atualizar_material(material_id, preparar_material(dados, repositorio))
    except RegistroDuplicado:
        raise HTTPException(status_code=409, detail="Este link já está cadastrado neste assunto.")
    if not material:
        raise HTTPException(status_code=404, detail="Material não encontrado.")
    registrar(repositorio, usuario, "alterar", "material", material_id, f'Alterou "{dados.titulo}" em {dados.assunto}')
    return material


@rotas.delete("/materiais/{material_id}", status_code=204)
def excluir_material(material_id: int, usuario=Depends(equipe_de_conteudo), repositorio=Depends(obter_repositorio)):
    material = repositorio.obter_material(material_id)
    if not material or not repositorio.excluir_material(material_id):
        raise HTTPException(status_code=404, detail="Material não encontrado.")
    registrar(repositorio, usuario, "excluir", "material", material_id, f'Excluiu "{material["titulo"]}" de {material["assunto"]}')
    return Response(status_code=204)

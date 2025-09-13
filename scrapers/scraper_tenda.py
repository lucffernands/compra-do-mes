import requests
import json
import time

# URL base da API de produtos
API_URL = "https://api.tendaatacado.com.br/api/public/store/search"

# Quantidade máxima de produtos por termo
MAX_PRODUTOS = 3

# Função para buscar produtos pelo nome
def buscar_produtos(produto, pagina=1):
    """
    Busca produtos pelo nome na API da Tenda.
    Retorna a lista de produtos da página.
    """
    headers = {
        "accept": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "origin": "https://www.tendaatacado.com.br",
        "referer": "https://www.tendaatacado.com.br/",
        "authorization": "Bearer 6ec3a499047c4600f987c4f928ac7524"  # token que você pegou no XHR
    }

    params = {
        "query": produto,
        "page": pagina,
        "order": "relevance",
        "save": "true",
        "cartId": 28224513  # ou outro que você usa
    }

    response = requests.get(API_URL, headers=headers, params=params)
    if response.status_code != 200:
        print(f"❌ Erro ao buscar {produto} (página {pagina}): {response.status_code}")
        return []
    data = response.json()
    return data.get("products", [])

# Função principal para percorrer os produtos do arquivo
def buscar_todos_produtos(arquivo_produtos="products.txt"):
    resultados = []
    with open(arquivo_produtos, "r", encoding="utf-8") as f:
        produtos_lista = [linha.strip() for linha in f if linha.strip()]

    for nome_produto in produtos_lista:
        print(f"🔍 Buscando: {nome_produto}")
        produtos_api = buscar_produtos(nome_produto, pagina=1)
        for p in produtos_api[:MAX_PRODUTOS]:
            item = {
                "supermercado": "Tenda",
                "produto": p.get("name"),
                "preco": p.get("price"),
                "preco_por_kg": p.get("price")  # aqui considera que é preço unitário/kg
            }
            resultados.append(item)
        time.sleep(0.5)
    return resultados

# Salvar em JSON
def salvar_json(produtos, arquivo="prices_tenda.json"):
    if not produtos:
        print("Nenhum produto para salvar.")
        return
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(produtos, f, ensure_ascii=False, indent=2)
    print(f"💾 {len(produtos)} produtos salvos em {arquivo}")

# Execução principal
if __name__ == "__main__":
    produtos_encontrados = buscar_todos_produtos()
    salvar_json(produtos_encontrados)

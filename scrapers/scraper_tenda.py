import requests
import json
import time

# URL base da API de produtos
API_URL = "https://api.tendaatacado.com.br/api/public/store/search"

# Função para buscar produtos pelo nome
def buscar_produtos(produto, pagina=1):
    """
    Busca produtos pelo nome na API da Tenda.
    Retorna um dict com informações de produtos e paginação.
    """
    headers = {
        "accept": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "origin": "https://www.tendaatacado.com.br",
        "referer": "https://www.tendaatacado.com.br/"
    }

    params = {
        "query": produto,
        "page": pagina,
        "order": "relevance",
        "save": "true",
        "cartId": "28224513"   # pode mudar, mas funciona fixo também
    }

    response = requests.get(API_URL, headers=headers, params=params)
    if response.status_code != 200:
        print(f"Erro ao buscar produtos: {response.status_code}")
        return None
    return response.json()

# Função para percorrer todas as páginas de resultados
def buscar_todos_produtos(produto):
    todos_produtos = []
    pagina = 1
    while True:
        data = buscar_produtos(produto, pagina)
        if not data or "products" not in data:
            break

        produtos = data["products"]
        if not produtos:
            break

        for p in produtos:
            item = {
                "id": p.get("id"),
                "sku": p.get("sku"),
                "barcode": p.get("barcode"),
                "nome": p.get("name"),
                "url": p.get("url"),
                "preco": p.get("price"),
                "moeda": p.get("currency"),
                "marca": p.get("brand"),
                "estoque_total": p.get("totalStock"),
                "disponibilidade": p.get("availability"),
                "estoque_filiais": [
                    {"filial": i["branchId"], "qtd": i["totalAvailable"]}
                    for i in p.get("inventory", [])
                ]
            }
            todos_produtos.append(item)

        # Paginação
        if pagina >= data.get("total_pages", 0):
            break
        pagina += 1
        time.sleep(0.5)  # evita sobrecarregar o servidor

    return todos_produtos

# Função para salvar em JSON
def salvar_json(produtos, arquivo="prices_tenda.json"):
    if not produtos:
        print("Nenhum produto para salvar.")
        return

    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(produtos, f, ensure_ascii=False, indent=4)
    print(f"{len(produtos)} produtos salvos em {arquivo}")

# Execução principal
if __name__ == "__main__":
    nome_produto = input("Digite o nome do produto: ")
    produtos = buscar_todos_produtos(nome_produto)
    salvar_json(produtos)

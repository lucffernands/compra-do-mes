import requests
import json
import time
import re

# URL da API da Tenda
API_URL = "https://api.tendaatacado.com.br/api/public/store/search"

# Lê os produtos do arquivo products.txt
def ler_produtos(arquivo="products.txt"):
    with open(arquivo, "r", encoding="utf-8") as f:
        return [linha.strip() for linha in f if linha.strip()]

# Função para buscar produtos pelo nome
def buscar_produtos(produto, pagina=1):
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": "Bearer 6ec3a499047c4600f987c4f928ac7524",  # se necessário, atualizar
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
        "cartId": "28224513"
    }

    response = requests.get(API_URL, headers=headers, params=params)
    if response.status_code == 404:
        print(f"Erro ao buscar {produto} (página {pagina}): 404")
        return None
    elif response.status_code != 200:
        print(f"Erro ao buscar {produto} (página {pagina}): {response.status_code}")
        return None

    return response.json()

# Função para calcular preço por kg, se houver peso na descrição
def calcular_preco_por_kg(produto):
    nome = produto.get("name", "")
    preco = produto.get("price", 0)
    # Procura algo como "500g", "1kg", "250ml"
    match = re.search(r"(\d+(?:[\.,]\d+)?)\s*(kg|g|l|ml)", nome, re.IGNORECASE)
    if match:
        valor, unidade = match.groups()
        valor = float(valor.replace(",", "."))
        if unidade.lower() == "g":
            return round(preco / (valor / 1000), 2)
        elif unidade.lower() == "kg":
            return preco
        elif unidade.lower() == "ml":
            return preco  # pode adaptar se quiser preço por litro
        elif unidade.lower() == "l":
            return preco
    return preco

# Função para buscar todos os produtos
def buscar_todos_produtos(produtos_lista):
    todos_produtos = []

    for produto_nome in produtos_lista:
        print(f"🔍 Buscando: {produto_nome}")
        pagina = 1
        while True:
            data = buscar_produtos(produto_nome, pagina)
            if not data or "products" not in data:
                break

            produtos = data["products"]
            if not produtos:
                break

            for p in produtos:
                item = {
                    "supermercado": "Tenda",
                    "produto": p.get("name"),
                    "preco": p.get("price"),
                    "preco_por_kg": calcular_preco_por_kg(p)
                }
                todos_produtos.append(item)

            if pagina >= data.get("total_pages", 0):
                break
            pagina += 1
            time.sleep(0.5)  # evita sobrecarga do servidor

    return todos_produtos

# Função para salvar JSON
def salvar_json(produtos, arquivo="prices_tenda.json"):
    if not produtos:
        print("Nenhum produto para salvar.")
        return
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(produtos, f, ensure_ascii=False, indent=4)
    print(f"{len(produtos)} produtos salvos em {arquivo}")

# Execução principal
if __name__ == "__main__":
    produtos_lista = ler_produtos()
    todos_produtos = buscar_todos_produtos(produtos_lista)
    salvar_json(todos_produtos)

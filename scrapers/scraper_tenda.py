import requests
import json
import time

API_URL = "https://api.tendaatacado.com.br/api/public/store/search"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    "origin": "https://www.tendaatacado.com.br",
    "referer": "https://www.tendaatacado.com.br/"
}

def buscar_produtos(produto, limite=3):
    """
    Busca até 'limite' produtos pelo termo na API do Tenda.
    """
    params = {
        "query": produto,
        "page": 1,
        "order": "relevance",
        "save": "true"
    }

    resp = requests.get(API_URL, headers=HEADERS, params=params)
    if resp.status_code != 200:
        print(f"❌ Erro ao buscar {produto} ({resp.status_code})")
        return []

    data = resp.json()
    produtos = data.get("products", [])[:limite]

    resultado = []
    for p in produtos:
        preco = p.get("price")
        nome = p.get("name")

        # calcula preco por kg se nome tiver peso
        preco_por_kg = preco
        nome_lower = nome.lower()
        if "kg" in nome_lower:
            preco_por_kg = preco
        elif "500g" in nome_lower or "500 g" in nome_lower:
            preco_por_kg = preco * 2
        elif "250g" in nome_lower or "250 g" in nome_lower:
            preco_por_kg = preco * 4
        elif "1,5kg" in nome_lower or "1.5kg" in nome_lower:
            preco_por_kg = preco / 1.5

        resultado.append({
            "supermercado": "Tenda",
            "produto": nome,
            "preco": preco,
            "preco_por_kg": round(preco_por_kg, 2) if preco_por_kg else None
        })

    return resultado


def carregar_lista_termos(arquivo="products.txt"):
    with open(arquivo, "r", encoding="utf-8") as f:
        return [linha.strip() for linha in f if linha.strip()]


def salvar_json(produtos, arquivo="prices_tenda.json"):
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(produtos, f, indent=2, ensure_ascii=False)
    print(f"💾 {len(produtos)} produtos salvos em {arquivo}")


if __name__ == "__main__":
    termos = carregar_lista_termos()
    todos = []

    for termo in termos:
        print(f"🔍 Buscando: {termo}")
        encontrados = buscar_produtos(termo, limite=3)
        todos.extend(encontrados)
        time.sleep(0.5)  # respeita o servidor

    salvar_json(todos)

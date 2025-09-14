import requests
import json
import re

TENDA_URL = "https://api.tendaatacado.com.br/api/public/retail/product"
INPUT_FILE = "products.txt"
OUTPUT_JSON = "docs/prices_tenda.json"
NUM_PRODUTOS = 3

headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

def extrair_peso(nome):
    """Tenta extrair peso em gramas do nome do produto e converter para kg"""
    match = re.search(r"(\d+)\s*g", nome.lower())
    if match:
        return int(match.group(1)) / 1000
    match = re.search(r"(\d+)\s*kg", nome.lower())
    if match:
        return int(match.group(1))
    return 1  # se não achar, assume 1kg

def buscar_tenda(produto):
    try:
        payload = {
            "page": 1,
            "pageSize": NUM_PRODUTOS,
            "order": "relevance",
            "query": produto
        }

        resp = requests.post(TENDA_URL, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()

        encontrados = []
        for item in data.get("products", [])[:NUM_PRODUTOS]:
            nome = item.get("name")
            preco = item.get("price")

            if not nome or preco is None:
                continue

            peso_kg = extrair_peso(nome)
            encontrados.append({
                "supermercado": "Tenda",
                "produto": nome,
                "preco": preco,
                "preco_por_kg": round(preco / peso_kg, 2)
            })

        return min(encontrados, key=lambda x: x["preco_por_kg"]) if encontrados else None

    except Exception as e:
        print(f"Erro Tenda ({produto}): {e}")
        return None

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        produtos = [linha.strip() for linha in f if linha.strip()]

    resultados = []
    faltando = []

    for produto in produtos:
        print(f"🔍 Buscando Tenda: {produto}")
        item = buscar_tenda(produto)
        if item:
            resultados.append(item)
        else:
            faltando.append(produto)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    print("\nProdutos encontrados Tenda:")
    for item in resultados:
        print(f"- {item['produto']}: R$ {item['preco']} | R$ {item['preco_por_kg']}/kg")

    total = sum(item["preco"] for item in resultados)
    print(f"\nTotal: R$ {total:.2f}")

    if faltando:
        print(f"\nProdutos não encontrados ({len(faltando)}): {', '.join(faltando)}")

if __name__ == "__main__":
    main()

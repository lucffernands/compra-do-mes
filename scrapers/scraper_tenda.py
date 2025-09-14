import requests
import json

OUTPUT_JSON = "docs/prices_tenda.json"
NUM_PRODUTOS = 3

def buscar_tenda(produto):
    url = "https://api.tendaatacado.com.br/api/public/retail/product"
    payload = {
        "filter": {
            "text": produto
        },
        "page": {
            "limit": NUM_PRODUTOS,
            "offset": 0
        },
        "sort": {
            "field": "relevance",
            "order": "desc"
        }
    }

    try:
        resp = requests.post(url, json=payload, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        encontrados = []
        for p in data.get("products", []):
            nome = p.get("name")
            preco = p.get("price")
            if not nome or not preco:
                continue

            encontrados.append({
                "supermercado": "Tenda",
                "produto": nome,
                "preco": preco,
                "preco_por_kg": preco  # por enquanto mantemos igual
            })

        return encontrados

    except Exception as e:
        print(f"Erro Tenda ({produto}): {e}")
        return []

def main():
    produto = "BACON"
    print(f"🔍 Buscando Tenda: {produto}")

    resultados = buscar_tenda(produto)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

    print("\nProdutos encontrados Tenda:")
    for item in resultados:
        print(f"- {item['produto']}: R$ {item['preco']} | R$ {item['preco_por_kg']}/kg")

    total = sum(item["preco"] for item in resultados)
    print(f"\nTotal: R$ {total:.2f}")

if __name__ == "__main__":
    main()

import requests
import json
import re

TENDA_URL = "https://www.tendaatacado.com.br/api/catalog_system/pub/products/search?ft="
INPUT_FILE = "products.txt"
OUTPUT_JSON = "docs/prices_tenda.json"
NUM_PRODUTOS = 3

def extrair_peso(nome):
    match = re.search(r"(\d+)\s*g", nome.lower())
    if match:
        return int(match.group(1)) / 1000
    match = re.search(r"(\d+(?:[.,]\d+)?)\s*kg", nome.lower())
    if match:
        return float(match.group(1).replace(",", "."))
    return 1  # default se não achar peso

def buscar_tenda(produto):
    try:
        resp = requests.get(f"{TENDA_URL}{produto}", timeout=15)
        resp.raise_for_status()
        data = resp.json()

        encontrados = []
        for item in data[:NUM_PRODUTOS]:
            nome = item.get("productName", "").strip()
            if not nome or produto.lower() not in nome.lower():
                continue

            try:
                preco = float(item["items"][0]["sellers"][0]["commertialOffer"]["Price"])
            except:
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

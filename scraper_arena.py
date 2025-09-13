import requests
import json
import re

# Configurações
ARENA_API_URL = "https://www.arenaatacado.com.br/on/demandware.store/Sites-Arena-Site/pt_BR/Search-Show"
INPUT_FILE = "products.txt"
OUTPUT_JSON = "docs/prices_arena.json"
NUM_PRODUTOS = 3

def extrair_peso(nome_produto):
    match = re.search(r"(\d+[,.]?\d*)\s*(kg|g)", nome_produto.lower())
    if match:
        valor = float(match.group(1).replace(",", "."))
        if match.group(2) == "g":
            return valor / 1000
        return valor
    return 1

def buscar_arena_api(produto):
    try:
        params = {
            "q": produto,
            "start": 0,
            "count": NUM_PRODUTOS
        }
        headers = {
            "Accept": "application/json"
        }

        response = requests.get(ARENA_API_URL, params=params, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        encontrados = []
        for item in data.get("hits", []):
            nome = item.get("productName") or item.get("name")
            if not nome or produto.lower() not in nome.lower():
                continue

            preco_str = str(item.get("price", "0")).replace(",", ".")
            try:
                preco = float(preco_str)
            except ValueError:
                continue

            peso_kg = extrair_peso(nome)
            preco_kg = round(preco / peso_kg, 2)

            encontrados.append({
                "supermercado": "Arena Atacado",
                "produto": nome,
                "preco": preco,
                "preco_por_kg": preco_kg
            })

        if encontrados:
            return min(encontrados, key=lambda x: x["preco_por_kg"])
    except Exception as e:
        print(f"Erro Arena ({produto}): {e}")
    return None

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        produtos_lista = [linha.strip() for linha in f if linha.strip()]

    resultados_finais = []

    for produto in produtos_lista:
        item_arena = buscar_arena_api(produto)
        if item_arena:
            resultados_finais.append(item_arena)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(resultados_finais, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()

import requests
import re
import json
import time

BASE_URL = "https://www.tendaatacado.com.br/"
API_URL = "https://api.tendaatacado.com.br/api/public/store/search"

INPUT_FILE = "products.txt"
OUTPUT_JSON = "docs/prices_tenda.json"

NUM_PRODUTOS = 3
CART_ID = "28224513"  # pode ser fixo

# --- Extrair token do HTML ---
def get_token():
    resp = requests.get(BASE_URL, timeout=15)
    html = resp.text
    match = re.search(r'"token"\s*:\s*"([^"]+)"', html)
    if match:
        return match.group(1)
    else:
        raise Exception("Token não encontrado")

# --- Extrair peso do nome ---
def extrair_peso(nome):
    match = re.search(r"(\d+(?:\.\d+)?)\s*(kg|g)", nome.lower())
    if match:
        valor, unidade = float(match.group(1)), match.group(2)
        return valor if unidade == "kg" else valor / 1000
    return 1

# --- Buscar produto, tenta renovar token se necessário ---
def buscar_produto(produto, token):
    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "desktop-platform": "true",
        "origin": "https://www.tendaatacado.com.br",
        "referer": "https://www.tendaatacado.com.br/",
        "user-agent": "Mozilla/5.0"
    }
    params = {
        "query": produto,
        "page": 1,
        "order": "relevance",
        "save": "true",
        "cartId": CART_ID
    }

    try:
        resp = requests.get(API_URL, headers=headers, params=params, timeout=15)
        # Se token expirou ou inválido, renova e tenta de novo
        if resp.status_code == 401:
            print("Token expirado, renovando...")
            token = get_token()
            headers["authorization"] = f"Bearer {token}"
            resp = requests.get(API_URL, headers=headers, params=params, timeout=15)

        if resp.status_code != 200:
            print(f"Erro Tenda ({produto}): {resp.status_code}")
            return None

        data = resp.json()
        encontrados = []

        for p in data.get("products", [])[:NUM_PRODUTOS]:
            nome = p.get("name")
            preco = p.get("price")
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

# --- Main ---
def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        produtos = [linha.strip() for linha in f if linha.strip()]

    resultados = []
    faltando = []

    try:
        token = get_token()
    except Exception as e:
        print(e)
        return

    for produto in produtos:
        item = buscar_produto(produto, token)
        if item:
            resultados.append(item)
        else:
            faltando.append(produto)
        # Evita bloqueio de IP com delay
        time.sleep(0.5)

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

import requests
from bs4 import BeautifulSoup
import json
import re
import os

TENDA_URL = "https://www.tendaatacado.com.br/busca?q="
INPUT_FILE = "products.txt"
OUTPUT_JSON = "docs/prices_tenda.json"
NUM_PRODUTOS = 3

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/129.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.tendaatacado.com.br/"
}

def extrair_peso(nome):
    match = re.search(r"(\d+)\s*g", nome.lower())
    return int(match.group(1)) / 1000 if match else 1

def buscar_tenda(produto):
    try:
        url = f"{TENDA_URL}{produto}"
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        # 🔹 DEBUG: salva o HTML retornado
        safe_name = re.sub(r'[^a-zA-Z0-9]', '_', produto)
        debug_file = f"debug_{safe_name}.html"
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(response.text)
        print(f"[DEBUG] HTML salvo em {debug_file}")

        soup = BeautifulSoup(response.text, "html.parser")
        encontrados = []

        for card in soup.find_all("a", class_="showcase-card-content")[:NUM_PRODUTOS]:
            nome_tag = card.find("h3", class_="TitleCardComponent")
            preco_tag = card.find("div", class_="SimplePriceComponent")

            if not nome_tag or not preco_tag:
                continue

            nome = nome_tag.get_text(strip=True)
            if produto.lower() not in nome.lower():
                continue

            try:
                preco = float(preco_tag.get_text(strip=True)
                              .replace("R$", "")
                              .replace("un", "")
                              .replace(",", ".")
                              .strip())
            except ValueError:
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

    os.makedirs(os.path.dirname(OUTPUT_JSON), exist_ok=True)
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

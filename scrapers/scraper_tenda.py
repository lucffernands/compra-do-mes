import requests
from bs4 import BeautifulSoup
import json
import re
import os

# --- Configurações ---
TENDA_URL = "https://www.tendaatacado.com.br/busca?q="
INPUT_FILE = "products.txt"
OUTPUT_JSON = "docs/prices_tenda.json"
NUM_PRODUTOS = 3
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/129.0.0.0 Safari/537.36"
}

def extrair_peso(nome, peso_texto):
    """
    Extrai peso em KG a partir do nome ou do texto do peso médio.
    """
    match_nome = re.search(r"(\d+)\s*g", nome.lower())
    match_peso = re.search(r"([\d,.]+)\s*kg", peso_texto.lower()) if peso_texto else None

    if match_peso:
        return float(match_peso.group(1).replace(",", "."))
    if match_nome:
        return int(match_nome.group(1)) / 1000
    return 1

def buscar_tenda(produto):
    try:
        resp = requests.get(f"{TENDA_URL}{produto}", headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        encontrados = []

        cards = soup.find_all("a", class_="showcase-card-content")[:NUM_PRODUTOS]
        for card in cards:
            nome_tag = card.find("h3", class_="TitleCardComponent")
            preco_tag = card.find("div", class_="SimplePriceComponent")
            peso_tag = card.find("div", class_="WeightInfoComponent")

            if not nome_tag or not preco_tag:
                continue

            nome = nome_tag.get_text(strip=True)
            preco_texto = preco_tag.get_text(strip=True)
            peso_texto = peso_tag.get_text(" ", strip=True) if peso_tag else ""

            try:
                preco = float(re.sub(r"[^\d,]", "", preco_texto).replace(",", "."))
            except:
                continue

            peso_kg = extrair_peso(nome, peso_texto)
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

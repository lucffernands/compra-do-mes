import requests
from bs4 import BeautifulSoup
import json
import re

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

def extrair_peso(nome, info_peso):
    # Tenta pelo campo "Peso médio"
    if info_peso:
        match = re.search(r"(\d+[,.]?\d*)\s*kg", info_peso.lower())
        if match:
            return float(match.group(1).replace(",", "."))
        match_g = re.search(r"(\d+)\s*g", info_peso.lower())
        if match_g:
            return int(match_g.group(1)) / 1000
    # Pelo nome do produto
    match_nome = re.search(r"(\d+)\s*g", nome.lower())
    if match_nome:
        return int(match_nome.group(1)) / 1000
    return 1.0

def buscar_tenda(produto):
    try:
        url = f"{TENDA_URL}{produto}"
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        encontrados = []

        for card in soup.find_all("a", class_="showcase-card-content")[:NUM_PRODUTOS]:
            nome_tag = card.find("h3", class_="TitleCardComponent")
            preco_tag = card.find("div", class_="SimplePriceComponent")
            peso_tag = card.find("div", class_="WeightInfoComponent")

            if not nome_tag or not preco_tag:
                continue

            nome = nome_tag.get_text(strip=True)
            if produto.lower() not in nome.lower():
                continue

            preco_str = preco_tag.get_text(strip=True).replace("R$", "").replace("un", "").replace(",", ".").strip()
            try:
                preco = float(preco_str)
            except:
                continue

            info_peso = peso_tag.get_text(strip=True) if peso_tag else None
            peso_kg = extrair_peso(nome, info_peso)
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

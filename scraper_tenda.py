import requests
from bs4 import BeautifulSoup
import json
import re

TENDA_URL = "https://www.tendaatacado.com.br/busca?q="
INPUT_FILE = "products.txt"
OUTPUT_JSON = "docs/prices_tenda.json"  # arquivo separado
NUM_PRODUTOS = 3

def extrair_peso(nome_produto, info_peso):
    if info_peso:
        match = re.search(r"(\d+[,.]?\d*)\s*kg", info_peso.lower())
        if match:
            return float(match.group(1).replace(",", "."))
        match_g = re.search(r"(\d+)\s*g", info_peso.lower())
        if match_g:
            return int(match_g.group(1)) / 1000

    match_nome = re.search(r"(\d+)\s*g", nome_produto.lower())
    if match_nome:
        return int(match_nome.group(1)) / 1000

    return 1.0

def buscar_tenda(produto):
    try:
        url = f"{TENDA_URL}{produto}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        cards = soup.find_all("a", class_="showcase-card-content")[:NUM_PRODUTOS]

        encontrados = []

        for card in cards:
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
            except ValueError:
                continue

            info_peso = peso_tag.get_text(strip=True) if peso_tag else None
            peso_kg = extrair_peso(nome, info_peso)
            preco_kg = round(preco / peso_kg, 2)

            encontrados.append({
                "supermercado": "Tenda",
                "produto": nome,
                "preco": preco,
                "preco_por_kg": preco_kg
            })

        if encontrados:
            return min(encontrados, key=lambda x: x["preco_por_kg"])

    except Exception as e:
        print(f"Erro Tenda ({produto}): {e}")

    return None

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        produtos_lista = [linha.strip() for linha in f if linha.strip()]

    resultados_finais = []
    faltando = []

    for produto in produtos_lista:
        item = buscar_tenda(produto)
        if item:
            resultados_finais.append(item)
        else:
            faltando.append(produto)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(resultados_finais, f, ensure_ascii=False, indent=2)

    print("\nProdutos encontrados Tenda:")
    for item in resultados_finais:
        print(f"- {item['produto']}: R$ {item['preco']} | R$ {item['preco_por_kg']}/kg")

    total = sum(item["preco"] for item in resultados_finais)
    print(f"\nTotal: R$ {total:.2f}")

    if faltando:
        print(f"\nProdutos não encontrados ({len(faltando)}): {', '.join(faltando)}")

if __name__ == "__main__":
    main()

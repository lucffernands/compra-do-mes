import requests
from bs4 import BeautifulSoup
import json
import re

# Configurações
BASE_URL = "https://www.goodbom.com.br/hortolandia/busca?q="
INPUT_FILE = "products.txt"
OUTPUT_JSON = "docs/prices.json"
SUPERMERCADO = "Goodbom"
NUM_PRODUTOS = 3


def extrair_peso(nome_produto):
    match = re.search(r"(\d+)\s*g", nome_produto.lower())
    if match:
        return int(match.group(1)) / 1000
    return 1  # assume 1kg se não achar peso


def buscar_produto(produto):
    url = f"{BASE_URL}{produto}"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    resultados = soup.find_all("span", class_="product-name")[:NUM_PRODUTOS]
    encontrados = []

    for nome_span in resultados:
        a_tag = nome_span.find_parent("a")
        preco_span = a_tag.find("span", class_="price")
        if not preco_span:
            continue

        nome = nome_span.get_text(strip=True)
        preco_str = preco_span.get_text(strip=True)
        preco_str = preco_str.replace("R$", "").split("/")[0].replace(",", ".").strip()

        try:
            preco = float(preco_str)
        except ValueError:
            continue

        peso_kg = extrair_peso(nome)
        preco_kg = round(preco / peso_kg, 2)

        encontrados.append({
            "supermercado": SUPERMERCADO,
            "produto": nome,
            "preco": preco,
            "preco_por_kg": preco_kg
        })

    if encontrados:
        return min(encontrados, key=lambda x: x["preco_por_kg"])
    return None


def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        produtos_lista = [linha.strip() for linha in f if linha.strip()]

    resultados_finais = []

    for produto in produtos_lista:
        item = buscar_produto(produto)
        if item:
            resultados_finais.append(item)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(resultados_finais, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()

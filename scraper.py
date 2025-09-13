import requests
from bs4 import BeautifulSoup
import json
import re

# Configurações
GOODBOM_URL = "https://www.goodbom.com.br/hortolandia/busca?q="
ARENA_URL = "https://www.arenaatacado.com.br/on/demandware.store/Sites-Arena-Site/pt_BR/Search-Show?q="
INPUT_FILE = "products.txt"
OUTPUT_JSON = "docs/prices.json"
NUM_PRODUTOS = 3

def extrair_peso(nome_produto):
    match = re.search(r"(\d+)\s*g", nome_produto.lower())
    if match:
        return int(match.group(1)) / 1000
    return 1

def buscar_goodbom(produto):
    try:
        url = f"{GOODBOM_URL}{produto}"
        response = requests.get(url, timeout=15)
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
            if produto.lower() not in nome.lower():
                continue

            preco_str = preco_span.get_text(strip=True).replace("R$", "").split("/")[0].replace(",", ".").strip()
            try:
                preco = float(preco_str)
            except ValueError:
                continue

            peso_kg = extrair_peso(nome)
            preco_kg = round(preco / peso_kg, 2)

            encontrados.append({
                "supermercado": "Goodbom",
                "produto": nome,
                "preco": preco,
                "preco_por_kg": preco_kg
            })

        if encontrados:
            return min(encontrados, key=lambda x: x["preco_por_kg"])
    except Exception as e:
        print(f"Erro Goodbom ({produto}): {e}")
    return None

def buscar_arena(produto):
    try:
        url = f"{ARENA_URL}{produto}"
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        # Salva HTML bruto para debug
        with open("arena_debug.html", "w", encoding="utf-8") as f:
            f.write(response.text)

        soup = BeautifulSoup(response.text, "html.parser")
        resultados = soup.find_all("div", class_="productCard")[:NUM_PRODUTOS]
        encontrados = []

        for card in resultados:
            nome_span = card.find("span", class_="productCard__title")
            preco_span = card.find("span", class_="productPrice__price")
            if not nome_span or not preco_span:
                continue

            nome = nome_span.get_text(strip=True)
            if produto.lower() not in nome.lower():
                continue

            preco_str = preco_span.get_text(strip=True).replace("R$", "").replace(".", "").replace(",", ".").strip()
            try:
                preco = float(preco_str)
            except ValueError:
                continue

            peso_kg = 1
            peso_info = card.find("div", class_="productPrice-averageWeight__price")
            if peso_info:
                match = re.search(r"(\d+[,.]?\d*)\s*kg", peso_info.get_text(strip=True).lower())
                if match:
                    peso_kg = float(match.group(1).replace(",", "."))

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
        item_goodbom = buscar_goodbom(produto)
        item_arena = buscar_arena(produto)

        if item_goodbom:
            resultados_finais.append(item_goodbom)
        if item_arena:
            resultados_finais.append(item_arena)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(resultados_finais, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
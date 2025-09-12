import requests
from bs4 import BeautifulSoup
import json
import re

#Teste Arena
def nomes_batem(produto_busca, nome_site):
    # deixa tudo em minúsculo
    p = produto_busca.lower()
    n = nome_site.lower()

    # divide em palavras
    palavras_p = set(p.split())
    palavras_n = set(n.split())

    # exige que pelo menos metade das palavras do termo de busca estejam no nome encontrado
    intersecao = palavras_p.intersection(palavras_n)
    return len(intersecao) >= max(1, len(palavras_p) // 2)
#--------------

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
    match = re.search(r"(\d+[,.]?\d*)\s*kg", nome_produto.lower())
    if match:
        return float(match.group(1).replace(",", "."))
    return 1  # assume 1kg se não achar peso

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
        soup = BeautifulSoup(response.text, "html.parser")

        resultados = soup.find_all("div", class_="productCard")[:NUM_PRODUTOS]
        encontrados = []

        for card in resultados:
            nome_span = card.find("span", class_="productCard__title")
            preco_span = card.find("span", class_="productPrice__price")
            if not nome_span or not preco_span:
                continue

            nome = nome_span.get_text(strip=True)
            if not nomes_batem(produto, nome): 
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
                "produto": nome,
                "preco": preco,
                "preco_por_kg": preco_kg
            })

        if encontrados:
            return min(encontrados, key=lambda x: x["preco_por_kg"])
    except Exception as e:
        print(f"Erro Arena ({produto}): {e}")
    return None

def montar_carrinho(nome_mercado, produtos_lista, func_scraper):
    carrinho = {"produtos": [], "total": 0.0, "faltando": 0}
    for produto in produtos_lista:
        item = func_scraper(produto)
        if item:
            carrinho["produtos"].append(item)
            carrinho["total"] += item["preco"]
        else:
            carrinho["faltando"] += 1
    carrinho["total"] = round(carrinho["total"], 2)
    return carrinho

def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        produtos_lista = [linha.strip() for linha in f if linha.strip()]

    resultados = {
        "Goodbom": montar_carrinho("Goodbom", produtos_lista, buscar_goodbom),
        "Arena Atacado": montar_carrinho("Arena Atacado", produtos_lista, buscar_arena)
    }

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()

import requests
from bs4 import BeautifulSoup
import json
import re

# Configurações
BASE_URL = "https://www.goodbom.com.br/hortolandia/busca?q="
PRODUTO = "bacon"
OUTPUT_JSON = "pages/precos.json"
SUPERMERCADO = "Goodbom"
NUM_PRODUTOS = 3

def extrair_peso(nome_produto):
    # Procura por peso em gramas (ex: 250G)
    match = re.search(r"(\d+)\s*g", nome_produto.lower())
    if match:
        return int(match.group(1)) / 1000  # converte para kg
    return 1  # padrão 1kg se não encontrado

def main():
    url = f"{BASE_URL}{PRODUTO}"
    response = requests.get(url)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    produtos = []
    
    # Seleciona os primeiros NUM_PRODUTOS produtos
    resultados = soup.find_all("span", class_="product-name")[:NUM_PRODUTOS]
    
    for nome_span in resultados:
        a_tag = nome_span.find_parent("a")
        preco_span = a_tag.find("span", class_="price")
        nome = nome_span.get_text(strip=True)
        preco_str = preco_span.get_text(strip=True).replace("R$", "").replace(",", ".")
        preco = float(preco_str)
        peso_kg = extrair_peso(nome)
        preco_kg = round(preco / peso_kg, 2)
        
        produtos.append({
            "supermercado": SUPERMERCADO,
            "produto": nome,
            "preco": preco,
            "preco_por_kg": preco_kg
        })
    
    # Salva no JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(produtos, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()

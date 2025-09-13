import requests
from bs4 import BeautifulSoup
import re
import json
import os

TENDA_URL = "https://www.tendaatacado.com.br/busca?q="
INPUT_FILE = "products.txt"
OUTPUT_JSON = "docs/prices_tenda.json"
NUM_PRODUTOS = 3

# CEP fixo para simulação
CEP = "13183-001"

def extrair_peso(nome):
    match = re.search(r"(\d+)\s*g", nome.lower())
    return int(match.group(1))/1000 if match else 1

def buscar_tenda(produto):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "x-shipping-cep": CEP,   # tentativa 1
        }
        cookies = {
            "cep": CEP,              # tentativa 2
        }

        resp = requests.get(f"{TENDA_URL}{produto}", headers=headers, cookies=cookies, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        encontrados = []
        cards = soup.find_all("a", class_="showcase-card-content")[:NUM_PRODUTOS]

        for card in cards:
            nome_tag = card.find("h3", class_="TitleCardComponent")
            preco_tag = card.find("div", class_="SimplePriceComponent")
            if not nome_tag or not preco_tag:
                continue

            nome = nome_tag.get_text(strip=True)
            preco = float(preco_tag.get_text(strip=True).replace("R$", "").split()[0].replace(",", "."))

            peso_kg = extrair_peso(nome)
            encontrados.append({
                "supermercado": "Tenda",
                "produto": nome,
                "preco": preco,
                "preco_por_kg": round(preco/peso_kg, 2)
            })

        # se não achou nada, salvar HTML para debug
        if not encontrados:
            debug_file = f"debug_{produto.replace(' ', '_')}.html"
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(resp.text)
            print(f"[DEBUG] Nenhum produto encontrado para '{produto}'. HTML salvo em {debug_file}")

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

    os.makedirs("docs", exist_ok=True)
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

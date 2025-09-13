# scraper_arena.py
import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.arenaatacado.com.br/on/demandware.store/Sites-Arena-Site/pt_BR/Search-Show?q="

def ler_produtos(filename="products.txt"):
    with open(filename, "r", encoding="utf-8") as f:
        produtos = [linha.strip() for linha in f if linha.strip()]
    return produtos

def buscar_produto(nome):
    url = BASE_URL + nome.replace(" ", "+")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Erro ao acessar {url}")
        return []
    return resp.text

def parse_cards(html):
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select(".search-card__grid__item .productCard")[:3]  # pegar os 3 primeiros
    resultados = []

    for card in cards:
        try:
            nome = card.select_one(".productCard__title").get_text(strip=True)
            preco_text = card.select_one(".productPrice__price").get_text(strip=True)
            preco = float(re.sub(r"[^\d,]", "", preco_text).replace(",", "."))
            peso_text = card.select_one(".productPrice-averageWeight__price")
            if peso_text:
                peso = float(re.sub(r"[^\d,]", "", peso_text.get_text(strip=True)).replace(",", "."))
            else:
                peso = 1.0  # se não tiver peso, assume 1 kg
            preco_kg = preco / peso
            resultados.append({
                "nome": nome,
                "preco": preco,
                "peso": peso,
                "preco_kg": preco_kg
            })
        except Exception as e:
            print("Erro ao parsear card:", e)
    return resultados

def main():
    produtos = ler_produtos()
    todos_resultados = []
    faltantes = []

    for produto in produtos:
        html = buscar_produto(produto)
        cards = parse_cards(html)
        if cards:
            todos_resultados.extend(cards)
        else:
            faltantes.append(produto)

    total = sum(item["preco"] for item in todos_resultados)

    print("Produtos encontrados:")
    for item in todos_resultados:
        print(f"{item['nome']} - R$ {item['preco']:.2f} - {item['peso']}kg - R$ {item['preco_kg']:.2f}/kg")

    print(f"\nTotal: R$ {total:.2f}")

    if faltantes:
        print(f"\nProdutos não encontrados: {len(faltantes)} -> {', '.join(faltantes)}")

if __name__ == "__main__":
    main()
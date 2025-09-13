# scraper_arena.py
import json
import asyncio
from playwright.async_api import async_playwright

OUTPUT_FILE = "arena_produtos.json"  # arquivo de saída

async def scrape_arena(search_term):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Abrir a página de busca
        search_url = f"https://www.arenaatacado.com.br/on/demandware.store/Sites-Arena-Site/pt_BR/Search-Show?q={search_term}"
        await page.goto(search_url)
        
        # Esperar os cards carregarem
        await page.wait_for_selector(".search-card__grid__item")
        
        # Extrair dados
        produtos = await page.evaluate("""
        () => {
            const cards = Array.from(document.querySelectorAll('.search-card__grid__item'));
            return cards.map(card => {
                const id = card.getAttribute('data-id');
                const nomeEl = card.querySelector('.productCard__title');
                const precoEl = card.querySelector('.productPrice__price');
                const pesoEl = card.querySelector('.productPrice-averageWeight__price');
                const linkEl = card.querySelector('.productCard__imageWrapper a');
                const imgEl = card.querySelector('.productCard__imageWrapper img');

                return {
                    id: id || null,
                    nome: nomeEl ? nomeEl.innerText.trim() : None,
                    preco: precoEl ? precoEl.innerText.trim() : None,
                    peso: pesoEl ? pesoEl.innerText.trim() : None,
                    link: linkEl ? linkEl.href : None,
                    imagem: imgEl ? imgEl.src : None
                };
            });
        }
        """)
        
        # Salvar JSON
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(produtos, f, ensure_ascii=False, indent=2)
        
        print(f"[✔] Scraping finalizado! {len(produtos)} produtos salvos em {OUTPUT_FILE}")
        await browser.close()

if __name__ == "__main__":
    termo = input("Digite o termo de busca: ").strip()
    asyncio.run(scrape_arena(termo))
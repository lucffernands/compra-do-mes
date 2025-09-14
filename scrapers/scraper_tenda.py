import requests
import json

url = "https://api.tendaatacado.com.br/api/public/retail/product/search"

headers = {
    "accept": "application/json",
    "content-type": "application/json",
    "origin": "https://www.tendaatacado.com.br",
    "referer": "https://www.tendaatacado.com.br/",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
}

payload = {
    "search": "bacon",
    "page": 1,
    "per_page": 20
}

try:
    print("🔍 Buscando Tenda: BACON")
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    
    data = response.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))

except requests.exceptions.RequestException as e:
    print(f"Erro Tenda (BACON): {e}")

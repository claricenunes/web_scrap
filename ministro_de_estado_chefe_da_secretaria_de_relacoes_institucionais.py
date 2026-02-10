import re
import json
import requests
from bs4 import BeautifulSoup

URL = "https://www.gov.br/sri/pt-br/composicao/ministra-1"

# Cargo canônico (fallback se não for encontrado no site)
CARGO_CANONICAL = "ministro de estado chefe da secretaria de relações internacionais"


def find_email(text, soup):
	# try mailto links first
	a = soup.find('a', href=lambda h: h and h.startswith('mailto:'))
	if a:
		return a.get('href').split(':', 1)[1].strip()
	# fallback to regex
	m = re.search(r'[\w\.-]+@[\w\.-]+', text)
	return m.group(0) if m else None


def find_phone(text):
	# loose phone regex for Brazilian numbers
	m = re.search(r'(?:\+?\d{2,3}[\s-]?)?(?:\(?\d{2}\)?[\s-]?)?\d{4,5}[\s-]?\d{4}', text)
	return m.group(0).strip() if m else None


def _masculinize_text(text: str) -> str:
	if not text:
		return text
	replacements = {
		'ministra': 'ministro',
		'secretária': 'secretário',
		'coordenadora': 'coordenador',
		'diretora': 'diretor',
		'assessora': 'assessor',
	}

	pattern = r"\b(" + "|".join(re.escape(k) for k in replacements.keys()) + r")\b"

	def repl(m):
		orig = m.group(0)
		key = orig.lower()
		val = replacements.get(key, key)
		if orig.isupper():
			return val.upper()
		if orig.istitle():
			return val.title()
		return val

	return re.sub(pattern, repl, text, flags=re.IGNORECASE)


def normalize_cargo(text):
	# Use the exact cargo text found on the site, but convert feminine titles to masculine
	if not text:
		return CARGO_CANONICAL
	cargo = _masculinize_text(text)
	return cargo.strip()


def clean_cargo_text(text: str) -> str:
	if not text:
		return text
	# remove common labels
	text = re.sub(r'(?i)telefone[s]?:', '', text)
	text = re.sub(r'(?i)e[- ]?mail[s]?:', '', text)
	# remove emails
	text = re.sub(r'[\w\.-]+@[\w\.-]+', '', text)
	# remove phone numbers
	text = re.sub(r'(?:\+?\d{2,3}[\s-]?)?(?:\(?\d{2}\)?[\s-]?)?\d{4,5}[\s-]?\d{4}', '', text)
	# remove separators and extra whitespace
	text = re.sub(r'[\|—–·\-]{1,}', ' ', text)
	text = re.sub(r'\s{2,}', ' ', text)
	return text.strip()


def scrape(url=URL):
	headers = {"User-Agent": "Mozilla/5.0 (compatible; scraper/1.0)"}
	r = requests.get(url, headers=headers, timeout=15)
	r.raise_for_status()
	soup = BeautifulSoup(r.text, 'html.parser')

	# Nome: normalmente no primeiro h1
	name_tag = soup.find(['h1', 'h2'])
	nome = name_tag.get_text(strip=True) if name_tag else None

	# Cargo: procurar por elementos que contenham 'Ministra' ou 'Ministro' ou palavras-chave
	# Primeiro tentar extrair o cargo do elemento específico: <p class="autoridade">
	cargo_text = None
	autoridade_tag = soup.find('p', class_='autoridade')
	if autoridade_tag:
		cargo_text = autoridade_tag.get_text(' ', strip=True)
	else:
		for tag in soup.find_all(['p', 'div', 'span', 'strong']):
			txt = tag.get_text(' ', strip=True)
			if re.search(r'(?i)ministr[ao]', txt):
				cargo_text = txt
				break
	# limpar telefone/email que às vezes ficam no mesmo bloco do cargo
	cargo_text = clean_cargo_text(cargo_text) if cargo_text else None
	cargo = normalize_cargo(cargo_text)

	# Buscar telefone e email no texto da página
	full_text = soup.get_text(' ', strip=True)
	telefone = find_phone(full_text)
	email = find_email(full_text, soup)

	result = {
		'nome': nome,
		'cargo': cargo,
		'telefone': telefone,
		'email': email,
		'fonte': url,
	}

	return result


if __name__ == '__main__':
	data = scrape()
	print(json.dumps(data, ensure_ascii=False, indent=2))
	with open('ministro_sri_ministra-1.json', 'w', encoding='utf-8') as f:
		json.dump(data, f, ensure_ascii=False, indent=2)


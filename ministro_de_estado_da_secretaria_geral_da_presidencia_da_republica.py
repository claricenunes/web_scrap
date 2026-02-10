import requests
from bs4 import BeautifulSoup
import re
import json
import csv
from urllib.parse import urljoin

URL = "https://www.gov.br/secretariageral/pt-br/composicao/ministro"


def get_soup(url):
	headers = {"User-Agent": "Mozilla/5.0 (compatible; scraper/1.0)"}
	resp = requests.get(url, headers=headers, timeout=15)
	resp.raise_for_status()
	return BeautifulSoup(resp.content, "html.parser")


def extract_minister(soup, base_url=URL):
	# Primeiro tenta seletores específicos da página da Secretaria-Geral
	try:
		h1 = soup.find('h1', class_='documentFirstHeading')
		if h1:
			name = h1.get_text(strip=True)
			autor = soup.find('p', class_='autoridade')
			title = autor.get_text(strip=True) if autor else None

			phones = []
			tel_p = soup.find('p', class_='telefone')
			if tel_p:
				phones = re.findall(r"\(?\d{2}\)?\s*\d{4,5}[-/\s]?\d{4}", tel_p.get_text())

			emails = []
			email_p = soup.find('p', class_='email')
			if email_p:
				emails = re.findall(r"[\w\.-]+@[\w\.-]+\.[A-Za-z]{2,}", email_p.get_text())

			return {
				"name": name,
				"title": title,
				"emails": list(dict.fromkeys(emails)),
				"phones": phones,
				"source": base_url,
			}
	except Exception:
		# se algo falhar no caminho específico, prossegue com heurística genérica
		pass

	# Fallback: heurística genérica (procura por ocorrências de 'Ministro'/'Ministra')
	candidates = soup.find_all(string=re.compile(r"\bMinistr[oa]\b", re.I))
	for text_node in candidates:
		container = text_node
		for _ in range(5):
			parent = container.parent
			if parent is None:
				break
			container = parent

		block_text = container.get_text("\n", strip=True)

		emails = []
		for a in container.find_all("a", href=True):
			href = a["href"]
			if href.startswith("mailto:"):
				emails.append(href.split("mailto:", 1)[1].strip())
		emails = [e for e in emails if not re.search(r"cerimonial|agenda", e, re.I)]

		phones = []
		lines = [l.strip() for l in block_text.splitlines() if l.strip()]
		tele_lines = [l for l in lines if re.search(r"Telefones?:", l, re.I) and not re.search(r"Fax", l, re.I)]
		if tele_lines:
			for tl in tele_lines:
				nums = re.findall(r"\(\d{2}\)\s*\d{4,5}-?\d{4}|\b\d{4,5}-?\d{4}\b", tl)
				ddd = None
				for n in nums:
					if re.match(r"\(\d{2}\)", n):
						ddd = re.search(r"\(\d{2}\)", n).group(0)
						break
				for n in nums:
					if not re.match(r"\(\d{2}\)", n) and ddd:
						n = ddd + " " + n
					if n not in phones:
						phones.append(n)

		if len(phones) < 3:
			all_phones = []
			for l in lines:
				if re.search(r"Fax", l, re.I):
					continue
				all_phones.extend(re.findall(r"\(\d{2}\)\s*\d{4,5}-?\d{4}", l))
			for p in all_phones:
				if p not in phones:
					phones.append(p)
				if len(phones) >= 3:
					break

		name = None
		title = None
		for i, line in enumerate(lines):
			if re.search(r"\bMinistr[oa]\b", line, re.I):
				title = line
				if i > 0:
					possible_name = lines[i - 1]
					if not re.search(r"\(\d{2}\)|mailto:|Telefones?:|Fax:", possible_name, re.I):
						name = possible_name
				if not name:
					m = re.search(r"^(?P<name>.+?)\s+Ministr[oa]", line, re.I)
					if m:
						name = m.group("name").strip()
				break

		if not name and lines:
			name = lines[0]

		result = {
			"name": name,
			"title": title,
			"emails": list(dict.fromkeys(emails)),
			"phones": phones,
			"source": base_url,
		}

		return result

	return None


def save_json(data, path):
	with open(path, "w", encoding="utf-8") as f:
		json.dump(data, f, ensure_ascii=False, indent=2)


def save_csv(data, path):
	keys = ["name", "title", "emails", "phones", "source"]
	with open(path, "w", newline="", encoding="utf-8") as f:
		writer = csv.DictWriter(f, fieldnames=keys)
		writer.writeheader()
		row = {k: ("; ".join(data[k]) if isinstance(data[k], list) else data.get(k, "")) for k in keys}
		writer.writerow(row)


def main():
	try:
		soup = get_soup(URL)
	except Exception as e:
		print("Erro ao baixar a página:", e)
		return

	minister = extract_minister(soup)
	if not minister:
		print("Não foi possível localizar as informações do ministro na página.")
		return

	out_json = "ministro_de_estado_da_secretaria_geral_da_presidencia_da_republica.json"
	out_csv = "ministro_de_estado_da_secretaria_geral_da_presidencia_da_republica.csv"
	save_json(minister, out_json)
	save_csv(minister, out_csv)

	print("Dados do ministro salvos em:", out_json, "e", out_csv)
	print(json.dumps(minister, ensure_ascii=False, indent=2))


if __name__ == '__main__':
	main()


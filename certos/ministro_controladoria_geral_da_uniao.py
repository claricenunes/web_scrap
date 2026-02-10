import requests
from bs4 import BeautifulSoup
import re
import json
import csv
import os
from urllib.parse import urljoin

URL = "https://www.gov.br/cgu/pt-br/acesso-a-informacao/institucional/quem-e-quem/gabinete-ministerial"


def get_soup(url):
	headers = {"User-Agent": "Mozilla/5.0 (compatible; scraper/1.0)"}
	resp = requests.get(url, headers=headers, timeout=15)
	resp.raise_for_status()
	return BeautifulSoup(resp.content, "html.parser")


def extract_minister(soup, base_url=URL):
	# Procura por ocorrências da palavra 'Ministro' e tenta extrair o bloco de informação
	candidates = soup.find_all(string=re.compile(r"\bMinistro\b", re.I))
	for text_node in candidates:
		container = text_node
		# sobe alguns níveis para pegar o wrapper do bloco
		for _ in range(4):
			parent = container.parent
			if parent is None:
				break
			container = parent

		# Heurística: bloco deve conter ao menos um e-mail ou telefone ou imagem
		block_text = container.get_text("\n", strip=True)
		has_email = bool(re.search(r"mailto:", str(container)) or re.search(r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}", block_text))
		has_phone = bool(re.search(r"\(\d{2}\)\s*\d{4,5}-?\d{4}", block_text))
		if not (has_email or has_phone):
			continue


		# Extrai e-mails (filtra cerimonial/agenda)
		emails = []
		for a in container.find_all("a", href=True):
			href = a["href"]
			if href.startswith("mailto:"):
				emails.append(href.split("mailto:", 1)[1].strip())
		# remover e-mails de cerimonial/agenda
		emails = [e for e in emails if not re.search(r"cerimonial|agenda", e, re.I)]
		# se nenhum e-mail útil encontrado, tenta pegar qualquer outro mailto previamente coletado
		if not emails:
			for a in container.find_all("a", href=True):
				href = a["href"]
				if href.startswith("mailto:"):
					emails.append(href.split("mailto:", 1)[1].strip())

		# Extrai telefones: prefere a linha que contém 'Telefones' e ignora linhas de 'Fax'
		phones = []
		lines = [l.strip() for l in block_text.splitlines() if l.strip()]
		tele_lines = [l for l in lines if re.search(r"Telefones?:", l, re.I) and not re.search(r"Fax", l, re.I)]
		if tele_lines:
			# normalmente a linha contém números separados por '/' ou '\\u002F' ou espaços
			for tl in tele_lines:
				nums = re.findall(r"\(\d{2}\)\s*\d{4,5}-?\d{4}|\b\d{4,5}-?\d{4}\b", tl)
				# normalizar números sem o DDD para incluir DDD da primeira ocorrência
				if nums:
					# se houver números sem DDD, prefixa com o DDD do primeiro com DDD
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
		# fallback: procura por quaisquer números no bloco, mas ignora linhas que contenham 'Fax'
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

		# Limpando e quebrando linhas para localizar nome e cargo
		lines = [l.strip() for l in block_text.splitlines() if l.strip()]

		name = None
		title = None
		# Busca por linha que contenha 'Ministro' para extrair cargo e possivelmente nome adjacente
		for i, line in enumerate(lines):
			if re.search(r"\bMinistro\b", line, re.I):
				title = line
				# tenta nome na linha anterior
				if i > 0:
					possible_name = lines[i - 1]
					# se a linha anterior não for telefone/email, assume nome
					if not re.search(r"\(\d{2}\)|mailto:|Telefones?:|Fax:", possible_name, re.I):
						name = possible_name
				# se mesmo a linha tiver o nome concatenado, tenta extrair parte anterior a 'Ministro'
				if not name:
					m = re.search(r"^(?P<name>.+?)\s+Ministro", line, re.I)
					if m:
						name = m.group("name").strip()
				break

		# Se não encontrou, pega primeira linha como nome alternativa
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
	# Garantir diretório
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

	out_json = "ministro_controladoria_geral_da_uniao.json"
	out_csv = "ministro_controladoria_geral_da_uniao.csv"
	save_json(minister, out_json)
	save_csv(minister, out_csv)

	print("Dados do ministro salvos em:", out_json, "e", out_csv)
	print(json.dumps(minister, ensure_ascii=False, indent=2))


if __name__ == '__main__':
	main()


import os
import re
import sys
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from typing import List, Dict

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")  # Custom search engine ID

def google_search(query: str, num_results: int = 5) -> List[Dict[str, str]]:
    """Search Google using the Custom Search API."""
    if not GOOGLE_API_KEY or not GOOGLE_CX:
        raise RuntimeError("GOOGLE_API_KEY and GOOGLE_CX must be set")
    encoded_query = urllib.parse.quote_plus(query)
    url = (
        "https://customsearch.googleapis.com/customsearch/v1?" +
        f"key={GOOGLE_API_KEY}&cx={GOOGLE_CX}&q={encoded_query}&num={num_results}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp:
        data = resp.read().decode("utf-8", errors="ignore")
    import json
    results_json = json.loads(data)
    items = results_json.get("items", [])
    return [
        {"title": item.get("title", ""), "url": item.get("link", "")}
        for item in items
    ]

def fetch_page(url: str):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode('utf-8', errors='ignore')

class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []

    def handle_data(self, data):
        self.text_parts.append(data)

def extract_text(html: str):
    parser = TextExtractor()
    parser.feed(html)
    text = ' '.join(parser.text_parts)
    return re.sub(r'\s+', ' ', text)

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

try:
    from deepseek import Summarizer  # type: ignore

    _summarizer = (
        Summarizer(api_key=DEEPSEEK_API_KEY)
        if DEEPSEEK_API_KEY is not None
        else Summarizer()
    )

    def summarize(text: str, max_sentences: int = 5) -> str:
        return _summarizer.summarize(text, max_sentences=max_sentences)
except Exception:
    def summarize(text: str, max_sentences: int = 5) -> str:
        sentences = re.split(r'[.!?]\s+', text)
        freq = {}
        for sentence in sentences:
            for word in re.findall(r'\w+', sentence.lower()):
                freq[word] = freq.get(word, 0) + 1
        ranking = []
        for sentence in sentences:
            score = sum(freq.get(word, 0) for word in re.findall(r'\w+', sentence.lower()))
            ranking.append((score, sentence))
        ranking.sort(key=lambda x: x[0], reverse=True)
        top_sentences = [s for _, s in ranking[:max_sentences]]
        return ' '.join(top_sentences)

def create_report(query: str, results):
    lines = [
        '<html>',
        '<head><meta charset="utf-8"><title>Report</title></head>',
        '<body>',
        f'<h1>Search results for {query}</h1>'
    ]
    for r in results:
        lines.append(f'<h2><a href="{r["url"]}">{r["title"]}</a></h2>')
        if "summary" in r:
            lines.append(f'<p>{r["summary"]}</p>')
    lines.extend(['</body>', '</html>'])
    return '\n'.join(lines)

def main(query: str):
    results = google_search(query)
    for r in results:
        try:
            page_html = fetch_page(r['url'])
            text = extract_text(page_html)
            r['summary'] = summarize(text)
        except Exception as exc:
            r['summary'] = f'Failed to fetch: {exc}'
        time.sleep(1)
    report_html = create_report(query, results)
    with open('report.html', 'w', encoding='utf-8') as f:
        f.write(report_html)
    print('Report saved to report.html')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python agent.py <search query>')
    else:
        main(' '.join(sys.argv[1:]))

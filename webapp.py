from flask import Flask, request, render_template_string
from agent import google_search, fetch_page, extract_text, summarize

app = Flask(__name__)

TEMPLATE = '''
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Netgo Search</title>
</head>
<body>
    <form method="get" action="/">
        <input type="text" name="q" placeholder="Enter search query" value="{{ query|default('') }}" />
        <button type="submit">Search</button>
    </form>
    {% if results %}
    <h1>Search results for {{ query }}</h1>
    {% for r in results %}
        <h2><a href="{{ r['url'] }}">{{ r['title'] }}</a></h2>
        {% if r.summary %}
            <p>{{ r.summary }}</p>
        {% endif %}
    {% endfor %}
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    query = request.args.get('q')
    results = []
    if query:
        google_results = google_search(query)
        for r in google_results:
            try:
                html = fetch_page(r['url'])
                text = extract_text(html)
                r['summary'] = summarize(text)
            except Exception as exc:
                r['summary'] = f'Failed to fetch: {exc}'
        results = google_results
    return render_template_string(TEMPLATE, query=query, results=results)

if __name__ == '__main__':
    app.run(debug=True)

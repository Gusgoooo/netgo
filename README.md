# netgo

A simple tool for performing Google searches, fetching pages, extracting text, and generating an HTML report summarizing the results. The summarization will use the `deepseek` library when available, otherwise it falls back to a basic frequency-based method implemented in `agent.py`.

## Usage

```bash
export GOOGLE_API_KEY=<your Google API key>
export GOOGLE_CX=<your Custom Search Engine ID>
export DEEPSEEK_API_KEY=<your DeepSeek API key>
python agent.py "search term"           # generate report.html via CLI
python webapp.py                        # run interactive web interface
```

The script retrieves Google results using the Custom Search API, visits each page, extracts text and generates a summary. A `report.html` file is written in the current directory.

### Web interface

Running `python webapp.py` starts a local Flask server (default `http://localhost:5000`) where you can submit queries through a browser. Results are displayed on the page with summaries for each search hit.

Network access is required for both the search and page retrieval steps, so the script may fail in restricted environments.

"""
Web Server for "Search a Group Chat Properly"
Zero-dependency HTTP server using Python standard library (http.server).
Serves API endpoints:
- GET /api/search?q=...&mode=...&window=...
- GET /api/benchmark
- GET /api/benchmark/run
- POST /api/chat
- GET /
"""

import http.server
import socketserver
import json
import urllib.parse
import os
import sys

base_dir = os.path.dirname(__file__)
engine_dir = os.path.join(base_dir, "engine")
data_dir = os.path.join(base_dir, "data")

if engine_dir not in sys.path:
    sys.path.insert(0, engine_dir)

from search_engine import GroupChatSearchEngine
from chatbot import generate_answer

# Load dataset and benchmark
data_file = os.path.join(data_dir, "group_chat_data.json")
bench_file = os.path.join(data_dir, "benchmark_queries.json")
eval_file = os.path.join(data_dir, "evaluation_results.json")

print("Initializing Group Chat Search Engine...")
with open(data_file, "r", encoding="utf-8") as f:
    messages = json.load(f)

with open(bench_file, "r", encoding="utf-8") as f:
    benchmark_queries = json.load(f)

evaluation_cache = None
if os.path.exists(eval_file):
    with open(eval_file, "r", encoding="utf-8") as f:
        evaluation_cache = json.load(f)

engine = GroupChatSearchEngine(messages)
print(f"Search engine ready with {len(messages)} messages.")

class ChatSearchHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if path == "/api/search":
            q = query_params.get("q", [""])[0]
            mode = query_params.get("mode", ["contextual_hybrid"])[0]
            top_k = int(query_params.get("top_k", [5])[0])
            window = int(query_params.get("window", [4])[0])

            results = engine.search(q, mode=mode, top_k=top_k, context_window=window)
            self._send_json({"query": q, "mode": mode, "results": results})

        elif path == "/api/benchmark":
            self._send_json({
                "queries": benchmark_queries,
                "cached_evaluation": evaluation_cache
            })

        elif path == "/api/stats":
            self._send_json({
                "total_messages": len(messages),
                "participants": list(set(m["sender"] for m in messages)),
                "date_range": [messages[0]["timestamp"], messages[-1]["timestamp"]],
                "benchmark_count": len(benchmark_queries)
            })

        elif path == "/" or path == "/index.html":
            html_path = os.path.join(base_dir, "web", "index.html")
            if os.path.exists(html_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                with open(html_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self._send_json({"status": "running", "endpoints": ["/api/search", "/api/benchmark", "/api/stats"]})
        else:
            super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        if parsed_url.path == "/api/chat":
            content_len = int(self.headers.get("Content-Length", 0))
            post_body = self.rfile.read(content_len).decode("utf-8")
            data = json.loads(post_body)
            q = data.get("query", "")
            mode = data.get("mode", "contextual_hybrid")
            results = engine.search(q, mode=mode, top_k=5, context_window=4)
            chat_resp = generate_answer(q, results)
            self._send_json({
                "query": q,
                "answer": chat_resp["answer"],
                "evidence": results[:3]
            })
        else:
            self.send_response(404)
            self.end_headers()

    def _send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

def run_server(port=8080):
    server_address = ("", port)
    httpd = socketserver.TCPServer(server_address, ChatSearchHandler)
    print(f"Group Chat Search Web App running at http://localhost:{port}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(p)

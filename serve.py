#!/usr/bin/env python3
"""Serve part-search-test.html from localhost.
This gives the browser a real origin (http://localhost:8080)
instead of 'null' (file://), which fixes CORS + credentials.

Usage: python serve.py
Then open http://localhost:8080
"""
import http.server, os
os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')
print(f"Serving at http://localhost:8080  (Ctrl+C to stop)")
http.server.HTTPServer(('', 8080), http.server.SimpleHTTPRequestHandler).serve_forever()

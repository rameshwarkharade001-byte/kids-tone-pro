from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote
import urllib.request
import json
import re

QUERY_MAP = {
    "all": "Motu Patlu Chhota Bheem Doraemon Hindi Cartoon",
    "motu": "Motu Patlu Hindi Cartoon",
    "bheem": "Chhota Bheem Hindi Cartoon",
    "doraemon": "Doraemon Hindi Cartoon",
    "shinchan": "Shinchan Hindi Cartoon",
    "oggy": "Oggy and the Cockroaches Hindi",
    "funnykids": "Funny Kids Comedy Videos",
    "masha": "Masha and the Bear Hindi",
    "singham": "Little Singham Hindi",
    "rudra": "Rudra Cartoon Hindi",
    "vir": "Vir The Robot Boy Hindi",
    "gattu": "Gattu Battu Hindi",
    "pakdam": "Pakdam Pakdai Hindi",
    "roll21": "Roll No 21 Hindi",
    "shiva": "Shiva Cartoon Hindi",
    "taarak": "Taarak Mehta Ka Chhota Chashmah",
    "rhymes": "Hindi Nursery Rhymes Kids"
}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        cat = (params.get('category') or ['all'])[0].strip().lower()
        q_raw = (params.get('q') or [''])[0].strip()
        final_query = q_raw if q_raw else QUERY_MAP.get(cat, "Motu Patlu Chhota Bheem Hindi Cartoon")

        videos = []
        seen = set()
        # Use Piped public API instances (never blocked by YouTube, returns exact 11-char IDs & clean UTF-8 titles)
        instances = [
            "https://pipedapi.kavin.rocks",
            "https://pipedapi.adminforge.de",
            "https://api.piped.yt"
        ]
        for base in instances:
            try:
                api_url = f"{base}/search?q={quote(final_query)}&filter=videos"
                req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
                raw = urllib.request.urlopen(req, timeout=7).read().decode('utf-8')
                data = json.loads(raw)
                items = data.get('items', [])
                for it in items:
                    url_part = it.get('url', '')
                    m = re.search(r'v=([a-zA-Z0-9_-]{11})', url_part)
                    if not m:
                        continue
                    vid = m.group(1)
                    if vid in seen:
                        continue
                    dur_sec = it.get('duration', 0)
                    if not isinstance(dur_sec, int) or dur_sec < 90:
                        continue
                    mins, secs = divmod(dur_sec, 60)
                    seen.add(vid)
                    videos.append({
                        'ytid': vid,
                        'title': it.get('title', 'Kids Cartoon'),
                        'category': cat.title(),
                        'duration': f"{mins}:{secs:02d}",
                        'views': 'Kids Safe'
                    })
                    if len(videos) >= 18:
                        break
                if videos:
                    break
            except Exception:
                continue

        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'ok', 'videos': videos}, ensure_ascii=False).encode('utf-8'))

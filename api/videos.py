from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, quote
import urllib.request
import json
import re

QUERY_MAP = {
    "all": "Motu Patlu Chhota Bheem Doraemon Oggy Hindi Cartoon Full Episode",
    "motu": "Motu Patlu cartoon full episode hindi",
    "bheem": "Chhota Bheem cartoon full episode hindi",
    "doraemon": "Doraemon cartoon hindi episode",
    "shinchan": "Shinchan cartoon hindi episode",
    "oggy": "Oggy and the Cockroaches hindi cartoon",
    "funnykids": "Funny Kids Comedy Videos Nastya Diana Vlad Niki",
    "masha": "Masha and the Bear Hindi cartoon",
    "singham": "Little Singham cartoon hindi",
    "rudra": "Rudra Boom Chik Chik Boom cartoon hindi",
    "vir": "Vir The Robot Boy cartoon hindi",
    "gattu": "Gattu Battu cartoon hindi",
    "pakdam": "Pakdam Pakdai cartoon hindi",
    "roll21": "Roll No 21 cartoon hindi",
    "shiva": "Shiva cartoon hindi full episode",
    "taarak": "Taarak Mehta Ka Chhota Chashmah cartoon",
    "paw": "Paw Patrol Hindi cartoon",
    "mickey": "Mickey Mouse Clubhouse Hindi cartoon",
    "spongebob": "SpongeBob SquarePants Hindi cartoon",
    "ben10": "Ben 10 cartoon hindi",
    "mrbean": "Mr Bean animated cartoon",
    "tomjerry": "Tom and Jerry cartoon",
    "krishna": "Little Krishna Balram cartoon",
    "ganesh": "Bal Ganesh animated cartoon",
    "akbar": "Akbar Birbal hindi cartoon stories",
    "tenali": "Tenali Rama hindi cartoon stories",
    "panchatantra": "Panchatantra cartoon hindi",
    "toys": "Kids Toys Unboxing Slime Craft Magic",
    "marathi": "Marathi Balgeet Goshti cartoon",
    "rhymes": "Chiki Chun ChuChu TV Hindi Kids Rhymes"
}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        cat = (params.get('category') or ['all'])[0].strip().lower()
        q_raw = (params.get('q') or [''])[0].strip()
        final_query = f"{q_raw} cartoon hindi" if q_raw else QUERY_MAP.get(cat, "Motu Patlu Chhota Bheem Hindi Cartoon")

        videos = []
        seen = set()
        try:
            url = f"https://www.youtube.com/results?search_query={quote(final_query)}"
            req = urllib.request.Request(url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9'
            })
            html = urllib.request.urlopen(req, timeout=9).read().decode('utf-8', errors='ignore')
            m = re.search(r'var ytInitialData = (\{.*?\});</script>', html)
            if m:
                data = json.loads(m.group(1))
                sections = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']
                for sec in sections:
                    items = sec.get('itemSectionRenderer', {}).get('contents', [])
                    for item in items:
                        vr = item.get('videoRenderer')
                        if not vr:
                            continue
                        vid = vr.get('videoId', '')
                        if not re.match(r'^[a-zA-Z0-9_-]{11}$', vid) or vid in seen:
                            continue
                        dur = vr.get('lengthText', {}).get('simpleText', '')
                        if not dur or ':' not in dur:
                            continue
                        title = ''.join(r.get('text', '') for r in vr.get('title', {}).get('runs', []))
                        if not title or '#shorts' in title.lower():
                            continue
                        seen.add(vid)
                        videos.append({
                            'ytid': vid,
                            'title': title,
                            'category': cat.title(),
                            'duration': dur,
                            'views': 'Kids Safe'
                        })
                        if len(videos) >= 18:
                            break
                    if len(videos) >= 18:
                        break
        except Exception:
            pass

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'ok', 'videos': videos}).encode('utf-8'))

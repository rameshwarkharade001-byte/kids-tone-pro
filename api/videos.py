import urllib.request
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import yt_dlp

QUERY_MAP = {
    "all": "Motu Patlu Chhota Bheem Doraemon Oggy Funny Kids",
    "motu": "Motu Patlu cartoon",
    "bheem": "Chhota Bheem cartoon",
    "doraemon": "Doraemon cartoon",
    "shinchan": "Shinchan cartoon",
    "oggy": "Oggy and the Cockroaches cartoon",
    "funnykids": "Funny Kids Comedy Videos Nastya Diana Vlad Niki",
    "masha": "Masha and the Bear Hindi cartoon",
    "singham": "Little Singham cartoon",
    "rudra": "Rudra Boom Chik Chik Boom cartoon",
    "vir": "Vir The Robot Boy cartoon",
    "gattu": "Gattu Battu cartoon",
    "pakdam": "Pakdam Pakdai cartoon",
    "roll21": "Roll No 21 cartoon",
    "shiva": "Shiva cartoon",
    "taarak": "Taarak Mehta Ka Chhota Chashmah cartoon",
    "rhymes": "Chiki Chun ChuChu TV Hindi Kids Rhymes"
}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        thumb_id = (params.get('thumb') or [''])[0].strip()
        if thumb_id:
            for quality in ('hqdefault.jpg', 'mqdefault.jpg', '0.jpg'):
                try:
                    req = urllib.request.Request(
                        f"https://i.ytimg.com/vi/{thumb_id}/{quality}",
                        headers={'User-Agent': 'Mozilla/5.0'}
                    )
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        img_bytes = resp.read()
                        if len(img_bytes) > 2000:
                            self.send_response(200)
                            self.send_header('Content-Type', 'image/jpeg')
                            self.send_header('Cache-Control', 'public, max-age=86400')
                            self.end_headers()
                            self.wfile.write(img_bytes)
                            return
                except Exception:
                    continue
            self.send_response(404)
            self.end_headers()
            return
        cat = (params.get('category') or ['all'])[0].strip().lower()
        q = (params.get('q') or [''])[0].strip()
        final_query = q if q else QUERY_MAP.get(cat, "Kids Cartoon Hindi")

        videos = []
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'skip_download': True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch18:{final_query}", download=False)
                for entry in info.get('entries', []):
                    vid = entry.get('id')
                    title = entry.get('title')
                    dur = entry.get('duration')
                    if not vid or not title or not dur or dur < 60:
                        continue
                    mins, secs = divmod(int(dur), 60)
                    videos.append({
                        'ytid': vid,
                        'title': title,
                        'category': cat.title(),
                        'duration': f"{mins}:{secs:02d}",
                        'views': 'Kids Safe'
                    })
        except Exception:
            pass

        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'ok', 'videos': videos}, ensure_ascii=False).encode('utf-8'))

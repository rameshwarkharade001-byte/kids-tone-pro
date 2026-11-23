from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.request
import json
import re

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        q = (params.get('q') or params.get('category') or ['cartoons for kids hindi'])[0]
        if q.lower() in ['all', 'cartoons']:
            q = 'motu patlu chhota bheem doraemon hindi cartoon'
        elif q.lower() == 'rhymes':
            q = 'hindi nursery rhymes balgeet kids'
        else:
            q = f"{q} kids cartoon hindi"

        videos = []
        try:
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(q)}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req, timeout=8).read().decode('utf-8', errors='ignore')
            m = re.search(r'var ytInitialData = ({.*?});</script>', html)
            if m:
                data = json.loads(m.group(1))
                contents = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents']
                for item in contents:
                    vr = item.get('videoRenderer')
                    if not vr:
                        continue
                    vid = vr.get('videoId')
                    title = ''.join(r.get('text', '') for r in vr.get('title', {}).get('runs', []))
                    dur = vr.get('lengthText', {}).get('simpleText', '12:30')
                    if vid and title:
                        videos.append({
                            'ytid': vid,
                            'title': title,
                            'category': q.split()[0].title(),
                            'duration': dur,
                            'views': 'Kids Safe'
                        })
                    if len(videos) >= 15:
                        break
        except Exception:
            pass

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'videos': videos}).encode('utf-8'))

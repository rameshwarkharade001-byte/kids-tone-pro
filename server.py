from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import yt_dlp
import requests

app = Flask(__name__, static_folder='.')
CORS(app)

YOUTUBE_API_KEY = ""
SEARCH_CACHE = {}

def fetch_youtube_kids_pro(query, page=1):
    target_count = page * 20
    start_idx = (page - 1) * 20
    cache_key = f"{query.lower()}_p{page}"

    if cache_key in SEARCH_CACHE:
        return SEARCH_CACHE[cache_key]

    videos = []

    if YOUTUBE_API_KEY and page == 1:
        try:
            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": f"{query} kids hindi",
                "type": "video",
                "videoEmbeddable": "true",
                "safeSearch": "strict",
                "maxResults": 20,
                "key": YOUTUBE_API_KEY
            }
            res = requests.get(url, params=params, timeout=6).json()
            for item in res.get("items", []):
                vid = item["id"]["videoId"]
                title = item["snippet"]["title"]
                videos.append({"ytId": vid, "title": title, "duration": "HD"})
            if videos:
                SEARCH_CACHE[cache_key] = videos
                return videos
        except Exception as e:
            print("API fallback:", e)

    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'skip_download': True,
    }

    page_suffix = [
        "full episode hindi",
        "funny videos for kids",
        "new episode 2026 hindi",
        "best comedy compilation",
        "latest kids video"
    ][(page - 1) % 5]

    search_term = f"ytsearch{target_count}:{query} {page_suffix}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(search_term, download=False)
            entries = info.get('entries', [])[start_idx:]
            for entry in entries:
                vid = entry.get('id')
                title = entry.get('title', 'Kids Cartoon Episode')
                dur = entry.get('duration')

                if dur:
                    mins, secs = divmod(int(dur), 60)
                    dur_str = f"{mins:02d}:{secs:02d}"
                else:
                    dur_str = "HD"

                if vid and len(vid) == 11:
                    videos.append({
                        "ytId": vid,
                        "title": title,
                        "duration": dur_str
                    })
    except Exception as e:
        print("Fetch error:", e)

    if videos:
        SEARCH_CACHE[cache_key] = videos
    return videos

@app.route('/')
def serve_home():
    return send_from_directory('.', 'index.html')

@app.route('/api/videos')
def get_videos():
    category = request.args.get('category', 'all').strip()
    search = request.args.get('q', '').strip()
    page = int(request.args.get('page', 1))

    query_map = {
        'all': 'Motu Patlu Chhota Bheem Doraemon Oggy Funny Kids',
        'motu': 'Motu Patlu cartoon',
        'bheem': 'Chhota Bheem cartoon',
        'doraemon': 'Doraemon cartoon',
        'shinchan': 'Shinchan cartoon',
        'oggy': 'Oggy and the Cockroaches cartoon',
        'funnykids': 'Funny Kids Comedy Videos Nastya Diana Vlad Niki',
        'masha': 'Masha and the Bear Hindi cartoon',
        'singham': 'Little Singham cartoon',
        'rudra': 'Rudra Boom Chik Chik Boom cartoon',
        'vir': 'Vir The Robot Boy cartoon',
        'gattu': 'Gattu Battu cartoon',
        'pakdam': 'Pakdam Pakdai cartoon',
        'roll21': 'Roll No 21 cartoon',
        'hattori': 'Ninja Hattori cartoon',
        'taarak': 'Taarak Mehta Ka Chhota Chashmah cartoon',
        'paw': 'Paw Patrol Hindi cartoon',
        'mickey': 'Mickey Mouse Clubhouse Hindi cartoon',
        'spongebob': 'SpongeBob SquarePants Hindi cartoon',
        'ben10': 'Ben 10 cartoon',
        'mrbean': 'Mr Bean animated cartoon',
        'tomjerry': 'Tom and Jerry cartoon',
        'krishna': 'Little Krishna Balram cartoon',
        'ganesh': 'Bal Ganesh animated cartoon',
        'akbar': 'Akbar Birbal Hindi cartoon stories',
        'tenali': 'Tenali Rama Hindi cartoon stories',
        'peppa': 'Peppa Pig Hindi cartoon',
        'toys': 'Kids Toys Unboxing Slime Craft Magic',
        'marathi': 'Marathi Balgeet Goshti cartoon',
        'rhymes': 'Chiki Chum ChuChu TV Hindi Kids Rhymes'
    }

    final_query = search if search else query_map.get(category, 'Kids Cartoon Hindi')
    videos = fetch_youtube_kids_pro(final_query, page=page)
    return jsonify({"status": "ok", "page": page, "count": len(videos), "videos": videos})

if __name__ == '__main__':
    print("Kids Tone Pro v4.0 Server Running on http://localhost:8080")
    app.run(host='0.0.0.0', port=8080)

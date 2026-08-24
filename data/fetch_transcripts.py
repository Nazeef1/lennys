import os
import json
import urllib.request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = os.path.dirname(__file__)
TRANSCRIPT_DIR = os.path.join(DATA_DIR, "transcripts")
INDEX_URL = "https://raw.githubusercontent.com/LennysNewsletter/lennys-newsletterpodcastdata/main/index.json"
RAW_BASE_URL = "https://raw.githubusercontent.com/LennysNewsletter/lennys-newsletterpodcastdata/main/"

def fetch_transcripts(limit=15):
    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
    logger.info(f"Downloading index.json from {INDEX_URL}...")
    try:
        req = urllib.request.Request(INDEX_URL, headers={'User-Agent': 'Mozilla/5.0'})
        index_data = json.loads(urllib.request.urlopen(req, timeout=10).read().decode('utf-8'))
        
        # Save local copy of index.json
        with open(os.path.join(DATA_DIR, "index.json"), "w", encoding="utf-8") as f:
            json.dump(index_data, f, indent=2)
            
        podcasts = index_data.get("podcasts", [])
        newsletters = index_data.get("newsletters", [])
        
        logger.info(f"Found {len(podcasts)} podcasts and {len(newsletters)} newsletters in index.json.")
        
        all_items = podcasts[:limit] + newsletters[:limit]
        fetched_count = 0
        
        for item in all_items:
            rel_path = item.get("filename")
            if not rel_path:
                continue
                
            basename = os.path.basename(rel_path)
            target_path = os.path.join(TRANSCRIPT_DIR, basename)
            
            if os.path.exists(target_path) and os.path.getsize(target_path) > 1000:
                logger.info(f"Using cached file: {basename}")
                fetched_count += 1
                continue
                
            url = RAW_BASE_URL + rel_path
            try:
                logger.info(f"Fetching {basename} from {url}...")
                r = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                content = urllib.request.urlopen(r, timeout=10).read().decode('utf-8')
                with open(target_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fetched_count += 1
                logger.info(f"Saved {basename} ({len(content)} bytes)")
            except Exception as e:
                logger.error(f"Error downloading {rel_path}: {e}")
                
        logger.info(f"Successfully processed {fetched_count} items into {TRANSCRIPT_DIR}")
        return fetched_count
    except Exception as e:
        logger.error(f"Failed to fetch index: {e}")
        return 0

if __name__ == "__main__":
    fetch_transcripts(limit=15)

import requests
import os
from datetime import datetime, timedelta

# ================= CONFIGURATION =================
# Fetches from GitHub Secrets via Environment Variable
SOURCE_URL = os.getenv("SOURCE_URL")
OUTPUT_FILE = "stream.m3u"
NEW_GROUP = 'group-title="𝐂𝐫𝐢𝐜𝐤𝐞𝐭 | 𝐥𝐢𝐯𝐞"'

def get_ist_time():
    """Generates the current time in IST (UTC+5:30)"""
    ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
    return ist_now.strftime("%dth %b %Y | %I:%M:%S%p")

def is_link_working(url):
    """Checks if a streaming link is active (200 OK)."""
    try:
        # Using a timeout of 5s to keep the Action fast
        response = requests.get(url, timeout=5, stream=True, allow_redirects=True)
        return response.status_code == 200
    except:
        return False

def filter_and_rename(data):
    lines = data.splitlines()
    current_ist = get_ist_time()
    
    filtered_content = [
        "#EXTM3U",
        f"# Last Updated : {current_ist} IST",
        "# Powered By @tvtelugu\n"
    ]
    
    target_groups = {
        'group-title="WPL |Live"': "WPL",
        'group-title="T20 |Live"': "T20"
    }

    for i in range(len(lines)):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            matched_prefix = None
            for key, prefix in target_groups.items():
                if key in line:
                    matched_prefix = prefix
                    break
            
            if matched_prefix:
                link = ""
                for j in range(i + 1, len(lines)):
                    if not lines[j].strip(): continue
                    if lines[j].startswith("#"): break
                    link = lines[j].strip()
                    break
                
                if link and is_link_working(link):
                    parts = line.split(",")
                    original_name = parts[-1]
                    clean_lang = original_name.split("|")[-1].strip()
                    new_channel_name = f"{matched_prefix} | |{clean_lang}"
                    
                    new_info = line
                    for old_group in target_groups.keys():
                        new_info = new_info.replace(old_group, NEW_GROUP)
                    
                    final_info_line = ",".join(parts[:-1]) + "," + new_channel_name
                    filtered_content.append(final_info_line)
                    filtered_content.append(link)
    
    return "\n".join(filtered_content)

def run():
    if not SOURCE_URL:
        print("❌ Error: SOURCE_URL secret not found!")
        return

    print(f"🚀 Update started at {get_ist_time()}")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(SOURCE_URL, headers=headers, timeout=15)
        response.raise_for_status()
        final_m3u = filter_and_rename(response.text)
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(final_m3u)
        print(f"✅ Success! Generated {OUTPUT_FILE}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    run()

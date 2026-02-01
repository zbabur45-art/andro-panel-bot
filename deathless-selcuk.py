import requests
import re
import urllib3
import warnings
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings('ignore')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
TIMEOUT_VAL = 15
PROXY_URL = "https://seep.eu.org/"
OUTPUT_FILENAME = "deathless-selcuk.m3u"
STATIC_LOGO = "https://i.hizliresim.com/8xzjgqv.jpg"
SELCUK_REFERRER = "https://selcuksportshd1903.xyz"

SELCUK_NAMES = {
    "selcukbeinsports1": "beIN Sports 1",
    "selcukbeinsports2": "beIN Sports 2",
    "selcukbeinsports3": "beIN Sports 3",
    "selcukbeinsports4": "beIN Sports 4",
    "selcukbeinsports5": "beIN Sports 5",
    "selcukbeinsportsmax1": "beIN Sports Max 1",
    "selcukbeinsportsmax2": "beIN Sports Max 2",
    "selcukssport": "S Sport 1",
    "selcukssport2": "S Sport 2",
    "selcuksmartspor": "Smart Spor 1",
    "selcuksmartspor2": "Smart Spor 2",
    "selcuktivibuspor1": "Tivibu Spor 1",
    "selcuktivibuspor2": "Tivibu Spor 2",
    "selcuktivibuspor3": "Tivibu Spor 3",
    "selcuktivibuspor4": "Tivibu Spor 4",
    "sssplus1": "S Sport Plus 1",
    "sssplus2": "S Sport Plus 2",
    "selcuktabiispor1": "Tabii Spor 1",
    "selcuktabiispor2": "Tabii Spor 2",
    "selcuktabiispor3": "Tabii Spor 3",
    "selcuktabiispor4": "Tabii Spor 4",
    "selcuktabiispor5": "Tabii Spor 5"
}

def get_selcuk_content():
    results = []
    
    def get_html_proxy(url):
        target_url = PROXY_URL + url
        try:
            r = requests.get(target_url, headers=HEADERS, timeout=TIMEOUT_VAL, verify=False)
            r.raise_for_status()
            return r.text
        except:
            return None

    def get_html_direct(url, referer=None):
        try:
            headers = HEADERS.copy()
            if referer:
                headers["Referer"] = referer
            r = requests.get(url, headers=headers, timeout=TIMEOUT_VAL, verify=False)
            r.raise_for_status()
            return r.text
        except:
            return None

    start_url = "https://www.selcuksportshd.is/"
    html = get_html_proxy(start_url)
    
    if not html:
        return results

    active_domain = ""
    section_match = re.search(r'data-device-mobile[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
    if section_match:
        link_match = re.search(r'href=["\'](https?://[^"\']*selcuksportshd[^"\']+)["\']', section_match.group(1))
        if link_match:
            active_domain = link_match.group(1).strip().rstrip('/')

    if not active_domain:
        return results

    domain_html = get_html_direct(active_domain)
    
    if not domain_html:
        return results

    player_links = re.findall(r'data-url=["\'](https?://[^"\']+?id=[^"\']+?)["\']', domain_html)
    if not player_links:
        player_links = re.findall(r'href=["\'](https?://[^"\']+?index\.php\?id=[^"\']+?)["\']', domain_html)

    base_stream_url = ""
    patterns = [
        r'this\.baseStreamUrl\s*=\s*[\'"](https://[^\'"]+)[\'"]',
        r'const baseStreamUrl\s*=\s*[\'"](https://[^\'"]+)[\'"]',
        r'baseStreamUrl\s*:\s*[\'"](https://[^\'"]+)[\'"]',
        r'streamUrl\s*=\s*[\'"](https://[^\'"]+)[\'"]'
    ]

    for player_url in player_links:
        html_player = get_html_direct(player_url)
        if html_player:
            for pattern in patterns:
                stream_match = re.search(pattern, html_player)
                if stream_match:
                    base_stream_url = stream_match.group(1)
                    if 'live/' in base_stream_url:
                        base_stream_url = base_stream_url.split('live/')[0] + 'live/'
                    break
            if base_stream_url: break

    if base_stream_url:
        if not base_stream_url.endswith('/'): base_stream_url += '/'
        if 'live/' not in base_stream_url: base_stream_url = base_stream_url.rstrip('/') + '/live/'
        
        for cid, name in SELCUK_NAMES.items():
            link = f"{base_stream_url}{cid}/playlist.m3u8"
            entry = f'#EXTINF:-1 tvg-logo="{STATIC_LOGO}" group-title="Selcuk-Panel", {name}\n#EXTVLCOPT:http-referrer={SELCUK_REFERRER}\n{link}'
            results.append(entry)

    return results

def main():
    all_content = ["#EXTM3U"]
    selcuk_lines = get_selcuk_content()
    all_content.extend(selcuk_lines)
    
    try:
        with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
            f.write("\n".join(all_content))
            
        print(f"Dosya oluşturuldu: {OUTPUT_FILENAME}")
        print(f"Kanal sayısı: {len(selcuk_lines)}")
        
    except IOError as e:
        print(f"Hata: {e}")

if __name__ == "__main__":
    main()
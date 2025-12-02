import sys
import requests
import re
import threading
from urllib.parse import urljoin, urlparse
from colorama import Fore, Style, init

init(autoreset=True)

# CẤU HÌNH
TARGET_URL = ""
JS_FILES = []
SECRETS_FOUND = []

def print_banner():
    print(Fore.RED + """
    =======================================================
    SECURITY TOOL V13 - THE JAVASCRIPT MINER
    (Đào mã nguồn Client-side tìm chìa khóa & API ẩn)
    Level: INTELLIGENCE AGENT | Coder: Người anh em
    =======================================================
    """)

# 1. QUÉT TÌM CÁC FILE JS TRÊN TRANG CHỦ
def find_js_files(url):
    print(Fore.CYAN + "[*] Đang quét trang chủ để tìm các file Javascript (.js)...")
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Security-Audit-V13)'}
        res = requests.get(url, headers=headers, timeout=10)
        
        # Regex tìm file .js (thường nằm trong thẻ <script src="...">)
        # Nuxt thường có dạng /_nuxt/....js
        matches = re.findall(r'src=["\'](.*?\.js)["\']', res.text)
        
        for m in matches:
            full_url = urljoin(url, m)
            if full_url not in JS_FILES and domain_in_url(full_url, url):
                JS_FILES.append(full_url)
                print(Fore.WHITE + f"    -> Tìm thấy: {m}")
        
        print(Fore.GREEN + f"[+] Tổng cộng: {len(JS_FILES)} file JS nội bộ cần đào bới.")
        
    except Exception as e:
        print(Fore.RED + f"Lỗi kết nối: {e}")

def domain_in_url(link, base):
    return urlparse(link).netloc == urlparse(base).netloc

# 2. ĐÀO MỎ TÌM TỪ KHÓA NHẠY CẢM (MINING)
def mine_js(js_url):
    try:
        res = requests.get(js_url, timeout=10)
        content = res.text
        
        # DANH SÁCH CÁC MẪU REGEX TÌM "KHO BÁU"
        patterns = {
            "Google API Key": r'AIza[0-9A-Za-z-_]{35}',
            "Firebase URL": r'[a-z0-9.-]+\.firebaseio\.com',
            "AWS API Key": r'AKIA[0-9A-Z]{16}',
            "Private Key (Generic)": r'(?i)(secret|private|token|password|auth_key)[\s]*[:=][\s]*[\'"]([^\'"]+)[\'"]',
            "Admin Path": r'(?i)(\/admin|\/dashboard|\/quan-tri|\/cms)',
            "API Endpoint": r'(?i)(\/api\/v[0-9]\/[a-zA-Z0-9\-_]+)'
        }
        
        for name, pattern in patterns.items():
            matches = re.findall(pattern, content)
            for m in matches:
                # Lọc bớt rác
                val = m if isinstance(m, str) else m[1] # Lấy giá trị nếu là group
                if len(val) < 100: # Bỏ qua nếu quá dài (thường là code html)
                    formatted = f"[{name}]: {val} \n    (Tại: {js_url})"
                    if formatted not in SECRETS_FOUND:
                        SECRETS_FOUND.append(formatted)
                        print(Fore.RED + f"[!] PHÁT HIỆN: {name} -> {val}")

    except:
        pass

def report_findings():
    print(Fore.YELLOW + "\n" + "="*60)
    print(Fore.YELLOW + "   BÁO CÁO KHAI THÁC SOURCE CODE (INTELLIGENCE REPORT)")
    print(Fore.YELLOW + "="*60)
    
    if not SECRETS_FOUND:
        print(Fore.WHITE + "Không tìm thấy API Key hay đường dẫn nhạy cảm nào lộ liễu.")
        print(Fore.WHITE + "Lập trình viên này có vẻ đã ẩn code backend kỹ.")
    else:
        print(Fore.GREEN + f"TÌM THẤY {len(SECRETS_FOUND)} THÔNG TIN NHẠY CẢM:")
        for item in SECRETS_FOUND:
            print(Fore.RED + item)
            
        # Xuất file
        filename = f"LO_KHOA_API_{int(urlparse(TARGET_URL).netloc.replace('.', '_'))}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"BÁO CÁO LỘ THÔNG TIN TRONG SOURCE JS: {TARGET_URL}\n")
            f.write("-" * 50 + "\n")
            for item in SECRETS_FOUND:
                f.write(item + "\n\n")
        print(Fore.GREEN + f"\n[DONE] Đã xuất file bằng chứng: {filename}")
        print(Fore.YELLOW + "Hãy gửi file này cho họ. Hỏi họ: 'Tại sao chìa khóa nhà anh lại vứt ngoài sân?'")

def main():
    global TARGET_URL
    print_banner()
    TARGET_URL = input(Fore.YELLOW + "Nhập URL trang chủ (vd: https://shophaosua.com): ").strip()
    
    # Bước 1: Tìm file
    find_js_files(TARGET_URL)
    
    if not JS_FILES:
        print(Fore.RED + "[-] Không tìm thấy file JS nào. Web có thể render server-side hoàn toàn.")
        return

    # Bước 2: Đào bới đa luồng
    print(Fore.CYAN + "\n[*] Đang đào bới từng dòng code (Multi-threading mining)...")
    threads = []
    for js in JS_FILES:
        t = threading.Thread(target=mine_js, args=(js,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    report_findings()

if __name__ == "__main__":
    main()
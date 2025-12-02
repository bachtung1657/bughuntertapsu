import sys
import requests
import threading
from urllib.parse import urlparse, parse_qs, urlencode
from colorama import Fore, Style, init

init(autoreset=True)

# BIẾN TOÀN CỤC ĐỂ LƯU BÁO CÁO
VULN_REPORT = []

def print_banner():
    print(Fore.GREEN + """
    =======================================================
    SECURITY TOOL V4 - VULNERABILITY ASSESSMENT
    Level: Professional | Coder: Người anh em
    =======================================================
    """)

# HÀM GHI NHẬN LỖI VÀ GIẢI PHÁP
def add_finding(name, severity, description, solution):
    color = Fore.WHITE
    if severity == "HIGH": color = Fore.RED
    elif severity == "MEDIUM": color = Fore.YELLOW
    elif severity == "LOW": color = Fore.CYAN
    
    finding = {
        "name": name,
        "severity": severity,
        "desc": description,
        "fix": solution,
        "color": color
    }
    VULN_REPORT.append(finding)
    print(f"{color}[!] Phát hiện: {name} ({severity})")

# 1. SQL INJECTION HEURISTIC (QUÉT LỖI SQL CƠ BẢN)
def check_sqli(url):
    print(Fore.BLUE + "[*] Đang kiểm tra khả năng lỗi SQL Injection...")
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    if not params:
        print(Fore.WHITE + "   [-] URL không có tham số để test (vd: ?id=1). Bỏ qua.")
        return

    # Các dấu hiệu lỗi SQL thường gặp trong text trả về
    sql_errors = ["You have an error in your SQL syntax", "Warning: mysql_", "unrecognized token", "quoted string not properly terminated"]
    
    for param in params:
        # Tạo URL độc hại: Thêm dấu nháy đơn ' vào tham số
        params_copy = params.copy()
        params_copy[param] = ["1'"] # Ví dụ: id=1 -> id=1'
        new_query = urlencode(params_copy, doseq=True)
        test_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{new_query}"
        
        try:
            res = requests.get(test_url, timeout=3)
            for err in sql_errors:
                if err in res.text:
                    add_finding(
                        name=f"Possible SQL Injection (Param: {param})",
                        severity="HIGH",
                        description=f"Web trả về lỗi SQL khi nhập ký tự ' vào tham số {param}.",
                        solution="Sử dụng 'Prepared Statements' (Tham số hóa) trong code để lọc dữ liệu đầu vào."
                    )
                    return
        except:
            pass
    print(Fore.WHITE + "   [-] Không thấy dấu hiệu lỗi SQL rõ ràng.")

# 2. SENSITIVE FILE HUNTER (SĂN FILE NHẠY CẢM)
def check_sensitive_files(base_url):
    print(Fore.BLUE + "[*] Đang săn tìm các file nhạy cảm bị lộ...")
    files = [
        ".env",              # Chứa mật khẩu database (Cực nguy hiểm)
        ".git/HEAD",         # Lộ source code qua Git
        "wp-config.php.bak", # Backup file cấu hình WordPress
        "backup.zip",        # File nén backup toàn bộ web
        "phpinfo.php"        # Lộ thông tin cấu hình PHP
    ]
    
    for f in files:
        url = f"{base_url}/{f}"
        try:
            res = requests.get(url, timeout=2)
            if res.status_code == 200:
                severity = "HIGH" if ".env" in f or "backup" in f else "MEDIUM"
                add_finding(
                    name=f"Lộ file nhạy cảm: {f}",
                    severity=severity,
                    description=f"Truy cập được file {f} công khai.",
                    solution="Xóa ngay file này hoặc chặn truy cập trong file .htaccess / nginx config."
                )
        except:
            pass

# 3. XSS PROTECTION AUDIT (KIỂM TRA HEADER BẢO MẬT XSS)
def check_xss_headers(headers):
    print(Fore.BLUE + "[*] Đang kiểm tra cơ chế chống XSS...")
    
    # Check CSP (Content Security Policy) - Lá chắn mạnh nhất
    if 'Content-Security-Policy' not in headers:
        add_finding(
            name="Thiếu Header Content-Security-Policy (CSP)",
            severity="MEDIUM",
            description="Web chưa cấu hình CSP để kiểm soát nguồn tải script.",
            solution="Cấu hình CSP để chỉ cho phép chạy script từ các nguồn tin cậy."
        )
    
    # Check X-XSS-Protection (Cũ nhưng vẫn nên có cho trình duyệt cũ)
    if 'X-XSS-Protection' not in headers:
         add_finding(
            name="Thiếu Header X-XSS-Protection",
            severity="LOW",
            description="Thiếu lớp bảo vệ XSS cho trình duyệt cũ.",
            solution="Thêm header: X-XSS-Protection: 1; mode=block"
        )

# 4. CLICKJACKING ANALYSIS
def check_clickjacking(headers):
    print(Fore.BLUE + "[*] Đang kiểm tra lỗi Clickjacking...")
    if 'X-Frame-Options' not in headers and 'Content-Security-Policy' not in headers:
        add_finding(
            name="Nguy cơ Clickjacking",
            severity="MEDIUM",
            description="Web cho phép nhúng vào thẻ iframe. Kẻ xấu có thể làm web giả mạo đè lên.",
            solution="Thêm header 'X-Frame-Options: DENY' hoặc 'SAMEORIGIN'."
        )

# 5. SERVER LEAK INFO
def check_server_leak(headers):
    print(Fore.BLUE + "[*] Kiểm tra lộ thông tin máy chủ...")
    if 'Server' in headers:
        server_info = headers['Server']
        # Nếu server hiện cả phiên bản (vd: Apache/2.4.49) là không tốt
        if any(char.isdigit() for char in server_info): 
             add_finding(
                name="Lộ phiên bản Server",
                severity="LOW",
                description=f"Server đang hiện rõ phiên bản: {server_info}.",
                solution="Cấu hình 'ServerTokens Prod' (Apache) hoặc 'server_tokens off' (Nginx) để ẩn số phiên bản."
            )

# 6. OPEN REDIRECT CHECK (URL)
def check_open_redirect(url):
    print(Fore.BLUE + "[*] Kiểm tra Open Redirect...")
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    dangerous_params = ['url', 'redirect', 'next', 'dest', 'destination', 'go']
    
    found = False
    for p in params:
        if p.lower() in dangerous_params:
            found = True
            add_finding(
                name=f"Tham số URL rủi ro: {p}",
                severity="LOW",
                description=f"Tham số '{p}' thường dùng để chuyển hướng, cần kiểm tra kỹ.",
                solution=f"Kiểm tra xem {url} có tự động chuyển hướng sang trang khác khi đổi giá trị '{p}' không."
            )
            break

# TỔNG HỢP VÀ BÁO CÁO
def generate_report():
    print(Fore.GREEN + "\n" + "="*50)
    print(Fore.GREEN + "   BÁO CÁO ĐÁNH GIÁ BẢO MẬT & GIẢI PHÁP")
    print(Fore.GREEN + "="*50)
    
    if not VULN_REPORT:
        print(Fore.GREEN + "Tuyệt vời! Tool chưa phát hiện lỗ hổng cơ bản nào.")
    else:
        for idx, item in enumerate(VULN_REPORT):
            print(f"\n{Fore.WHITE}#{idx+1}. {item['color']}{item['name']}")
            print(f"   {Fore.WHITE}- Mức độ: {item['color']}{item['severity']}")
            print(f"   {Fore.WHITE}- Mô tả: {item['desc']}")
            print(f"   {Fore.YELLOW}- GIẢI PHÁP KHẮC PHỤC: {item['fix']}")
    
    print("\n")

def main():
    while True:
        print_banner()
        target = input(Fore.YELLOW + "Nhập URL đầy đủ (vd: http://testphp.vulnweb.com/listproducts.php?cat=1): ").strip()
        
        if not target.startswith("http"):
            print(Fore.RED + "Vui lòng nhập đầy đủ http:// hoặc https://")
            continue
        
        # Reset báo cáo cũ
        VULN_REPORT.clear()
        
        # Lấy thông tin cơ bản để scan
        try:
            res = requests.get(target, timeout=5)
            headers = res.headers
            parsed = urlparse(target)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            
            # --- CHẠY CÁC SKILL ---
            check_sqli(target)
            check_sensitive_files(base_url)
            check_xss_headers(headers)
            check_clickjacking(headers)
            check_server_leak(headers)
            check_open_redirect(target)
            
            # --- XUẤT BÁO CÁO ---
            generate_report()
            
        except Exception as e:
            print(Fore.RED + f"Lỗi kết nối tới mục tiêu: {e}")

        choice = input("Nhấn Enter để tiếp tục hoặc '0' để thoát: ")
        if choice == '0': break

if __name__ == "__main__":
    main()
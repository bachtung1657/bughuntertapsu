import sys
import requests
import os
from urllib.parse import urlparse
from colorama import Fore, Style, init

init(autoreset=True)

# BIẾN LƯU BÁO CÁO
REPORT_CONTENT = []

def print_banner():
    print(Fore.GREEN + """
    =======================================================
    SECURITY TOOL V5 - WHITE HAT REMEDIATOR
    (Khai thác giả lập & Tạo code vá lỗi tự động)
    Level: Professional Consultant | Coder: Người anh em
    =======================================================
    """)

# HÀM THÊM VÀO BÁO CÁO
def add_to_report(title, level, poc, remediation_code):
    entry = f"""
{'='*60}
LỖI BẢO MẬT: {title}
MỨC ĐỘ: {level}
{'='*60}

1. BẰNG CHỨNG KHAI THÁC (Proof of Concept):
{poc}

2. GIẢI PHÁP KHẮC PHỤC (CODE MẪU CHO LẬP TRÌNH VIÊN):
{remediation_code}
    """
    REPORT_CONTENT.append(entry)
    print(Fore.RED + f"[!] Đã xác nhận lỗi: {title}")
    print(Fore.GREEN + f"    -> Đã tạo code vá lỗi xong.")

# 1. SQL INJECTION (VÁ LỖI DATABASE)
def fix_sqli(url):
    print(Fore.CYAN + "\n[*] Đang kiểm tra & tạo bản vá SQL Injection...")
    # Giả lập tấn công
    test_url = url + "'"
    try:
        res = requests.get(test_url, timeout=3)
        if "SQL" in res.text or "syntax" in res.text:
            poc = f"Truy cập đường dẫn: {test_url}\nServer trả về lỗi cú pháp SQL -> Chứng tỏ dữ liệu đầu vào không được lọc."
            
            fix_code = """
[Dành cho PHP - Sử dụng PDO Prepared Statements]
------------------------------------------------
// Code CŨ (Lỗi):
// $sql = "SELECT * FROM users WHERE id = " . $_GET['id'];

// Code MỚI (An toàn):
$stmt = $pdo->prepare('SELECT * FROM users WHERE id = :id');
$stmt->execute(['id' => $_GET['id']]);
$user = $stmt->fetch();
------------------------------------------------
Lý do: Prepared Statements tách biệt câu lệnh SQL và dữ liệu, hacker không thể chèn mã độc.
            """
            add_to_report("SQL Injection", "CAO (HIGH)", poc, fix_code)
        else:
            print(Fore.WHITE + "[-] Không tìm thấy lỗi SQL rõ ràng.")
    except:
        pass

# 2. SENSITIVE FILES (CHẶN TRUY CẬP FILE ẨN)
def fix_sensitive_files(base_url):
    print(Fore.CYAN + "\n[*] Đang tạo luật chặn file nhạy cảm (.env, .git)...")
    files = ['.env', '.git/HEAD']
    found = False
    for f in files:
        if requests.get(f"{base_url}/{f}").status_code == 200:
            found = True
            poc = f"Truy cập công khai được: {base_url}/{f}"
            
            fix_code = """
[Dành cho NGINX (nginx.conf)]
-----------------------------
location ~ /\.(env|git|svn) {
    deny all;
    return 403;
}

[Dành cho APACHE (.htaccess)]
-----------------------------
<FilesMatch "^\.(env|git|svn)">
    Order allow,deny
    Deny from all
</FilesMatch>
            """
            add_to_report(f"Lộ file nhạy cảm {f}", "CAO (HIGH)", poc, fix_code)
            break # Chỉ cần tìm thấy 1 cái là báo cáo chung
    if not found: print(Fore.WHITE + "[-] Không lộ file nhạy cảm.")

# 3. CLICKJACKING (FIX BẰNG HEADER)
def fix_clickjacking(headers):
    print(Fore.CYAN + "\n[*] Đang tạo cấu hình chống Clickjacking...")
    if 'X-Frame-Options' not in headers:
        poc = "Header 'X-Frame-Options' bị thiếu. Trang web có thể bị nhúng vào thẻ <iframe> của web xấu."
        
        fix_code = """
[Dành cho NGINX]
----------------
add_header X-Frame-Options "SAMEORIGIN";

[Dành cho APACHE]
-----------------
Header always set X-Frame-Options "SAMEORIGIN"

[Dành cho PHP]
--------------
header('X-Frame-Options: SAMEORIGIN');
        """
        add_to_report("Missing Clickjacking Protection", "TRUNG BÌNH (MEDIUM)", poc, fix_code)
    else:
        print(Fore.WHITE + "[-] Đã có bảo vệ Clickjacking.")

# 4. SERVER LEAK (ẨN THÔNG TIN SERVER)
def fix_server_leak(headers):
    print(Fore.CYAN + "\n[*] Đang tạo cấu hình ẩn thông tin Server...")
    if 'Server' in headers and any(char.isdigit() for char in headers['Server']):
        poc = f"Server trả về header: {headers['Server']}. Kẻ tấn công biết chính xác phiên bản để tìm lỗi CVE."
        
        fix_code = """
[Dành cho NGINX]
----------------
server_tokens off;

[Dành cho APACHE]
-----------------
ServerTokens Prod
ServerSignature Off
        """
        add_to_report("Information Disclosure (Server Version)", "THẤP (LOW)", poc, fix_code)
    else:
        print(Fore.WHITE + "[-] Thông tin server đã được ẩn.")

# 5. COOKIE SECURITY (BẢO MẬT COOKIE)
def fix_cookie(url):
    print(Fore.CYAN + "\n[*] Đang kiểm tra cờ bảo mật Cookie...")
    res = requests.get(url)
    if res.cookies:
        for cookie in res.cookies:
            if not cookie.secure or not cookie.has_nonstandard_attr('HttpOnly'):
                poc = f"Cookie '{cookie.name}' thiếu cờ Secure hoặc HttpOnly. Javascript có thể đọc được cookie này."
                
                fix_code = """
[Dành cho PHP (php.ini hoặc code)]
----------------------------------
session.cookie_httponly = 1
session.cookie_secure = 1

// Hoặc set trong code:
setcookie("session_id", "xyz", [
    'expires' => time() + 3600,
    'path' => '/',
    'domain' => 'domain.com',
    'secure' => true,     // Chỉ gửi qua HTTPS
    'httponly' => true,   // JS không đọc được
    'samesite' => 'Strict'
]);
                """
                add_to_report("Insecure Cookie Settings", "TRUNG BÌNH (MEDIUM)", poc, fix_code)
                return # Báo 1 lần là đủ
    print(Fore.WHITE + "[-] Cookie có vẻ ổn hoặc không có cookie.")

# 6. OPEN REDIRECT (FIX URL CHUYỂN HƯỚNG)
def fix_open_redirect(url):
    print(Fore.CYAN + "\n[*] Đang tạo code lọc URL chuyển hướng...")
    parsed = urlparse(url)
    if "redirect=" in url or "url=" in url:
        poc = f"URL chứa tham số chuyển hướng. Thử thay đổi thành: {url.split('?')[0]}?redirect=http://evil.com"
        
        fix_code = """
[Dành cho PHP - Whitelist Domains]
----------------------------------
$redirect_url = $_GET['redirect'];
$allowed_domains = ['mysite.com', 'google.com'];

$parsed = parse_url($redirect_url);
if (in_array($parsed['host'], $allowed_domains)) {
    header("Location: " + $redirect_url);
} else {
    echo "Chuyển hướng không an toàn!";
}
        """
        add_to_report("Open Redirect", "TRUNG BÌNH (MEDIUM)", poc, fix_code)
    else:
        print(Fore.WHITE + "[-] Không phát hiện tham số chuyển hướng rõ ràng.")

# XUẤT FILE BÁO CÁO
def save_report_file(domain):
    filename = f"baocao_{domain}.txt"
    if not REPORT_CONTENT:
        print(Fore.YELLOW + "\n[!] Không tìm thấy lỗi nào để viết báo cáo. Web này khá an toàn!")
        return

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"BÁO CÁO BẢO MẬT WEBSITE: {domain}\n")
        f.write(f"Ngày quét: {os.path.basename(sys.argv[0])}\n")
        f.write("Người thực hiện: Security Researcher (White Hat)\n")
        f.write("-" * 50 + "\n")
        
        for content in REPORT_CONTENT:
            f.write(content + "\n")
            
    print(Fore.GREEN + f"\n[SUCCESS] Đã xuất file báo cáo: {filename}")
    print(Fore.GREEN + "Hãy mở file này lên, chỉnh sửa và gửi cho khách hàng/chủ web.")

def main():
    print_banner()
    target = input(Fore.YELLOW + "Nhập URL mục tiêu (vd: http://testphp.vulnweb.com/listproducts.php?cat=1): ").strip()
    
    if not target.startswith("http"):
        print(Fore.RED + "Vui lòng nhập http:// hoặc https://")
        return

    domain = urlparse(target).netloc
    
    # Chạy các module fix lỗi
    fix_sqli(target)
    fix_sensitive_files(f"{urlparse(target).scheme}://{domain}")
    
    # Lấy header để check
    try:
        res = requests.get(target, timeout=5)
        fix_clickjacking(res.headers)
        fix_server_leak(res.headers)
        fix_cookie(target)
        fix_open_redirect(target)
        
        # Lưu báo cáo
        save_report_file(domain)
        
    except Exception as e:
        print(Fore.RED + f"Lỗi kết nối: {e}")

if __name__ == "__main__":
    main()
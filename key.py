import socket
import sqlite3
import sys
from tqdm import tqdm

# Common ports to scan
COMMON_PORTS = [80, 21, 22, 5900, 2222, 2200, 22222, 2375, 2376, 5000, 5001, 6666, 6667, 6668, 10250, 6379, 9000, 9001]

# Fetch banners using socket from common ports
def fetch_banners(ip_addresses):
    banners = {}

    for ip in tqdm(ip_addresses, desc="Scanning IPs"):
        try:
            for port in COMMON_PORTS:
                banner = fetch_banner_socket(ip, port)
                if banner:
                    banners.setdefault(ip, []).append((port, banner))
        except Exception as e:
            print(f"Error fetching banners for {ip}: {e}")

    return banners

# Fetch banner from a specific port using socket
def fetch_banner_socket(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            s.connect((ip, port))
            
            if port == 80:  # HTTP on port 80
                request = "GET / HTTP/1.0\r\nHost: {}\r\n\r\n".format(ip)
            elif port == 21:  # FTP on port 21
                request = "USER anonymous\r\n"
            elif port == 22:  # SSH on port 22
                request = "\r\n"  # SSH doesn't require an initial request
            elif port == 5900:  # VNC on port 5900
                request = "RFB 003.003\n"
            elif port in [2222, 2200, 22222]:  # SSH on various ports
                request = "\r\n"
            elif port in [2375, 2376]:  # Docker API on ports 2375 and 2376
                request = "GET /info HTTP/1.0\r\nHost: {}\r\n\r\n".format(ip)
            elif port in [5000, 5001]:  # Common web ports
                request = "GET / HTTP/1.0\r\nHost: {}\r\n\r\n".format(ip)
            elif port in [6666, 6667, 6668]:  # IRC on ports 6666-6668
                request = "NICK test\r\n"
            elif port == 10250:  # Kubernetes API on port 10250
                request = "GET /healthz HTTP/1.0\r\nHost: {}\r\n\r\n".format(ip)
            elif port == 6379:  # Redis on port 6379
                request = "INFO\r\n"
            elif port in [9000, 9001]:  # Common ports
                request = "\r\n"  # Empty request as default
            else:
                request = "\r\n"  # Default: an empty request
            
            s.sendall(request.encode())
            
            banner = s.recv(4096).decode("utf-8", errors="ignore")
            return banner
    except Exception:
        return None

# Read IP addresses from the output file
def read_ip_addresses(file_name):
    with open(file_name, 'r') as file:
        ip_addresses = file.read().splitlines()
    return ip_addresses

# Create or connect to SQLite3 database
def create_database(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS banners
                     (ip_address TEXT, port INTEGER, banner TEXT, PRIMARY KEY (ip_address, port))''')
    conn.commit()
    return conn, cursor

# Store banners in the database
def store_banners(conn, cursor, banners):
    for ip, port_banner_list in banners.items():
        for port, banner in port_banner_list:
            cursor.execute('INSERT OR REPLACE INTO banners (ip_address, port, banner) VALUES (?, ?, ?)',
                           (ip, port, banner))
    conn.commit()

def main():
    if len(sys.argv) != 2:
        print("Usage: python key.py <input_file>")
        return

    input_file = sys.argv[1]
    db_name = "banners.db"

    ip_list = read_ip_addresses(input_file)
    banners = fetch_banners(ip_list)

    conn, cursor = create_database(db_name)
    store_banners(conn, cursor, banners)

    conn.close()

if __name__ == "__main__":
    main()

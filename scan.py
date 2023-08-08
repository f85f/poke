import os
import sqlite3
import socket

def create_database(provider, port):
    conn = sqlite3.connect(f"{provider}_{port}.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scanned_ips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT,
            ip TEXT,
            banner TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_ip_banner(provider, port, ip, banner):
    conn = sqlite3.connect(f"{provider}_{port}.db")
    cursor = conn.cursor()
    cursor.execute('INSERT INTO scanned_ips (provider, ip, banner) VALUES (?, ?, ?)', (provider, ip, banner))
    conn.commit()
    conn.close()

def grab_banner(ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((ip, int(port)))
            banner = s.recv(1024).decode("utf-8").strip()
            return banner
    except (socket.timeout, ConnectionRefusedError, OSError, UnicodeDecodeError):
        return None

# User input for provider and port
provider = input("Provider (GCP, AWS, Azure): ").lower()
port = input("Port: ")

# Determine the text file based on provider and port
ip_file_path = f"{provider}{port}"

# Read IPs from the determined text file
with open(ip_file_path, "r") as ip_file:
    ip_list = ip_file.read().splitlines()

# Create the database
create_database(provider, port)

# Scan IPs and collect banners, then store in the database
for ip in ip_list:
    banner = grab_banner(ip, port)
    if banner:
        insert_ip_banner(provider, port, ip, banner)
        print(f"Scanned IP: {ip}, Banner: {banner}")
    else:
        print(f"Scanned IP: {ip}, No banner found or decoding error.")

print("Scanning and storing completed.")

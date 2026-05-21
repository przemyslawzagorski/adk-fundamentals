"""
TCP proxy: 127.0.0.1:LOCAL_PORT -> WSL_IP:REMOTE_PORT
No admin rights required. Usage: python _wsl_proxy.py [local_port] [remote_port]
"""
import socket, threading, subprocess, sys, time

LOCAL_PORT  = int(sys.argv[1]) if len(sys.argv) > 1 else 8770
REMOTE_PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8770

def get_wsl_ip():
    r = subprocess.run(
        ["wsl", "--", "bash", "-c", "hostname -I"],
        capture_output=True, text=True, timeout=5
    )
    return r.stdout.strip().split()[0]

def pipe(src, dst):
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except Exception:
        pass
    finally:
        try: src.close()
        except Exception: pass
        try: dst.close()
        except Exception: pass

def handle(client):
    try:
        wsl_ip = get_wsl_ip()
        server = socket.create_connection((wsl_ip, REMOTE_PORT), timeout=5)
        threading.Thread(target=pipe, args=(client, server), daemon=True).start()
        threading.Thread(target=pipe, args=(server, client), daemon=True).start()
    except Exception as e:
        print(f"[proxy] connect error: {e}")
        client.close()

srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.bind(("127.0.0.1", LOCAL_PORT))
srv.listen(32)
wsl_ip = get_wsl_ip()
print(f"[proxy] 127.0.0.1:{LOCAL_PORT} -> {wsl_ip}:{REMOTE_PORT}  (Ctrl+C to stop)", flush=True)

while True:
    try:
        client, addr = srv.accept()
        threading.Thread(target=handle, args=(client,), daemon=True).start()
    except KeyboardInterrupt:
        print("[proxy] stopped")
        break

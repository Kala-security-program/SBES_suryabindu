# ============================================================
# SURYABINDU ENCRYPTION SYSTEM v2.1
# Fixed + Stable + Hacker Terminal UI
# ============================================================

import os
import sys
import json
import base64
import hashlib
import time
import datetime
import pytz

from colorama import Fore, init
from astral import LocationInfo
from astral.sun import azimuth, elevation

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet, InvalidToken

init(autoreset=True)

# ============================================================
# CONFIG
# ============================================================
CITY = LocationInfo("Hyderabad", "India", "Asia/Kolkata", 17.3850, 78.4867)
TZ = pytz.timezone("Asia/Kolkata")

# ============================================================
# UI
# ============================================================
def clear():
    os.system("clear")

def slow(text, color=Fore.GREEN):
    for c in text:
        print(color + c, end="", flush=True)
        time.sleep(0.002)
    print()

def banner():
    print(Fore.GREEN + r"""
   ███████╗██╗   ██╗██████╗ ██╗   ██╗ █████╗ ██████╗ ██╗███╗   ██╗
   ██╔════╝██║   ██║██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗██║████╗  ██║
   ███████╗██║   ██║██████╔╝ ╚████╔╝ ███████║██████╔╝██║██╔██╗ ██║
   ╚════██║██║   ██║██╔══██╗  ╚██╔╝  ██╔══██║██╔══██╗██║██║╚██╗██║
   ███████║╚██████╔╝██║  ██║   ██║   ██║  ██║██║  ██║██║██║ ╚████║
   ╚══════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝
    """)

def header():
    clear()
    banner()
    print(Fore.GREEN + "=" * 65)
    print(Fore.GREEN + f"root@suryabindu:~# ONLINE")
    print(Fore.GREEN + f"TIME: {datetime.datetime.now(TZ)}")
    print(Fore.GREEN + "=" * 65)

def scan():
    for i in range(0, 101, 10):
        print(Fore.CYAN + f"[{'#'*(i//10):<10}] {i}%")
        time.sleep(0.04)

# ============================================================
# SOLAR SYSTEM
# ============================================================
def get_solar():
    now = datetime.datetime.now(TZ)
    obs = CITY.observer
    return round(float(azimuth(obs, now)), 6), round(float(elevation(obs, now)), 6)

def solar63(theta, phi):
    raw = f"{theta}:{phi}:SURYABINDU:V2"
    return hashlib.sha256(raw.encode()).hexdigest().upper()[:63]

# ============================================================
# KEY
# ============================================================
def derive(password, salt, skey):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt + skey.encode(),
        iterations=200000,
        backend=default_backend()
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))

# ============================================================
# ENCRYPT
# ============================================================
def encrypt():
    header()
    print(Fore.YELLOW + "[ ENCRYPT MODE ]\n")

    path = input("file> ").strip()
    pwd = input("password> ").strip()

    if not os.path.exists(path):
        print(Fore.RED + "[!] File not found")
        input("Enter...")
        return

    try:
        with open(path, "rb") as f:
            data = f.read()

        slow("[*] Generating solar coordinates...", Fore.CYAN)
        t, p = get_solar()

        slow(f"    Theta: {t}")
        slow(f"    Phi  : {p}")

        skey = solar63(t, p)
        salt = os.urandom(16)

        slow("[*] Deriving secure key...", Fore.CYAN)
        key = derive(pwd, salt, skey)

        cipher = Fernet(key)

        slow("[*] Encrypting data...", Fore.CYAN)
        scan()

        enc = cipher.encrypt(data)

        packet = {
            "theta": t,
            "phi": p,
            "solar63": skey,
            "salt": base64.b64encode(salt).decode(),
            "payload": enc.decode()
        }

        out = path + ".sbes"

        with open(out, "wb") as f:
            f.write(base64.b64encode(json.dumps(packet).encode()))

        print(Fore.GREEN + f"\n[+] SUCCESS -> {out}")

    except Exception as e:
        print(Fore.RED + f"[!] Error: {e}")

    input("\nPress Enter...")

# ============================================================
# DECRYPT
# ============================================================
def decrypt():
    header()
    print(Fore.YELLOW + "[ DECRYPT MODE ]\n")

    path = input("encrypted_file> ").strip()
    pwd = input("password> ").strip()

    if not os.path.exists(path):
        print(Fore.RED + "[!] File not found")
        input("Enter...")
        return

    try:
        with open(path, "rb") as f:
            blob = f.read()

        slow("[*] Reading encrypted container...", Fore.CYAN)

        packet = json.loads(base64.b64decode(blob).decode())

        salt = base64.b64decode(packet["salt"])
        skey = packet["solar63"]

        slow("[*] Reconstructing key...", Fore.CYAN)

        key = derive(pwd, salt, skey)
        cipher = Fernet(key)

        slow("[*] Decrypting...", Fore.CYAN)
        scan()

        data = cipher.decrypt(packet["payload"].encode())

        out = path.replace(".sbes", ".dec")

        with open(out, "wb") as f:
            f.write(data)

        print(Fore.GREEN + f"\n[+] SUCCESS -> {out}")

    except InvalidToken:
        print(Fore.RED + "[!] Wrong password or corrupted file")

    except Exception as e:
        print(Fore.RED + f"[!] Error: {e}")

    input("\nPress Enter...")

# ============================================================
# MAIN LOOP
# ============================================================
def main():
    while True:
        header()

        print(Fore.YELLOW + "[1] Encrypt File")
        print(Fore.YELLOW + "[2] Decrypt File")
        print(Fore.YELLOW + "[3] Exit\n")

        cmd = input(Fore.GREEN + "root@suryabindu:~# ").strip()

        if cmd == "1":
            encrypt()
        elif cmd == "2":
            decrypt()
        elif cmd == "3":
            print("Shutting down...")
            sys.exit()
        else:
            print(Fore.RED + "Invalid option")
            time.sleep(1)

# ============================================================
# START
# ============================================================
if __name__ == "__main__":
    main()

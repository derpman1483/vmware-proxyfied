import os
import subprocess
import time
import re

# --- 1. ENVIRONMENT SETUP ---
os.environ['USER'] = 'root'
os.environ['HOME'] = '/root'
os.environ['WINEARCH'] = 'win64'
os.environ['DISPLAY'] = ':1'

print("🧹 Deep Cleaning old session...")
os.system("pkill -9 vncserver || pkill -9 Xvnc")
os.system("pkill -9 websockify")
os.system("pkill -9 cloudflared")
os.system("rm -rf /tmp/.X1-lock /tmp/.X11-unix/X1 /root/.vnc/*.log /root/.vnc/*.pid")

# --- 2. INSTALL WINE & WINETRICKS ---
print("📦 Installing Wine and Winetricks (Takes ~3 mins)...")
os.system("dpkg --add-architecture i386")
os.system("apt update > /dev/null")
os.system("apt install -y xfce4 xfce4-goodies tightvncserver websockify novnc brave-browser \
          wine64 wine32 winbind winetricks cabextract > /dev/null")

# --- 3. START VNC (Required for Winetricks to run) ---
print("🖥️ Starting VNC Server...")
vnc_dir = os.path.expanduser("~/.vnc")
os.makedirs(vnc_dir, exist_ok=True)
with open(f"{vnc_dir}/xstartup", "w") as f:
    f.write("#!/bin/sh\nstartxfce4 &\n")
os.chmod(f"{vnc_dir}/xstartup", 0o755)
os.system(f"echo 'colab123' | vncpasswd -f > {vnc_dir}/passwd")
os.chmod(f"{vnc_dir}/passwd", 0o600)
os.system("vncserver :1 -geometry 1280x720 -depth 24")

# --- 4. FIX MISSING WINDOWS LIBRARIES (The Fix) ---
print("🔧 Installing Microsoft Common Controls & C++ (This takes time, wait for completion)...")
# We install comctl32 (Common Controls) and vcrun (Visual C++)
# 'silent' mode -q is used to prevent EULA popups
os.system("winetricks -q comctl32 vcrun2015")

# --- 5. SETUP DESKTOP ---
os.makedirs("/root/Desktop", exist_ok=True)
with open("/root/Desktop/Brave.sh", "w") as f:
    f.write("#!/bin/bash\nbrave-browser --no-sandbox --user-data-dir=/root/.config/brave &\n")
os.chmod("/root/Desktop/Brave.sh", 0o755)

# Download Roblox Installer
os.system("wget -O /root/Desktop/RobloxPlayerLauncher.exe https://www.roblox.com/download/client?os=win")

# --- 6. START TUNNEL ---
print("☁️ Requesting Cloudflare Tunnel...")
if not os.path.exists("cloudflared-linux-amd64.deb"):
    os.system("wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb")
    os.system("dpkg -i cloudflared-linux-amd64.deb")

subprocess.Popen(["websockify", "--web", "/usr/share/novnc/", "6080", "localhost:5901"], stdout=subprocess.DEVNULL)
process = subprocess.Popen(["cloudflared", "tunnel", "--url", "http://127.0.0.1:6080"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

for line in process.stdout:
    if "trycloudflare.com" in line:
        match = re.search(r"https://[a-zA-Z0-9.-]+\.trycloudflare\.com", line)
        if match:
            url = match.group(0)
            print("\n" + "═"*60)
            print("🚀 VM LIVE - COMMON CONTROLS INSTALLED")
            print(f"🔗 URL: {url}/vnc.html?autoconnect=true")
            print("🔑 PASSWORD: colab123")
            print("═"*60)
            break
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("Stopped.")

import os
import subprocess
import time
import re

# --- 1. ENVIRONMENT SETUP ---
os.environ['USER'] = 'root'
os.environ['HOME'] = '/root'
os.environ['WINEARCH'] = 'win64'
os.environ['DISPLAY'] = ':1'

print("🧹 Deep Cleaning...")
os.system("pkill -9 vncserver || pkill -9 Xvnc")
os.system("pkill -9 websockify")
os.system("pkill -9 cloudflared")
os.system("rm -rf /tmp/.X1-lock /tmp/.X11-unix/X1 /root/.vnc/*.log /root/.vnc/*.pid /root/.wine")

# --- 2. INSTALL CRITICAL LIBRARIES (The "Integer" Fix) ---
print("📦 Installing Wine, Winbind, and Graphics Libraries...")
os.system("dpkg --add-architecture i386")
os.system("apt update > /dev/null")

# Brave Repo
os.system("curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg")
os.system("echo 'deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main' | tee /etc/apt/sources.list.d/brave-browser-release.list")

# Install Wine, Winbind (fixes range errors), and Vulkan/OpenGL
os.system("apt install -y xfce4 xfce4-goodies tightvncserver websockify novnc brave-browser \
          wine64 wine32 winbind libvulkan1 libvulkan1:i386 libgnutls30:i386 > /dev/null")

# --- 3. CONFIGURE VNC & DESKTOP ---
print("🖥️ Starting VNC Server...")
vnc_dir = os.path.expanduser("~/.vnc")
os.makedirs(vnc_dir, exist_ok=True)
with open(f"{vnc_dir}/xstartup", "w") as f:
    f.write("#!/bin/sh\nunset SESSION_MANAGER\nunset DBUS_SESSION_BUS_ADDRESS\nstartxfce4 &\n")
os.chmod(f"{vnc_dir}/xstartup", 0o755)
os.system(f"echo 'colab123' | vncpasswd -f > {vnc_dir}/passwd")
os.chmod(f"{vnc_dir}/passwd", 0o600)

# Start VNC with 24-bit depth to avoid integer math errors in Wine
os.system("vncserver :1 -geometry 1280x720 -depth 24")

# Brave Shortcut
os.makedirs("/root/Desktop", exist_ok=True)
with open("/root/Desktop/Brave.sh", "w") as f:
    f.write("#!/bin/bash\nbrave-browser --no-sandbox --user-data-dir=/root/.config/brave &\n")
os.chmod("/root/Desktop/Brave.sh", 0o755)

# Download Roblox
os.system("wget -O /root/Desktop/RobloxPlayerLauncher.exe https://www.roblox.com/download/client?os=win")

# --- 4. INITIALIZE WINE AS WINDOWS 10 ---
print("🍷 Setting up Wine (Windows 10 mode)...")
# This command tells Wine to act like Windows 10 without opening a GUI
os.system('wine reg add "HKEY_CURRENT_USER\\Software\\Wine" /v Version /t REG_SZ /d "win10" /f > /dev/null 2>&1')

# --- 5. START TUNNEL ---
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
            print("🚀 VM LIVE - INTEGER ERROR FIXED")
            print(f"🔗 URL: {url}/vnc.html?autoconnect=true")
            print("🔑 PASSWORD: colab123")
            print("═"*60)
            break
try:
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("Stopped.")

# Use the official Jupyter base image
FROM jupyter/base-notebook:ubuntu-22.04

USER root

# 1. Fix Architecture and Repositories
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y curl wget gpg sudo && \
    # Add WineHQ Repo
    mkdir -pm 755 /etc/apt/keyrings && \
    wget -nc -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key && \
    wget -nc -P /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/jammy/winehq-jammy.sources && \
    # Add Brave Repo
    curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg && \
    echo "deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main" | tee /etc/apt/sources.list.d/brave-browser-release.list

# 2. Install Desktop Environment, Wine 9.0, and Brave
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
    xfce4 xfce4-goodies \
    tigervnc-standalone-server \
    winehq-stable \
    winbind \
    winetricks \
    brave-browser \
    libvulkan1 libvulkan1:i386 \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libgbm1 \
    dbus-x11 x11-xserver-utils \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 3. Setup User (Binder uses 'jovyan')
ENV USER jovyan
ENV HOME /home/jovyan
WORKDIR /home/jovyan

# 4. Pre-download Roblox Installer so it is ready
RUN mkdir -p /home/jovyan/Desktop && \
    wget -O /home/jovyan/Desktop/RobloxPlayerLauncher.exe https://www.roblox.com/download/client?os=win && \
    chown -R jovyan:users /home/jovyan/Desktop

# 5. Create Brave bypass script (Root not needed in Binder, but sandbox fix is helpful)
RUN echo '#!/bin/bash\nbrave-browser --no-sandbox --user-data-dir=$HOME/.config/brave &' > /home/jovyan/Desktop/Brave.sh && \
    chmod +x /home/jovyan/Desktop/Brave.sh

# Switch back to the default user
USER jovyan

# 6. Pre-initialize Wine (Fixes 'Integer range' and 'Common Controls' during build)
# Using xvfb-run to trick Wine into thinking a screen is active during build
RUN xvfb-run -a winetricks -q comctl32 vcrun2015

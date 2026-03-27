#!/usr/bin/env python3
"""
Utility Functions Module
"""

import subprocess
import os
import socket
from colorama import Fore, Style

def check_root():
    """Check if running as root"""
    if os.geteuid() != 0:
        print(f"{Fore.RED}[!] This tool requires root privileges!{Fore.WHITE}")
        return False
    return True

def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def check_tool(tool):
    """Check if tool is installed"""
    try:
        subprocess.run(["which", tool], capture_output=True, check=True)
        return True
    except:
        return False

def install_tool(tool):
    """Install required tool"""
    print(f"{Fore.YELLOW}[+] Installing {tool}...{Fore.WHITE}")
    subprocess.run(["sudo", "apt", "install", "-y", tool], capture_output=True)

def create_directory(path):
    """Create directory if not exists"""
    if not os.path.exists(path):
        os.makedirs(path)

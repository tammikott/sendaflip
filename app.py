import os
import random
import subprocess
import sys
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# KRITIILISED FAILID
CRITICAL_FILES = {
    "linux_kernel": [
        "/boot/vmlinuz",
        "/boot/initrd.img",
        "/boot/grub/grub.cfg",
    ],
    "system_binaries": [
        "/bin/bash",
        "/bin/sh",
        "/usr/bin/sudo",
    ],
    "system_configs": [
        "/etc/passwd",
        "/etc/shadow",
        "/etc/fstab",
    ]
}

class SystemDestroyer:
    def __init__(self):
        self.destruction_log = "system_destruction.log"
        self.os_type = self.detect_os()
        
    def detect_os(self):
        if sys.platform == "linux":
            return "linux"
        return "unknown"
    
    def delete_with_sudo(self, file_path):
        """Kustuta fail sudo'ga - see TÖÖTAB!"""
        try:
            # 1. Esmalt backup (kui saab)
            backup_cmd = f"sudo cp '{file_path}' '{file_path}.sendaflip_backup' 2>/dev/null || true"
            subprocess.run(backup_cmd, shell=True, timeout=2)
            
            # 2. Kustuta sudo'ga
            delete_cmd = f"sudo rm -f '{file_path}'"
            print(f"🔥 Running sudo command: {delete_cmd}")
            
            result = subprocess.run(
                delete_cmd, 
                shell=True, 
                capture_output=True, 
                text=True,
                timeout=5
            )
            
            # 3. Kontrolli, kas fail on kadunud
            if result.returncode == 0:
                # Veendu, et fail on tõesti kadunud
                import time
                time.sleep(0.5)
                
                if not os.path.exists(file_path):
                    return {
                        "success": True,
                        "message": f"💥💥💥 DELETED WITH SUDO: {file_path}",
                        "command": delete_cmd
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Command succeeded but file still exists: {file_path}"
                    }
            else:
                # 4. Kui sudo ei tööta, proovi otsese käsuga
                print(f"⚠️ Sudo failed, trying direct...")
                direct_cmd = f"rm -f '{file_path}'"
                subprocess.run(direct_cmd, shell=True)
                
                if not os.path.exists(file_path):
                    return {
                        "success": True, 
                        "message": f"💥 DELETED (direct): {file_path}"
                    }
                else:
                    return {
                        "success": False,
                        "message": f"Failed: {result.stderr}"
                    }
                    
        except subprocess.TimeoutExpired:
            return {"success": False, "message": "Timeout"}
        except Exception as e:
            return {"success": False, "message": f"Error: {str(e)}"}
    
    def find_deletable_file(self):
        """Leia kustutatav fail"""
        # Proovi kõigepealt kõige tähtsamaid
        priority_targets = [
            "/boot/vmlinuz",
            "/boot/initrd.img", 
            "/etc/passwd",
            "/bin/bash",
            "/usr/bin/sudo"
        ]
        
        for target in priority_targets:
            if os.path.exists(target):
                return target
        
        # Kui prioriteetsed puuduvad, proovi muid
        for category, files in CRITICAL_FILES.items():
            for file_path in files:
                if os.path.exists(file_path):
                    return file_path
        
        # Viimase võimalusena /tmp fail
        tmp_file = "/tmp/sendaflip_critical.txt"
        with open(tmp_file, "w") as f:
            f.write("Demo fail\n")
        return tmp_file
    
    def simulate_crash(self):
        """Simuleeri süsteemi kokkuvarisemist"""
        effects = []
        
        # Kernel panic log
        with open("/tmp/kernel_panic.log", "w") as f:
            f.write("KERNEL PANIC - Critical file deleted\n")
        effects.append("Created panic log")
        
        # Reboot timer
        reboot_script = "/tmp/sendaflip_reboot.sh"
        with open(reboot_script, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("sleep 60\n")
            f.write('echo "System rebooting due to file deletion..."\n')
            f.write("sudo reboot\n")
        os.chmod(reboot_script, 0o755)
        subprocess.Popen([reboot_script], stdout=subprocess.DEVNULL)
        effects.append("Scheduled reboot")
        
        return effects

@app.route('/')
def index():
    destroyer = SystemDestroyer()
    
    # Näita haavatavaid faile
    vulnerable = []
    for files in CRITICAL_FILES.values():
        for f in files:
            if os.path.exists(f):
                vulnerable.append(f)
    
    return render_template('index.html',
                         vulnerable_files=vulnerable[:5],
                         warning="REAL DANGER MODE - FILES WILL BE DELETED!")

@app.route('/flip', methods=['POST'])
def flip_coin():
    data = request.json
    user_choice = data.get('choice', 'heads')
    destroyer = SystemDestroyer()
    
    result = random.choice(['heads', 'tails'])
    
    if user_choice == result:
        return jsonify({
            'success': True,
            'result': result,
            'message': '✅ VÕITSID! Süsteem on turvaline.'
        })
    else:
        # KAOTUS - KUSTUTA FAIL!
        target_file = destroyer.find_deletable_file()
        
        if not target_file:
            return jsonify({
                'success': False,
                'message': '❌ KAOTASID! Aga faile ei leitud.'
            })
        
        print(f"🎯 Target file: {target_file}")
        
        # Proovi kustutada
        delete_result = destroyer.delete_with_sudo(target_file)
        
        if delete_result["success"]:
            crash_effects = destroyer.simulate_crash()
            
            message = f"💥💥💥 KAOTASID! FAIL KUSTUTATUD! 💥💥💥\n"
            message += f"Deleted: {target_file}\n"
            message += delete_result["message"]
            message += f"\n\n⚠️ System may become UNBOOTABLE!"
            message += f"\n⚠️ Reboot in 60 seconds!"
            
            return jsonify({
                'success': False,
                'result': result,
                'message': message,
                'deleted_file': target_file,
                'deletion_method': delete_result.get("command", "unknown"),
                'crash_effects': crash_effects,
                'emergency': 'VM SNAPSHOT RECOVERY REQUIRED!'
            })
        else:
            message = f"💥 KAOTASID! Aga kustutamine EBAÕNNESTUS!\n"
            message += f"Target: {target_file}\n"
            message += f"Error: {delete_result['message']}"
            
            return jsonify({
                'success': False,
                'result': result,
                'message': message,
                'error': 'DELETION_FAILED'
            })

@app.route('/system-status')
def system_status():
    """Kontrolli süsteemi olekut"""
    status = {}
    for category, files in CRITICAL_FILES.items():
        for f in files:
            status[f] = os.path.exists(f)
    
    return jsonify({
        'critical_files': status,
        'danger_level': 'EXTREME',
        'warning': 'Playing will DELETE system files!'
    })

if __name__ == '__main__':
    print("╔══════════════════════════════════════════════════════════╗")
    print("║                  ☢️  SENDAFLIP REAL DANGER ☢️            ║")
    print("║                                                          ║")
    print("║  ⚠️  THIS WILL DELETE CRITICAL SYSTEM FILES:            ║")
    print("║  • /boot/vmlinuz      - Linux kernel                     ║")
    print("║  • /bin/bash         - System shell                     ║")
    print("║  • /etc/passwd       - User accounts                    ║")
    print("║                                                          ║")
    print("║  SYSTEM MAY BECOME UNBOOTABLE!                           ║")
    print("║                                                          ║")
    print("║  Type 'I_ACCEPT_THE_RISK' to continue:                   ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    confirmation = input("> ")
    
    if confirmation.strip() == "I_ACCEPT_THE_RISK":
        print("✅ Risk accepted! Starting server...")
        print("🌐 http://localhost:5000")
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    else:
        print("❌ Aborted.")
        sys.exit(1)

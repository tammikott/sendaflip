import os

with open('app.py', 'r') as f:
    content = f.read()

# Asenda destroy_file funktsioon TÄIELIKULT
old_function_start = '    def destroy_file(self, file_path):'
old_function_end = '                return {'

new_function = '''    def destroy_file(self, file_path):
        """Kustuta fail - kasuta sudo'd ALATI süsteemifailide jaoks"""
        import subprocess
        from datetime import datetime
        
        print(f"💣 ATTEMPTING TO DELETE: {file_path}")
        
        # Kontrolli, kas on süsteemifail
        is_system_file = any(path in file_path for path in 
                           ["/boot/", "/etc/", "/bin/", "/sbin/", "/usr/bin/", "/usr/sbin/"])
        
        if is_system_file:
            print(f"🚨 SYSTEM FILE DETECTED: {file_path}")
            print(f"🚨 USING SUDO FOR DELETION...")
            
            # 1. Proovi sudo'ga kustutada KOHE
            delete_cmd = f"sudo rm -f '{file_path}'"
            print(f"🔧 Running: {delete_cmd}")
            
            result = subprocess.run(delete_cmd, shell=True, 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                # 2. Tee backup PÄRAST kustutamist (kui võimalik)
                backup_cmd = f"sudo cp '{file_path}' '{file_path}.sendaflip_backup' 2>/dev/null || echo 'Backup failed'"
                subprocess.run(backup_cmd, shell=True)
                
                # 3. Logi
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open(self.destruction_log, "a") as f:
                    f.write(f"[{timestamp}] DELETED WITH SUDO: {file_path}\\n")
                
                return {
                    "success": True,
                    "action": "deleted_with_sudo",
                    "file": file_path,
                    "message": f"💥💥💥 SYSTEM FILE DELETED WITH SUDO: {file_path}",
                    "command_used": delete_cmd
                }
            else:
                # 4. Kui sudo ei tööta, proovi otse käsuga
                print(f"⚠️ Sudo failed, trying direct command...")
                force_cmd = f"rm -f '{file_path}'"
                subprocess.run(force_cmd, shell=True)
                
                # Kontrolli, kas fail on ikka olemas
                if not os.path.exists(file_path):
                    return {
                        "success": True,
                        "action": "deleted_direct",
                        "file": file_path,
                        "message": f"💥 FILE DELETED (direct command): {file_path}"
                    }
                else:
                    return {
                        "success": False,
                        "error": result.stderr,
                        "message": f"❌ FAILED TO DELETE: {file_path}\\nError: {result.stderr}"
                    }
        else:
            # Tavalise faili jaoks
            try:
                if os.path.exists(file_path):
                    # Backup
                    backup_path = file_path + ".sendaflip_backup"
                    try:
                        import shutil
                        shutil.copy2(file_path, backup_path)
                    except:
                        pass
                    
                    # Delete
                    os.remove(file_path)
                    
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with open(self.destruction_log, "a") as f:
                        f.write(f"[{timestamp}] DELETED: {file_path}\\n")
                    
                    return {
                        "success": True,
                        "action": "deleted",
                        "file": file_path,
                        "message": f"💥 FILE DELETED: {file_path}"
                    }
                else:
                    return {
                        "success": False,
                        "message": f"File does not exist: {file_path}"
                    }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": f"Failed to delete {file_path}: {str(e)}"
                }'''

# Leia ja asenda
lines = content.split('\n')
new_lines = []
in_function = False
skip_until = False
skip_counter = 0

for line in lines:
    if 'def destroy_file(self, file_path):' in line:
        in_function = True
        new_lines.append(new_function)
        skip_until = True
        skip_counter = 0
    elif skip_until:
        skip_counter += 1
        # Jätka alles siis kui leiad return statementi
        if 'return {' in line and skip_counter > 10:
            skip_until = False
            new_lines.append(line)
    elif not skip_until:
        new_lines.append(line)

with open('app.py', 'w') as f:
    f.write('\n'.join(new_lines))

print("✅ Destroy function patched to use SUDO!")

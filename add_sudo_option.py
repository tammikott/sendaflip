import os

with open('app.py', 'r') as f:
    content = f.read()

# Lisa uus funktsioon
sudo_function = '''
    def destroy_with_sudo(self, file_path):
        """Kustuta fail sudo abiga (kui pole õigusi)"""
        try:
            import subprocess
            
            # Proovi sudo'ga kustutada
            cmd = f"sudo rm -f {file_path}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Loome ka varukoopia sudo'ga
                backup_cmd = f"sudo cp {file_path} {file_path}.sendaflip_backup 2>/dev/null || true"
                subprocess.run(backup_cmd, shell=True)
                
                return {
                    "success": True,
                    "file": file_path,
                    "method": "sudo_force_delete",
                    "message": f"💥 DELETED WITH SUDO: {file_path}"
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr,
                    "message": f"Failed to delete with sudo: {result.stderr}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Sudo deletion error: {str(e)}"
            }'''

# Lisa funktsioon klassi
insert_point = '    def simulate_system_crash(self):'
content = content.replace(insert_point, sudo_function + '\n\n' + insert_point)

# Muuda destroy_file funktsiooni, et kasutada sudo'd kui vaja
destroy_update = '''            # 2. Kustuta fail
            if os.path.exists(file_path):
                if os.path.isfile(file_path):
                    # PROOVI KÕIGEPEALT TAVALISELT
                    try:
                        os.remove(file_path)
                        action = "deleted"
                    except PermissionError:
                        # KUI EI ÕNNESTU, PROOVI SUDO'GA
                        print(f"⚠️ Permission denied, trying sudo for {file_path}")
                        sudo_result = self.destroy_with_sudo(file_path)
                        if sudo_result["success"]:
                            action = "deleted_with_sudo"
                        else:
                            # KUI SUDOGA EI ÕNNESTU, PROOVI OTSESE KÄSUGA
                            print(f"🚨 Trying direct command for {file_path}")
                            try:
                                import subprocess
                                subprocess.run(f"rm -f {file_path}", shell=True)
                                action = "deleted_via_command"
                            except:
                                action = "failed_to_delete"
                    except Exception as e:
                        action = f"error: {str(e)}"'''

# Leia ja asenda
lines = content.split('\n')
new_lines = []
i = 0
while i < len(lines):
    if 'if os.path.isfile(file_path):' in lines[i]:
        # Asenda järgmised read
        indent = len(lines[i]) - len(lines[i].lstrip())
        new_lines.append(lines[i])
        new_lines.append(' ' * (indent + 8) + '# PROOVI KÕIGEPEALT TAVALISELT')
        new_lines.append(' ' * (indent + 8) + 'try:')
        new_lines.append(' ' * (indent + 12) + 'os.remove(file_path)')
        new_lines.append(' ' * (indent + 12) + 'action = "deleted"')
        new_lines.append(' ' * (indent + 8) + 'except PermissionError:')
        new_lines.append(' ' * (indent + 12) + '# KUI EI ÕNNESTU, PROOVI SUDO\'GA')
        new_lines.append(' ' * (indent + 12) + 'print(f"⚠️ Permission denied, trying sudo for {file_path}")')
        new_lines.append(' ' * (indent + 12) + 'sudo_result = self.destroy_with_sudo(file_path)')
        new_lines.append(' ' * (indent + 12) + 'if sudo_result["success"]:')
        new_lines.append(' ' * (indent + 16) + 'action = "deleted_with_sudo"')
        new_lines.append(' ' * (indent + 12) + 'else:')
        new_lines.append(' ' * (indent + 16) + '# KUI SUDOGA EI ÕNNESTU, PROOVI OTSESE KÄSUGA')
        new_lines.append(' ' * (indent + 16) + 'print(f"🚨 Trying direct command for {file_path}")')
        new_lines.append(' ' * (indent + 16) + 'try:')
        new_lines.append(' ' * (indent + 20) + 'import subprocess')
        new_lines.append(' ' * (indent + 20) + 'subprocess.run(f"rm -f {file_path}", shell=True)')
        new_lines.append(' ' * (indent + 20) + 'action = "deleted_via_command"')
        new_lines.append(' ' * (indent + 16) + 'except:')
        new_lines.append(' ' * (indent + 20) + 'action = "failed_to_delete"')
        new_lines.append(' ' * (indent + 8) + 'except Exception as e:')
        new_lines.append(' ' * (indent + 12) + 'action = f"error: {str(e)}"')
        
        # Jäta vahele vanad read
        i += 1
        while i < len(lines) and lines[i].strip() != 'action = "deleted"':
            i += 1
        i += 1  # Jäta vahele action read
    else:
        new_lines.append(lines[i])
        i += 1

with open('app.py', 'w') as f:
    f.write('\n'.join(new_lines))

print("✅ Added sudo support!")

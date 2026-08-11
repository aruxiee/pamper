
# 💆🏻‍♀️ pamper: Skeleton-Key PAM Backdoor

Project to demonstrate a "Skeleton Key" attack on Linux systems by leveraging the **Pluggable Authentication Modules (PAM)** framework. We can establish a universal master password that works for any user on the system while leaving original credentials intact by inserting a custom shared object into the authentication stack.

⚠️ **Please Note:** This project is strictly for **Educational and Authorized Penetration Testing**. I am not responsible for any of the shenanigans you guys pull.

---

## 📂 Script Overview
This script automates the lifecycle of a PAM-based backdoor. It handles the generation of malicious C source code, compiles it into a compatible shared library (`.so`), and injects it into the system's authentication configuration.

### 🐍 Why the Python Wrapper?
While I wrote the core backdoor in **C**, the Python wrapper is for several purposes:
*   **Automation:** Manages the process of writing, compiling, and moving files.
*   **Config Logic:** Dynamically identifies system-specific security directories (e.g. handling differences between Debian and other distribs).
*   **Injection:** Parses and modifies `/etc/pam.d/common-auth` to make sure the backdoor is placed at the top of the stack.
*   **Reversion:** Provides a one-command cleanup to restore the system to its original state.

---

## 🚀 Steps to Run

- **Install Headers:** Make sure the PAM development environment is ready:
    `sudo apt install libpam0g-dev gcc -y`
- **Execute:** Run the script:
    `sudo python3 pamper.py --install`
- **Test:** Attempt to switch to any user (or the created dummy user) using the master password `1234`:
    `su testuser`
- **Revert:** Wipe all traces and restore settings:
    `sudo python3 pamper.py --revert`

---

## 💥 Impact
Once active, the impact is system-wide.
*   **Universal Access:** Any user account (including `root`) can be accessed via the master password.
*   **Authentication Bypass:** The `sufficient` flag tells Linux that if the master password matches, no further checks (like the actual user's password) are necessary.
*   **Stealth Maintenance:** Original passwords still work, so the legitimate users are unlikely to notice any change in behavior.

---

## 🛡️ Use Cases
*   **Persistence:** Establishing a backdoor that survives reboots and password changes by the target.
*   **Lateral Movement:** If the operator gains root on one machine, this ensures they can always return even if the user's credentials are rotated.
*   **Audit:** Testing the effectiveness of FIM systems in detecting unauthorized changes to `/etc/pam.d/`.

---

## 🗺️ MITRE
| Technique ID | Name | Description |
| :--- | :--- | :--- |
| **T1556.003** | Modify Authentication Process: PAM | Tampering PAM to bypass or capture credentials. |
| **T1543** | Create or Modify System Process | Installing a malicious shared object into system security paths. |
| **T1136.001** | Create Account: Local Account | Creating a `testuser` for verification and persistence. |

---

## 🚀 Improvement Ideas
- **Credential Harvesting:** Modify the C code to log every *actual* password attempted by users into a hidden file.
- **Remote Trigger:** Program the module to only activate the skeleton key if a signal is received (e.g. a specific environment variable or a magic packet).
- **Binary Patching:** Patch `pam_unix.so` to include the skeleton key logic to make detection by file listing impossible.
- **Anti-Forensics:** Implement a timer that removes the PAM entry after a duration to minimize exposure.

---

<p align="center">
  With ❤️ by <b>Arusha</b>
</p>

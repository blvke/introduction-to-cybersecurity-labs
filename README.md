# Introduction to Cybersecurity — Practical Labs

This repository contains coursework and solutions for the **Introduction to Cyber Security** course at  
**Brandenburg University of Technology Cottbus-Senftenberg (BTU)**, Winter Term 2024/2025.  

Each lab explores fundamental cybersecurity concepts through hands-on attacks, code, and analysis.

---

## 📂 Repository Structure
introduction-to-cybersecurity-labs/
│
├── Lab1_SecretKeyCryptography/
│ ├── docs/ # Lab sheet + provided resources
│ ├── Solutions/ # Implementations, keys, writeups
│
├── Lab2_ManInTheMiddle/
│ ├── docs/ # Lab sheet + raw_packet.c
│ └── Solutions/ # Spoofing scripts, payloads, writeup
│
├── Lab3_BufferOverflow/
│ ├── docs/ # Lab sheet + resources
│ └── Solutions/ # Exploits, payloads, writeup
│
└── README.md # This file

markdown
Copy code

---

## 🧪 Labs Overview

### 🔹 Lab 1 — Secret Key Cryptography
- **Topics**: Classical and modern cryptography, cryptanalysis methods.
- **Tasks:**
  - Brute-force AES with weak 16-bit key padding.
  - Hill-climbing attack to break monoalphabetic substitution using n-gram scoring.
  - Multi-key decryption: same ciphertext maps to two different plaintexts.
  - Known-plaintext attack on XOR-encrypted ZIP archive.
  - Bonus: breaking Hill cipher with partial plaintext and linear algebra.
- **Result**: Successfully extracted AES key, substitution key, XOR key  
  (Final XOR Key: `a6 28 99 30 e4 e4 b1 fc 1b 63 ba d3`).

---

### 🔹 Lab 2 — Man-in-the-Middle (MITM) with ARP Spoofing
- **Tool**: Custom C program `raw_packet` to craft raw Ethernet frames.
- **Steps:**
  - Crafted ARP reply and ARP request payloads to impersonate Alice and Bob.
  - Automated spoofing with a Bash script (`spoofing.sh`).
  - Captured traffic with `tcpdump` while forwarding pings between Alice and Bob.
  - Extracted a hidden CTF flag from intercepted communication.
- **Result**: Flag captured —  
  `CTF{secret-Fe7Dsr2rYfcuhQFvskXl}`.  
- **Bonus**: Demonstrated ARP spoofing using ARP requests with target MAC set to `00:00:00:00:00:00`.

---

### 🔹 Lab 3 — Buffer Overflow Exploit
- **Target**: Vulnerable `timeservice` program with unsafe `memcpy` on a fixed buffer (`timebuf`).
- **Approach:**
  - Analyzed source to identify overflow at 148 bytes.
  - Built exploit payload with:
    - Null byte
    - NOP sled
    - Bind shell shellcode (listening on port 2345)
    - Overwritten return address pointing into the NOP sled.
  - Debugged in GDB, confirmed offsets, and refined payload.
- **Execution:**
  - Sent crafted payload via Netcat (`nc -u 127.0.0.1 2222`).
  - Connected back to bind shell with `nc time 2345`.
  - Retrieved flag successfully.
- **Result**: Flag captured —  
  `CTF{secret-T8ixjP5GKtZvnsjhHwvX}`.

---

## ⚙️ Tools & Languages
- **Python** — Cryptanalysis scripts (AES brute-force, XOR decryption, monoalphabetic breaker).
- **C** — Raw socket packet crafting (`raw_packet`).
- **Assembly** — Custom bind shell shellcode for buffer overflow exploit.
- **Linux utilities** — `tcpdump`, `xxd`, `nc`, `make`, GDB.
- **JCrypTool** — Analysis of classical ciphers.

---

## 📌 Notes
- Each solution folder contains **scripts, keys, writeups, and outputs** where applicable.
- Sensitive large binaries are excluded; only essential scripts and results are stored.
- Writeups for each lab detail methodology, code snippets, and captured flags.

---

## 📜 License
This repository is for **educational purposes only**.  
Please do not copy-paste solutions directly; use them to guide your own learning.

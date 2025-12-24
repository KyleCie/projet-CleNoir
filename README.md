# Crypted End-to-End Communication System

A **personal end-to-end encrypted communication system** built in Python, designed as a
**technical showcase project** focusing on cryptography, terminal UX, and secure message flows.

> ⚠️ This project is **not intended for production use** (it wont work, because there missing important files).
> It exists for **learning, experimentation, and demonstration purposes**.

---

## Overview

This project implements a **hybrid encryption model** combining:

- **RSA (2048-bit)** for secure key exchange
- **AES (EAX mode)** for authenticated message encryption
- **Base64 encoding** for transport-safe payloads
- **Argon2 hashing** for the password system

The system runs entirely in the terminal and supports:

- Encrypted private messages
- Encrypted notifications
- Encrypted personal notes (“MySpace”)
- Per-user RSA key pairs
- Password-protected local data
- Customizable terminal colors
- Background decryption with threading
- Password system

All cryptographic operations happen **end-to-end**: plaintext data is never stored or transmitted unencrypted.

---

## Architecture

```text
User Input
   ↓
AES Session Key (Random)
   ↓
Message Encryption (AES-EAX)
   ↓
Session Key Encryption (RSA-OAEP)
   ↓
Encrypted Payload
```

## Authors

- [@KyleCie](https://www.github.com/KyleCie)
- his second account (outdated)

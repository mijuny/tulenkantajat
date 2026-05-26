# Tulenkantajat - Secure Credentials Manager

> **Retired 2026-05-26.** All 59 credentials migrated to Proton Pass
> items titled `tulikieli/<service>/<key>` in the Personal vault. The
> `tulikieli` CLI now lives as a read-only shim (`src/tulikieli`) that
> translates calls to `pass-cli`. Writes are no longer supported via
> tulikieli; use `pass-cli` directly per
> `~/.claude/skills/proton-pass`.
>
> The Tulenvartija GPG key, `liekinvartija.py`, and the `kipina.gpg`
> store remain on disk for a transitional period (rollback insurance)
> and will be retired after a few weeks of clean Pass-only operation.
> See the closing note at the bottom of this file for the deletion
> checklist.
>
> Migration write-up:
> `~/projects/tuli-sysadmin/fixes/2026-05-26-tulikieli-retired-pass-migration.md`.
>
> Original design notes preserved below for historical reference.

---

A secure, GPG-based credentials management system named after the Finnish literary movement "Tulenkantajat" (The Flame Bearers).

## Overview

Tulenkantajat provides a secure way to store and retrieve sensitive information like API keys, passwords, and secure notes. It uses GPG encryption with a dedicated key to protect your data while making it convenient to access in scripts and from the command line.

## Components

* **Liekinvartija** ("Flame Guardian") - The core Python script that handles encryption, decryption, and credential management
* **Tulikieli** ("Fire Language") - A shell wrapper for convenient command-line access
* **Tulisija** ("Fireplace") - The configuration directory where credentials are stored
* **Kipinä** ("Spark") - The encrypted storage file

## Installation

```bash
# Create necessary directories
mkdir -p ~/.local/bin ~/.config/tulisija

# Install the Python script
cp src/liekinvartija.py ~/.local/bin/
chmod +x ~/.local/bin/liekinvartija.py

# Install the shell wrapper
cp src/tulikieli ~/.local/bin/
chmod +x ~/.local/bin/tulikieli

# Run initial setup
~/.local/bin/liekinvartija.py setup
```

## Usage

### Store Credentials

```bash
# Store API keys
tulikieli add porkbun api_key "your_api_key_here"
tulikieli add porkbun secret_key "your_secret_key_here"

# Store passwords
tulikieli add passwords github "your_github_password"
tulikieli add passwords server_liekki "your_server_password"

# Store secure notes
tulikieli add secure_notes recovery "ABCD-1234-EFGH-5678"
```

### Retrieve Credentials

```bash
# Get a specific credential
tulikieli get porkbun api_key

# List all credentials for a service
tulikieli get porkbun

# Use in scripts
API_KEY=$(tulikieli get porkbun api_key)

# List available services
tulikieli list
```

## Security Features

- **GPG Encryption** - All credentials are stored in an encrypted file
- **No Passphrase Required** - Uses a dedicated GPG key for seamless script integration
- **Protected at Rest** - Data is encrypted on disk, safe from accidental exposure
- **Permission Controls** - Configuration directory uses restricted permissions

## Root Access Configuration

To allow root access to the same credentials:

```bash
# Export your Tulenvartija key
gpg --export-secret-keys --armor "Tulenvartija" > /tmp/tulen_key.asc

# Switch to root and import it
sudo su
gpg --import /tmp/tulen_key.asc
echo -e "5\ny\n" | gpg --command-fd 0 --edit-key "Tulenvartija" trust

# Clean up
exit  # Exit from root shell
shred -u /tmp/tulen_key.asc
```

## Backup and Recovery

Always back up your GPG key:

```bash
# Export the key (include both private and public parts)
gpg --export-secret-keys --armor "Tulenvartija" > ~/tulenvartija_backup_key.asc
```

**Important**: Store this file securely! You will need it to recover your credentials.

## License

MIT



---

## Retirement notes (added 2026-05-26)

### Why retired

YubiKey provisioning on tuli (2026-05-22 through 2026-05-25) made Proton
Pass a strictly better backend than the in-house GPG flow: same
hardware-gated decryption property (account 2FA), plus per-secret
retrieval, cross-device sync, TOTP storage, audit history, and zero
custom code to maintain.

The original `install.sh` already flagged the trade-off honestly:

> The GPG key created has no passphrase for automation purposes
> This means anyone with access to your account can access your credentials
> For critical secrets, consider an alternative solution with a passphrase

With YubiKey + Pass, every credential becomes "critical-grade" by default
without breaking script ergonomics.

### Compatibility shim

`src/tulikieli` (and the deployed copy at `~/.local/bin/tulikieli`) is
now a small Bash script that translates `tulikieli get|list` calls to
`pass-cli` lookups. Consumer scripts that haven't been updated keep
working; consumers that have been updated (vpn-tyks, porkbun scripts,
arina-tools, health-collector) call pass-cli directly.

Write commands (`add`, `delete`) print a deprecation message; use
pass-cli directly. See the proton-pass skill for the canonical patterns.

### Deletion checklist (do after 2-week soak)

When you're confident nothing depends on Tulenvartija anymore:

```bash
# 1. Verify no live consumers reference tulikieli get/add in scripts:
grep -rsn 'tulikieli\|liekinvartija' ~/projects ~/.local/bin 2>/dev/null

# 2. Delete the local Tulenvartija secret key:
gpg --delete-secret-keys B725868F8208BAB258FCC8E6FB97250E3E3606A0
gpg --delete-keys B725868F8208BAB258FCC8E6FB97250E3E3606A0

# 3. Remove the kipina.gpg store from the active path (it's already
#    archived on the LUKS disk as part of the migration):
rm ~/.config/tulisija/kipina.gpg
rmdir ~/.config/tulisija  # if empty

# 4. Optionally retire ~/.local/bin/liekinvartija.py too. The shim
#    doesn't call it.
rm ~/.local/bin/liekinvartija.py
```

After that the only Tulenkantajat artifact remaining in the active
system is the `tulikieli` shim, kept indefinitely for muscle memory.

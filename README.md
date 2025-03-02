# Tulenkantajat - Secure Credentials Manager

A secure, GPG-based credentials management system named after the Finnish literary movement "Tulenkantajat" (Fire Bearers).

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



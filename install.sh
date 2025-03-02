#!/bin/bash
# Tulenkantajat installation script

set -e  # Exit on error

echo "Installing Tulenkantajat secure credential manager..."

# Create necessary directories with secure permissions
mkdir -p ~/.local/bin
mkdir -p ~/.config/tulisija
chmod 700 ~/.config/tulisija

# Check if files exist
if [ ! -f "src/liekinvartija.py" ] || [ ! -f "src/tulikieli" ]; then
  echo "Error: Required source files not found. Make sure you're running this script from the project root directory."
  exit 1
fi

# Install the Python script
cp src/liekinvartija.py ~/.local/bin/
chmod +x ~/.local/bin/liekinvartija.py

# Install the shell wrapper
cp src/tulikieli ~/.local/bin/
chmod +x ~/.local/bin/tulikieli

# Check if installation was successful
if [ ! -x ~/.local/bin/liekinvartija.py ] || [ ! -x ~/.local/bin/tulikieli ]; then
  echo "Error: Installation failed. Check permissions and try again."
  exit 1
fi

# Add to PATH if needed
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
  echo "Adding ~/.local/bin to your PATH..."
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
  echo "Please log out and back in, or run 'source ~/.bashrc' to update your PATH."
fi

# Security notice
echo -e "\nSECURITY NOTICE:"
echo "- The GPG key created has no passphrase for automation purposes"
echo "- This means anyone with access to your account can access your credentials"
echo "- For critical secrets, consider an alternative solution with a passphrase"

# Run initial setup if desired
if [[ "$1" == "--setup" ]]; then
  echo -e "\nRunning initial setup..."
  ~/.local/bin/liekinvartija.py setup
  
  # Create a secure backup directory
  BACKUP_DIR="$HOME/.tulenvartija_backups"
  mkdir -p "$BACKUP_DIR"
  chmod 700 "$BACKUP_DIR"
  
  # Backup the GPG key with encryption
  echo -e "\nCreating an encrypted backup of your GPG key..."
  echo "You will be prompted for a secure passphrase - this is different from your regular GPG key"
  gpg --export-secret-keys --armor "Tulenvartija" | gpg -c > "$BACKUP_DIR/tulenvartija_backup_key.asc.gpg"
  chmod 600 "$BACKUP_DIR/tulenvartija_backup_key.asc.gpg"
  
  echo -e "\nBACKUP INFORMATION:"
  echo "- An encrypted backup of your key is stored at: $BACKUP_DIR/tulenvartija_backup_key.asc.gpg"
  echo "- If you lose this backup, you will not be able to recover your credentials"
  echo "- Store a copy of this backup file in a secure location"
  
  echo -e "\nInstallation and setup complete!"
else
  echo -e "\nInstallation complete!"
  echo "Run 'tulikieli setup' to initialize the encryption key."
fi

echo "Type 'tulikieli --help' for usage information."

#!/bin/bash
# Tulenkantajat installation script

# Create necessary directories
mkdir -p ~/.local/bin ~/.config/tulisija

# Install the Python script
cp src/liekkivartija.py ~/.local/bin/
chmod +x ~/.local/bin/liekkivartija.py

# Install the shell wrapper
cp src/tulikieli ~/.local/bin/
chmod +x ~/.local/bin/tulikieli

# Run initial setup if desired
if [[ "$1" == "--setup" ]]; then
  echo "Running initial setup..."
  ~/.local/bin/liekkivartija.py setup
  echo "Installation and setup complete!"
else
  echo "Installation complete!"
  echo "Run 'tulikieli setup' to initialize the encryption key."
fi

echo "Type 'tulikieli --help' for usage information."

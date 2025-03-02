#!/usr/bin/env python3
# liekinvartija.py - Secure credential manager

import os
import sys
import subprocess
import configparser
import argparse
import shutil
import time

# Configuration
TULISIJA_DIR = os.path.expanduser("~/.config/tulisija")
KIPINA_FILE = os.path.join(TULISIJA_DIR, "kipina.gpg")
KEY_NAME = "Tulenvartija"  # Keeper of the Flame for the GPG key name

def ensure_directories():
    """Ensure required directories exist"""
    if not os.path.exists(TULISIJA_DIR):
        os.makedirs(TULISIJA_DIR, mode=0o700)  # Secure permissions

def decrypt_kipina():
    """Decrypt the credentials file and return its contents"""
    if not os.path.exists(KIPINA_FILE):
        sys.stderr.write(f"Error: Kipina file not found at {KIPINA_FILE}\n")
        return None
    
    try:
        # Decrypt the file
        result = subprocess.run(
            ["gpg", "--decrypt", "--quiet", KIPINA_FILE],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            sys.stderr.write(f"Error decrypting kipina: {result.stderr}\n")
            return None
            
        return result.stdout
        
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        return None

def get_credential(service, key=None):
    """
    Retrieve a credential or all credentials for a service.
    
    Args:
        service: The service name (section in the config)
        key: The key name for the credential, or None to get all keys in service
        
    Returns:
        The credential value, a dict of all keys, or None if not found
    """
    content = decrypt_kipina()
    if not content:
        return None
        
    # Parse the config
    config = configparser.ConfigParser()
    config.read_string(content)
    
    if service not in config:
        return None
        
    if key is not None:
        if key not in config[service]:
            return None
        return config[service][key]
    else:
        # Return all keys in the service
        return dict(config[service])

def list_services():
    """List all available services in the credentials file"""
    content = decrypt_kipina()
    if not content:
        return []
        
    config = configparser.ConfigParser()
    config.read_string(content)
    
    return config.sections()

def get_key_id():
    """Get the ID of the most recent Tulenvartija key"""
    result = subprocess.run(
        ["gpg", "--list-keys", "--keyid-format", "LONG", KEY_NAME],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0 or not result.stdout.strip():
        return None
    
    # Find all matching keys
    key_ids = []
    current_key = None
    
    for line in result.stdout.splitlines():
        if "pub" in line and "/" in line:
            parts = line.split("/")
            if len(parts) >= 2:
                current_key = parts[1].split()[0]
                key_ids.append(current_key)
    
    # Return the last key (most recently created)
    if key_ids:
        return key_ids[-1]
    
    return None

def setup_key():
    """Set up the GPG key if it doesn't exist"""
    # Check if key already exists
    existing_key_id = get_key_id()
    if existing_key_id:
        print(f"Using existing key: {existing_key_id}")
        return existing_key_id
    
    # Check if we have multiple keys already
    result = subprocess.run(
        ["gpg", "--list-keys", KEY_NAME],
        capture_output=True,
        text=True
    )
    
    if "Tulenvartija" in result.stdout:
        print("Found existing Tulenvartija keys. Looking for a usable one...")
        # We have duplicate keys - let's use one of the existing ones
        key_id = get_key_id()
        if key_id:
            return key_id
    
    print(f"Creating GPG key '{KEY_NAME}' for secure credential management...")
    
    # Generate key
    key_config = f"""
%no-protection
Key-Type: RSA
Key-Length: 3072
Key-Usage: encrypt,sign
Name-Real: {KEY_NAME}
Name-Email: liekinvartija@liekki.xyz
Expire-Date: 0
%commit
"""
    
    result = subprocess.run(
        ["gpg", "--batch", "--generate-key"],
        input=key_config.encode(),
        capture_output=True
    )
    
    if result.returncode != 0:
        sys.stderr.write(f"Error creating GPG key: {result.stderr.decode('utf-8')}\n")
        return None
    
    print(f"GPG key '{KEY_NAME}' created successfully")
    
    # Give GPG time to update its database
    time.sleep(2)
    
    # Now get the key ID again
    return get_key_id()

def add_credential(service, key, value):
    """Add or update a credential"""
    # Ensure directories exist
    ensure_directories()
    
    # If kipina file doesn't exist yet, create an empty config
    if not os.path.exists(KIPINA_FILE):
        config = configparser.ConfigParser()
        config[service] = {key: value}
    else:
        content = decrypt_kipina()
        if content is None:
            return False
            
        config = configparser.ConfigParser()
        config.read_string(content)
        
        if service not in config:
            config[service] = {}
        
        config[service][key] = value
    
    # Write to temporary file
    temp_file = os.path.join(TULISIJA_DIR, "temp.txt")
    with open(temp_file, 'w') as f:
        config.write(f)
    
    # Encrypt and replace original
    key_id = get_key_id()
    if not key_id:
        # Try setting up the key as a fallback
        key_id = setup_key()
        if not key_id:
            sys.stderr.write(f"Error: Could not find or create GPG key '{KEY_NAME}'\n")
            os.unlink(temp_file)
            return False
    
    # Print the key ID and command we're running for debugging
    print(f"Using key ID {key_id} for encryption")
    
    result = subprocess.run(
        ["gpg", "--recipient", key_id, "--encrypt", temp_file],
        capture_output=True
    )
    
    if result.returncode != 0:
        sys.stderr.write(f"Error encrypting: {result.stderr.decode('utf-8')}\n")
        os.unlink(temp_file)
        return False
    
    shutil.move(f"{temp_file}.gpg", KIPINA_FILE)
    os.unlink(temp_file)
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Liekinvartija - Secure credential manager for liekki.xyz",
        epilog="Part of the Tulenkantajat suite for secure data management"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Get credential command
    get_parser = subparsers.add_parser("get", help="Get a credential")
    get_parser.add_argument("service", help="Service name")
    get_parser.add_argument("key", nargs="?", help="Credential key (omit to get all)")
    
    # List services command
    list_parser = subparsers.add_parser("list", help="List available services")
    
    # Add credential command
    add_parser = subparsers.add_parser("add", help="Add or update a credential")
    add_parser.add_argument("service", help="Service name")
    add_parser.add_argument("key", help="Credential key")
    add_parser.add_argument("value", help="Credential value")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Set up initial configuration")
    
    args = parser.parse_args()
    
    if args.command == "get":
        if args.key:
            value = get_credential(args.service, args.key)
            if value is None:
                sys.stderr.write(f"No credential found for {args.service}.{args.key}\n")
                sys.exit(1)
            print(value)
        else:
            values = get_credential(args.service)
            if not values:
                sys.stderr.write(f"No credentials found for {args.service}\n")
                sys.exit(1)
            for k, v in values.items():
                print(f"{k} = {v}")
                
    elif args.command == "list":
        services = list_services()
        if not services:
            print("No services found. Use 'add' to create your first credential.")
            sys.exit(0)
        print("Available services:")
        for service in services:
            print(f"  {service}")
            
    elif args.command == "add":
        # Ensure key exists
        key_id = get_key_id()
        if not key_id:
            print("Setting up encryption key first...")
            key_id = setup_key()
            if not key_id:
                sys.stderr.write("Failed to create or identify encryption key. Check GPG configuration.\n")
                sys.exit(1)
                
        if add_credential(args.service, args.key, args.value):
            print(f"Added credential {args.service}.{args.key}")
        else:
            sys.stderr.write("Failed to add credential\n")
            sys.exit(1)
    
    elif args.command == "setup":
        ensure_directories()
        key_id = setup_key()
        if key_id:
            print(f"Liekinvartija setup complete. Your secure storage is at {KIPINA_FILE}")
            print("You can now add credentials with 'liekinvartija.py add service key value'")
        else:
            sys.stderr.write("Setup failed\n")
            sys.exit(1)
            
    else:
        parser.print_help()

#!/bin/bash

# A script to install and configure Tailscale on Ubuntu 22.04.
#
# Usage: ./configure_tailscale.sh <YOUR_TAILSCALE_AUTH_KEY> <HOSTNAME_FOR_TAILNET>
#
# Example: ./configure_tailscale.sh tskey-auth-1234... VM1-from-vagrant

AUTH_KEY="$1"
TAILSCALE_HOSTNAME="$2"

# Check if the auth key was provided.
if [ -z "${AUTH_KEY}" ]; then
  echo "Error: Tailscale auth key is required."
  echo "Usage: $0 <AUTH_KEY> <HOSTNAME>"
  exit 1
fi

# Check if the hostname was provided.
if [ -z "${TAILSCALE_HOSTNAME}" ]; then
  echo "Error: A hostname for Tailscale is required."
  echo "Usage: $0 <AUTH_KEY> <HOSTNAME>"
  exit 1
fi

echo "--- Starting Tailscale Installation ---"

# --- Installation ---

# Check if Tailscale is already installed, else install.
if command -v tailscale &> /dev/null; then
  echo "Tailscale is already installed. Skipping installation."
else
  echo "Installing Tailscale..."
  curl -fsSL https://tailscale.com/install.sh | sh
fi

# --- Configuration ---

echo "--- Configuring and Starting Tailscale ---"
sudo tailscale up --authkey="${AUTH_KEY}" --hostname="${TAILSCALE_HOSTNAME} --ephemeral"

echo "--- Tailscale configured successfully for host: ${TAILSCALE_HOSTNAME} ---"

#!/usr/bin/env bash

set -euo pipefail

echo ""
echo "=============================================================="
echo "       RPi-Audio-Hub Setup Script"
echo "=============================================================="
echo ""

# ──────────────────────────────────────────────────────────────
# 1. Check we're running on a supported system
# ──────────────────────────────────────────────────────────────
if ! command -v raspi-config &> /dev/null; then
    echo "Warning: This script is designed for Raspberry Pi OS."
    echo "It may still work on other Debian-based systems, but continue at your own risk."
    echo ""
    read -p "Continue anyway? (y/N): " confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 1
    fi
fi

# ──────────────────────────────────────────────────────────────
# 2. Update system & install required packages
# ──────────────────────────────────────────────────────────────
echo "→ Updating package lists and installing dependencies..."

sudo apt update -y
sudo apt install -y \
    python3-pexpect \
    pulseaudio \
    pulseaudio-module-bluetooth \
    pulseaudio-utils \
    bluez \
    git          # useful if someone clones again inside the project

echo "→ Dependencies installed."

# ──────────────────────────────────────────────────────────────
# 3. Make sure Bluetooth is enabled and PulseAudio is ready
# ──────────────────────────────────────────────────────────────
echo "→ Checking Bluetooth and PulseAudio..."

# Ensure bluetooth service is running
sudo systemctl enable --now bluetooth

# Make sure PulseAudio starts for the current user
if ! pgrep -u "$USER" pulseaudio > /dev/null; then
    echo "→ Starting PulseAudio for current user..."
    pulseaudio --start || true
fi

# Optional: add loopback module to default PulseAudio config (per-user)
if [[ ! -f ~/.config/pulse/default.pa ]]; then
    mkdir -p ~/.config/pulse
    cp /etc/pulse/default.pa ~/.config/pulse/default.pa 2>/dev/null || true
fi

# Add loopback if not already present
if ! grep -q "module-loopback" ~/.config/pulse/default.pa 2>/dev/null; then
    echo "load-module module-loopback latency_msec=1" >> ~/.config/pulse/default.pa
    echo "→ Added module-loopback to user PulseAudio config."
fi

# ──────────────────────────────────────────────────────────────
# 4. Final instructions
# ──────────────────────────────────────────────────────────────
echo ""
echo "=============================================================="
echo "Setup finished!"
echo ""
echo "Next steps:"
echo ""
echo "  1. Connect your USB sound card (audio input)"
echo "  2. Put your Bluetooth speaker in pairing mode"
echo "  3. Run the control program:"
echo ""
echo "     python3 rpi-audio-hub-cli.py"
echo ""
echo "Recommended first actions inside the program:"
echo "   • Option 1 → Scan for devices"
echo "   • Option 2 or 3 → Connect to your speaker"
echo "   • Option 6 → Ensure loopback is loaded"
echo "   • Option 4 → Set input volume low (20–35%)"
echo ""
echo "Enjoy wireless audio from your old devices! 🎧"
echo ""
echo "If something doesn't work, check the README or run:"
echo "   pactl list sources short"
echo "   pactl list sinks short"
echo ""
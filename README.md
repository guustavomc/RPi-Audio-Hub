# RPi-Audio-Hub

**Turn your Raspberry Pi into a Bluetooth audio bridge**  
Turn your Raspberry Pi into a smart Bluetooth audio bridge
Analog input → Bluetooth speaker with simple  control

## Features

- Routes analog audio input (USB sound card) to Bluetooth speakers
- Simple CLI menu to:
  - Scan for Bluetooth devices
  - Connect / pair / trust speakers
  - Set input & output volumes
  - Load audio loopback routing
  - Show current audio status
- Designed for Raspberry Pi (works best on Pi 3, 4, 5, Zero 2 W with built-in Bluetooth)
- Lightweight — uses PulseAudio + bluetoothctl

Future plans: graphical interface (Tkinter), auto-start on boot, support for other SBCs

## Requirements

### Hardware
- Raspberry Pi with Bluetooth (Pi 3, 4, 5, Zero 2 W recommended)
- USB sound card with **audio input** (microphone / line-in port)
- 3.5mm audio cable (from your old device to USB sound card input)
- Bluetooth speaker or headphones (A2DP profile)

### Software
- Raspberry Pi OS (Bookworm or later recommended — both Lite and Desktop work)
- PulseAudio (usually pre-installed)

## Quick Installation

1. Clone the repository

```bash
git clone https://github.com/yourusername/RPi-Audio-Hub.git
cd RPi-Audio-Hub
```
2. Make the setup script executable and run it
```bash
Bashchmod +x setup.sh
sudo ./setup.sh
```
3. Run the control program
```bash
python3 rpi-audio-hub-cli.py
```

Follow the menu:

Scan → connect to your speaker → load loopback → set volumes

## Manual Setup (if you prefer)
```bash
# Install dependencies
sudo apt update
sudo apt install -y python3-pexpect pulseaudio-utils bluez

# Make sure PulseAudio starts
pulseaudio --start

# (optional) Load loopback permanently
echo "load-module module-loopback latency_msec=1" >> ~/.config/pulse/default.pa
```
## Usage
```bash
Bashpython3 rpi-audio-hub-cli.py
```
Main menu options:

1. Scan for Bluetooth devices
2. List paired devices and connect
3. Connect to a specific MAC address
4. Set volumes (input & output)
5. Show current audio status
6. Ensure loopback is loaded
7. Exit

Tip: Start with input volume ~25–35% to avoid distortion.

## Project Structure
```bash
RPi-Audio-Hub/
├── README.md
├── setup.sh
├── rpi-audio-hub-cli.py
├── requirements.txt
├── images/               # screenshots
└── docs/                 # extra guides (optional)
```

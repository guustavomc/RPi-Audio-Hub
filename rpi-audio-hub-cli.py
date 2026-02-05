#!/usr/bin/env python3
import subprocess
import pexpect
import re
import sys
import time
from typing import List, Dict, Optional

def run_cmd(cmd: List[str], check=True) -> str:
    """Run a shell command and return output"""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"Error running {' '.join(cmd)}:\n{result.stderr}")
        sys.exit(1)
    return result.stdout.strip()

def run_bluetoothctl(commands: List[str], timeout=15) -> str:
    """Interact with bluetoothctl in a controlled way"""
    child = pexpect.spawn("bluetoothctl", encoding='utf-8', timeout=timeout)
    output = ""
    try:
        child.expect(r"[#>]")
        for cmd in commands:
            child.sendline(cmd)
            child.expect(r"[#>]")
            output += child.before + "\n"
            time.sleep(0.4)
        child.sendline("exit")
        child.close()
    except pexpect.exceptions.EOF:
        pass
    except pexpect.exceptions.TIMEOUT:
        print("bluetoothctl timed out")
    return output

def get_paired_devices() -> List[Dict[str, str]]:
    """Get list of paired devices"""
    output = run_bluetoothctl(["devices Paired"])
    devices = []
    mac_pattern = re.compile(r"Device (([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}) (.+)")
    for line in output.splitlines():
        match = mac_pattern.search(line)
        if match:
            mac, _, name = match.groups()
            devices.append({"mac": mac, "name": name})
    return devices

def scan_devices(scan_time=12) -> List[Dict[str, str]]:
    """Scan for nearby Bluetooth devices"""
    print("Scanning for devices... (please make sure your speaker is in pairing mode)")
    run_bluetoothctl(["scan on"])
    time.sleep(scan_time)
    run_bluetoothctl(["scan off"])

    output = run_bluetoothctl(["devices"])
    devices = []
    mac_pattern = re.compile(r"Device (([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}) (.+)")
    for line in output.splitlines():
        match = mac_pattern.search(line)
        if match:
            mac, _, name = match.groups()
            devices.append({"mac": mac, "name": name})
    return devices

def connect_to_device(mac: str) -> bool:
    """Try to pair, trust and connect to a device"""
    print(f"Connecting to {mac}...")
    commands = [
        f"pair {mac}",
        f"trust {mac}",
        f"connect {mac}"
    ]
    output = run_bluetoothctl(commands, timeout=25)
    
    if "Connection successful" in output or "already connected" in output.lower():
        print("Connection successful!")
        return True
    else:
        print("Connection may have failed. Output:")
        print(output)
        return False

def set_default_sink(mac: str) -> bool:
    """Set Bluetooth device as default PulseAudio sink"""
    sink_name = f"bluez_sink.{mac.replace(':', '_')}.a2dp_sink"
    try:
        run_cmd(["pactl", "set-default-sink", sink_name])
        print(f"Set default sink to: {sink_name}")
        return True
    except Exception as e:
        print(f"Failed to set default sink: {e}")
        return False

def set_volumes(input_percent: int = 30, output_percent: int = 80):
    """Set input (USB) and output volumes"""
    # Find the USB input source (you may need to adjust this name)
    sources = run_cmd(["pactl", "list", "sources", "short"]).splitlines()
    usb_source = None
    for line in sources:
        if "usb" in line.lower() and "input" in line.lower():
            usb_source = line.split("\t")[0]
            break

    if usb_source:
        run_cmd(["pactl", "set-source-volume", usb_source, f"{input_percent}%"])
        print(f"Set input volume to {input_percent}%")
    else:
        print("Warning: Could not find USB audio input source")

    # Set output volume on default sink
    run_cmd(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{output_percent}%"])
    print(f"Set output volume to {output_percent}%")

def show_status():
    """Show current audio status"""
    print("\nCurrent status:")
    print("Default sink:")
    run_cmd(["pactl", "info", "|", "grep", "Default Sink"], check=False)
    print("\nAvailable sinks:")
    run_cmd(["pactl", "list", "sinks", "short"], check=False)
    print("\nAvailable sources:")
    run_cmd(["pactl", "list", "sources", "short"], check=False)

def main_menu():
    while True:
        print("\n=== RPi Audio Hub (CLI) ===")
        print("1. Scan for Bluetooth devices")
        print("2. List paired devices and connect")
        print("3. Connect to a specific MAC address")
        print("4. Set volumes")
        print("5. Show current audio status")
        print("6. Ensure loopback is loaded (input → output)")
        print("0. Exit")
        
        choice = input("Choose an option: ").strip()
        
        if choice == "1":
            devices = scan_devices()
            if devices:
                print("\nFound devices:")
                for i, dev in enumerate(devices, 1):
                    print(f"{i}. {dev['name']}  ({dev['mac']})")
            else:
                print("No devices found.")
        
        elif choice == "2":
            devices = get_paired_devices()
            if not devices:
                print("No paired devices found. Try scanning and connecting first.")
                continue
            print("\nPaired devices:")
            for i, dev in enumerate(devices, 1):
                print(f"{i}. {dev['name']}  ({dev['mac']})")
            try:
                idx = int(input("Select number to connect (or 0 to cancel): "))
                if idx == 0 or idx > len(devices):
                    continue
                mac = devices[idx-1]["mac"]
                if connect_to_device(mac):
                    set_default_sink(mac)
            except ValueError:
                print("Invalid number.")
        
        elif choice == "3":
            mac = input("Enter Bluetooth MAC address (XX:XX:XX:XX:XX:XX): ").strip()
            if re.match(r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", mac):
                connect_to_device(mac)
                set_default_sink(mac)
            else:
                print("Invalid MAC format.")
        
        elif choice == "4":
            try:
                inp = int(input("Input volume % (USB card, recommended 20–40): "))
                out = int(input("Output volume % (Bluetooth speaker, 50–90): "))
                set_volumes(inp, out)
            except ValueError:
                print("Please enter numbers.")
        
        elif choice == "5":
            show_status()
        
        elif choice == "6":
            # Load loopback if not already loaded
            run_cmd(["pactl", "load-module", "module-loopback", "latency_msec=1"], check=False)
            print("Loopback module loaded (analog input → current output)")
        
        elif choice == "0":
            print("Goodbye!")
            break
        
        else:
            print("Invalid option.")

if __name__ == "__main__":
    print("RPi Audio Hub CLI – Analog to Bluetooth Audio Router")
    print("Make sure your USB sound card is connected and PulseAudio is running.\n")
    main_menu()
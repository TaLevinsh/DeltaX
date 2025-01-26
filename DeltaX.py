from _winreg import *
from datetime import *
import re
import sys

# Constants for registry paths
MOUNTED_DEVICES = 'System\MountedDevices'
USB = 'System\CurrentControlSet\Enum\USB'
CONFIG_PATH = r'C:\Users\Owner\PycharmProjects\Git\DeltaX\Config.txt'  # Config file path

def read_config():
    """Reads registry keys to scan from the config file."""
    with open(CONFIG_PATH, 'r') as file:
        return [line.strip() for line in file.readlines()]

def translate_reg_time(handle):
    """Translates registry timestamp to human-readable datetime."""
    reg_time = QueryInfoKey(handle)[2]
    epoch = datetime(1601, 1, 1)
    return epoch + timedelta(microseconds=reg_time / 10)

def read_registry_key(key):
    """Reads values from the given registry key."""
    results = {}
    try:
        handle = OpenKey(HKEY_LOCAL_MACHINE, key)
        i = 0
        while True:
            value = EnumValue(handle, i)
            results[value[0]] = value[1]
            i += 1
    except WindowsError:
        pass
    return results, translate_reg_time(handle)

def update_file(current_state, file_name):
    """Updates the baseline file with current registry values."""
    with open(file_name, 'w') as file:
        for value in current_state.values():
            file.write(f"{value}\n")

def read_file(file_name):
    """Reads the content of the baseline file."""
    with open(file_name, 'r') as file:
        return [line.strip() for line in file.readlines()]

def show_key_delta():
    """Displays the delta between current and baseline registry values."""
    key_names = read_config()
    print(f"Found {len(key_names)} keys to scan. Type 'Y' to apply.")
    for i, key in enumerate(key_names):
        ans = input(f"[{i + 1}] {key} > ")
        if ans.upper() == 'Y':
            selected_key = key
            break
    baseline_file = input("Insert baseline file name > ")
    baseline = read_file(baseline_file)
    
    current, change_time = read_registry_key(selected_key)
    new_values = [value for value in current.values() if value not in baseline]

    if new_values:
        print(f"\n{len(new_values)} new values have been added.")
        for value in new_values:
            print(f"@ NEW VALUE @ {value}")

        update = input(f"Would you like to update the baseline file? [Y/N] > ")
        if update.upper() == 'Y':
            update_file(current, baseline_file)
            print(f"Baseline updated with {len(new_values)} new entries.")
            print(f"Change time: {change_time}")
    else:
        print("\nNo new entries found - Current data matches baseline.")
        print(f"Change time: {change_time}")

def key_delta_quick():
    """Quick scan of the 'Run' registry key for new entries."""
    key_name = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    baseline_file = r"C:\DeltaX\Registry\Run.txt"
    baseline = read_file(baseline_file)
    
    current, change_time = read_registry_key(key_name)
    new_values = [value for value in current.values() if value not in baseline]

    if new_values:
        print(f"\n{len(new_values)} new values have been added.")
        for value in new_values:
            print(f"@ NEW VALUE @ {value}")

        update = input(f"Would you like to update the baseline file? [Y/N] > ")
        if update.upper() == 'Y':
            update_file(current, baseline_file)
            print(f"Baseline updated with {len(new_values)} new entries.")
            print(f"Change time: {change_time}")
    else:
        print("\nNo new entries found - Current data matches baseline.")
        print(f"Change time: {change_time}")

def analyze_key():
    """Analyze connected USB devices and display relevant information."""
    temp = "VID_(.+)&PID_(.+)"
    results = []
    vendors = {}
    devices = 0

    try:
        handle = OpenKey(HKEY_LOCAL_MACHINE, USB)
        i = 0
        while True:
            key_name = EnumKey(handle, i)
            results.append(key_name)
            if re.match(r'VID*', key_name):
                devices += 1
                vid_pid = re.search(temp, key_name)
                vid, pid = vid_pid.group(1), vid_pid.group(2)
                vendors[vid] = vendors.get(vid, 0) + 1
            i += 1
    except WindowsError:
        pass

    print("Devices connected:")
    for result in results:
        print(result)
    print(f"\nTotal of {devices} devices were connected to this host.")
    
    print("\nVendor list:")
    for vendor, count in vendors.items():
        print(f"{vendor}: {count} devices")

    last_device_time = translate_reg_time(handle)
    print(f"Last device connection time: {last_device_time}")
    print(f"{datetime.now() - last_device_time} ago")

    for result in results:
        key = OpenKey(HKEY_LOCAL_MACHINE, USB + "\\" + result)
        key_time = translate_reg_time(key)
        print(f"{result}\nChanged at {key_time}")

def main():
    """Main function to drive the DeltaX tool."""
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'quickscan':
        key_delta_quick()
    else:
        print('- - - Delta X - - -')
        print('Please select an action:')
        opt = input('[1] Analyze Connected Devices\n[2] Show Key Delta\n> ')
        if opt == '1':
            analyze_key()
        elif opt == '2':
            show_key_delta()
        else:
            print('Invalid Selection!')

if __name__ == '__main__':
    main()

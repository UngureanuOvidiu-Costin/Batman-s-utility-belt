import winreg
import csv
import argparse
import time
import os
import sys

# Default output file name
registry_data = "registry_data.csv"

# Create the dictionary object to hold the registry keys
keys = dict()

# Building and returning a registry dictionary/HashMap to store the registry keys handlers
def open_registry_keys():
    keys["HKEY_CLASSES_ROOT"] = winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, '')
    keys["HKEY_CURRENT_USER"] = winreg.OpenKey(winreg.HKEY_CURRENT_USER, '')
    keys["HKEY_LOCAL_MACHINE"] = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, '')
    keys["HKEY_USERS"] = winreg.OpenKey(winreg.HKEY_USERS, '')
    keys["HKEY_CURRENT_CONFIG"] = winreg.OpenKey(winreg.HKEY_CURRENT_CONFIG, '')
    return keys


# Recursive function that iterates through each key to get it's subkeys and values
def enumerate_keys(key, current_path, csv_writer, verbose):
    # To iterate through a key, we need to use an index that is 0 indexed
    index_value = 0
    # We don't know from the start how many values the key has so we loop infinitely till we throw an exception
    while True:
        try:
            # From the current index we retreive the value name, data and type
            value_name, value_data, value_type = winreg.EnumValue(key, index_value)
            # To the current path we add the value name such that we have the complete path to the value
            full_path = f"{current_path}\\{value_name}"

            # If verbose is true, then we print it to the terminal
            if verbose is True:
                print(f"Full Path: {full_path}")
                print(f"Value Name: {value_name}")
                print(f"Value Data: {value_data}")
                print(f"Value Type: {value_type}\n")

            # Add the data to the csv
            csv_writer.writerow([full_path, value_type, value_data])
            # Increase the index
            index_value += 1

        # If we get this exception, this means that there are no more values so we stop the loop
        except OSError:
            break

    # Again, we dont know how many subkeys are there so we must use an index to loop through the subkeys till we throw and exception
    try:
        # The index must be 0 indexed at the beginning
        index_key = 0
        # Infinite loop
        while True:
            # We extract the subkey name
            subkey_name = winreg.EnumKey(key, index_key)
            # We add the subkey name to the current path name
            new_path = f"{current_path}\\{subkey_name}"

            # We create a new key which is the subkey for the current key
            next_key = winreg.OpenKey(key, subkey_name)
            # Recursive approach for the subkey
            enumerate_keys(next_key, new_path, csv_writer, verbose)
            # Increase the index till we get an exception
            index_key += 1

    # If we get an exception, then there are no more subkeys for the current key
    except OSError:
        # We stop the loop
        pass

    # We close the opened current key
    winreg.CloseKey(key)


def start_venom_shot(registry_data, verbose):
    with open(registry_data, mode='w', newline='', encoding='utf-8') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(["RegistryKey", "ValueType", "ValueData"])
        enumerate_keys(keys["HKEY_USERS"], "HKEY_USERS", csv_writer, verbose)
        enumerate_keys(keys["HKEY_CLASSES_ROOT"], "HKEY_CLASSES_ROOT", csv_writer, verbose)
        enumerate_keys(keys["HKEY_CURRENT_USER"], "HKEY_CURRENT_USER", csv_writer, verbose)
        enumerate_keys(keys["HKEY_LOCAL_MACHINE"], "HKEY_LOCAL_MACHINE", csv_writer, verbose)
        enumerate_keys(keys["HKEY_CURRENT_CONFIG"], "HKEY_CURRENT_CONFIG", csv_writer, verbose)


def prompt_user(file_path):
    while True:
        response = input(f"The file '{file_path}' already exists. Do you want to overwrite it? (Y/Yes to continue, N/No to exit): ")
        if response.lower() in ['y', 'yes']:
            print("File will be overwritten.")
            return True
        elif response.lower() in ['n', 'no']:
            print("Operation aborted.")
            sys.exit(0)
        else:
            print("Invalid response. Please enter Y/Yes or N/No.")


def compare_registry_files(file1, file2):
    return


def main():

    # Create the dictionary to store the
    keys = open_registry_keys()

    # Create the parser
    parser = argparse.ArgumentParser(description="Bane takes a Venom shot to be strong enough to check the registry")

    # Add the arguments
    parser.add_argument('-v', '--verbose', action='store_true', help="Print the registry values at standard output")
    parser.add_argument('-o', '--output_file', type=str, help="The path to the file where the output will be stored")
    parser.add_argument('-c', '--compare', action='store_true', help="Compares two previous shots.\n[!]Requires `file1` and `file2` parameters")
    parser.add_argument('-f1', '--file1', type=str, help="First file which contains the registry capture before running the malware")
    parser.add_argument('-f2', '--file2', type=str, help="Second file which contains the registry capture after running the malware")
    parser.add_argument('-f', '--force', action='store_true', help="Force to overwrite existing files")

    # Parsing the arguments
    args = parser.parse_args()

    # Store the values
    verbose = args.verbose

    # If verbose is enabled, we set the variable as True, to print the output at standard output
    if verbose:
        print("[I] Verbose mode enabled")
    else:
        print("[I] Verbose mode not enabled")

    if args.output_file:
        global registry_data
        registry_data = args.output_file
        print(f"[I] Chosen output file {registry_data}")
        
        if not args.force:
            if os.path.exists(registry_data):
                prompt_user(registry_data)

    if args.compare:
        if not args.file1 or not args.file2:
            parser.error("[**ERROR**] -c flag requires -f1 and -f2 to be specified")
        else:
            print(f"[I] Started to compare {args.f1} - {args.f2}")
            # Add existence check for both files
            compare_registry_files(args.f1, args.f2)
    else:
        print(f"[I] Venom...dumping the registry to {registry_data}")
        start_time = time.time()
        print(f"[I] Started at {start_time}")
        start_venom_shot(registry_data, verbose)
        end_time = time.time()
        print(f"Estimated run time {end_time - start_time} seconds")


if __name__ == "__main__":
    main()

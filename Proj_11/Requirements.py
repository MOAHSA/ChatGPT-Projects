import subprocess
import logging
import pkg_resources

# Configure logging to display more user-friendly output
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Check if emoji support is enabled
USE_EMOJIS = True  # Set this to False to disable emoji usage

def check_if_library_installed(lib):
    """Check if a library is already installed."""
    try:
        pkg_resources.get_distribution(lib)
        return True
    except pkg_resources.DistributionNotFound:
        return False

def get_emoji(symbol):
    """Return the corresponding emoji if enabled or fallback to text."""
    if USE_EMOJIS:
        emoji_dict = {
            'success': '?',
            'skip': '?',
            'install': '??',
            'warning': '??',
            'check': '??',
            'error': '?'
        }
        return emoji_dict.get(symbol, '')
    else:
        emoji_dict = {
            'success': '[SUCCESS]',
            'skip': '[FAILED]',
            'install': '[INSTALLING]',
            'warning': '[WARNING]',
            'check': '[INSTALLED]',
            'error': '[ERROR]'
        }
        return emoji_dict.get(symbol, '')

def install_python_libraries(libraries, package_manager):
    for lib in libraries:
        # Check if the library is already installed
        if check_if_library_installed(lib):
            logging.info(f"{get_emoji('success')} '{lib}' is already installed. Skipping installation.")
            continue

        # Ask for installation method only if it's not already installed
        logging.info(f"{get_emoji('install')} Installing '{lib}'...")

        if package_manager == 'conda':
            logging.info(f"Using Conda to install '{lib}'...")
            command_conda = ["conda", "install", lib, "-y"]
            conda_result = subprocess.run(command_conda, capture_output=True, text=True)

            if conda_result.returncode != 0:
                logging.error(f"{get_emoji('error')} Failed to install '{lib}' using Conda.")
                logging.debug(f"conda error output: {conda_result.stderr}")
            else:
                logging.info(f"{get_emoji('check')} '{lib}' successfully installed using Conda.")
            continue

        if package_manager == 'other':
            custom_command = input(f"Please provide the custom command to install '{lib}': ").strip()
            logging.info(f"Using custom command to install '{lib}': {custom_command}")
            custom_result = subprocess.run(custom_command.split(), capture_output=True, text=True)

            if custom_result.returncode != 0:
                logging.error(f"{get_emoji('error')} Failed to install '{lib}' using the custom command.")
                logging.debug(f"Custom command error output: {custom_result.stderr}")
            else:
                logging.info(f"{get_emoji('check')} '{lib}' successfully installed using the custom command.")
            continue

        # Default to pip installation
        logging.info(f"Using Pip to install '{lib}'...")
        command_pip = ["pip", "install", lib]
        pip_result = subprocess.run(command_pip, capture_output=True, text=True)

        if pip_result.returncode != 0:
            logging.warning(f"{get_emoji('warning')} Pip installation failed for '{lib}'. Trying pip3...")
            command_pip3 = ["pip3", "install", lib]
            pip3_result = subprocess.run(command_pip3, capture_output=True, text=True)

            if pip3_result.returncode != 0:
                logging.error(f"{get_emoji('error')} Failed to install '{lib}' using both Pip and Pip3.")
                logging.debug(f"pip3 error output: {pip3_result.stderr}")
            else:
                logging.info(f"{get_emoji('check')} '{lib}' successfully installed using Pip3.")
        else:
            logging.info(f"{get_emoji('check')} '{lib}' successfully installed using Pip.")

def main():
    libraries = [
        "os", "datetime", "tkinter", "ttk", "tkcalendar", "scrolledtext", "json", 
        "colorchooser", "ttkthemes", "functools", "threading", "queue", "time", 
        "collections", "weakref"
    ]

    # Ask the user if they want to install libraries
    install_choice = input("Would you like to install the required libraries? (yes/no): ").strip().lower()
    if install_choice == 'no' or install_choice == 'n':
        logging.info("You chose not to install the libraries. Exiting the process.")
        return

    # Ask the user for the package manager method
    package_manager = input("Which package manager would you like to use for installation? (pip/conda/other): ").strip().lower()

    logging.info("\nStarting the library installation process...\n")
    install_python_libraries(libraries, package_manager)
    logging.info("\nLibrary installation process completed.")

    # Add input to wait for the user to press Enter before closing the program
    input('Press Enter to close the program...')

if __name__ == "__main__":
    main()

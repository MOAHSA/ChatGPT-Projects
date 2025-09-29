# Keyboard Layout Flipper Pro

A powerful tool to convert text between English and Arabic keyboard layouts with customizable hotkeys, system tray integration, and automatic startup configuration.

![Keyboard Layout Flipper Pro Interface](screenshots/interface.png)

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Keyboard Layout Mappings](#keyboard-layout-mappings)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)
- [Support](#support)

## Features

- 🔥 **System-wide Hotkey**: Convert selected text anywhere with a customizable hotkey (default: Ctrl+Shift)
- 🔄 **Auto Language Detection**: Automatically detects if text is Arabic or English
- 📝 **Manual Conversion**: Convert text manually in the application interface
- ⚙️ **Customizable Hotkey**: Change the hotkey to any combination you prefer (e.g., Ctrl+Alt+Z, Shift+Alt+M)
- 📊 **Conversion History**: Keep track of your conversions with timestamps
- 🪟 **System Tray Integration**: Minimize to system tray and access from there
- 🚀 **Run on Startup**: Option to start the application automatically when Windows starts
- 📤 **Export/Import**: Export converted text to files or import text for conversion
- 🎨 **Modern Dark UI**: Clean, modern interface with dark theme
- 🛠️ **Settings Panel**: Comprehensive settings for customization
- 🔔 **Notifications**: Status notifications for user actions
- 📋 **Clipboard Integration**: Direct clipboard conversion functionality

## Installation

### Prerequisites
- Python 3.6 or higher
- Windows OS (tested on Windows 10 and 11)

### Method 1: Using pip
1. Clone or download this repository
2. Navigate to the project directory
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
   Or install dependencies individually:
   ```
   pip install keyboard pyperclip pystray pillow
   ```
4. Run the application:
   ```
   python main.py
   ```


## Usage

### System-wide Hotkey
1. Select any text anywhere (browser, Word, etc.)
2. Press your configured hotkey (default: Ctrl+Shift)
3. The text automatically converts between English and Arabic layouts

**Note**: For best results, run the application as administrator if the hotkey doesn't work in certain applications.

### Manual Conversion
1. Type or paste text in the "Input Text" box
2. Select the source and target languages
3. (Optional) Enable "Auto-detect language" for automatic detection
4. Click "Convert" to convert the text
5. Use "Copy Output" to copy the converted text to clipboard

### Customizing the Hotkey
1. Go to "Tools" → "Settings" or click the gear icon
2. In the "Hotkey Settings" section, enter your desired hotkey combination
   - Examples: `ctrl+alt+z`, `shift+alt+m`, `ctrl+shift+1`
3. Click "Save Settings"
4. Restart the application for changes to take effect

### Configuring Startup
1. Go to "Tools" → "Settings"
2. Check "Run on Windows startup" to enable automatic startup
3. The application will now start automatically when Windows starts
4. To remove from startup, either:
   - Uncheck "Run on Windows startup" and save settings, OR
   - Click the "Remove from Startup" button

### System Tray Operations
- Right-click the system tray icon to access:
  - Show application
  - Convert clipboard
  - Enable/Disable hotkey
  - Remove from startup
  - Quit application
- Click the system tray icon to show the application

### Additional Features
- **History**: Access conversion history through "View" → "History" or the quick action button
- **Statistics**: View usage statistics through "View" → "Statistics"
- **Export/Import**: Save your converted text or load text for conversion

## Configuration

The application stores its configuration in a file named `.keyboard_flipper_config.json` in your home directory. You can manually edit this file to change settings.

### Configuration File Structure
```json
{
  "hotkey_enabled": true,
  "run_on_startup": false,
  "start_minimized": false,
  "theme": "dark",
  "show_notifications": true,
  "history_enabled": true,
  "hotkey": "ctrl+shift"
}
```

### Configuration Options
- `hotkey_enabled`: Enable or disable the system-wide hotkey
- `run_on_startup`: Automatically start the application when Windows starts
- `start_minimized`: Start the application minimized to the system tray
- `theme`: UI theme (currently only "dark" is supported)
- `show_notifications`: Show status notifications
- `history_enabled`: Enable conversion history tracking
- `hotkey`: The keyboard shortcut for system-wide conversion

### Manual Configuration
1. Close the application
2. Navigate to your home directory
3. Open `.keyboard_flipper_config.json` with a text editor
4. Modify the values as needed
5. Save the file
6. Restart the application

## Troubleshooting

### Hotkey Issues
- **Hotkey not working**: 
  - Try running the application as administrator
  - Check if the hotkey is being used by another application
  - Verify the hotkey combination in Settings
  - Restart the application after changing hotkey settings

- **Hotkey adds extra characters**: 
  - This has been fixed in the latest version with hotkey suppression
  - If you still experience this issue, please report it

- **Hotkey works in some applications but not others**: 
  - Run the application as administrator for system-wide compatibility

### Conversion Issues
- **Text not converting properly**: 
  - Make sure the correct source language is selected
  - Try using the auto-detect feature
  - Check if the text contains special characters that may not convert

### Startup Issues
- **Application not starting on startup**: 
  - Check Windows Task Manager → Startup tab
  - Make sure the "Run on Startup" option is enabled in Settings
  - Verify the application is not blocked by antivirus software
  - Check if the registry entry was created successfully

### General Issues
- **Application crashes on startup**: 
  - Check if all required dependencies are installed
  - Try deleting the configuration file to reset settings
  - Ensure you're using a compatible Python version

- **UI appears broken or elements are missing**: 
  - Try resizing the application window
  - Check if your system has the required UI libraries
  - Restart the application

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Areas for Improvement
- Additional language support
- UI enhancements
- Performance optimizations
- Bug fixes
- Documentation improvements

Please ensure your code follows the existing style and includes appropriate tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Thanks to all the open-source libraries that made this project possible
  - [keyboard](https://github.com/boppreh/keyboard) - Hook and simulate keyboard events
  - [pyperclip](https://github.com/asweigart/pyperclip) - Cross-platform clipboard module
  - [pystray](https://github.com/moses-palmer/pystray) - System tray integration
  - [Pillow](https://python-pillow.org/) - Python Imaging Library
- Inspired by the need to easily convert between English and Arabic keyboard layouts

## Keyboard Layout Mappings

The application converts between the standard QWERTY English layout and the Arabic keyboard layout. Here are some examples:

### Common Conversions
- English 'a' ↔ Arabic 'ش'
- English 'b' ↔ Arabic 'لا'
- English 'c' ↔ Arabic 'ؤ'
- English 'd' ↔ Arabic 'ي'
- English 'e' ↔ Arabic 'ث'
- English 'f' ↔ Arabic 'ب'
- English 'g' ↔ Arabic 'ل'
- English 'h' ↔ Arabic 'ا'
- English 'i' ↔ Arabic 'ه'
- English 'j' ↔ Arabic 'ت'
- English 'k' ↔ Arabic 'ن'
- English 'l' ↔ Arabic 'م'
- English 'm' ↔ Arabic 'ة'
- English 'n' ↔ Arabic 'ى'
- English 'o' ↔ Arabic 'خ'
- English 'p' ↔ Arabic 'ح'
- English 'q' ↔ Arabic 'ض'
- English 'r' ↔ Arabic 'ق'
- English 's' ↔ Arabic 'س'
- English 't' ↔ Arabic 'ف'
- English 'u' ↔ Arabic 'ع'
- English 'v' ↔ Arabic 'ر'
- English 'w' ↔ Arabic 'ص'
- English 'x' ↔ Arabic 'ء'
- English 'y' ↔ Arabic 'غ'
- English 'z' ↔ Arabic 'ئ'

The application also handles numbers and special characters appropriately.

## Support


If you encounter any issues or have questions, please [open an issue](https://github.com/your-username/keyboard-layout-flipper-pro/issues) on GitHub.

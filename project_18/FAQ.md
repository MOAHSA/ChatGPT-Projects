# Frequently Asked Questions (FAQ)

## General Questions

### What does this program do?
Keyboard Layout Flipper Pro helps you convert text between English and Arabic keyboard layouts. If you accidentally type in the wrong language, this program fixes it instantly.

### Do I need to know programming to use this?
No! This program is designed for everyone. Just follow the simple steps in the User Guide.

### Is this program free?
Yes, it's completely free to use.

### Which operating systems does it work on?
It works on Windows 10 and Windows 11. Other Windows versions might work but haven't been tested.

## Using the Program

### How do I convert text quickly?
1. Select any text (highlight it)
2. Press Ctrl+Shift at the same time
3. The text automatically converts!

### What if Ctrl+Shift doesn't work?
- Try right-clicking the system tray icon and selecting "Enable/Disable Hotkey" to make sure it's turned on
- Try running the program as administrator (right-click the program file → "Run as administrator")
- Change the hotkey in Settings to something else

### How do I change the shortcut keys?
1. Click the gear icon (⚙) in the top-right corner
2. Type your new shortcut in the "Current hotkey" box (like "Ctrl+Alt+Z")
3. Click "Save Settings"
4. Close and reopen the program

### Can I convert text without selecting it first?
Yes! Use the manual method:
1. Copy the text you want to convert (Ctrl+C)
2. Right-click the system tray icon (bottom-right corner)
3. Click "Convert Clipboard"
4. Paste the converted text anywhere (Ctrl+V)

### How do I see my previous conversions?
1. Click the gear icon (⚙)
2. Make sure "Enable conversion history" is checked
3. Click "Save Settings"
4. To view history: Click "Open History" button or go to View → History

## Startup and System Tray

### How do I make the program start automatically?
1. Click the gear icon (⚙)
2. Check "Run on Windows startup"
3. Click "Save Settings"
4. Restart your computer to test

### How do I completely close the program?
- Right-click the system tray icon (bottom-right corner)
- Click "Quit"

### What does "minimize to system tray" mean?
Instead of closing the program completely, it hides to a small icon in the bottom-right corner of your screen. This way it's still running and ready to convert text.

### How do I get the main window back?
- Click the system tray icon (bottom-right corner)
- Or right-click it and select "Show"

## Problems and Solutions

### Why does the program add extra letters when I use the hotkey?
This was a known issue that has been fixed in the latest version. Make sure you're using the newest version of the program.

### The program window is too small/too big
You can resize the window by dragging the corners or edges. The program remembers your preferred size.

### I can't find the program after minimizing it
Look in the system tray (bottom-right corner of your screen, near the clock). The program icon looks like "KB" in a blue square.

### The program crashes when I start it
- Make sure you have Python installed on your computer
- Try downloading and reinstalling the program
- Check that your antivirus software isn't blocking it

### My antivirus says this program is dangerous
This is a false positive. The program is safe, but some antivirus software mistakenly flags it because it can simulate keyboard presses. You may need to add it to your antivirus whitelist.

## Features and Customization

### What's the difference between auto-detect and manual language selection?
- Auto-detect: The program figures out if your text is English or Arabic automatically
- Manual: You tell the program which language to convert from and to

### How do I export my converted text?
1. After converting text, click "Export Text" button
2. Choose where to save the file
3. The text is saved as a .txt file you can open in any text editor

### Can I import text to convert?
Yes:
1. Click "Import Text" button
2. Select a .txt file
3. The text appears in the input box ready to convert

### What are the quick action buttons for?
- Convert Clipboard: Convert whatever text you copied last
- Open History: See all your previous conversions
- Clear History: Delete your conversion history
- Export Text: Save your converted text to a file

## Technical Questions

### Do I need to install anything?
You need Python installed on your computer. If you don't have it, download it from python.org

### Where are my settings saved?
In a file called `.keyboard_flipper_config.json` in your user home folder. You don't need to worry about this file unless you want to manually change settings.

### Can I use this with other languages?
Currently, it only works with English and Arabic. Support for other languages might be added in future versions.

### How do I update the program?
Download the newest version and replace your current files. Your settings will be preserved.

## Still Need Help?

If your question isn't answered here:
1. Read the USER_FRIENDLY_GUIDE.md file
2. Check the detailed USER_GUIDE.md file
3. Look at the README.md file for technical information
4. Contact support or open an issue on GitHub
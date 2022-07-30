# Discord Rich Presence for StarCraft II

### How to use it
1. Download Python 3.8+. Don't forget to checkbox ☑ "pip" and  ☑ "Add Python to environment variables"
2. Download the latest release
3. Extract ``release.zip`` anywhere
4. Run ``configure.bat`` to install required Python modules 
5. Open ``run.bat`` with notepad and replace "UserName" with your in-game name. It's needed to display correct player.
6. Double-click on run.bat or run it with Command Prompt

### Dependencies:
* https://github.com/qwertyquerty/pypresence
* https://github.com/psf/requests

### Instructions for setting up the project:
1. Clone the project
2. open the project in PyCharm with the default settings
3. Create a virtual environment (through settings -> project "SC2DirscordRichPresence" -> project interpreter)
4. Open the terminal in PyCharm
5. **Check that the virtual environment is activated**.
6. Update the pip:
    ```bash.
    pip install --upgrade pip
    ```
7. Install the necessary packages in the virtual environment: 
    ```bash
    pip install -r requirements.txt
    ```
8. Create a startup configuration in PyCharm (file ``run.py``)
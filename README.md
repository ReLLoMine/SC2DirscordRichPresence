#Discord Rich Presence for StarCraft II

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
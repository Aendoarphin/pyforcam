# Tool Life Utility
A utility desktop app to visualize contents of xml files. Reduces monitoring overhead for CNC machine operators.

## Synopsis
Each machine represents one url and the program makes looping data requests for each given url. The request outputs xml data which contain multiple tool numbers. These tool numbers contain values needed to be displayed onto the app GUI for the operators to see at a centralized location of the shop.

## Machine Data
The repo contains sample xml files for demonstration purposes, but this is actively being used under BMP's internal network. The [main window](./main_window.py) runs the program. Make sure to start a [server](./server/server.py) for the program to work. This project was bundled via [PyInstaller](https://pyinstaller.org/en/stable/).

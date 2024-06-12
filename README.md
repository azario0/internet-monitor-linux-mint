# Internet Usage Monitor App

This Python application monitors live internet usage and displays network statistics using tkinter for GUI, matplotlib for plotting charts, and psutil for system monitoring FOR LINUX.

## Features

- **Live Chart**: Displays live internet usage (sent and received) in megabytes per second (MB/s).
- **Process List**: Shows a list of processes currently using the network, with details on their sent and received data rates.
- **Terminate Process**: Allows terminating selected network processes directly from the GUI.
- **Network Control**: Provides a button to disconnect/reconnect the network (requires `nmcli` command-line tool).

## Requirements

- Python 3.x
- Required Python packages are listed in `requirements.txt`


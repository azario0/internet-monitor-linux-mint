import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import psutil
import os

class InternetUsageApp:
    def __init__(self, root):
        self.root = root
        self.proc_data = {}
        self.root.title("Internet Usage Monitor")
        
        # Initialize matplotlib figure and canvas for live chart
        self.figure, self.ax = plt.subplots(figsize=(5, 2.5))
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Initialize treeview for process list
        self.tree = ttk.Treeview(root, columns=('PID', 'Application', 'Sent', 'Received'), show='headings')
        self.tree.heading('PID', text='PID')
        self.tree.heading('Application', text='Application')
        self.tree.heading('Sent', text='Sent (MB/s)')
        self.tree.heading('Received', text='Received (MB/s)')
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Button to terminate selected process
        self.terminate_button = tk.Button(root, text="Terminate Selected Process", command=self.terminate_selected_process)
        self.terminate_button.pack(side=tk.BOTTOM, fill=tk.X)
        self.terminate_button.config(state=tk.DISABLED)
        
        # Button to disconnect/reconnect network
        self.button = tk.Button(root, text="Disconnect", command=self.toggle_network)
        self.button.pack(side=tk.BOTTOM, fill=tk.X)
        self.disconnect_flag = False
        
        # Initialize lists to store historical data for chart
        self.sent_history = []
        self.recv_history = []
        
        # Initialize previous network I/O counters
        self.prev_net_io = psutil.net_io_counters()
        
        # Start updating chart and treeview
        self.update_chart()
        self.update_treeview()
        
        # Bind treeview selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_treeview_select)
    
    def update_chart(self):
        current_net_io = psutil.net_io_counters()
        sent = current_net_io.bytes_sent - self.prev_net_io.bytes_sent
        recv = current_net_io.bytes_recv - self.prev_net_io.bytes_recv
        self.prev_net_io = current_net_io
        sent = round(sent / (1024 * 1024), 2)  # Convert to MB and round to 2 decimal places
        recv = round(recv / (1024 * 1024), 2)  # Convert to MB and round to 2 decimal places
        self.sent_history.append(sent)
        self.recv_history.append(recv)
        if len(self.sent_history) > 30:
            self.sent_history.pop(0)
            self.recv_history.pop(0)
        self.ax.clear()
        self.ax.plot(self.sent_history, label='Sent MB/s', color='r')
        self.ax.plot(self.recv_history, label='Received MB/s', color='b')
        self.ax.legend()
        self.ax.set_title("Live Internet Usage (MB/s)")
        self.canvas.draw()
        self.root.after(1000, self.update_chart)
    
    def update_treeview(self):
        selected_item = self.tree.selection()
        selected_pid = self.tree.item(selected_item, 'values')[0] if selected_item else None
        connections = psutil.net_connections(kind='inet')
        new_proc_data = {}
        for conn in connections:
            if conn.status == psutil.CONN_ESTABLISHED and conn.pid:
                try:
                    proc = psutil.Process(conn.pid)
                    name = proc.name()
                    net_io = proc.io_counters()
                    sent = net_io.write_bytes
                    recv = net_io.read_bytes
                    if conn.pid in self.proc_data:
                        sent_diff = (sent - self.proc_data[conn.pid]['sent']) / (1024 * 1024)
                        recv_diff = (recv - self.proc_data[conn.pid]['recv']) / (1024 * 1024)
                    else:
                        sent_diff = 0
                        recv_diff = 0
                    new_proc_data[conn.pid] = {'name': name, 'sent': sent, 'recv': recv, 'sent_diff': sent_diff, 'recv_diff': recv_diff}
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        self.proc_data = new_proc_data
        for row in self.tree.get_children():
            self.tree.delete(row)
        for pid, info in self.proc_data.items():
            sent_mb = round(info['sent_diff'], 2)  # Convert to MB and round to 2 decimal places
            recv_mb = round(info['recv_diff'], 2)  # Convert to MB and round to 2 decimal places
            self.tree.insert('', 'end', values=(pid, info['name'], sent_mb, recv_mb))
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.selection_set(selected_item)
        if selected_pid is not None:
            for item in self.tree.get_children():
                if self.tree.item(item, 'values')[0] == selected_pid:
                    self.tree.selection_set(item)
                    break
        self.root.after(1000, self.update_treeview)
    
    def toggle_network(self):
        try:
            if self.disconnect_flag:
                os.system("nmcli networking on")
                self.button.config(text="Disconnect")
            else:
                os.system("nmcli networking off")
                self.button.config(text="Reconnect")
            self.disconnect_flag = not self.disconnect_flag
        except Exception as e:
            print(f"Error toggling network: {e}")
    
    def on_treeview_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            self.terminate_button.config(state=tk.NORMAL)
        else:
            self.terminate_button.config(state=tk.DISABLED)
    
    def terminate_selected_process(self):
        selected_item = self.tree.selection()
        if selected_item:
            process_name = self.tree.item(selected_item, 'values')[1]
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] == process_name:
                    try:
                        p = psutil.Process(proc.info['pid'])
                        p.terminate()
                        print(f"Terminated process {proc.info['pid']}")
                    except Exception as e:
                        print(f"Error terminating process {proc.info['pid']}: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = InternetUsageApp(root)
    root.mainloop()

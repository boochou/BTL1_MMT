import tkinter as tk
from tkinter import Entry, Button, Text, Scrollbar, Label
import threading
from GUI_server import Server
import socket

IP = socket.gethostbyname(socket.gethostname())  # "127.0.0.1" #HOST #loopback
SERVER_PORT = 56789
ADDRESS = (IP, SERVER_PORT)

class ServerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Server GUI")

        # Initialize the server
        self.server = Server()

        # Create GUI components
        self.server_label = Label(root, text="This is the server for simple file sharing")
        self.server_label.pack(pady=5)
        self.address_label = Label(root, text=f"Server Address: IP {ADDRESS[0]} port {ADDRESS[1]}")
        self.address_label.pack(pady=10)

        self.clients_online_label = Label(root, text=f"Clients Online: {self.server.clietnts}")
        self.clients_online_label.pack(pady=10)

        self.command_entry = Entry(root, width=50)
        self.command_entry.pack(pady=10)

        self.send_button = Button(root, text="Send Command", command=self.send_command)
        self.send_button.pack(pady=10)

        self.output_text = Text(root, height=20, width=80, wrap=tk.WORD)
        self.output_text.pack(pady=10)

        # Add a scrollbar to the output text
        scrollbar = Scrollbar(root, command=self.output_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=scrollbar.set)

        # Start the thread to handle commands
        self.thread = threading.Thread(target=self.handle_command)
        self.thread.daemon = True
        self.thread.start()

    def send_command(self):
        # Get the command from the entry
        command = self.command_entry.get()

        # Display the command in the output text
        self.output_text.insert(tk.END, f">> {command}\n")
        self.command_entry.delete(0, tk.END)

        # Process the command using the server
        result = self.server.handle_command_GUI(command)

        # Display the result in the output text
        self.output_text.insert(tk.END, f"{result}\n")
        self.output_text.yview(tk.END)

        # Update the number of clients online
        self.clients_online_label.config(text=f"Clients Online: {self.server.clietnts}")

    def handle_command(self):
        try:
            while True:
                # Check if the server is still running
                if not self.server.status:
                    break

                # Process commands from the server
                command_output = self.server.connect_client()

                # Display the command output in the GUI
                if command_output:
                    self.output_text.insert(tk.END, f"{command_output}\n")
                    self.output_text.yview(tk.END)

                    # Update the number of clients online
                    self.clients_online_label.config(text=f"Clients Online: {self.server.clietnts}")
        except Exception as e:
            print(f"Error in handle_command: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    server_gui = ServerGUI(root)
    root.mainloop()

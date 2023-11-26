import tkinter as tk
from tkinter import Entry, Button, Label, StringVar
import tkinter.messagebox
from GUI_client import Client  # Assuming you have a module named 'c' with the Client class
from tkinter.simpledialog import askstring
class MyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Input Function Call")

        self.entry_label = tk.Label(root, text="Give me the IP server")
        self.entry_label.pack(pady=10)

        self.entry = Entry(root)
        self.entry.pack(pady=10)
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.call_button = Button(root, text="Connect to server", command=self.call_function)
        self.call_button.pack(pady=20)
        self.connected_frame = None
        self.signin_frame = None  # New frame for sign-in
        self.instruction_frame = None  # New frame for instructions
        self.client = None
        self.clients_frame=None
        self.clients_listbox =None
    def create_connected_frame(self):
        self.connected_frame = tk.Frame(self.root)

        # Add widgets for the connected frame
        connected_label = tk.Label(self.connected_frame, text="Connected to the server!")
        connected_label.pack(pady=10)

        # Add choice input
        self.choice_var = StringVar()
        choice_label = tk.Label(self.connected_frame, text="You need to login first (1). \nIf you don't have an account: sign up first (2).\nChoose an option:")
        choice_label.pack(pady=5)

        choice_entry = Entry(self.connected_frame, textvariable=self.choice_var)
        choice_entry.pack(pady=10)

        choice_button = Button(self.connected_frame, text="Submit", command=self.process_choice)
        choice_button.pack(pady=20)

    def create_signin_frame(self):
        self.signin_frame = tk.Frame(self.root)

        # Add widgets for the sign-in frame
        signin_label = tk.Label(self.signin_frame, text="Sign in to your account")
        signin_label.pack(pady=10)

        # Add sign-in input fields
        username_label = tk.Label(self.signin_frame, text="Username:")
        username_label.pack(pady=5)

        self.username_entry = Entry(self.signin_frame)
        self.username_entry.pack(pady=5)

        password_label = tk.Label(self.signin_frame, text="Password:")
        password_label.pack(pady=5)

        self.password_entry = Entry(self.signin_frame, show="*")  # Show '*' for password
        self.password_entry.pack(pady=5)

        # Create a separate button to trigger the sign-in process
        signin_button = Button(self.signin_frame, text="Sign In", command=self.sign_in)
        signin_button.pack(pady=20)



    # def call_function(self):
    #     user_input = self.entry.get()
    #     self.client = Client()
    #     self.client.server_status = self.client.connect_server(user_input)
    #     if self.client.server_status:
    #         # Hide the current frame
    #         self.entry_label.pack_forget()
    #         self.entry.pack_forget()
    #         self.call_button.pack_forget()

    #         # Create connected_frame after connect_server to initialize choice_var
    #         self.create_connected_frame()

    #         # Show the connected frame
    #         self.connected_frame.pack()
    #     else:
    #         tkinter.messagebox.showinfo("Error IP", "Can not access to that IP")
    def call_function(self):
        user_input = self.entry.get()
        self.client = Client()
        self.client.server_status = self.client.connect_server(user_input)

        while not self.client.server_status:
            # Continue prompting the user for a new IP until a valid one is provided or the user cancels
            user_input = askstring("Error IP", "Cannot access that IP. Enter a new IP:")
            if user_input is None:
                # User clicked Cancel, break out of the loop
                break

            self.client.server_status = self.client.connect_server(user_input)
            if self.client.server_status:
                break
        if self.client.server_status:
            # Hide the current frame
            self.entry_label.pack_forget()
            self.entry.pack_forget()
            self.call_button.pack_forget()

            # Create connected_frame after connect_server to initialize choice_var
            self.create_connected_frame()

            # Show the connected frame
            self.connected_frame.pack()
        else:
            tkinter.messagebox.showinfo("Error IP", "Cannot access the server. Exiting...")
            self.root.destroy()
    def process_choice(self):
        choice = self.choice_var.get()
        print(f"User chose: {choice}")
        if choice == "1":
            # Hide the connected frame
            self.connected_frame.pack_forget()
            # Create the sign-in frame
            self.create_signin_frame()
            # Show the sign-in frame
            self.signin_frame.pack()
        elif choice == "2":
            # Hide the connected frame
            self.connected_frame.pack_forget()
            # Create the sign-up frame
            self.create_signup_frame()
            # Show the sign-up frame
            self.signup_frame.pack()
        else:
            tkinter.messagebox.showinfo("Invalid option", "Please choose valid option")

    def sign_in(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # Add your logic for signing in with the provided username and password
        # For example, you can call a method on your Client object to perform the login
        if self.client:
            check_log_in = self.client.log_in(username, password)

            if check_log_in:
                # Logic for successful login (you can add code here if needed)
                print("Login successful!")
                self.signin_frame.pack_forget()  # Hide the current frame
                self.create_instruction_frame()  # Show the frame to choose the option
                self.instruction_frame.pack()

            else:
                # Display a message and return to the frame where the user chooses the option
                tkinter.messagebox.showinfo("Login Failed", "Invalid username or password.")
                self.signin_frame.pack_forget()  # Hide the current frame
                self.create_connected_frame()  # Show the frame to choose the option
                self.connected_frame.pack()

    def create_signup_frame(self):
        self.signup_frame = tk.Frame(self.root)

        # Add widgets for the sign-up frame
        signup_label = tk.Label(self.signup_frame, text="Sign up for a new account")
        signup_label.pack(pady=10)

        # Add sign-up input fields
        new_username_label = tk.Label(self.signup_frame, text="New Username:")
        new_username_label.pack(pady=5)

        self.new_username_entry = Entry(self.signup_frame)
        self.new_username_entry.pack(pady=5)

        new_password_label = tk.Label(self.signup_frame, text="New Password:")
        new_password_label.pack(pady=5)

        self.new_password_entry = Entry(self.signup_frame, show="*")  # Show '*' for password
        self.new_password_entry.pack(pady=5)

        # Create a separate button to trigger the sign-up process
        signup_button = Button(self.signup_frame, text="Sign Up", command=self.sign_up)
        signup_button.pack(pady=20)
    def sign_up(self):
        new_username = self.new_username_entry.get()
        new_password = self.new_password_entry.get()

        # Add your logic for signing up with the provided new username and password
        # For example, you can call a method on your Client object to perform the sign-up
        if self.client:
            # Assuming you have a method called 'sign_up' in your Client class
            check_sign_up = self.client.sign_up(new_username, new_password)

            if check_sign_up:
                # Logic for successful sign-up (you can add code here if needed)
                tkinter.messagebox.showinfo("Sign-up successful!","Please sign-in to use this app")
                # Hide the connected frame
                self.signup_frame.pack_forget()
                # Create the sign-in frame
                self.create_signin_frame()
                # Show the sign-in frame
                self.signin_frame.pack()
            else:
                # Display a message and return to the frame where the user chooses the option
                tkinter.messagebox.showinfo("Sign-up Failed", "Failed to create a new account.")
                self.signup_frame.pack_forget()  # Hide the current frame
                self.create_connected_frame()  # Show the frame to choose the option
                self.connected_frame.pack()
    def create_instruction_frame(self):
        self.instruction_frame = tk.Frame(self.root)

        # Add widgets for the instruction frame
        instruction_label = tk.Label(self.instruction_frame, text="Instructions:")
        instruction_label.pack(pady=10)

        instruction_text = "To publish a file: publish <localfile> <filenameinrepo>\n" \
                            "To download a file: fetch <filename>\n" \
                            "To delete a file: delete <filename> <pathfilename>"\
                            "To disconnect server: end"

        instruction_text_label = tk.Label(self.instruction_frame, text=instruction_text)
        instruction_text_label.pack(pady=10)

        # Add an entry box for user input
        input_label = tk.Label(self.instruction_frame, text="Enter your command:")
        input_label.pack(pady=5)

        self.command_entry = Entry(self.instruction_frame, width=50)
        self.command_entry.pack(pady=10)

        submit_button = Button(self.instruction_frame, text="Submit", command=self.process_command)
        submit_button.pack(pady=20)

    def process_command(self):
        message = self.command_entry.get()
        # Implement the logic to process the user's command
        print(f"User entered command: {message}")
        # Add your logic to handle different commands
        if message.startswith("publish"):
                    parts = message.split(" ")
                    if len(parts) == 3:
                        lname = parts[1]
                        fname = parts[2]
                        result = self.client.publish_file(lname, fname, './repo_publish')                   
                        if result:
                            tkinter.messagebox.showinfo("Publish successful.","Continue do what you want")
                            self.instruction_frame.pack_forget()  # Hide the current frame
                            self.create_instruction_frame()  # Show the frame to choose the option
                            self.instruction_frame.pack()
                        else:
                             tkinter.messagebox.showinfo("Publish fail.")
                    else:
                        print("Please enter the correct syntax!")
                        tkinter.messagebox.showinfo("Valid syntax", "Please enter the correct syntax")
        elif "fetch" in message:
                    parts = message.split(" ")
                    if len(parts) != 2:
                        tkinter.messagebox.showinfo("Valid syntax", "Please enter the correct syntax")
                    else:
                        fname = message.split(" ")[-1]
                        if not fname:
                            tkinter.messagebox.showinfo("Valid syntax", "Please enter the correct syntax")
                        else:
                            list_clients = self.client.fetch_GUI(fname)
                            if list_clients == "1":
                                tkinter.messagebox.showinfo("Failed fetch","File in your local.")
                            elif list_clients == "3":
                                tkinter.messagebox.showinfo("Failed fetch","Process error.")        
                            else:
                                self.create_clients_frame(list_clients,fname)
                                self.instruction_frame.pack_forget()  # Hide the current frame
                                self.clients_frame.pack()  # Show the frame with the list of clients 
        elif "delete" in message:
            parts = message.split(" ")
            if len(parts) == 3:
                fname = parts[1]
                fpath = parts[2]
                if fname and fpath:
                    result = self.client.delete_file(fname, fpath)                   
                    if result == "1":
                        print("File in your local.")
                    elif result == "3":
                        tkinter.messagebox.showinfo("Delete fail", "Proccess error")
                    else:
                        print("Delete file", fname, "successfully!")
                        tkinter.messagebox.showinfo("Delete successfully", "Delete successfully")
                        self.instruction_frame.pack_forget()  # Hide the current frame
                        self.create_instruction_frame()  # Show the frame to choose the option
                        self.instruction_frame.pack()
                else:
                    tkinter.messagebox.showinfo("Valid syntax", "It doesn't contain fname or fpath")
            else:
                print(len(parts))
                tkinter.messagebox.showinfo("Valid syntax", "Please enter the correct syntax")
        elif "end" in message:
            self.client.server_status = False
            self.client.new_socket.close()
            self.client.stop_ping_thread()
            self.root.destroy()       
        else:
            tkinter.messagebox.showinfo("Valid syntax", "Please enter the valid option")                      
    def create_clients_frame(self, clients, fname):
        self.clients_frame = tk.Frame(self.root)

        clients_label = tk.Label(self.clients_frame, text="Available Clients:")
        clients_label.pack(pady=10)

        # Use a Listbox to display the list of clients
        self.clients_listbox = tk.Listbox(self.clients_frame)
        for client_info in clients:
            self.clients_listbox.insert(tk.END, f"{client_info['username']} - {client_info['ipaddr']}:{client_info['port']}")

        self.clients_listbox.pack(pady=20)

        # Use lambda to pass parameters to the select_client method
        select_button = Button(self.clients_frame, text="Select Client", command=lambda: self.select_client(fname))
        select_button.pack(pady=10)

    def select_client(self, fname):
        selected_index = self.clients_listbox.curselection()
        if selected_index:
            # Retrieve the selected client information from the list
            selected_client_info = self.clients_listbox.get(selected_index)

            # Split the selected client information to get individual components
            selected_client_components = selected_client_info.split(" - ")

            # Extract username, ipaddr, and port from the selected components
            selected_username = selected_client_components[0]
            selected_ipaddr_port = selected_client_components[1].split(":")
            selected_ipaddr = selected_ipaddr_port[0]
            selected_port = selected_ipaddr_port[1]
            selected_port_num = int(selected_port) + 1
            addr = (selected_ipaddr, selected_port_num)
            print(f"Selected client: Username={selected_username}, IP={selected_ipaddr}, Port={selected_port_num}")
            
            if self.client.fetch_GUI_P2P(fname, addr):
                tkinter.messagebox.showinfo("Successful fetching", "Download successful!!!!")
            else:
                tkinter.messagebox.showinfo("Failed fetching", "Please try again")

            # Destroy the clients_frame widget
            self.clients_frame.destroy()

            # Create the instruction frame
            self.create_instruction_frame()

            # Show the frame to choose the option
            self.instruction_frame.pack()

        else:
            print("No client selected.")

    def on_close(self):
            if self.client:
                # Add any cleanup or finalization logic you need before closing the application
                self.client.server_status = False
                self.client.new_socket.close()
                self.client.stop_ping_thread()

            self.root.destroy()
if __name__ == "__main__":
    root = tk.Tk()
    my_gui = MyGUI(root)
    root.mainloop()

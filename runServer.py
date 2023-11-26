from server import Server
import threading

server = Server()

def help_list():
    print("To see the list file of an client: discover <username>")
    print("To check active status of client: ping <username>")
    print("To add client: add <username> <passwword>")
    print("To delete client: delete <username>")
    print("To shutdown server: end")
    
def handle_command():
    try:
        while True:
            message = input("Input command: ")

            if "ping" in message:
                # Extract username from the command
                parts = message.split(" ")
                if len(parts) == 2:
                    username = parts[1]
                    ping_result = server.ping_client(username)
                    if ping_result:
                        print(f"{username} is alive.")
                    else:
                        print(f"{username} is not responding.")
                else:
                    print("Invalid ping command format. Usage: ping <username>")
            elif "discover" in message:
                username = message.split(" ")[-1]
                list_file = server.discover(username)
                if list_file:
                    print(f"Files for user {username}: {list_file}")
                else:
                    print(f"No files found for user {username} or an error occurred during discovery.")
            elif "add" in message:
                parts = message.split(" ")
                if len(parts) == 3:
                    username = parts[1]
                    password = parts[2]
                    add_result = server.add_client(username, password)
                    if add_result == "1":
                        print("Successful to add new client with username :", username, "and password: ", password)
                    elif add_result == "3":
                        print("Failed to add new client")
                else:
                    print("Invalid add command format. Usage: add <username> <password>")
            elif "delete" in message:
                parts = message.split(" ")
                if len(parts) == 2:
                    username = parts[1]
                    delete_result = server.delete_client(username)
                    if delete_result == "1":
                        print("Successful to delete client with username :", username)
                    elif delete_result == "3":
                        print("Failed to delete client")
                else:
                    print("Invalid add command format. Usage: delete <username>")
            elif "end" in message:
                server.status = False
                server.socket.close()
                break
    except:
        print("a")

help_list()

thread = threading.Thread(target=handle_command)

thread.daemon = False

thread.start()

server.connect_client()
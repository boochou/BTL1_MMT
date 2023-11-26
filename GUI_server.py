import os
import socket
import threading
import sqlite3
import json
import hashlib
import mysql.connector

IP = socket.gethostbyname(socket.gethostname()) #"127.0.0.1" #HOST #loopback
SERVER_PORT = 56789
ADDRESS = (IP, SERVER_PORT)
FORMAT = "UTF-8"
TEMP_USERNAME = 'na'

class Server:
    PING_MESSAGE = "PING"
    PONG_MESSAGE = "PONG"
    #start the server
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(ADDRESS)
        self.socket.listen() #waiting to client
        
        self.can_publish = True
        self.status = True
        self.clietnts = 0
        self.can_fetch = True
        #self.client_username = ""
        
        print("--- Server side:", IP, ":", SERVER_PORT, "---")

    def handle_command_GUI(self,message):
        try:
            while True:
                #message = input("Input command: ")

                if "ping" in message:
                    # Extract username from the command
                    parts = message.split(" ")
                    if len(parts) == 2:
                        username = parts[1]
                        ping_result = self.ping_client(username)
                        if ping_result:
                            return f"{username} is alive.\n"
                        else:
                            return f"{username} is not responding."
                    else:
                        return "Invalid ping command format. Usage: ping <username>"
                elif "discover" in message:
                    username = message.split(" ")[-1]
                    list_file = self.discover(username)
                    if list_file:
                        return f"Files for user {username}: {list_file}"
                    else:
                        return f"No files found for user {username} or an error occurred during discovery."
                elif "add" in message:
                    parts = message.split(" ")
                    if len(parts) == 3:
                        username = parts[1]
                        password = parts[2]
                        add_result = self.add_client(username, password)
                        if add_result == "1":
                            return f"Successful to add new client with username : {username}, and password: {password} "
                        elif add_result == "3":
                            return "Failed to add new client"
                    else:
                        return "Invalid add command format. Usage: add <username> <password>"
                elif "delete" in message:
                    parts = message.split(" ")
                    if len(parts) == 2:
                        username = parts[1]
                        delete_result = self.delete_client(username)
                        if delete_result == "1":
                            return f"Successful to delete client with username : {username}"
                        elif delete_result == "3":
                            return "Failed to delete client"
                    else:
                        return "Invalid add command format. Usage: delete <username>"
                elif "end" in message:
                    self.status = False
                    self.socket.close()
                    return "Server is off"
                    break
        except:
            return "There are something wrong"

    def handle_client(self, conn, addr):
        print(f"New client connected: {addr}")
        #username = self.handle_login(conn, addr)
        while True:
            try:
                message = conn.recv(1024).decode(FORMAT)
                if not message:
                    break
                if message == "CONNECT":
                    conn.send("RESPONSE 200".encode(FORMAT))
                elif message == "SIGNUP":
                    self.handle_signup(conn, addr)
                elif message == "SIGNIN":
                    self.handle_login(conn, addr)
                elif message == "707 EXIT":
                    self.clietnts -= 1 #client disconnect
                    conn.close()
                    break
                elif "ASK" in message:
                    if message == "ASK _PUBLISH":
                        if self.can_publish == True:
                            conn.send("You can publish file".encode(FORMAT))
                            mess = conn.recv(1024).decode(FORMAT)
                            mess = json.loads(mess)
                            client_username, lname, fname, fpath = mess["username"], mess["lname"], mess["fname"], mess["fpath"]
                            ipaddr = addr[0]
                            #port = addr[1]
                            print(str(mess))
                            self.handle_publish(client_username, ipaddr, fname, fpath)
                        else:
                            conn.send("You can't publish any file.".encode(FORMAT))
                    elif message == "ASK _FILE":
                        conn.send("File name to fetch?".encode(FORMAT))
                        fname_username = conn.recv(1024).decode(FORMAT)
                        fname_username = json.loads(fname_username)
                        file_name, client_username = fname_username
                        list_clients = self.discover_file(file_name, client_username)
                        try:
                            db = mysql.connector.connect(user='root', password='123456', host='localhost', database='mmt_db')
                            mycursor = db.cursor()
                            query = f"SELECT username FROM account WHERE fname = '{file_name}';"
                            mycursor.execute(query)
                            results = mycursor.fetchall()
                            print(results)
                            print(client_username)
                            if results:
                                for result in results:
                                    if result[0] == client_username:
                                        conn.send("You cannot fetch existed file!".encode(FORMAT))
                                        self.can_fetch = False
                                        break
                            if self.can_fetch:
                                send = json.dumps(list_clients)
                                conn.send(send.encode(FORMAT))
                        except Exception as e:
                            print(f"Error during access database: {e}")
                        finally:
                            mycursor.close()
                            db.close()
                elif message == "FETCH_SUCCESSFULLY":
                    conn.send("Progressing update database.".encode(FORMAT))
                    mess = conn.recv(1024).decode(FORMAT)
                    mess = json.loads(mess)
                    client_username, fname, fpath = mess["username"], mess["fname"], mess["fpath"]
                    ipaddr = addr[0]
                    print(str(mess))
                    self.handle_publish(client_username, ipaddr, fname, fpath)
                elif message == "DELETE":
                    conn.send("File name to delete?".encode(FORMAT))
                    fname_username = conn.recv(1024).decode(FORMAT)
                    fname_username = json.loads(fname_username)
                    file_name, client_username = fname_username
                    # Inform the client to proceed with the local deletion
                    conn.send("DELETE_LOCAL".encode(FORMAT))

                    # Wait for the client to notify about the success or failure of local deletion
                    local_deletion_status = conn.recv(1024).decode(FORMAT)

                    if local_deletion_status == "DELETE_SUCCESS":
                        deletion_success = self.handle_client_delete_file(file_name, client_username)

                        if deletion_success:
                            conn.send("DELETE_SUCCESS".encode(FORMAT))
                        else:
                            conn.send("DELETE_FAIL".encode(FORMAT))
                    else:
                        print(f"Client failed to delete file '{file_name}' locally.")
                    
            except:
                print(str(message))
                self.clietnts -= 1 #client disconnect
                conn.close()
                break
                
        
    def connect_client(self):
        while self.status: #server is starting
            try:
                conn, addr = self.socket.accept() #accept connection of client
                #print(f"New connection from: {addr}")
                thread = threading.Thread(target=self.handle_client, args=(conn, addr, ))
                thread.daemon = False
                thread.start()
                self.clietnts += 1 #increase number of connected clients by 1
            except:
                #add some catch error
                break
    
    def add_to_database(self, username, passw, port, ipaddr, fname, fpath):
        db = mysql.connector.connect(user = 'root', password='123456', host = 'localhost', database = 'mmt_db')
        mycursor = db.cursor()
        query = f"INSERT INTO account (username, pass, ipaddr, fname, fpath) VALUES (%s, %s, %s, %s, %s)"
        values = (username, passw, ipaddr, fname, fpath)

        try:
            mycursor.execute(query, values)
            db.commit()
            print("Successfully added to the database")
        except Exception as e:
            print(f"Error adding to the database: {e}")
            db.rollback()
        finally:
            mycursor.close()
            db.close()
    
    def handle_publish(self, username, ipaddr, fname, fpath):
        #a_port = port
        a_username = username
        a_ipaddr = ipaddr
        a_fname = fname
        a_fpath = fpath
        try:
            self.add_to_database(a_username, '1234', '', a_ipaddr, a_fname, a_fpath)
            print("Successfully add to database")
        except:
            print("Unsuccessfully add to database")
    
    def ping_client(self, username):
        try:
            db = mysql.connector.connect(user='root', password='123456', host='localhost', database='mmt_db')
            mycursor = db.cursor()

            query = f"SELECT * FROM account WHERE username = '{username}' AND fname = '_'"
            mycursor.execute(query)
            result = mycursor.fetchone()

            if result:
                client_ip = result[3]
                client_port = result[2] + 1
                
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_address = (client_ip, client_port)
                
                client_socket.settimeout(5)

                try:
                    client_socket.connect(client_address)
                    client_socket.send(self.PING_MESSAGE.encode(FORMAT))
                    response = client_socket.recv(1024).decode(FORMAT)

                    if response == self.PONG_MESSAGE:
                        print(f"{username} is alive")
                        return True
                    else:
                        print(f"{username} is not responding")
                        self.clietnts-=1
                        return False

                except Exception as e:
                    print(f"Error pinging {username}: {e}")
                    return False

                finally:
                    client_socket.close()

            else:
                print(f"User {username} not found in the database")
                return False

        except Exception as e:
            print(f"Error pinging {username}: {e}")
            return False

        finally:
            #mycursor.fetchall()
            mycursor.close()
            db.close()

    def discover(self, username):
        list_file = []
        try:
            db = mysql.connector.connect(user='root', password='123456', host='localhost', database='mmt_db')
            mycursor = db.cursor()
            query = f"SELECT fname FROM account WHERE username = '{username}' AND fname != '_';"
            mycursor.execute(query)
            result = mycursor.fetchall()
            list_file = [item[0] for item in result]
        except Exception as e:
            print(f"Error during discovery: {e}")
        finally:
            mycursor.close()
            db.close()
        return list_file
    
    def handle_login(self, conn, addr):
        conn.send("Username: ".encode(FORMAT))
        username = conn.recv(1024).decode(FORMAT)
        conn.send("Password: ".encode(FORMAT))
        password = conn.recv(1024).decode(FORMAT)
        #hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            db = mysql.connector.connect(user='root', password='123456', host='localhost', database='mmt_db')
            mycursor = db.cursor()

            query = "SELECT * FROM account WHERE fname = '_' AND username = %s AND pass = %s"
            #values = (username, hashed_password)
            values = (username, password)
            mycursor.execute(query, values)

            if mycursor.fetchall():
                conn.send("Login successful.".encode(FORMAT))
                self.can_publish = True
                
                #self.client_username = username
        
                # update ip and port for client in database
                (login_ip, login_port) = addr
                try:
                    update_query = f"UPDATE account SET _port = %s, ipaddr = %s WHERE username = '{username}' AND fname = '_'"
                    mycursor.execute(update_query, (login_port, login_ip))
                    db.commit()
                except Exception as e:
                    print(f"Error adding to the database: {e}")
                    db.rollback()
                #return username
            else:
                conn.send("Login fail.".encode(FORMAT))
                #return None
        except Exception as e:
            print(f"Error during login: {e}")
            #return None
        finally:
            mycursor.close()
            db.close()
    
    def handle_signup(self, conn, addr):
        conn.send("Username: ".encode(FORMAT))
        username = conn.recv(1024).decode(FORMAT)
        conn.send("Password: ".encode(FORMAT))
        password = conn.recv(1024).decode(FORMAT)

        if username and password:
            try:
                db = mysql.connector.connect(user='root', password='123456', host='localhost', database='mmt_db')
                mycursor = db.cursor()

                # Check if the username already exists
                mycursor.execute(f"SELECT username FROM account WHERE username = '{username}'")
                existing_user = mycursor.fetchone()

                if existing_user:
                    conn.send("Signup fail. Username already exists.".encode(FORMAT))
                else:
                    # Insert the new user into the database
                    mycursor.execute("INSERT INTO account (username, pass, fname) VALUES (%s, %s, %s)", (username, password, '_'))
                    db.commit()
                    conn.send("Signup successfully.".encode(FORMAT))
                    self.can_publish = True

            except Exception as db_error:
                print(f"Database error during signup: {db_error}")
                conn.send("Error during signup. Database issue.".encode(FORMAT))

            finally:
                mycursor.close()
                db.close()
    
    def discover_file(self, fname, client_username):
        list_clients = []
        try:
            db = mysql.connector.connect(user='root', password='123456', host='localhost', database='mmt_db')
            mycursor = db.cursor()
            query = "SELECT username, ipaddr, _port FROM account WHERE fname = '_' AND username IN (SELECT username FROM account WHERE fname = %s) AND username <> %s;"
            mycursor.execute(query, (fname, client_username))

            results = mycursor.fetchall()
            
            for result in results:
                username, ipaddr, port = result
                # Check if the client is alive using the ping_client method
                if self.ping_client(username):
                    list_clients.append({"username": username, "ipaddr": ipaddr, "port": port})
            print(list_clients)

        except Exception as e:
            print(f"Error during discovery: {e}")
        finally:
            mycursor.close()
            db.close()
        return list_clients
    
    def handle_client_delete_file(self, fname, username):
        try:
            db = mysql.connector.connect(user='root', password='123456', host='localhost', database='mmt_db')
            mycursor = db.cursor()

            # Check if the file exists for the user
            query = f"SELECT * FROM account WHERE username = '{username}' AND fname = '{fname}';"
            mycursor.execute(query)
            result = mycursor.fetchone()

            if result:
                # Delete the file entry from the database
                delete_query = f"DELETE FROM account WHERE username = '{username}' AND fname = '{fname}';"
                mycursor.execute(delete_query)
                db.commit()
                print(f"File '{fname}' deleted for user '{username}'.")
                return True
            else:
                print(f"File '{fname}' does not exist for user '{username}'.")
                return False

        except Exception as e:
            print(f"Error during file deletion: {e}")
            return False

        finally:
            mycursor.close()
            db.close()
            
    def add_client(self, username, password):
        try:
            with mysql.connector.connect(user='root', password='123456', host='localhost', database='mmt_db') as db:
                with db.cursor() as mycursor:
                    # Check if the username already exists
                    mycursor.execute(f"SELECT username FROM account WHERE username = '{username}'")
                    existing_user = mycursor.fetchone()

                    if existing_user:
                        print("Username already exists.")
                        return "3"
                    else:
                        # Insert the new user into the database
                        mycursor.execute("INSERT INTO account (username, pass, fname) VALUES (%s, %s, %s)", (username, password, '_'))
                        db.commit()
                        self.can_publish = True
                        return "1"

        except mysql.connector.Error as db_error:
            print(f"Database error during add new client: {db_error}")
            return "3"

    def delete_client(self, username):
        try:
            with mysql.connector.connect(user='root', password='123456', host='localhost', database='mmt_db') as db:
                with db.cursor() as mycursor:
                    # Check if the username exists
                    mycursor.execute(f"SELECT * FROM account WHERE username = '{username}'")
                    existing_user = mycursor.fetchone()

                    if existing_user:
                        # Delete the user from the database
                        mycursor.execute(f"DELETE FROM account WHERE username = '{username}'")
                        db.commit()
                        return "1"  # Deletion successful
                    else:
                        print(f"User with username '{username}' not found.")
                        return "3"  # User not found

        except mysql.connector.Error as db_error:
            print(f"Database error during delete client: {db_error}")
            return "3"  # Error during deletion

    def __del__(self):
        self.status = False
        print("Server off !!")





        
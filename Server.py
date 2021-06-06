from socket import *
from threading import *
import tqdm
import os

clients = set()

BUFFER_SIZE = 1024
SEPARATOR = "<SEPARATOR>"

""" This function is for inserting users into database and updating it when needed"""
def updateFile(fileName,cName,param):
    with open(fileName, 'r') as f:
        lines = []
        for line in f:
            if line.startswith(param):
                split_line = line.split()
                res = len(split_line) >= 4
                if res == False :
                    split_line.insert(200, cName)
                    lines.append(' '.join(split_line) + '\n')
                else:
                    split_line[3] = cName
                    lines.append(' '.join(split_line) + '\n')
            else:
                lines.append(line)

    with open(fileName, 'w') as f:
        for line in lines:
            f.write(line)

def insertSelected(fileName):
    with open(fileName, 'r') as file:
        lines = []
        for line in file:
            split_line = line.split()
            if 'SELECTED=0' in split_line:
                lines.append(' '.join(split_line) + '\n')
            elif 'SELECTED=1' in split_line:
                lines.append(' '.join(split_line) + '\n')
            else:
                split_line.insert(200, 'SELECTED=0')
                lines.append(' '.join(split_line) + '\n')
    with open(fileName, 'w') as f:
        for line in lines:
            f.write(line)

def checkSelected():
    with open('Information.txt','r') as file:
        found=""
        for line in file:
            if "SELECTED=1" in line:
                found = line.split(' SELECTED')[0]

        return found

def changeMode():
    with open('textOrAttachment.txt','w') as file:
        file.write("Mode=1")


def checkMode():
    with open('textOrAttachment.txt', 'r') as file:
     first_line = file.readline()
     if first_line=="Mode=1":
         return True
     else:
         return False

def clientThread(clientSocket, clientAddress):
    connected = True
    while connected==True:

        if checkMode():
            message = clientSocket.recv(1024).decode("utf-8")
            clientName = message.split(':')[0].replace('joined', '')
            originalMsg = message.replace(clientName+ ": ", "")
            updateFile("Information.txt", clientName, str(clientAddress))
            print(clientAddress[0] + ":" + str(clientAddress[1]) + " says: " + message)
            for client in clients:
                if str(client.getpeername()) == checkSelected():
                    print(checkMode())
                    client.send(message.encode("utf-8"))

            if originalMsg == "Disconnect":
                f = open("Information.txt")
                output = []
                for line in f:
                    if not str(clientAddress) in line:
                        output.append(line)
                f.close()
                f = open("Information.txt", 'w')
                f.writelines(output)
                f.close()
                clients.remove(clientSocket)
                for client in clients:
                    client.send((clientName + " Disconnected from Server").encode("utf-8"))
                print(str(clientAddress) + " disconnected")
                break

        else:

            received = clientSocket.recv(BUFFER_SIZE).decode()
            filename, filesize = received.split(SEPARATOR)
            # remove absolute path if there is
            filename = os.path.basename(filename)
            # convert to integer
            filesize = int(filesize)
            progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
            with open("filename.zip", "wb") as f:
                for _ in progress:
                    bytes_read = clientSocket.recv(BUFFER_SIZE)
                    if len(bytes_read)<BUFFER_SIZE:
                        break
                    f.write(bytes_read)
                    progress.update(len(bytes_read))

            for client in clients:
                if str(client.getpeername()) == checkSelected():
                    print(checkMode())
                    client.send(("Received the File ").encode("utf-8"))
                    changeMode()

    clientSocket.close()

hostSocket = socket(AF_INET, SOCK_STREAM)
hostSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR,1)

hostIp = "127.0.0.1"
portNumber = 7500
hostSocket.bind((hostIp, portNumber))
hostSocket.listen()
print ("Waiting for connection...")


while True:
    clientSocket, clientAddress = hostSocket.accept()
    clients.add(clientSocket)
    print ("Connection established with: ", clientAddress[0] + ":" + str(clientAddress[1]))
    """
    for client in clients:
        print(client.getpeername())
    """
    #writing client's ip to a file
    file1 = open("Information.txt", "a")
    file1.write(str(clientAddress) + "\n")
    file1.close()
    insertSelected('Information.txt')

    file2 = open("textOrAttachment.txt",'w')
    file2.write("Mode=1")
    file2.close()


    thread = Thread(target=clientThread, args=(clientSocket, clientAddress, ))
    thread.start()


import tkinter as tk
from socket import *
from threading import *
from tkinter import filedialog
from time import time
import tqdm
import os
from tkinter import messagebox


clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

hostIp = "127.0.0.1"
portNumber = 7500
clientSocket.connect((hostIp, portNumber))

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 1024

buttons = []

def callback(event):
 senders_name = nameSection.get().strip() + ": "
 data = user_entry.get().strip()
 message = (senders_name + data).encode('utf-8')
 T.insert('end', "\n"+message.decode('utf-8'))
 clientSocket.send(message)
 user_entry.delete(0,tk.END)


def checkAvailable(name):
    with open("Information.txt",'r') as f:
        contents = f.read()
        if name not in contents:
            return True
        else:
            return False

def when_L1_is_Pressed():
    if checkAvailable(nameSection.get()):
        nameSection.config(state='disabled')
        clientSocket.send((nameSection.get() + " joined").encode('utf-8'))
    else:
        messagebox.showinfo("Error", "This name is taken, Choose another one")


def changeName():
 nameSection.config(state='normal')
 nameSection.delete(0, 'end')



def clientIconFunc(counter,address):
    selectedButton = buttons[counter]
    if selectedButton['relief'] == 'raised':
        selectedButton.config(relief='sunken')
    else:
        selectedButton.config(relief='raised')
    ZeroToOnesToZero(address)

def ZeroToOnesToZero(buttName):
    with open('Information.txt', 'r') as file:
        lines = []
        for line in file:
            if line.startswith(buttName):
                #change that fucker to one
                split_line = line.split()
                split_line[2] = "SELECTED=1"
                lines.append(' '.join(split_line) + '\n')
            else:
                #change rest of em' to zero
                split_line = line.split()
                if "SELECTED=1" in line:
                    split_line[2] = "SELECTED=0"
                    lines.append(' '.join(split_line) + '\n')
                else:
                    lines.append(line)

    with open('Information.txt', 'w') as f:
        for line in lines:
            f.write(line)


def addClientButton():
    file2= open("Information.txt", "r")
    lines = file2.readlines()
    vertical = 10
    horizontal = 10
    COUNT=0
    for line in lines:
        NEW=line.split('SELECTED')[0]
        if 'SELECTED=0' in line:
            getName = line.partition('SELECTED=0')[2]
        else:
            getName = line.partition('SELECTED=1')[2]

        clientButton = tk.Button(window, text = getName, relief='raised', command= lambda name=NEW,count=COUNT: clientIconFunc(count,name))
        clientButton.place(x=horizontal,y=vertical)
        vertical+=50
        buttons.append(clientButton)
        COUNT=COUNT+1

def onRefresh():

    addClientButton()

def changeMode():
    with open('textOrAttachment.txt','w') as file:
        file.write("Mode=2")


def openAttachment():
  senders_name = nameSection.get().strip() + ": "
  fileName= filedialog.askopenfile(initialdir="/", title="Select a file", filetype=(("Jpeg Files", ".jpg"),("All Files","*.*")))
  clientSocket.send((nameSection.get()+": " + fileName.name).encode('utf-8'))
  message = (senders_name + "Sending "+ fileName.name).encode('utf-8')
  T.insert('end', "\n" + message.decode('utf-8'))
  changeMode()
  #sdf
  filesize = os.path.getsize(fileName.name)
  clientSocket.send(f"{fileName.name}{SEPARATOR}{filesize}".encode())
  progress = tqdm.tqdm(range(filesize), f"Sending {fileName.name}", unit="B", unit_scale=True, unit_divisor=1024)
  with open(fileName.name, "rb") as f:
      for _ in progress:
          bytes_read = f.read(BUFFER_SIZE)
          if not bytes_read:
              break
          clientSocket.sendall(bytes_read)
          # clientSocket.send(bytes_read)
          progress.update(len(bytes_read))




window = tk.Tk()
window.title("Connected To: "+ hostIp+ ":"+str(portNumber))
window.geometry("745x500")

f1 = tk.Frame(window, background="salmon", width=150, height=500)
f2 = tk.Frame(window, background="gold", width=650, height=500)
f1.pack(fill=tk.BOTH, side=tk.LEFT, expand=False)
f2.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
#text box
user_entry = tk.Entry(relief=tk.RIDGE,fg="black", bg="white", width=90)
user_entry.place(x=155, y=480)
#Main Chatroom
T = tk.Text(window, height=29, width=66,bg="deep sky blue")
#T.config(state=tk.DISABLED)
window.bind('<Return>', callback)


T.place(x=160, y=5)
#Adding attachment picture and button
photo = tk.PhotoImage(file =r"images.png")
attach=tk.Button(window, text = 'Click Me !', image = photo,borderwidth=0, command= openAttachment)
attach.place(x=710, y=468)

#Adding refresh button
photo2 = tk.PhotoImage(file =r"refresh.png")
attach=tk.Button(window, text = 'Click Me !', image = photo2,borderwidth=0,command= onRefresh)
attach.place(x=710, y=10)

#name section
L1 = tk.Button(window, text="Submit Name:", command=when_L1_is_Pressed)
L1.place(x=10, y=447)
nameSection = tk.Entry(relief=tk.RIDGE,fg="black", bg="white", width=20)
nameSection.place(x=10, y=475)


#change name
L2= tk.Button(window, text="CHNG", command=changeName)
L2.place(x=100, y=447)


window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)


def recvMessage():
    while True:
        serverMessage = clientSocket.recv(1024).decode("utf-8")
        print(serverMessage)
        T.insert(tk.END, "\n"+serverMessage)


recvThread = Thread(target=recvMessage)
recvThread.daemon = True
recvThread.start()


window.mainloop()
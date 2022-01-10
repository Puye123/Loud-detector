import socket

ip_address = '192.168.1.20'
port = 18888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip_address, port))

while True:
    try:
        msg = s.recv(512)
        if len(msg) == 0:
            print("shutdown")
            break
        print(msg.decode("utf-8"))
        # ここで何か処理をする ##

        ######################

    except Exception as ex:
        print(ex)
        break

s.close()
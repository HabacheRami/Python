import socket

server="127.0.0.1"
s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

### méthode : fonction
def scanport(port):
    try:
        s.connect((server, port))         
        return True
    except:         
        return False
    s.close()
    
### Programme principal    
for port in range(0,145):   ### ou par plage 
    if scanport(port):
        print("port", port, "is open!!!!!!!!")
    else:    
        print("port", port, "is closed")
        continue
        
##--------------------------Résultat sur ma machine-------------------------
##port 135 is open !!!!
##port 445 is open !!!!
##port 843 is open !!!!
##port 3939 is open !!!!
##port 5040 is open !!!!
##port 7532 is open !!!!

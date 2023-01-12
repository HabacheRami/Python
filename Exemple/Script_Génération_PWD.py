#Exemple de génération de mot de passe
##from getpass import getpass

import random
import string
import hashlib  ### hashage, MD5, SHA...

passw = " "

#### génération des PWD hashés
def password():
    liste_de_caracteres=string.ascii_letters+string.digits
    #print('Les caratères disponibles : ', liste_de_caracteres)
    ### initialisation du pwd à générer aléatoirement
    passwd=""

    for i in range(12): ### de taille 12
        passwd+=liste_de_caracteres[random.randint(0,len(liste_de_caracteres)-1)]
    return hash(passwd)


### hashage password
def hash(passwd):
    salt="ESGI" ### pour md5
    passwd_hashé = hashlib.md5(passwd.encode()+salt.encode()).hexdigest()
    print(passwd_hashé)
    passw = passwd_hashé
    return passwd_hashé
    

### Authentification
def auth():
    res=hash("ESGI")
    for count in range(3):
        pwd = str(input("Saisissez votre mot de passe : "))
        hash_pwd = hash(pwd)
        if(hash_pwd==res):
            print("Good password")
            break
        else :
            print("Incorrect password")
            str1 = "Il vous reste plus que "
            str2 = " essaies"
            nb = 2-count
            print(str1 +  str(nb) + str2)
    return "Fin"


print (auth())

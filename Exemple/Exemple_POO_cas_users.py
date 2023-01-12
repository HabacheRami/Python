class Salarié(object):  ## qui hérite de object
    """Classe des salariés"""           # Documentation de la classe
    def __init__(self, nom, pnom):
        print ("Création d'un objet salarié...")
        self.Nom = nom
        self.Prenom=pnom
 
    def get_nom(self):                # Méthode 'get' pour retourner le nom
        return self.Nom
    def get_pnom(self):
        return self.Prenom
 
    def set_nom(self, nouveau_nom):   # Méthode 'set' pour modifier le nom
        if nouveau_nom == "":
            print ("Le nom de l'employé ne peut pas être vide!!!!")
        else:
            self.Nom = nouveau_nom
            print ("Le Nom à été modifié.") 
     
    def afficher(self):
        print (self.Nom,self.Prenom, " a été ajouté(e)")

class User(Salarié):
    def __init__(self, nom, pnom, login, pwd):
        print ("Création d'un objet User...")
        Salarié.__init__(self,nom, pnom)
        ##self.Nom = nom
        ##self.Prenom=pnom
        self.Login=login
        self.Password=pwd
    def Afficher_User(self):
        print("User : ", self.get_nom(),"", self.get_pnom())
    
 
# main, programme principal
salarié1 = Salarié(input("le nom du salarié : \n"),input("le prénom du salarié : \n"))  # Initialiser un objet de la classe vide
salarié1.afficher()               # Accéder à une méthode de la classe

User1=User(salarié1.get_nom(),salarié1.get_pnom(), "coulmi", "Mypass")
User1.Afficher_User()




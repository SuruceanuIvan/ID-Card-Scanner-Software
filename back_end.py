import pytesseract
import cv2
from datetime import datetime
import sqlite3 as sql3
import os.path

class Const:
    MYCONFIG = r'--psm 7 --oem 3'

class Imagine:
    def __init__(self, calea):
        self._calea = calea
    
    def getCalea(self):
        return self._calea

    def getCV2Image(self):
        return cv2.imread(self.getCalea())

class ImagineTools:
    def __init__(self, imagine):
        self._imagine = imagine
    
    def blackAndWhite(self):
        grayImage = cv2.cvtColor(self.getImagine(), cv2.COLOR_BGR2GRAY)

        (thresh, self._imagine) = cv2.threshold(grayImage, 127, 255, cv2.THRESH_BINARY)

    def getSeriaNumar(self):
        buletin_stanga_jos = self.getImagine()[370:404, 36:166]

        text_stanga_jos = pytesseract.image_to_string(buletin_stanga_jos, lang="ron", config=Const.MYCONFIG)

        return (text_stanga_jos[0:2], text_stanga_jos[2:-1])

    def getNames(self):
        buletin_jos_sus = self.getImagine()[330:369, 40:590]

        text_jos_sus = pytesseract.image_to_string(buletin_jos_sus, lang="ron", config=Const.MYCONFIG)

        lista_text_jos_sus = text_jos_sus.split("<")
        lista_text_jos_sus.pop()
        lista_text_jos_sus[0] = lista_text_jos_sus[0][5:]

        lista_buna = list()

        for i in range(len(lista_text_jos_sus)):
            if lista_text_jos_sus[i] != "" and lista_text_jos_sus[i] != " ":
                lista_buna.append(lista_text_jos_sus[i])

        return tuple(lista_buna)

    def getImagine(self):
        return self._imagine

class Guest:
    def __init__(self, nume, prenume, seria, numar, id=0, poza=""):
        self._nume = nume
        self._prenume = prenume
        self._seria = seria
        self._numar = numar
        self._id = id
        self._poza = poza

    def getProps(self):
        return (self.getID(), self.getNume(), self.getPrenume(), self.getSeria(), self.getNumar(), self.getPoza())

    def getNume(self):
        return self._nume
    
    def getPrenume(self):
        return self._prenume
    
    def getSeria(self):
        return self._seria
    
    def getNumar(self):
        return self._numar
    
    def getID(self):
        return self._id
    
    def getPoza(self):
        return self._poza

class DateTime:
    def __init__(self, template = "%d/%m/%Y %H:%M:%S"):
        self._template = template

    def getStamp(self):
        now = datetime.now()

        dt_string = now.strftime(self.getTemplate())
        
        return dt_string
    
    def getTemplate(self):
        return self._template

class DBHandler:
    DB_NAME = "project.db"

    def __init__(self):
        self._con = sql3.connect(DBHandler.DB_NAME)

        self._cursor = self.getConnection().cursor()

    def verifyExistentGuest(self, serie_numar):
        ver = self.getCursor().execute(f"SELECT * FROM vizitator WHERE seria='{serie_numar[0]}' AND numar='{serie_numar[1]}'")

        rezultat = ver.fetchall()

        if len(list(rezultat)):
            return list(rezultat)[0][0]
        else:
            return False
    
    def scanGuest(self, guest : Guest):
        guest_data = guest.getProps()

        if self.verifyExistentGuest((guest_data[3], guest_data[4])) == False:
            self.getCursor().execute("INSERT INTO vizitator (nume, prenume, seria, numar, poza) VALUES(?, ?, ?, ?, ?)", guest_data[1:])

            self.getConnection().commit()

            guest = Guest(*guest_data[1:-1], self.verifyExistentGuest((guest_data[3], guest_data[4])), guest_data[-1])
        else:
            guest = Guest(*guest_data[1:-1], self.verifyExistentGuest((guest_data[3], guest_data[4])), guest_data[-1])

        return guest
    
    def giveCard(self, guest, code, nr_camera):
        data_time = DateTime()

        timp = data_time.getStamp()

        self.getCursor().execute("INSERT INTO vizitator_timp (vizitator_id, numar_camerei, time_in) VALUES(?, ?, ?)", (guest.getID(), nr_camera, timp))
        self.getConnection().commit()

        self.getCursor().execute("INSERT INTO vizitator_card (vizitator_id, card_key, time_in) VALUES(?, ?, ?)", (guest.getID(), code, timp))
        self.getConnection().commit()
    
    def takeCard(self, code):
        data_time = DateTime()

        self.getCursor().execute(f"""UPDATE vizitator_timp
                SET time_out = '{data_time.getStamp()}'
                WHERE vizitator_id = (
                    SELECT vizitator_id FROM vizitator_card
                    WHERE card_key = '{code}'
                    ORDER BY time_in DESC
                    LIMIT 1
                ) AND time_in=(SELECT time_in FROM vizitator_card WHERE card_key='{code}' ORDER BY time_in DESC LIMIT 1)""")
        self.getConnection().commit()

        self.getCursor().execute(f"DELETE FROM vizitator_card WHERE card_key='{code}'")
        self.getConnection().commit()

    def getConnection(self):
        return self._con
    
    def getCursor(self):
        return self._cursor

class CardReader:
    pass

data_si_timp = DateTime()
print(data_si_timp.getStamp())
'''
img = Imagine("buletin_scanat.jpg")
img_tools = ImagineTools(img.getCV2Image())
img_tools.blackAndWhite()
print(img_tools.getSeriaNumar())
print(img_tools.getNames())

print(img_tools.getNames()[0], "-".join(img_tools.getNames()[1:]))

guest = Guest(img_tools.getNames()[0], "-".join(img_tools.getNames()[1:]), img_tools.getSeriaNumar()[0], img_tools.getSeriaNumar()[1])
print(guest.getProps())

db = DBHandler()
guest = db.scanGuest(guest)
db.giveCard(guest, "12355123")
db.takeCard("12355123")'''
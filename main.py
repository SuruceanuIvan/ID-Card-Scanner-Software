import tkinter as tk
import cv2
from tkinter import messagebox
from gpiozero import LED, Button, Servo
from time import sleep, strftime
from PIL import Image, ImageTk
import os
import back_end as bck
import card

# Configurare GPIO
led = LED(21)
sensor = Button(26)

led.on()

data_si_timp = bck.DateTime()

nr_camerei = 0

card_cheie = 0

def confirmare(adv, vizitator):
    global card_cheie

    db = bck.DBHandler()
    guest = db.scanGuest(vizitator)
    db.giveCard(guest, card_cheie, nr_camerei)

    messagebox.showinfo("Succes!", f"Datele au fost salvate cu succes!")

    adv.destroy()

def rescanare(adv):
    messagebox.showinfo("Oops, ceva nu a mers bine", f"Rescanați buletinul!")
    
    adv.destroy()

def afiseaza_date_vizitator(vizitator):
    global w, nr_camerei
    
    adv = tk.Toplevel(w)

    adv.title("Verificați datele")

    adv.geometry("1280x720")

    tk.Label(adv, text="Verificați datele:", font=("Arial", 20)).grid(row=1, column=1)
    
    tk.Label(adv, text=f"Nume: {vizitator.getNume()}", font=("Arial", 20)).grid(row=2, column=1)
    
    tk.Label(adv, text=f"Prenume: {vizitator.getPrenume()}", font=("Arial", 20)).grid(row=3, column=1)
    
    tk.Label(adv, text=f"Seria: {vizitator.getSeria()}", font=("Arial", 20)).grid(row=4, column=1)
    
    tk.Label(adv, text=f"Număr: {vizitator.getNumar()}", font=("Arial", 20)).grid(row=5, column=1)

    tk.Label(adv, text=f"Camera: {nr_camerei}", font=("Arial", 20)).grid(row=6, column=1)

    tk.Button(adv, text="Confirmă", background="green", font=("Arial", 25), command=lambda: confirmare(adv, vizitator)).grid(row=10, column=1)

    tk.Button(adv, text="Rescanare", background="yellow", font=("Arial", 25), command=lambda: rescanare(adv)).grid(row=10, column=2)


def capture_image_and_close(window, cap):
    global nr_camerei

    # Definirea numelui fișierului pe baza datei și orei curente
    image_path = f"buletin_{strftime('%Y%m%d_%H%M%S')}.jpg"
    
    # Capturăm o imagine din feed-ul live
    ret, frame = cap.read()

    if ret:
        cv2.imwrite(image_path, frame)
        messagebox.showinfo("Imagine Capturată", f"Imaginea a fost salvată!\nLuați un card și plasati-l pe cititorul de card.")
    
    nr_card = card.obtainUID()

    img = bck.Imagine("buletin_scanat.jpg")
    img_tools = bck.ImagineTools(img.getCV2Image())
    img_tools.blackAndWhite()

    guest = bck.Guest(img_tools.getNames()[0], "-".join(img_tools.getNames()[1:]), img_tools.getSeriaNumar()[0], img_tools.getSeriaNumar()[1], 0, "buletin_scanat.jpg")
    print(guest.getProps())

    vizitator = guest
    card_cheie = nr_card

    #db = bck.DBHandler()
    #guest = db.scanGuest(guest)
    #db.giveCard(guest, nr_card, nr_camerei)

    messagebox.showinfo("Card Info", f"Cardul cu nr. {nr_card} a fost asociat cu succes!.")

    # Închidem aplicația și fereastra
    cap.release()
    window.destroy()

    afiseaza_date_vizitator(guest)

def start_live_feed():
    global w
    
    # Deschidem camera
    cap = cv2.VideoCapture(0)  # 0 este de obicei camera implicită

    # Setăm rezoluția 2K (2560x1440)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)  # Lățimea imaginii (2560px)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)  # Înălțimea imaginii (1440px)

    # Creăm fereastra Tkinter
    window = tk.Toplevel(w)
    
    #window.attributes("-fullscreen", True)
    
    window.title("Feed Live de la Cameră")

    # Creăm un canvas pentru a afișa feed-ul live
    window_width = 750# Dimensiunea dorită a ferestrei
    window_height = 550
    
    #print(window_width)
    
    canvas = tk.Canvas(window, width=window_width, height=window_height)
    canvas.pack()

    # Funcția pentru a actualiza feed-ul live în fereastră
    def update_frame():
        ret, frame = cap.read()
        if ret:
            # Convertim frame-ul în format care poate fi utilizat în Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Redimensionăm imaginea pentru a se potrivi cu dimensiunea ferestrei
            image_pil = Image.fromarray(frame_rgb)
            image_resized = image_pil.resize((window_width, window_height))

            # Creăm o imagine Tkinter din imaginea redimensionată
            imgtk = ImageTk.PhotoImage(image=image_resized)
            canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            canvas.imgtk = imgtk  # Salvăm referința imaginii pentru a preveni eliberarea memoriei
        
        sensor.when_pressed = led.off

        window.after(10, update_frame)  # Actualizăm fiecare 10ms

    update_frame()

    # Creăm un buton pentru capturarea imaginii
    capture_button = tk.Button(
        window,
        text="Capturează Imagine",
        command=lambda: capture_image_and_close(window, cap),
        width=120,
        height=100,
        background="green"
    )
    
    capture_button.pack()

    # Lansează aplicația Tkinter
    window.mainloop()

def motion_detected():
    start_live_feed()  # Deschidem fereastra cu feed-ul live
    led.on()

def salveaza_camera(ic, entry):
    global nr_camerei

    nr_camerei = entry.get()

    ic.destroy()

    motion_detected()

def introducerea_camerei():
    def adauga_numar(entry, nr):
        entry.insert(tk.END, nr)

    def sterge():
        ic_entry.delete(0, tk.END)

    global w

    ic = tk.Toplevel(w)

    ic.title("Introduceți numărul camerei")

    ic.geometry("1280x720")

    ic_label = tk.Label(ic, text="Numărul camerei:", font=("Arial", 40))
    ic_entry = tk.Entry(ic, bd =5, width=20, font=("Arial", 40), justify="center")

    # Creez lista cu butoane de numere
    butoane = [
        ('1', 1, 0), ('2', 1, 1), ('3', 1, 2),
        ('4', 2, 0), ('5', 2, 1), ('6', 2, 2),
        ('7', 3, 0), ('8', 3, 1), ('9', 3, 2),
        ('0', 4, 1)
    ]

    for (text, row, col) in butoane:
        tk.Button(ic, text=text, width=10, height=4, font=("Arial", 20),
                command=lambda t=text: adauga_numar(ic_entry, t)).grid(row=row, column=col, padx=5, pady=5)

    tk.Button(ic, text="Șterge", width=10, height=4, font=("Arial", 20), background="red",
          command=sterge).grid(row=4, column=0, padx=5, pady=5)

    ic_btn = tk.Button(ic,
        text="OK",
        width=10,
        height=4,
        font=("Arial", 20),
        background="green",
        command=lambda: salveaza_camera(ic, ic_entry)
    )

    ic_label.place(relx=0.7, rely=0.1, anchor=tk.CENTER)
    ic_entry.place(relx=0.7, rely=0.25, anchor=tk.CENTER, width=600, height=105)
    ic_btn.grid(row=4, column=2, padx=5, pady=5)

def iesire():
    messagebox.showinfo("Plecare", "Plasați cardul pe cititorul de card!")

    nr_card = card.obtainUID()

    db_handler = bck.DBHandler()

    db_handler.takeCard(nr_card)

    messagebox.showinfo("Succes!", "Cardul a fost citit. Lăsați cardul acolo de unde l-ați luat!")

if __name__=="__main__":
    w = tk.Tk()

    reg_btn = tk.Button(
        w,
        text="Întrare",
        width=20,
        height=5,
        font = ("tahoma 30"),
        background="green",
        command=introducerea_camerei
    )

    # motion_detected porneste feed live

    out_btn = tk.Button(
        w,
        text="Iesire",
        width=20,
        height=5,
        font = ("tahoma 30"),
        background="blue",
        command=iesire
    )

    reg_btn.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

    out_btn.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

    w.attributes("-fullscreen", True)
    
    w.mainloop()
import tkinter as tk
import subprocess
import os
import time
import pyautogui
import pygetwindow as gw  # Für Fensterfokus

REPEAT_DELAY_MS = 100                               # Verzögerung des Motores nach dem drücken der Pfeiltasten, steht ganz vorne weil es alles betrifft.

class App:                                          # Klasse # Hier wird die Klasse App erstellt dies schliesst die ganze Benutzeroberfläche ein.
    def __init__(self):                             # Konstruktor-Methode # Das Init ist eine Methode sie greift auf self zu und startet das Fenster. Durch def wir das Init definiert.
        self.root = tk.Tk()                           # Attribut # Hier wird das Fenster erstellt.
        self.root.title ("Startfenster")            # Methode# Hier wird dem Fenster den Namen gegeben.

        start_button = tk.Button(self.root, text="Start", font=("Arial", 24), width=10, height=2, command=self.open_main_menu)      # Mit der tk.Button Klasse wird ein Knopf erstellt danach folgen die Argumente. Beim Command wird die methode open main menu ausgeführt in dieser Methode wird ein neues Fenster erstellt.
        start_button.pack(expand=True, padx=50, pady=50)            # Hier wird noch die Position des Buttons definiert und ob er sich bewegt wenn das fenster vergrössert wird.

    def open_main_menu(self):                                       # Methode # Hier wird die Methode von oben definiert
        self.root.withdraw()                                        # Methode # durch das withdraw versteckt sich das self.root (Startfenster)

        self.menu_win = tk.Toplevel()                                 # Attribut
        self.menu_win.title("Menü")                                 # Title Menü wird gegeben.
        self.menu_win.protocol("WM_DELETE_WINDOW", self.close_app)  # Methode # wird verwendet um zu fragen was passiert wenn mann das Fenster schliessen möchte. Das WM_Delet ist für tkinter das beschreibt was passiert wenn man auf X drückt

        self.left_running = False                                   # diese vier Zeilen sind dazu da um zu definieren ob die Pfeiltasten gedrückt werden oder nicht.
        self.right_running = False
        self.after_id_left = None
        self.after_id_right = None

        options = ["Bitte wählen", "Washbuffer","Lysis","Diluent","CMR +","CMR -","Reagent","MGP"]      #Hier werden die Optione für den Dropdown Button angegeben.
        self.selected_option = tk.StringVar(self.menu_win)                                              # Attribut # StringVar wird für die Speicherung der Dropdowns verwendet welche dan für option menue verwendet wird.
        self.selected_option.set(options[0])                                                            # Es wird immmer Option 1 angezeit.
        
        lable_option = tk.Label(self.menu_win, text="Typ")                                              # Attribut zur beschriftung des Buttons
        lable_option.grid(row=0, column=0, padx=10, pady=10, sticky="e")     
                                   
        options_menu = tk.OptionMenu(self.menu_win, self.selected_option, *options)                     # das Dropdown Menü mit allen optionen die in der Klammer angegben werden Wo und Was 
        options_menu.config(width=10)
        options_menu.grid(row=0 ,column=1, padx=10, pady=10 ,sticky="w")

        label_number = tk.Label(self.menu_win, text="Anzahl")                                           # Feld zur eingabe der zu druckenden Tags
        label_number.grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.number_entry = tk.Entry(self.menu_win, width=10)
        self.number_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        menu_start_button = tk.Button(self.menu_win, text="Start", command=self.start_script)           # Hier wird der Start Button erstellt und definiert was passiert wenn man ihn drückt
        menu_start_button.grid(row= 2, column=0,columnspan=2, padx=10, pady=20)                         # Ducht Columnspan wird verwenden um ein Element über mehrer Spalten zu strecken, so das er in der Mitte erscheint

        left_button = tk.Button(self.menu_win, text="←", font=("Arial",12))                             # Hier werden die Pfeiltasten erstellt # Hier wird der Font angegeben weil der PFeil sonst nicht gut aussieht, ander Buttons habe den Font schon vordefiniert
        left_button.grid(row=3, column=0, padx=10, pady=10)             
        left_button.bind("<ButtonPress-1>", self.start_left)                                           # Da die Taste merken muss ob sie gedrückt ist wird hier die Funktion bind benutzt "ButtonPress" ist eine Tkinter Funktion deshalb auc hdie <> sie definniert eine Tkinter Ereignis Syntaxe. Press steht für drücken und -1 für linke maustaste.
        left_button.bind("<ButtonRelease-1>", self.stop_left)                                          # Was bei start und stop passiert wird später noch definiert

        right_button = tk.Button(self.menu_win, text="→", font=("Arial", 12))                           # Das gleiche noch für die rechte Pfeiltaste
        right_button.grid(row=3, column=1, padx=10, pady=10)
        right_button.bind("<ButtonPress-1>", self.start_right)
        right_button.bind("<ButtonRelease-1>", self.stop_right)


    def start_left(self,event):                                                                          # Von hier....
        self.left_running = True
        self.run_left()

    def run_left(self):
        if not self.left_running:
            return
        self.after_id_left = self.menu_win.after(REPEAT_DELAY_MS, self.run_left) 
    
    def stop_left(self, evennt):
        self.left_running = False
        if self.after_id_left:
            self.menu_win.after_cancel(self.after_id_left)
            self.after_id_left = None

    def start_right(self, event):
        self.right_running = True
        self.run_right()
    
    def run_right(self):
        if not self.right_running:
            return
        self.after_id_right = self.menu_win.after(REPEAT_DELAY_MS, self.run_right)
    
    def stop_right(self, event):
    
        self.right_running = False
        if self.after_id_right:
            self.menu_win.after_cancel(self.after_id_right)
            self.after_id_right = None                                                                      # ...bis hier befidet sich die temporäre steuerung der motoren, die Steuerung der Motoren wird durch ein Skript ersetzt das mit RPI.GPIO geschrieben ist.

    def start_script(self):                                                                                 # Hier werden die Attribute gesammel die dann bestimmen welches Consumable Skript ablaufen soll und wie viel mal beschriften gedrückt werden muss und wie of der Motor die bewegungne durchfüren muss
        option  = self.selected_option.get()
        number_str = self.number_entry.get().strip()
        if number_str == "":
            number_str = "(keine Eingabe erhalten)"
        print(f"Starte Skript mit Option {option} und Anzahl {number_str}")

    def close_app(self):                                                                                    # Befehel zum schliessen des Interface
        self.root.destroy()
    
    def run(self):                                                                                           # Hier wird die Tkinter Anwendung aufrecht erhalten so wird der Code ständig wiederholt und reagiert auf eingaben                                                   
        self.root.mainloop()  


if __name__ == "__main__":                                                                                  # Durch das main wird der Code nur ausgeführt wenn er direkt gestartet wird / Bei einem Skript müsse es der __name__ sein
    app = App()
    app.run()

            
            
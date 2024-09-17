import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedStyle
from tkinter import *
from datetime import datetime
import json
import os
from PIL import Image, ImageTk

# Variabili globali per la configurazione grafica
BACKGROUND_COLOR = '#EFFFAF'
TEXT_COLOR = 'blue'
LABEL_FONT = ("Roboto", 16)
BUTTON_FONT = ("Arial", 12)
ENTRY_BG_COLOR = 'white'
ENTRY_FG_COLOR = 'black'

class Volo(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("VOLO")
        

        # Carica l'immagine di sfondo
        background_image = Image.open("background.png")
        self.background_photo = ImageTk.PhotoImage(background_image)

        # Crea un canvas per posizionare l'immagine di sfondo
        self.canvas = tk.Canvas(self, width=background_image.width, height=background_image.height)
        self.canvas.pack(fill="both", expand=True)  # Utilizza pack per centrare e rendere responsive
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.background_photo)

        # Crea un frame trasparente per contenere i widget
        self.pan = tk.Frame(self)
        self.pan.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        # Imposta il colore di sfondo del frame principale
        self.pan.configure(bg='#EFFFAF')  # Colore grigio con opacità

        self.create_widgets()
        self.file_path = "record.json"



    def on_window_resize(self, event):
        # Aggiorna le dimensioni e la posizione dell'immagine di sfondo al ridimensionamento della finestra
        self.canvas.config(width=event.width, height=event.height)


    def create_widgets(self):
        # Etichette e campi di testo
        labels_text = ["Nome e cognome", "Data (GG/MM/AAAA)", "Codice", "Compagnia", "Costo totale", "Posto", "Tratta (Tratta 1-Tratta 2)"]
        self.entries = {}

        row = 0
        tk.Label(self.pan, text="VOLO", bg=BACKGROUND_COLOR, fg=TEXT_COLOR, font=LABEL_FONT).grid(row=row, column=1, pady=10)

        row += 1
        for text in labels_text:
            tk.Label(self.pan, text=text, bg=BACKGROUND_COLOR).grid(row=row, column=0, pady=5, sticky=tk.W)
            entry = tk.Entry(self.pan, bg=ENTRY_BG_COLOR, fg=ENTRY_FG_COLOR)
            entry.grid(row=row, column=1, pady=5)
            self.entries[text.lower()] = entry
            row += 1

        # Pulsanti radio
        self.solo_var = tk.IntVar()
        self.bagaglio_var = tk.IntVar()
        tk.Label(self.pan, text="Eri solo?(clicca per sì, vuoto per no)", bg=BACKGROUND_COLOR).grid(row=row, column=0, pady=5, sticky=tk.W)
        tk.Checkbutton(self.pan, variable=self.solo_var, bg=BACKGROUND_COLOR).grid(row=row, column=1, pady=5)

        row += 1
        tk.Label(self.pan, text="Bagagli in più?(clicca per sì, vuoto per no)", bg=BACKGROUND_COLOR).grid(row=row, column=0, pady=5, sticky=tk.W)
        tk.Checkbutton(self.pan, variable=self.bagaglio_var, bg=BACKGROUND_COLOR).grid(row=row, column=1, pady=5)

        row += 1
        tk.Button(self.pan, text="Inserisci dettagli volo", command=self.insert_details, font=BUTTON_FONT).grid(row=row, column=1, pady=10)

        row += 1
        tk.Label(self.pan, text="Campo di ricerca, inserisci nome e tratta (opzionale)", bg=BACKGROUND_COLOR, fg=TEXT_COLOR).grid(row=row, column=1, pady=10)

        row += 1
        self.search_entry = tk.Entry(self.pan, bg=ENTRY_BG_COLOR, fg=ENTRY_FG_COLOR)
        self.search_entry.grid(row=row, column=1, pady=5)

        row += 1
        tk.Button(self.pan, text="Totale soldi spesi", command=self.calculate_total_spent, font=BUTTON_FONT).grid(row=row, column=1, pady=10)

        row += 1
        tk.Button(self.pan, text="Numero di volte in viaggio", command=self.calculate_trips, font=BUTTON_FONT).grid(row=row, column=1, pady=10)

        row += 1
        tk.Button(self.pan, text="Visualizza record ordinati", command=self.show_sorted_records, font=BUTTON_FONT).grid(row=row, column=1, pady=10)

    def insert_details(self):
        details = {key: entry.get() for key, entry in self.entries.items()}

        # Validazione degli input
        try:
            datetime.strptime(details["data (gg/mm/aaaa)"], "%d/%m/%Y")
            valid_date = True
        except ValueError:
            valid_date = False

        if (valid_date and
            details["costo totale"].replace('.', '', 1).isdigit() and
            details["compagnia"].isalpha() and details["nome e cognome"].replace(" ", "").isalpha() and
            '-' in details["tratta (tratta 1-tratta 2)"] and len(details["tratta (tratta 1-tratta 2)"].split('-')) == 2):
            
            details["costo totale"] = float(details["costo totale"])
            details["bagaglio"] = bool(self.bagaglio_var.get())
            details["solo"] = bool(self.solo_var.get())
            details["tratta"] = details.pop("tratta (tratta 1-tratta 2)")

            with open(self.file_path, 'r+') as f:
                data = json.load(f)
                data.append(details)
                f.seek(0)
                json.dump(data, f, indent=4)

            messagebox.showinfo("Successo", "Dettagli del volo inseriti correttamente!")
            for entry in self.entries.values():
                entry.delete(0, tk.END)
            self.solo_var.set(0)
            self.bagaglio_var.set(0)
        else:
            messagebox.showerror("Errore", "Errore nell'immissione dei parametri")

    def calculate_total_spent(self):
        search_terms = self.search_entry.get().split(',')
        nome = search_terms[0].strip() if len(search_terms) > 0 else ""
        tratta = search_terms[1].strip() if len(search_terms) > 1 else ""

        if nome:
            total_spent = 0
            found = False

            with open(self.file_path, 'r') as f:
                data = json.load(f)
                for entry in data:
                    if nome.lower() in entry["nome e cognome"].lower() and (not tratta or tratta.lower() in entry["tratta"].lower()):
                        total_spent += entry["costo totale"]
                        found = True

            if found:
                total_spent = "{:.2f}".format(total_spent)
                messagebox.showinfo("Totale Speso", f"Totale soldi spesi per {nome} è di: {total_spent}")
            else:
                messagebox.showerror("Errore", "Nessun record trovato")
        else:
            messagebox.showerror("Errore", "Inserisci un nome per la ricerca")

    def calculate_trips(self):
        search_terms = self.search_entry.get().split(',')
        nome = search_terms[0].strip() if len(search_terms) > 0 else ""
        tratta = search_terms[1].strip() if len(search_terms) > 1 else ""

        if nome:
            trip_count = 0
            found = False

            with open(self.file_path, 'r') as f:
                data = json.load(f)
                for entry in data:
                    if nome.lower() in entry["nome e cognome"].lower() and (not tratta or tratta.lower() in entry["tratta"].lower()):
                        trip_count += 1
                        found = True

            if found:
                messagebox.showinfo("Numero di Viaggi", f"Il totale di volte in cui {nome} ha viaggiato è di: {trip_count}")
            else:
                messagebox.showerror("Errore", "Nessun record trovato")
        else:
            messagebox.showerror("Errore", "Inserisci un nome per la ricerca")

    def show_sorted_records(self):
        search_terms = self.search_entry.get().split(',')
        nome = search_terms[0].strip() if len(search_terms) > 0 else ""
        tratta = search_terms[1].strip() if len(search_terms) > 1 else ""

        with open(self.file_path, 'r') as f:
            data = json.load(f)
            if nome:
                filtered_data = [entry for entry in data if nome.lower() in entry["nome e cognome"].lower() and (not tratta or tratta.lower() in entry["tratta"].lower())]
            else:
                filtered_data = data

            sorted_data = sorted(filtered_data, key=lambda x: datetime.strptime(x["data (gg/mm/aaaa)"], "%d/%m/%Y"), reverse=True)

            if sorted_data:
                self.show_records_in_scrollable_window(sorted_data)
            else:
                messagebox.showerror("Errore", "Nessun record trovato")

    def show_records_in_scrollable_window(self, records):
        top = tk.Toplevel(self)
        top.title("Records")

        tree = ttk.Treeview(top, columns=list(records[0].keys()), show="headings")
        tree.pack(fill="both", expand=True)

        # Aggiungere le intestazioni della tabella
        for col in records[0].keys():
            tree.heading(col, text=col.title())
            tree.column(col, minwidth=50, width=100, anchor=tk.CENTER)

        # Aggiungere i dati alla tabella
        for entry in records:
            row_data = [entry[col] for col in records[0].keys()]
            tree.insert("", tk.END, values=row_data)

        # Aggiungere scrollbar
        scrollbar = ttk.Scrollbar(top, orient="vertical", command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)

        # Bottone per chiudere la finestra
        close_button = tk.Button(top, text="Chiudi", command=top.destroy, font=BUTTON_FONT)
        close_button.pack(pady=10)


if __name__ == "__main__":
    app = Volo()
    app.mainloop()


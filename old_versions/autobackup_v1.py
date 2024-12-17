import os
import time
import tkinter as tk
from tkinter import filedialog, ttk
from datetime import datetime, timedelta
import threading
import schedule
import zipfile

# Fonction pour supprimer les fichiers .zip plus anciens qu'une durée définie par l'utilisateur
def check_and_delete_zip_files(directory, days):
    now = datetime.now()
    delete_before = now - timedelta(days=days)
    
    for filename in os.listdir(directory):
        if filename.endswith(".zip"):
            file_path = os.path.join(directory, filename)
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            
            if file_mod_time < delete_before:
                os.remove(file_path)
                print(f"Deleted: {filename}")

# Fonction pour créer une sauvegarde automatique sous forme de zip
def create_backup(root_dir, dest_dir):
    try:
        now = datetime.now()
        date_str = now.strftime("%d-%m-%Y")
        backup_number = 1
        backup_name = f"Backup_{date_str}_{backup_number}.zip"
        
        while os.path.exists(os.path.join(dest_dir, backup_name)):
            backup_number += 1
            backup_name = f"Backup_{date_str}_{backup_number}.zip"
        
        zip_path = os.path.join(dest_dir, backup_name)
        
        total_files = sum([len(files) for _, _, files in os.walk(root_dir)])
        current_file = 0
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
            for foldername, subfolders, filenames in os.walk(root_dir):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    backup_zip.write(file_path, os.path.relpath(file_path, root_dir))
                    current_file += 1
                    progress = int((current_file / total_files) * 100)
                    progress_var.set(progress)
                    progress_bar.update()
        
        progress_var.set(0)
        display_status("Backup terminée", "green")
        print(f"Backup created: {backup_name}")
    except Exception as e:
        progress_var.set(0)
        display_status("Erreur Backup", "red")
        print(f"Error during backup: {e}")

# Fonction pour afficher un message d'état temporaire
def display_status(message, color):
    status_label.config(text=message, fg=color)
    root.after(5000, lambda: status_label.config(text=""))

# Fonction appelée par le bouton "Backup Manuelle"
def manual_backup():
    root_dir = root_dir_entry.get()
    dest_dir = dest_dir_entry.get()
    if root_dir and dest_dir:
        progress_var.set(0)
        create_backup(root_dir, dest_dir)
    else:
        print("No root or destination directory selected")

# Fonction pour démarrer la sauvegarde automatique avec fréquence et heure définies
def start_backup_schedule():
    root_dir = root_dir_entry.get()
    dest_dir = dest_dir_entry.get()
    try:
        frequency_days = int(frequency_entry.get())
        backup_time = f"{int(hour_entry.get()):02}:00"
    except ValueError:
        print("Invalid input for frequency or time")
        return
    
    if root_dir and dest_dir:
        schedule.every(frequency_days).days.at(backup_time).do(create_backup, root_dir, dest_dir)
        
        def run_schedule():
            while True:
                schedule.run_pending()
                time.sleep(1)
        
        schedule_thread = threading.Thread(target=run_schedule, daemon=True)
        schedule_thread.start()
        
        start_backup_button.config(state="disabled")
        stop_backup_button.config(state="normal")
        print(f"Automatic backup scheduled every {frequency_days} days at {backup_time}")

# Fonction pour arrêter la sauvegarde automatique
def stop_backup_schedule():
    global stop_flag
    stop_flag = True
    start_backup_button.config(state="normal")
    stop_backup_button.config(state="disabled")
    print("Automatic backup stopped")

# Fonction pour démarrer la vérification automatique à 3h du matin pour supprimer les fichiers .zip
def start_auto_delete_schedule():
    directory = directory_entry.get()
    try:
        days = int(days_entry.get())
    except ValueError:
        print("Invalid number of days")
        return
    if directory:
        schedule.every().day.at("03:00").do(check_and_delete_zip_files, directory, days)
        
        def run_schedule():
            while True:
                schedule.run_pending()
                time.sleep(1)
        
        schedule_thread = threading.Thread(target=run_schedule, daemon=True)
        schedule_thread.start()

        start_delete_button.config(state="disabled")
        stop_delete_button.config(state="normal")
        print("Automatic delete started")

# Fonction pour arrêter la vérification automatique de suppression
def stop_auto_delete_schedule():
    global stop_flag
    stop_flag = True
    start_delete_button.config(state="normal")
    stop_delete_button.config(state="disabled")
    print("Automatic delete stopped")

# Fonction pour suppression manuelle des fichiers .zip
def manual_delete():
    directory = directory_entry.get()
    try:
        days = int(days_entry.get())
    except ValueError:
        print("Invalid number of days")
        return
    if directory:
        check_and_delete_zip_files(directory, days)
    else:
        print("No directory selected")

# Interface graphique avec Tkinter
def browse_root_folder():
    folder_selected = filedialog.askdirectory()
    root_dir_entry.delete(0, tk.END)
    root_dir_entry.insert(0, folder_selected)

def browse_dest_folder():
    folder_selected = filedialog.askdirectory()
    dest_dir_entry.delete(0, tk.END)
    dest_dir_entry.insert(0, folder_selected)

def browse_delete_folder():
    folder_selected = filedialog.askdirectory()
    directory_entry.delete(0, tk.END)
    directory_entry.insert(0, folder_selected)

# Création de la fenêtre principale
root = tk.Tk()
root.title("Backup and Auto Delete")
root.minsize(800, 400)

# Création du conteneur principal
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Partie Backup
backup_frame = tk.Frame(main_frame, bg="lightblue", padx=10, pady=10)
backup_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

backup_label = tk.Label(backup_frame, text="Sauvegarde Automatique", bg="lightblue", font=("Arial", 14, "bold"))
backup_label.pack(pady=5)

root_dir_entry = tk.Entry(backup_frame, width=50)
root_dir_entry.pack(pady=5)

browse_root_button = tk.Button(backup_frame, text="Parcourir Dossier Racine", command=browse_root_folder)
browse_root_button.pack(pady=5)

dest_dir_entry = tk.Entry(backup_frame, width=50)
dest_dir_entry.pack(pady=5)

browse_dest_button = tk.Button(backup_frame, text="Parcourir Dossier Destination", command=browse_dest_folder)
browse_dest_button.pack(pady=5)

frequency_frame = tk.Frame(backup_frame, bg="lightblue")
frequency_frame.pack(pady=10)

frequency_label = tk.Label(frequency_frame, text="Backuper tous les", bg="lightblue")
frequency_label.grid(row=0, column=0, padx=5)

frequency_entry = tk.Entry(frequency_frame, width=5)
frequency_entry.insert(0, "1")
frequency_entry.grid(row=0, column=1, padx=5)

frequency_days_label = tk.Label(frequency_frame, text="jours", bg="lightblue")
frequency_days_label.grid(row=0, column=2, padx=5)

hour_frame = tk.Frame(backup_frame, bg="lightblue")
hour_frame.pack(pady=10)

hour_label = tk.Label(hour_frame, text="À", bg="lightblue")
hour_label.grid(row=0, column=0, padx=5)

hour_entry = tk.Entry(hour_frame, width=5)
hour_entry.insert(0, "2")
hour_entry.grid(row=0, column=1, padx=5)

hour_suffix_label = tk.Label(hour_frame, text="heures", bg="lightblue")
hour_suffix_label.grid(row=0, column=2, padx=5)

progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(backup_frame, orient="horizontal", length=400, mode="determinate", variable=progress_var)
progress_bar.pack(pady=10)

status_label = tk.Label(backup_frame, text="", bg="lightblue", font=("Arial", 10))
status_label.pack(pady=5)

start_backup_button = tk.Button(backup_frame, text="Démarrer Backup Auto", command=start_backup_schedule)
start_backup_button.pack(pady=5)

stop_backup_button = tk.Button(backup_frame, text="Stop Backup Auto", command=stop_backup_schedule, state="disabled")
stop_backup_button.pack(pady=5)

manual_backup_button = tk.Button(backup_frame, text="Backup Manuelle", command=manual_backup)
manual_backup_button.pack(pady=5)

# Partie Suppression Auto
delete_frame = tk.Frame(main_frame, bg="lightcoral", padx=10, pady=10)
delete_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

delete_label = tk.Label(delete_frame, text="Suppression Automatique", bg="lightcoral", font=("Arial", 14, "bold"))
delete_label.pack(pady=5)

directory_entry = tk.Entry(delete_frame, width=50)
directory_entry.pack(pady=5)

browse_delete_button = tk.Button(delete_frame, text="Parcourir Dossier", command=browse_delete_folder)
browse_delete_button.pack(pady=5)

days_label = tk.Label(delete_frame, text="Nombre de jours avant suppression:", bg="lightcoral")
days_label.pack(pady=5)

days_entry = tk.Entry(delete_frame, width=10)
days_entry.insert(0, "30")  # Valeur par défaut

days_entry.pack(pady=5)

start_delete_button = tk.Button(delete_frame, text="Démarrer Suppression Auto", command=start_auto_delete_schedule)
start_delete_button.pack(pady=5)

stop_delete_button = tk.Button(delete_frame, text="Stop Suppression Auto", command=stop_auto_delete_schedule, state="disabled")
stop_delete_button.pack(pady=5)

manual_delete_button = tk.Button(delete_frame, text="Suppression Manuelle", command=manual_delete)
manual_delete_button.pack(pady=5)

# Configuration des colonnes et des lignes
main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(0, weight=1)

# Démarrer l'interface Tkinter
root.mainloop()

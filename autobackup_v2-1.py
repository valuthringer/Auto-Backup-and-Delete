import os
import time
import tkinter as tk
from tkinter import filedialog, ttk
from datetime import datetime, timedelta
import threading
import schedule
import zipfile
import webbrowser

########################################
def open_github_link():
    webbrowser.open("https://valuthringer.github.io")
def open_logs_versions():
    webbrowser.open("https://valuthringer.github.io")
########################################

#Supprimer les fichier zip du répertoire de sauvegarde
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

#Créer une sauvegarde auto à partir des dossiers sources
def create_backup(root_dirs, dest_dir):
    try:
        now = datetime.now()
        date_str = now.strftime("%d-%m-%Y")
        backup_number = 1
        backup_name = f"Backup_{date_str}_{backup_number}.zip"
        
        while os.path.exists(os.path.join(dest_dir, backup_name)):
            backup_number += 1
            backup_name = f"Backup_{date_str}_{backup_number}.zip"
        
        zip_path = os.path.join(dest_dir, backup_name)
        
        total_files = 0
        for root_dir in root_dirs.split(';'):
            total_files += sum([len(files) for _, _, files in os.walk(root_dir.strip())])

        current_file = 0
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as backup_zip:
            for root_dir in root_dirs.split(';'):
                for foldername, subfolders, filenames in os.walk(root_dir.strip()):
                    for filename in filenames:
                        file_path = os.path.join(foldername, filename)
                        archive_dir = os.path.basename(root_dir.strip())
                        backup_zip.write(file_path, os.path.join(archive_dir, os.path.relpath(file_path, root_dir.strip())))
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

# Afficher le status de la sauvegarde
def display_status(message, color):
    status_label.config(text=message, fg=color)
    root.after(5000, lambda: status_label.config(text=""))

#Backup manuelle
def manual_backup():
    root_dirs = root_dirs_text.get("1.0", tk.END).strip()
    dest_dir = dest_dir_entry.get()
    if root_dirs and dest_dir:
        progress_var.set(0)
        create_backup(root_dirs, dest_dir)
    else:
        print("No root or destination directory selected")

#Démarer la sauvegarde automatique
def start_backup_schedule():
    root_dirs = root_dirs_text.get("1.0", tk.END).strip()
    dest_dir = dest_dir_entry.get()
    try:
        frequency_days = int(frequency_entry.get())
        backup_time = f"{int(hour_entry.get()):02}:00"
    except ValueError:
        print("Invalid input for frequency or time")
        return
    
    if root_dirs and dest_dir:
        stop_event.clear()
        
        schedule.every(frequency_days).days.at(backup_time).do(create_backup, root_dirs, dest_dir)
        
        def run_schedule():
            while not stop_event.is_set():
                schedule.run_pending()
                time.sleep(1)
        
        schedule_thread = threading.Thread(target=run_schedule, daemon=True)
        schedule_thread.start()
        
        start_backup_button.config(state="disabled")
        stop_backup_button.config(state="normal")
        print(f"Automatic backup scheduled every {frequency_days} days at {backup_time}")

stop_event = threading.Event()

# Arret sauvegarde automatique
def stop_backup_schedule():
    stop_event.set()
    start_backup_button.config(state="normal")
    stop_backup_button.config(state="disabled")
    print("Automatic backup stopped")

# Ajouter un dossier source
def add_root_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        current_text = root_dirs_text.get("1.0", tk.END).strip()
        if current_text:
            root_dirs_text.delete("1.0", tk.END)
            root_dirs_text.insert("1.0", f"{current_text}; {folder_selected}")
        else:
            root_dirs_text.insert("1.0", folder_selected)

# Stopper la suppression automatique
def stop_backup_schedule():
    global stop_flag
    stop_flag = True
    start_backup_button.config(state="normal")
    stop_backup_button.config(state="disabled")
    print("Automatic backup stopped")

# Démarrer la vérification automatique à 3h du matin pour supprimer les fichiers .zip
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

# Stoper l'auto suppression
def stop_auto_delete_schedule():
    global stop_flag
    stop_flag = True
    start_delete_button.config(state="normal")
    stop_delete_button.config(state="disabled")
    print("Automatic delete stopped")

# Suppression manuelle
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

def browse_dest_folder():
    folder_selected = filedialog.askdirectory()
    dest_dir_entry.delete(0, tk.END)
    dest_dir_entry.insert(0, folder_selected)

def browse_delete_folder():
    folder_selected = filedialog.askdirectory()
    directory_entry.delete(0, tk.END)
    directory_entry.insert(0, folder_selected)


###############################################################
# Interface graphique avec Tkinter

def open_help():
    help_popup = tk.Toplevel(root)
    help_popup.title("Aide")
    help_popup.geometry("500x270")
    help_popup.minsize(500, 270)
    help_popup.maxsize(500, 270)
    help_popup.resizable(0, 0)
    help_popup.configure(bg="lightgrey")
    
    help_frame = tk.Frame(help_popup, bg="lightgrey", padx=10, pady=10)
    help_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    explications1 = tk.Label(help_frame, text="Sauvegardes", font=("Arial", 14, "bold"), anchor="w", bg="lightgrey")
    explications1.grid(row=0, column=0, sticky="w", padx=5, pady=5)

    explications2 = tk.Label(help_frame, text="> Choisir un ou plusieurs dossiers à sauvegarder.", font=("Arial", 11), anchor="w", bg="lightgrey")
    explications2.grid(row=1, column=0, sticky="w", padx=0, pady=0)
    explications3 = tk.Label(help_frame, text="> Choisir un dossier de destination pour les backups.", font=("Arial", 11), anchor="w", bg="lightgrey")
    explications3.grid(row=2, column=0, sticky="w", padx=0, pady=0)
    explications31 = tk.Label(help_frame, text="> Les backups s'évrivent de la forme 'Backup_JJ_MM_YYYY_num'", font=("Arial", 11), anchor="w", bg="lightgrey")
    explications31.grid(row=3, column=0, sticky="w", padx=0, pady=0)
    explications4 = tk.Label(help_frame, text="> Choisir une fréquence de backup en jours et une heure.", font=("Arial", 11), anchor="w", bg="lightgrey")
    explications4.grid(row=4, column=0, sticky="w", padx=0, pady=0)

    explications5 = tk.Label(help_frame, text="Suppression", font=("Arial", 14, "bold"), anchor="w", bg="lightgrey")
    explications5.grid(row=5, column=0, sticky="w", padx=5, pady=5)

    explications6 = tk.Label(help_frame, text="> Choisir un dossier à surveiller pour supprimer les backups .zip.", font=("Arial", 11), anchor="w", bg="lightgrey")
    explications6.grid(row=6, column=0, sticky="w", padx=0, pady=0)
    explications7 = tk.Label(help_frame, text="> Choisir le nombre de jours avant suppression.", font=("Arial", 11), anchor="w", bg="lightgrey")
    explications7.grid(row=7, column=0, sticky="w", padx=0, pady=0)

def open_a_propos():
    help_popup = tk.Toplevel(root)
    help_popup.title("A Propos")
    help_popup.geometry("500x160")
    help_popup.minsize(500, 160)
    help_popup.maxsize(500, 160)
    help_popup.resizable(0, 0)
    help_popup.configure(bg="lightgrey")
    
    help_frame = tk.Frame(help_popup, bg="lightgrey", padx=10, pady=10)
    help_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    explications1 = tk.Label(help_frame, text="A Propos", font=("Arial", 14, "bold"), anchor="w", bg="lightgrey")
    explications1.grid(row=0, column=0, sticky="w", padx=5, pady=5)

    explications2 = tk.Label(help_frame, text="© Copyright - Valentin Luthringer", font=("Arial", 11), anchor="w", bg="lightgrey")
    explications2.grid(row=1, column=0, sticky="w", padx=0, pady=0)
    github_link = tk.Label(
        help_frame, 
        text="Github: @valuthringer", 
        font=("Arial", 11), 
        anchor="w", 
        bg="lightgrey", 
        fg="dodgerblue", 
        cursor="hand2"
    )
    github_link.grid(row=1, column=1, sticky="w", padx=0, pady=0)
    github_link.bind("<Button-1>", lambda e: open_github_link())

    explications3 = tk.Label(help_frame, text="Version 2.1 - Mise à jour du 12-12-2024", font=("Arial", 11), anchor="w", bg="lightgrey")
    explications3.grid(row=2, column=0, sticky="w", padx=0, pady=0)

    logversions = tk.Label(
        help_frame, 
        text="Historique des versions", 
        font=("Arial", 11), 
        anchor="w", 
        bg="lightgrey", 
        fg="teal", 
        cursor="hand2"
    )
    logversions.grid(row=4, column=0, sticky="w", padx=0, pady=0)
    logversions.bind("<Button-1>", lambda e: open_logs_versions())


root = tk.Tk()
root.title("Backup and Delete by @valuthringer")
root.minsize(800, 580)
root.resizable(0, 0)
root.configure(bg="lightgrey")


main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)
main_frame.configure(bg="lightgrey")

top_buttons_frame = tk.Frame(root, bg="white")
top_buttons_frame.pack(side="top", pady=10)
top_buttons_frame.configure(bg="lightgrey")

help_button = tk.Button(top_buttons_frame, text="Aide", command=open_help, bg="silver", font=("Arial", 11))
help_button.pack(side="left", padx=5)

apropos_button = tk.Button(top_buttons_frame, text="À Propos", command=open_a_propos, bg="silver", font=("Arial", 11))
apropos_button.pack(side="left", padx=5)

# Partie Backup
backup_frame = tk.Frame(main_frame, bg="lightskyblue", padx=10, pady=10)
backup_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

backup_label = tk.Label(backup_frame, text="Sauvegardes", bg="lightskyblue", font=("Arial", 14, "bold"))
backup_label.pack(pady=5)

root_dirs_text = tk.Text(backup_frame, width=50, height=4)
root_dirs_text.pack(pady=5)

add_root_button = tk.Button(backup_frame, text="Ajouter Dossier Source", command=add_root_folder)
add_root_button.pack(pady=5)

dest_dir_entry = tk.Entry(backup_frame, width=66)
dest_dir_entry.pack(pady=5)

browse_dest_button = tk.Button(backup_frame, text="Parcourir Dossier Destination", command=browse_dest_folder)
browse_dest_button.pack(pady=5)

frequency_frame = tk.Frame(backup_frame, bg="lightskyblue")
frequency_frame.pack(pady=10)

frequency_label = tk.Label(frequency_frame, text="Sauvegarder tous les", bg="lightskyblue")
frequency_label.grid(row=0, column=0, padx=5)

frequency_entry = tk.Entry(frequency_frame, width=5)
frequency_entry.insert(0, "1")
frequency_entry.grid(row=0, column=1, padx=5)

frequency_days_label = tk.Label(frequency_frame, text="jours", bg="lightskyblue")
frequency_days_label.grid(row=0, column=2, padx=5)

hour_frame = tk.Frame(backup_frame, bg="lightskyblue")
hour_frame.pack(pady=10)

hour_label = tk.Label(hour_frame, text="À", bg="lightskyblue")
hour_label.grid(row=0, column=0, padx=5)

hour_entry = tk.Entry(hour_frame, width=5)
hour_entry.insert(0, "2")
hour_entry.grid(row=0, column=1, padx=5)

hour_suffix_label = tk.Label(hour_frame, text="heures", bg="lightskyblue")
hour_suffix_label.grid(row=0, column=2, padx=5)

progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(backup_frame, orient="horizontal", length=400, mode="determinate", variable=progress_var)
progress_bar.pack(pady=10)

status_label = tk.Label(backup_frame, text="", bg="lightskyblue", font=("Arial", 10))
status_label.pack(pady=5)

start_backup_button = tk.Button(backup_frame, text="Démarrer Backup Auto", bg="springgreen",command=start_backup_schedule)
start_backup_button.pack(pady=5)

stop_backup_button = tk.Button(backup_frame, text="Stop Backup Auto", bg="lightcoral", state="disabled", command=stop_backup_schedule)
stop_backup_button.pack(pady=5)

manual_backup_button = tk.Button(backup_frame, text="Backup Manuelle", bg="goldenrod", command=manual_backup)
manual_backup_button.pack(pady=5)

# Partie Suppression Auto
delete_frame = tk.Frame(main_frame, bg="sandybrown", padx=10, pady=10)
delete_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

delete_label = tk.Label(delete_frame, text="Suppression", bg="sandybrown", font=("Arial", 14, "bold"))
delete_label.pack(pady=5)

directory_entry = tk.Entry(delete_frame, width=50)
directory_entry.pack(pady=5)

browse_delete_button = tk.Button(delete_frame, text="Parcourir Dossier", command=browse_delete_folder)
browse_delete_button.pack(pady=5)

days_label = tk.Label(delete_frame, text="Nombre de jours de backup à garder :", bg="sandybrown")
days_label.pack(pady=5)

days_entry = tk.Entry(delete_frame, width=10)
days_entry.insert(0, "30")

days_entry.pack(pady=5)


espace = tk.Label(delete_frame, text="", bg="sandybrown")
espace.pack(pady=95)

start_delete_button = tk.Button(delete_frame, text="Démarrer Suppression Auto", bg="springgreen", command=start_auto_delete_schedule)
start_delete_button.pack(pady=5)

stop_delete_button = tk.Button(delete_frame, text="Stop Suppression Auto", bg="lightcoral", command=stop_auto_delete_schedule, state="disabled")
stop_delete_button.pack(pady=5)

manual_delete_button = tk.Button(delete_frame, text="Suppression Manuelle", bg="goldenrod", command=manual_delete)
manual_delete_button.pack(pady=5)

# Colonnes et lignes
main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)
main_frame.rowconfigure(0, weight=1)
main_frame.rowconfigure(1, weight=1)

# Démarrage interface
root.mainloop()
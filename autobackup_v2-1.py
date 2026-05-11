import os
import time
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from datetime import datetime, timedelta
import threading
import schedule
import zipfile
import webbrowser
import sys
from pathlib import Path


# Tentative de charger le thème Forest-ttk
def load_forest_theme():
    """Charge le thème Forest-ttk s'il est disponible, sinon utilise les styles par défaut"""
    try:
        # Chemins possibles pour le thème Forest
        theme_paths = [
            (
                Path(__file__).parent / "Forest-ttk-theme-1.0" / "forest-dark.tcl",
                "forest-dark",
            ),
            (
                Path(__file__).parent / "Forest-ttk-theme-1.0" / "forest-light.tcl",
                "forest-light",
            ),
            (
                Path.home() / ".config" / "python-apps" / "forest-dark.tcl",
                "forest-dark",
            ),
        ]

        for theme_path, theme_name in theme_paths:
            if theme_path.exists():
                root.tk.call("source", str(theme_path))
                ttk.Style().theme_use(theme_name)
                return True

        # Si le thème n'est pas trouvé, créer des styles personnalisés
        create_custom_styles()
        return False
    except Exception as e:
        print(f"Erreur lors du chargement du thème: {e}")
        create_custom_styles()
        return False


def create_custom_styles():
    """Crée des styles personnalisés modernes si Forest n'est pas disponible"""
    style = ttk.Style()

    # Thème par défaut moderne
    style.theme_use("clam")

    # Couleurs modernes
    bg_color = "#f0f0f0"
    fg_color = "#333333"
    accent_color = "#2E7D32"  # Vert Forest

    style.configure("TFrame", background=bg_color)
    style.configure("TLabel", background=bg_color, foreground=fg_color)
    style.configure(
        "Header.TLabel", font=("Segoe UI", 13, "bold"), foreground=accent_color
    )
    style.configure("TButton", font=("Segoe UI", 11))
    style.configure("Success.TButton", font=("Segoe UI", 10))
    style.configure("Danger.TButton", font=("Segoe UI", 10))
    style.configure("Info.TButton", font=("Segoe UI", 10))


########################################
def open_github_link():
    webbrowser.open("https://valuthringer.github.io")


def open_logs_versions():
    webbrowser.open("https://valuthringer.github.io")


########################################


# Supprimer les fichiers zip du répertoire de sauvegarde
def check_and_delete_zip_files(directory, days):
    """Supprime les fichiers .zip plus anciens que le nombre de jours spécifié"""
    now = datetime.now()
    delete_before = now - timedelta(days=days)

    deleted_count = 0
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".zip"):
                file_path = os.path.join(directory, filename)
                file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))

                if file_mod_time < delete_before:
                    os.remove(file_path)
                    deleted_count += 1
                    print(f"Deleted: {filename}")

        if deleted_count > 0:
            display_status(f"[OK] {deleted_count} fichier(s) supprimé(s)", "green")
        else:
            display_status("[OK] Aucun fichier à supprimer", "blue")
    except Exception as e:
        display_status(f"[ERROR] Erreur lors de la suppression: {str(e)}", "red")
        print(f"Error during deletion: {e}")


# Créer une sauvegarde auto à partir des dossiers sources
def create_backup(root_dirs, dest_dir):
    """Crée un fichier ZIP de sauvegarde des dossiers spécifiés"""
    try:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        now = datetime.now()
        date_str = now.strftime("%d-%m-%Y")
        backup_number = 1
        backup_name = f"Backup_{date_str}_{backup_number}.zip"

        while os.path.exists(os.path.join(dest_dir, backup_name)):
            backup_number += 1
            backup_name = f"Backup_{date_str}_{backup_number}.zip"

        zip_path = os.path.join(dest_dir, backup_name)

        total_files = 0
        for root_dir in root_dirs.split(";"):
            root_dir = root_dir.strip()
            if os.path.exists(root_dir):
                total_files += sum([len(files) for _, _, files in os.walk(root_dir)])

        if total_files == 0:
            display_status("[ERROR] Aucun fichier à sauvegarder", "red")
            return

        current_file = 0

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as backup_zip:
            for root_dir in root_dirs.split(";"):
                root_dir = root_dir.strip()
                if os.path.exists(root_dir):
                    for foldername, subfolders, filenames in os.walk(root_dir):
                        for filename in filenames:
                            file_path = os.path.join(foldername, filename)
                            archive_dir = os.path.basename(root_dir)
                            backup_zip.write(
                                file_path,
                                os.path.join(
                                    archive_dir, os.path.relpath(file_path, root_dir)
                                ),
                            )
                            current_file += 1
                            progress = int((current_file / total_files) * 100)
                            progress_var.set(progress)
                            progress_bar.update()

        progress_var.set(0)
        display_status(f"[OK] Backup terminée: {backup_name}", "green")
        print(f"Backup created: {backup_name}")
    except Exception as e:
        progress_var.set(0)
        display_status(f"[ERROR] Erreur Backup: {str(e)}", "red")
        print(f"Error during backup: {e}")


# Afficher le status de la sauvegarde
def display_status(message, color):
    """Affiche un message de statut temporaire"""
    status_label.config(text=message, foreground=color)
    root.after(5000, lambda: status_label.config(text=""))


# Backup manuelle
def manual_backup():
    """Lance une sauvegarde manuelle"""
    root_dirs = root_dirs_text.get("1.0", tk.END).strip()
    dest_dir = dest_dir_entry.get()
    if root_dirs and dest_dir:
        progress_var.set(0)
        threading.Thread(
            target=create_backup, args=(root_dirs, dest_dir), daemon=True
        ).start()
    else:
        display_status(
            "[ERROR] Veuillez sélectionner des dossiers sources et une destination",
            "red",
        )


# Démarrer la sauvegarde automatique
def start_backup_schedule():
    """Démarre la sauvegarde automatique selon la fréquence définie"""
    root_dirs = root_dirs_text.get("1.0", tk.END).strip()
    dest_dir = dest_dir_entry.get()
    try:
        frequency_days = int(frequency_entry.get())
        backup_time = f"{int(hour_entry.get()):02}:00"
    except ValueError:
        display_status("[ERROR] Entrée invalide pour la fréquence ou l'heure", "red")
        print("Invalid input for frequency or time")
        return

    if root_dirs and dest_dir:
        stop_event.clear()

        schedule.every(frequency_days).days.at(backup_time).do(
            create_backup, root_dirs, dest_dir
        )

        def run_schedule():
            while not stop_event.is_set():
                schedule.run_pending()
                time.sleep(1)

        schedule_thread = threading.Thread(target=run_schedule, daemon=True)
        schedule_thread.start()

        start_backup_button.config(state="disabled")
        stop_backup_button.config(state="normal")
        display_status(
            f"[OK] Backup automatique démarrée tous les {frequency_days} jours à {backup_time}",
            "green",
        )
        print(
            f"Automatic backup scheduled every {frequency_days} days at {backup_time}"
        )
    else:
        display_status(
            "[ERROR] Veuillez sélectionner des dossiers sources et une destination",
            "red",
        )


stop_event = threading.Event()


# Arrêt sauvegarde automatique
def stop_backup_schedule():
    """Arrête la sauvegarde automatique"""
    stop_event.set()
    start_backup_button.config(state="normal")
    stop_backup_button.config(state="disabled")
    display_status("[OK] Backup automatique arrêtée", "blue")
    print("Automatic backup stopped")


# Ajouter un dossier source
def add_root_folder():
    """Ajoute un dossier source à la liste"""
    folder_selected = filedialog.askdirectory(title="Sélectionner un dossier source")
    if folder_selected:
        current_text = root_dirs_text.get("1.0", tk.END).strip()
        if current_text:
            root_dirs_text.delete("1.0", tk.END)
            root_dirs_text.insert("1.0", f"{current_text}; {folder_selected}")
        else:
            root_dirs_text.insert("1.0", folder_selected)


# Démarrer la vérification automatique pour supprimer les fichiers .zip
def start_auto_delete_schedule():
    """Démarre la suppression automatique quotidienne à 3h du matin"""
    directory = directory_entry.get()
    try:
        days = int(days_entry.get())
    except ValueError:
        display_status("[ERROR] Nombre de jours invalide", "red")
        print("Invalid number of days")
        return
    if directory and os.path.exists(directory):
        schedule.every().day.at("03:00").do(check_and_delete_zip_files, directory, days)

        def run_schedule():
            while True:
                schedule.run_pending()
                time.sleep(1)

        schedule_thread = threading.Thread(target=run_schedule, daemon=True)
        schedule_thread.start()

        start_delete_button.config(state="disabled")
        stop_delete_button.config(state="normal")
        display_status(
            "[OK] Suppression automatique démarrée (03:00 quotidienne)", "green"
        )
        print("Automatic delete started")
    else:
        display_status("[ERROR] Répertoire invalide", "red")


# Arrêter l'auto suppression
def stop_auto_delete_schedule():
    """Arrête la suppression automatique"""
    start_delete_button.config(state="normal")
    stop_delete_button.config(state="disabled")
    display_status("[OK] Suppression automatique arrêtée", "blue")
    print("Automatic delete stopped")


# Suppression manuelle
def manual_delete():
    """Lance une suppression manuelle"""
    directory = directory_entry.get()
    try:
        days = int(days_entry.get())
    except ValueError:
        display_status("[ERROR] Nombre de jours invalide", "red")
        print("Invalid number of days")
        return
    if directory and os.path.exists(directory):
        threading.Thread(
            target=check_and_delete_zip_files, args=(directory, days), daemon=True
        ).start()
    else:
        display_status("[ERROR] Répertoire invalide", "red")


def browse_dest_folder():
    """Ouvre un dialogue pour sélectionner le dossier de destination"""
    folder_selected = filedialog.askdirectory(
        title="Sélectionner le dossier de destination"
    )
    if folder_selected:
        dest_dir_entry.delete(0, tk.END)
        dest_dir_entry.insert(0, folder_selected)


def browse_delete_folder():
    """Ouvre un dialogue pour sélectionner le dossier à surveiller"""
    folder_selected = filedialog.askdirectory(
        title="Sélectionner le dossier à surveiller"
    )
    if folder_selected:
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, folder_selected)


###############################################################
# Interface graphique avec Tkinter et Forest-ttk


def open_help():
    """Ouvre la fenêtre d'aide"""
    help_popup = tk.Toplevel(root)
    help_popup.title("Aide - Auto Backup & Delete")
    help_popup.geometry("600x400")
    help_popup.minsize(600, 300)
    help_popup.resizable(True, True)

    # Créer un style pour le popup
    style = ttk.Style()

    main_help_frame = ttk.Frame(help_popup, padding=15)
    main_help_frame.pack(fill="both", expand=True)

    # Titre
    title_label = ttk.Label(
        main_help_frame, text="Guide d'utilisation", style="Header.TLabel"
    )
    title_label.pack(anchor="w", pady=(0, 10))

    # Créer un Notebook (onglets)
    notebook = ttk.Notebook(main_help_frame)
    notebook.pack(fill="both", expand=True)

    # Onglet Sauvegardes
    backup_frame = ttk.Frame(notebook, padding=10)
    notebook.add(backup_frame, text="Sauvegardes")

    help_texts_backup = [
        "1. Choisir un ou plusieurs dossiers à sauvegarder",
        "2. Choisir un dossier de destination pour les backups",
        "3. Les backups s'écrivent de la forme 'Backup_DD_MM_YYYY_num'",
        "4. Choisir une fréquence de backup en jours et une heure",
        "5. Cliquer sur 'Démarrer Backup Auto' pour activer les sauvegardes automatiques",
        "",
        "[TIP] Astuce: Vous pouvez ajouter plusieurs dossiers en les séparant par ';'",
    ]

    for text in help_texts_backup:
        label = ttk.Label(backup_frame, text=text, wraplength=550, justify="left")
        label.pack(anchor="w", pady=5)

    # Onglet Suppression
    delete_frame = ttk.Frame(notebook, padding=10)
    notebook.add(delete_frame, text="Suppression")

    help_texts_delete = [
        "1. Choisir un dossier à surveiller pour supprimer les backups .zip",
        "2. Choisir le nombre de jours avant suppression",
        "3. Cliquer sur 'Démarrer Suppression Auto' pour activer les suppressions",
        "",
        "[WARNING] Attention: Les fichiers .zip plus vieux que le nombre de jours spécifié seront supprimés",
        "[TIME] Les suppressions s'exécutent quotidiennement à 03:00 du matin",
    ]

    for text in help_texts_delete:
        label = ttk.Label(delete_frame, text=text, wraplength=550, justify="left")
        label.pack(anchor="w", pady=5)


def open_a_propos():
    """Ouvre la fenêtre À Propos"""
    about_popup = tk.Toplevel(root)
    about_popup.title("À Propos")
    about_popup.geometry("500x250")
    about_popup.minsize(500, 250)
    about_popup.resizable(False, False)

    main_about_frame = ttk.Frame(about_popup, padding=20)
    main_about_frame.pack(fill="both", expand=True)

    # Titre
    title_label = ttk.Label(
        main_about_frame, text="Auto Backup & Delete", style="Header.TLabel"
    )
    title_label.pack(pady=(0, 20))

    # Contenu
    content_frame = ttk.Frame(main_about_frame)
    content_frame.pack(fill="both", expand=True)

    ttk.Label(
        content_frame, text="© Copyright - Valentin Luthringer", foreground="#666"
    ).pack(anchor="w", pady=5)

    github_frame = ttk.Frame(content_frame)
    github_frame.pack(anchor="w", pady=5)

    ttk.Label(github_frame, text="GitHub: ").pack(side="left")
    github_link = ttk.Label(
        github_frame, text="@valuthringer", foreground="#2E7D32", cursor="hand2"
    )
    github_link.pack(side="left")
    github_link.bind("<Button-1>", lambda e: open_github_link())

    ttk.Label(
        content_frame,
        text="Version 2.2 - Modernisée avec Forest-ttk",
        foreground="#666",
    ).pack(anchor="w", pady=5)
    ttk.Label(content_frame, text="Mise à jour: 12-12-2024", foreground="#999").pack(
        anchor="w", pady=5
    )

    # Lien vers l'historique
    history_frame = ttk.Frame(content_frame)
    history_frame.pack(anchor="w", pady=10)
    history_link = ttk.Label(
        history_frame,
        text="Version History",
        foreground="#2E7D32",
        cursor="hand2",
    )
    history_link.pack()
    history_link.bind("<Button-1>", lambda e: open_logs_versions())


# Création de la fenêtre principale
root = tk.Tk()
root.title("Auto Backup & Delete by @valuthringer")
root.geometry("900x700")
root.minsize(900, 600)

# Charger le thème
load_forest_theme()

# Configuration du style global
style = ttk.Style()
# Le thème Forest gère tous les styles - ne pas écraser ses couleurs !

# Configuration personnalisée des Entry et Spinbox pour les rendre plus gris
style.configure(
    "TEntry", fieldbackground="#3a3a3a", background="#3a3a3a", foreground="#e0e0e0"
)
style.configure(
    "TSpinbox", fieldbackground="#3a3a3a", background="#3a3a3a", foreground="#e0e0e0"
)
style.configure(
    "TCombobox", fieldbackground="#3a3a3a", background="#3a3a3a", foreground="#e0e0e0"
)

# Ajouter des styles d'accentuation verte (Forest style)
style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))


# Configurer les zones de texte après création
def configure_text_widget(widget):
    """Configure un widget Text avec les couleurs Forest"""
    widget.config(
        bg="#3a3a3a", fg="#e0e0e0", insertbackground="#2E7D32", relief="solid", bd=1
    )


# Frame principal avec scrollbar
main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# Canvas avec scrollbar pour la zone principale
canvas_frame = ttk.Frame(main_frame)
canvas_frame.pack(fill="both", expand=True)

canvas = tk.Canvas(canvas_frame, highlightthickness=0)
scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

# Barre de boutons supérieure
top_buttons_frame = ttk.Frame(scrollable_frame)
top_buttons_frame.pack(fill="x", pady=(0, 10))

help_button = ttk.Button(
    top_buttons_frame, text="Help", command=open_help, style="Accent.TButton"
)
help_button.pack(side="left", padx=5)

apropos_button = ttk.Button(
    top_buttons_frame, text="About", command=open_a_propos, style="Accent.TButton"
)
apropos_button.pack(side="left", padx=5)

# Conteneur à deux colonnes
columns_frame = ttk.Frame(scrollable_frame)
columns_frame.pack(fill="both", expand=True)

columns_frame.columnconfigure(0, weight=1)
columns_frame.columnconfigure(1, weight=1)

# ============ PARTIE SAUVEGARDES (Colonne gauche) ============
backup_frame = ttk.LabelFrame(columns_frame, text="BACKUPS", padding=15)
backup_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))

# Titre section
backup_label = ttk.Label(
    backup_frame, text="Configuration des sauvegardes", style="Section.TLabel"
)
backup_label.pack(pady=(0, 10))

# Dossiers source
ttk.Label(backup_frame, text="Dossiers sources:").pack(anchor="w", pady=(10, 0))
root_dirs_text = tk.Text(backup_frame, width=50, height=4, font=("Consolas", 10))
root_dirs_text.pack(pady=(0, 5))
configure_text_widget(root_dirs_text)

add_root_button = ttk.Button(
    backup_frame,
    text="+ Add Source Folder",
    command=add_root_folder,
    style="Accent.TButton",
)
add_root_button.pack(pady=5)

# Destination
ttk.Label(backup_frame, text="Dossier destination:").pack(anchor="w", pady=(10, 0))
dest_frame = ttk.Frame(backup_frame)
dest_frame.pack(fill="x", pady=5)

dest_dir_entry = ttk.Entry(dest_frame)
dest_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

browse_dest_button = ttk.Button(
    dest_frame,
    text="Browse",
    command=browse_dest_folder,
    width=12,
    style="Accent.TButton",
)
browse_dest_button.pack(side="left")

# Fréquence
freq_frame = ttk.LabelFrame(backup_frame, text="Planification", padding=10)
freq_frame.pack(fill="x", pady=10)

freq_row = ttk.Frame(freq_frame)
freq_row.pack(fill="x", pady=5)

ttk.Label(freq_row, text="Tous les").pack(side="left", padx=5)
frequency_entry = ttk.Entry(freq_row, width=5)
frequency_entry.insert(0, "1")
frequency_entry.pack(side="left", padx=5)
ttk.Label(freq_row, text="jour(s)").pack(side="left", padx=5)

hour_row = ttk.Frame(freq_frame)
hour_row.pack(fill="x", pady=5)

ttk.Label(hour_row, text="À").pack(side="left", padx=5)
hour_entry = ttk.Entry(hour_row, width=5)
hour_entry.insert(0, "2")
hour_entry.pack(side="left", padx=5)
ttk.Label(hour_row, text="heures").pack(side="left", padx=5)

# Barre de progression
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(
    backup_frame,
    orient="horizontal",
    length=400,
    mode="determinate",
    variable=progress_var,
)
progress_bar.pack(pady=10, fill="x")

# Statut
status_label = ttk.Label(
    backup_frame, text="", foreground="#2E7D32", font=("Segoe UI", 10)
)
status_label.pack(pady=5)

# Boutons de contrôle
button_frame = ttk.Frame(backup_frame)
button_frame.pack(fill="x", pady=10)

start_backup_button = ttk.Button(
    button_frame,
    text="Start Backup",
    command=start_backup_schedule,
    style="Accent.TButton",
)
start_backup_button.pack(pady=5, fill="x")

stop_backup_button = ttk.Button(
    button_frame,
    text="Stop Backup",
    state="disabled",
    command=stop_backup_schedule,
)
stop_backup_button.pack(pady=5, fill="x")

manual_backup_button = ttk.Button(
    button_frame,
    text="Manual Backup",
    command=manual_backup,
    style="Accent.TButton",
)
manual_backup_button.pack(pady=5, fill="x")

# ============ PARTIE SUPPRESSION (Colonne droite) ============
delete_frame = ttk.LabelFrame(columns_frame, text="AUTO DELETE", padding=15)
delete_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

# Titre section
delete_label = ttk.Label(
    delete_frame, text="Configuration de la suppression", style="Section.TLabel"
)
delete_label.pack(pady=(0, 10))

# Dossier à surveiller
ttk.Label(delete_frame, text="Dossier à surveiller:").pack(anchor="w", pady=(10, 0))
dir_frame = ttk.Frame(delete_frame)
dir_frame.pack(fill="x", pady=5)

directory_entry = ttk.Entry(dir_frame)
directory_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

browse_delete_button = ttk.Button(
    dir_frame,
    text="Browse",
    command=browse_delete_folder,
    width=12,
    style="Accent.TButton",
)
browse_delete_button.pack(side="left")

# Paramètres de suppression
params_frame = ttk.LabelFrame(delete_frame, text="Paramètres", padding=10)
params_frame.pack(fill="x", pady=10)

ttk.Label(params_frame, text="Garder les backups depuis:").pack(anchor="w", pady=(0, 5))

days_frame = ttk.Frame(params_frame)
days_frame.pack(fill="x", pady=5)

days_entry = ttk.Entry(days_frame, width=5)
days_entry.insert(0, "30")
days_entry.pack(side="left", padx=5)

ttk.Label(days_frame, text="jour(s)").pack(side="left", padx=5)

ttk.Label(
    params_frame,
    text="Schedule: Daily at 03:00",
    foreground="#999",
    font=("Segoe UI", 9),
).pack(anchor="w", pady=(10, 0))

# Espace élastique
espace = ttk.Frame(delete_frame)
espace.pack(pady=30)

# Boutons de contrôle
delete_button_frame = ttk.Frame(delete_frame)
delete_button_frame.pack(fill="x", pady=10)

start_delete_button = ttk.Button(
    delete_button_frame,
    text="Start Delete",
    command=start_auto_delete_schedule,
    style="Accent.TButton",
)
start_delete_button.pack(pady=5, fill="x")

stop_delete_button = ttk.Button(
    delete_button_frame,
    text="Stop Delete",
    command=stop_auto_delete_schedule,
    state="disabled",
)
stop_delete_button.pack(pady=5, fill="x")

manual_delete_button = ttk.Button(
    delete_button_frame,
    text="Manual Delete",
    command=manual_delete,
    style="Accent.TButton",
)
manual_delete_button.pack(pady=5, fill="x")

# Empaqueter canvas et scrollbar
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Démarrage interface
root.mainloop()

import os
import time
import tkinter as tk
from tkinter import filedialog, ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import threading
import schedule
import zipfile
import webbrowser
import sys
import json
from pathlib import Path


# Configuration profiles management
def get_config_dir():
    """Retourne le répertoire de configuration (AppData sur Windows, ~/.auto-backup-delete sur Unix)"""
    if sys.platform == "win32":
        config_dir = Path(os.getenv("APPDATA")) / "Auto-Backup-and-Delete"
    else:
        config_dir = Path.home() / ".auto-backup-delete"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_profiles_file():
    """Retourne le chemin du fichier de profils"""
    return get_config_dir() / "profiles.json"


def load_profiles_dict():
    """Charge tous les profils depuis le fichier JSON"""
    profiles_file = get_profiles_file()
    if profiles_file.exists():
        try:
            with open(profiles_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erreur chargement profils: {e}")
            return {}
    return {}


def save_profiles_dict(profiles):
    """Sauvegarde les profils dans le fichier JSON"""
    profiles_file = get_profiles_file()
    try:
        with open(profiles_file, "w", encoding="utf-8") as f:
            json.dump(profiles, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Erreur sauvegarde profils: {e}")


def save_current_config_as_profile(profile_name):
    """Sauvegarde la configuration actuelle comme un profil"""
    profiles = load_profiles_dict()
    profiles[profile_name] = {
        "root_dirs": root_dirs_text.get_paths(),
        "dest_dir": dest_dir_entry.get(),
        "frequency_days": frequency_entry.get(),
        "hour": hour_entry.get(),
        "minute": minute_entry.get(),
        "directory": directory_entry.get(),
        "days": days_entry.get(),
        "delete_hour": delete_hour_entry.get(),
        "delete_minute": delete_minute_entry.get(),
    }
    save_profiles_dict(profiles)
    display_status(f"[OK] Profil '{profile_name}' sauvegardé", "green")
    refresh_profile_list()


def load_profile_config(profile_name):
    """Charge une configuration depuis un profil"""
    profiles = load_profiles_dict()
    if profile_name in profiles:
        config = profiles[profile_name]
        root_dirs_text.set_paths(config.get("root_dirs", ""))
        dest_dir_entry.delete(0, tk.END)
        dest_dir_entry.insert(0, config.get("dest_dir", ""))
        frequency_entry.delete(0, tk.END)
        frequency_entry.insert(0, config.get("frequency_days", "1"))
        hour_entry.delete(0, tk.END)
        hour_entry.insert(0, config.get("hour", "2"))
        minute_entry.delete(0, tk.END)
        minute_entry.insert(0, config.get("minute", "0"))
        directory_entry.delete(0, tk.END)
        directory_entry.insert(0, config.get("directory", ""))
        days_entry.delete(0, tk.END)
        days_entry.insert(0, config.get("days", "30"))
        delete_hour_entry.delete(0, tk.END)
        delete_hour_entry.insert(0, config.get("delete_hour", "3"))
        delete_minute_entry.delete(0, tk.END)
        delete_minute_entry.insert(0, config.get("delete_minute", "0"))
        display_status(f"[OK] Profil '{profile_name}' chargé", "green")


def delete_profile(profile_name):
    """Supprime un profil"""
    profiles = load_profiles_dict()
    if profile_name in profiles:
        del profiles[profile_name]
        save_profiles_dict(profiles)
        display_status(f"[OK] Profil '{profile_name}' supprimé", "green")
        refresh_profile_list()


def refresh_profile_list():
    """Actualise la liste des profils dans l'UI"""
    profiles = load_profiles_dict()
    profile_listbox.delete(0, tk.END)
    for profile_name in sorted(profiles.keys()):
        profile_listbox.insert(tk.END, profile_name)


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


# Utility functions for sizes
def get_directory_size(path):
    """Calcule la taille totale d'un répertoire en bytes"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
    except Exception as e:
        print(f"Erreur lors du calcul de taille: {e}")
    return total_size


def get_selected_dirs_total_size(root_dirs_str):
    """Calcule la taille totale des répertoires sélectionnés"""
    total_size = 0
    for root_dir in root_dirs_str.split(";"):
        root_dir = root_dir.strip()
        if os.path.exists(root_dir):
            total_size += get_directory_size(root_dir)
    return total_size


def get_disk_free_space(path):
    """Retourne l'espace libre disponible sur le disque contenant le chemin"""
    try:
        if os.path.exists(path):
            stat = os.statvfs(path) if hasattr(os, "statvfs") else None
            if stat:
                return stat.f_bavail * stat.f_frsize
            else:
                # Windows fallback
                import ctypes

                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(path), None, None, ctypes.pointer(free_bytes)
                )
                return free_bytes.value
    except Exception as e:
        print(f"Erreur lors de la récupération de l'espace disque: {e}")
    return 0


def format_size(size_bytes):
    """Formate une taille en bytes vers une unité lisible"""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def update_backup_info_display():
    """Met à jour l'affichage des informations de sauvegarde"""
    root_dirs = root_dirs_text.get_paths()
    dest_dir = dest_dir_entry.get()

    if root_dirs:
        total_size = get_selected_dirs_total_size(root_dirs)
        backup_size_label.config(text=f"Taille totale: {format_size(total_size)}")
    else:
        backup_size_label.config(text="Taille totale: -")

    if dest_dir and os.path.exists(dest_dir):
        free_space = get_disk_free_space(dest_dir)
        dest_space_label.config(text=f"Espace disponible: {format_size(free_space)}")
    else:
        dest_space_label.config(text="Espace disponible: -")


def update_next_backup_display():
    """Met à jour l'affichage de la prochaine sauvegarde programmée"""
    try:
        frequency_days = int(frequency_entry.get())
        hour = int(hour_entry.get())
        minute = int(minute_entry.get())
    except (ValueError, AttributeError):
        next_backup_label.config(text="Prochaine backup: -")
        return

    if start_backup_button.cget("state") == "normal":
        next_backup_label.config(text="Prochaine backup: Pas de backup programmée")
    else:
        now = datetime.now()
        next_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if next_time <= now:
            next_time += timedelta(days=frequency_days)
        next_backup_label.config(
            text=f"Prochaine backup: {next_time.strftime('%d-%m-%Y à %H:%M:%S')}"
        )


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
    root_dirs = root_dirs_text.get_paths()
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
    root_dirs = root_dirs_text.get_paths()
    dest_dir = dest_dir_entry.get()
    try:
        frequency_days = int(frequency_entry.get())
        hour = int(hour_entry.get())
        minute = int(minute_entry.get())
        backup_time = f"{hour:02}:{minute:02}"
    except ValueError:
        display_status(
            "[ERROR] Entrée invalide pour la fréquence, l'heure ou les minutes", "red"
        )
        print("Invalid input for frequency, hour or minute")
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
            f"[OK] Backup automatique démarrée tous les {frequency_days} jour(s) à {backup_time}",
            "green",
        )
        update_next_backup_display()
        print(
            f"Automatic backup scheduled every {frequency_days} days at {backup_time}"
        )
    else:
        display_status(
            "[ERROR] Veuillez sélectionner des dossiers sources et une destination",
            "red",
        )


stop_event = threading.Event()
delete_stop_event = threading.Event()


# Arrêt sauvegarde automatique
def stop_backup_schedule():
    """Arrête la sauvegarde automatique"""
    stop_event.set()
    start_backup_button.config(state="normal")
    stop_backup_button.config(state="disabled")
    display_status("[OK] Backup automatique arrêtée", "blue")
    update_next_backup_display()
    print("Automatic backup stopped")


# Ajouter un dossier source
def add_root_folder():
    """Ajoute un dossier source à la liste"""
    folder_selected = filedialog.askdirectory(title="Sélectionner un dossier source")
    if folder_selected and folder_selected not in root_dirs_text.paths:
        root_dirs_text.paths.append(folder_selected)
        root_dirs_text.update_display()


# Démarrer la vérification automatique pour supprimer les fichiers .zip
def start_auto_delete_schedule():
    """Démarre la suppression automatique quotidienne à l'heure/minute configurée"""
    directory = directory_entry.get()
    try:
        days = int(days_entry.get())
        delete_hour = int(delete_hour_entry.get())
        delete_minute = int(delete_minute_entry.get())
        delete_time = f"{delete_hour:02}:{delete_minute:02}"
    except ValueError:
        display_status("[ERROR] Paramètres invalides pour la suppression", "red")
        print("Invalid parameters for delete schedule")
        return
    if directory and os.path.exists(directory):
        delete_stop_event.clear()
        schedule.every().day.at(delete_time).do(
            check_and_delete_zip_files, directory, days
        )

        def run_schedule():
            while not delete_stop_event.is_set():
                schedule.run_pending()
                time.sleep(1)

        schedule_thread = threading.Thread(target=run_schedule, daemon=True)
        schedule_thread.start()

        start_delete_button.config(state="disabled")
        stop_delete_button.config(state="normal")
        display_status(
            f"[OK] Suppression automatique démarrée quotidiennement à {delete_time}",
            "green",
        )
        print(f"Automatic delete started daily at {delete_time}")
    else:
        display_status("[ERROR] Répertoire invalide", "red")


# Arrêter l'auto suppression
def stop_auto_delete_schedule():
    """Arrête la suppression automatique"""
    delete_stop_event.set()
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


# Fonctions UI pour les profils
def save_profile_dialog():
    """Ouvre un dialogue pour nommer et sauvegarder un profil"""
    profile_name = simpledialog.askstring(
        "Sauvegarder profil", "Nom du profil:", parent=root
    )
    if profile_name:
        if profile_name.strip():
            save_current_config_as_profile(profile_name.strip())
        else:
            display_status("[ERROR] Nom de profil vide", "red")


def load_selected_profile():
    """Charge le profil sélectionné"""
    selection = profile_listbox.curselection()
    if selection:
        profile_name = profile_listbox.get(selection[0])
        load_profile_config(profile_name)


def delete_selected_profile():
    """Supprime le profil sélectionné après confirmation"""
    selection = profile_listbox.curselection()
    if selection:
        profile_name = profile_listbox.get(selection[0])
        if messagebox.askyesno(
            "Confirmation", f"Supprimer le profil '{profile_name}' ?"
        ):
            delete_profile(profile_name)


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
root.geometry("1000x800")
root.minsize(700, 500)

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


class TagsWidget:
    """Widget personnalisé avec liste scrollable de tags/paths en blocs"""

    def __init__(self, parent, **kwargs):
        self.paths = []
        self.main_frame = ttk.Frame(parent)

        # Frame pour l'input EN HAUT
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill="x", pady=(0, 5))

        self.input_entry = ttk.Entry(self.input_frame)
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.input_entry.bind("<Return>", lambda e: self.add_tag_from_input())

        self.ok_button = ttk.Button(
            self.input_frame, text="OK", command=self.add_tag_from_input, width=5
        )
        self.ok_button.pack(side="left")

        # Canvas SCROLLABLE pour les tags
        canvas_frame = ttk.Frame(self.main_frame)
        canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            canvas_frame, height=120, highlightthickness=0, bg="#3a3a3a", bd=0
        )
        scrollbar = ttk.Scrollbar(
            canvas_frame, orient="vertical", command=self.canvas.yview
        )

        self.tags_frame = tk.Frame(self.canvas, bg="#3a3a3a")

        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.tags_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Bind pour redimensionner le canvas window avec le canvas
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Bind la molette pour scroll
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

        self.tags_frame.bind("<Configure>", self._on_frame_configure)

        self.update_display()

    def _on_canvas_configure(self, event):
        """Redimensionne le canvas window quand le canvas change de taille"""
        canvas_width = event.width - 20
        if canvas_width > 0:
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)

    def _bind_scroll_to_widget(self, widget):
        """Attache les événements de scroll à un widget"""
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>", self._on_mousewheel)
        widget.bind("<Button-5>", self._on_mousewheel)
        # Récursivement binder les enfants aussi
        for child in widget.winfo_children():
            self._bind_scroll_to_widget(child)

    def _on_mousewheel(self, event):
        """Gère le scroll à la molette - uniquement si le contenu dépasse"""
        # Vérifier si le contenu dépasse la hauteur du canvas
        scrollregion = self.canvas.cget("scrollregion")
        if scrollregion:
            # scrollregion est au format "x1 y1 x2 y2"
            try:
                parts = [int(x) for x in scrollregion.split()]
                content_height = parts[3] - parts[1]
                canvas_height = self.canvas.winfo_height()

                # Bloquer le scroll si le contenu rentre entièrement
                if content_height <= canvas_height:
                    return "break"
            except:
                pass

        # Faire le scroll si le contenu dépasse
        if event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(3, "units")
        elif event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-3, "units")

        return "break"

    def _on_frame_configure(self, event=None):
        """Rafraîchit la région scrollable"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def pack(self, **kwargs):
        """Émule pack pour le frame principal"""
        self.main_frame.pack(**kwargs)

    def grid(self, **kwargs):
        """Émule grid pour le frame principal"""
        self.main_frame.grid(**kwargs)

    def add_tag_from_input(self):
        """Ajoute le chemin depuis le champ de saisie"""
        path = self.input_entry.get().strip()
        if path and path not in self.paths:
            self.paths.append(path)
            self.input_entry.delete(0, tk.END)
            self.update_display()

    def remove_tag(self, path):
        """Supprime un chemin de la liste"""
        if path in self.paths:
            self.paths.remove(path)
            self.update_display()

    def update_display(self):
        """Rafraîchit l'affichage des blocs en liste verticale"""
        for widget in self.tags_frame.winfo_children():
            widget.destroy()

        if self.paths:
            for i, path in enumerate(self.paths):
                tag_frame = tk.Frame(
                    self.tags_frame,
                    relief="solid",
                    borderwidth=1,
                    bg="#4a4a4a",
                    height=35,
                )
                tag_frame.pack(fill="x", padx=2, pady=2)
                tag_frame.pack_propagate(False)
                tag_frame.columnconfigure(0, weight=1)

                # Truncate long paths
                display_text = path if len(path) <= 60 else path[:57] + "..."
                path_label = tk.Label(
                    tag_frame,
                    text=display_text,
                    bg="#4a4a4a",
                    fg="#e0e0e0",
                    padx=5,
                    pady=3,
                    anchor="w",
                    justify="left",
                    font=("Consolas", 9),
                )
                path_label.grid(row=0, column=0, sticky="ew", padx=(5, 0), pady=3)

                remove_button = tk.Button(
                    tag_frame,
                    text="✕",
                    width=3,
                    bg="#d32f2f",
                    fg="white",
                    command=lambda p=path: self.remove_tag(p),
                    relief="flat",
                    padx=2,
                    pady=2,
                    font=("Segoe UI", 11, "bold"),
                )
                remove_button.grid(row=0, column=1, sticky="e", padx=5, pady=3)

                # Bind scroll à tous les widgets de la ligne
                self._bind_scroll_to_widget(tag_frame)
        else:
            empty_label = tk.Label(
                self.tags_frame,
                text="Aucun dossier sélectionné",
                bg="#3a3a3a",
                fg="#888888",
                pady=20,
            )
            empty_label.pack(fill="x")
            # Bind scroll aussi au label vide
            self._bind_scroll_to_widget(empty_label)

        # Update canvas scroll region
        self.tags_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def get_paths(self):
        """Retourne les chemins séparés par ;"""
        return "; ".join(self.paths)

    def set_paths(self, paths_str):
        """Définit les chemins à partir d'une chaîne séparée par ;"""
        self.paths = [p.strip() for p in paths_str.split(";") if p.strip()]
        self.update_display()


# Frame principal avec scrollbar
main_frame = ttk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=12, pady=12)
main_frame.rowconfigure(1, weight=1)
main_frame.columnconfigure(0, weight=1)

# Barre de boutons supérieure
top_buttons_frame = ttk.Frame(main_frame)
top_buttons_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8))

help_button = ttk.Button(
    top_buttons_frame, text="Help", command=open_help, style="Accent.TButton"
)
help_button.pack(side="left", padx=5)

apropos_button = ttk.Button(
    top_buttons_frame, text="About", command=open_a_propos, style="Accent.TButton"
)
apropos_button.pack(side="left", padx=5)

# ============ SECTION PROFILS ============
profiles_frame = ttk.LabelFrame(main_frame, text="PROFILS", padding=10)
profiles_frame.grid(row=0, column=0, sticky="ew", pady=(0, 8), padx=0)

profiles_list_label = ttk.Label(profiles_frame, text="Profils sauvegardés:")
profiles_list_label.pack(anchor="w", pady=(0, 5))

profile_listbox = tk.Listbox(
    profiles_frame, height=3, font=("Consolas", 9), bg="#3a3a3a", fg="#e0e0e0"
)
profile_listbox.pack(fill="x", pady=5)

profiles_buttons_frame = ttk.Frame(profiles_frame)
profiles_buttons_frame.pack(fill="x", pady=5)

load_profile_button = ttk.Button(
    profiles_buttons_frame,
    text="Load Profile",
    command=load_selected_profile,
    style="Accent.TButton",
    width=10,
)
load_profile_button.pack(side="left", padx=3)

save_profile_button = ttk.Button(
    profiles_buttons_frame,
    text="Save Profile",
    command=save_profile_dialog,
    style="Accent.TButton",
    width=10,
)
save_profile_button.pack(side="left", padx=3)

delete_profile_button = ttk.Button(
    profiles_buttons_frame,
    text="Delete Profile",
    command=delete_selected_profile,
    width=10,
)
delete_profile_button.pack(side="left", padx=3)

# Charger les profils au démarrage
refresh_profile_list()

# Helper pour créer une zone scrollable avec scroll vertical auto-masqué
def _make_scrollable_area(parent):
    """Retourne (container, inner_frame, canvas) — scrollbar affichée seulement si contenu dépasse"""
    try:
        bg = ttk.Style().lookup("TFrame", "background") or "#313131"
    except Exception:
        bg = "#313131"
    container = ttk.Frame(parent)
    canvas = tk.Canvas(container, highlightthickness=0, bd=0, bg=bg)
    vscroll = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vscroll.set)
    inner = ttk.Frame(canvas)
    win_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _check_scroll(_=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        if inner.winfo_reqheight() > canvas.winfo_height() + 2:
            if not vscroll.winfo_ismapped():
                vscroll.pack(side="right", fill="y")
        else:
            if vscroll.winfo_ismapped():
                vscroll.pack_forget()

    def _on_resize(event):
        canvas.itemconfig(win_id, width=event.width)
        _check_scroll()

    canvas.bind("<Configure>", _on_resize)
    inner.bind("<Configure>", _check_scroll)
    canvas.pack(side="left", fill="both", expand=True)
    return container, inner, canvas


# Conteneur à deux colonnes
columns_frame = ttk.Frame(main_frame)
columns_frame.grid(row=1, column=0, sticky="nsew", pady=0, padx=0)
columns_frame.rowconfigure(0, weight=1)
columns_frame.columnconfigure(0, weight=1)
columns_frame.columnconfigure(1, weight=1)

# ============ PARTIE SAUVEGARDES (Colonne gauche) ============
backup_frame = ttk.LabelFrame(columns_frame, text="BACKUPS", padding=12)
backup_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

# Boutons ÉPINGLÉS en bas — packés en premier pour réserver l'espace
button_frame = ttk.Frame(backup_frame)
button_frame.pack(side="bottom", fill="x", pady=(8, 0))
button_frame.columnconfigure(0, weight=1)
button_frame.columnconfigure(1, weight=1)
button_frame.columnconfigure(2, weight=1)

start_backup_button = ttk.Button(
    button_frame, text="Start Backup", command=start_backup_schedule, style="Accent.TButton",
)
start_backup_button.grid(row=0, column=0, sticky="ew", padx=(0, 3))

stop_backup_button = ttk.Button(
    button_frame, text="Stop Backup", state="disabled", command=stop_backup_schedule,
)
stop_backup_button.grid(row=0, column=1, sticky="ew", padx=3)

manual_backup_button = ttk.Button(
    button_frame, text="Manual Backup", command=manual_backup, style="Accent.TButton",
)
manual_backup_button.grid(row=0, column=2, sticky="ew", padx=(3, 0))

# Zone scrollable (prend tout l'espace restant au-dessus des boutons)
backup_scroll_container, backup_inner, backup_canvas = _make_scrollable_area(backup_frame)
backup_scroll_container.pack(side="top", fill="both", expand=True)
backup_inner.columnconfigure(0, weight=1)
backup_inner.columnconfigure(1, weight=1)

# Titre section
backup_label = ttk.Label(
    backup_inner, text="Configuration des sauvegardes", style="Section.TLabel"
)
backup_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

# Dossiers source
ttk.Label(backup_inner, text="Dossiers sources:", font=("Segoe UI", 10)).grid(
    row=1, column=0, sticky="w", pady=(8, 3)
)
root_dirs_text = TagsWidget(backup_inner)
root_dirs_text.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 8))

add_root_button = ttk.Button(
    backup_inner, text="+ Add Source Folder", command=add_root_folder, style="Accent.TButton",
)
add_root_button.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))

# Destination
ttk.Label(backup_inner, text="Dossier destination:", font=("Segoe UI", 10)).grid(
    row=4, column=0, sticky="w", pady=(8, 3)
)
dest_frame = ttk.Frame(backup_inner)
dest_frame.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 8))
dest_frame.columnconfigure(0, weight=1)

dest_dir_entry = ttk.Entry(dest_frame)
dest_dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

browse_dest_button = ttk.Button(
    dest_frame, text="Browse", command=browse_dest_folder, width=12, style="Accent.TButton",
)
browse_dest_button.pack(side="left")

# Fréquence
freq_frame = ttk.LabelFrame(backup_inner, text="Planification", padding=10)
freq_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(0, 8))
freq_frame.columnconfigure(1, weight=1)

freq_row = ttk.Frame(freq_frame)
freq_row.pack(fill="x", pady=4)

ttk.Label(freq_row, text="Tous les", font=("Segoe UI", 10)).pack(side="left", padx=5)
frequency_entry = ttk.Entry(freq_row, width=5)
frequency_entry.insert(0, "1")
frequency_entry.pack(side="left", padx=5)
ttk.Label(freq_row, text="jour(s)", font=("Segoe UI", 10)).pack(side="left", padx=5)

time_row = ttk.Frame(freq_frame)
time_row.pack(fill="x", pady=4)

ttk.Label(time_row, text="À", font=("Segoe UI", 10)).pack(side="left", padx=5)
hour_entry = ttk.Entry(time_row, width=3)
hour_entry.insert(0, "2")
hour_entry.pack(side="left", padx=2)
ttk.Label(time_row, text="h", font=("Segoe UI", 10)).pack(side="left", padx=2)
minute_entry = ttk.Entry(time_row, width=3)
minute_entry.insert(0, "0")
minute_entry.pack(side="left", padx=2)
ttk.Label(time_row, text="min", font=("Segoe UI", 10)).pack(side="left", padx=2)

# Barre de progression
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(
    backup_inner, orient="horizontal", length=400, mode="determinate", variable=progress_var,
)
progress_bar.grid(row=7, column=0, columnspan=2, sticky="ew", pady=8, padx=0)

# Info labels
info_frame = ttk.Frame(backup_inner)
info_frame.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(5, 5), padx=5)

backup_size_label = ttk.Label(
    info_frame, text="Taille totale: -", foreground="#2E7D32", font=("Segoe UI", 9)
)
backup_size_label.pack(anchor="w", pady=2)

dest_space_label = ttk.Label(
    info_frame, text="Espace disponible: -", foreground="#2E7D32", font=("Segoe UI", 9),
)
dest_space_label.pack(anchor="w", pady=2)

next_backup_label = ttk.Label(
    info_frame, text="Prochaine backup: -", foreground="#2E7D32", font=("Segoe UI", 9)
)
next_backup_label.pack(anchor="w", pady=2)

# Statut
status_label = ttk.Label(
    backup_inner, text="", foreground="#2E7D32", font=("Segoe UI", 10)
)
status_label.grid(row=9, column=0, columnspan=2, sticky="ew", pady=5)


# ============ PARTIE SUPPRESSION (Colonne droite) ============
delete_frame = ttk.LabelFrame(columns_frame, text="AUTO DELETE", padding=12)
delete_frame.grid(row=0, column=1, sticky="nsew", padx=(6, 0))

# Boutons ÉPINGLÉS en bas — packés en premier
delete_button_frame = ttk.Frame(delete_frame)
delete_button_frame.pack(side="bottom", fill="x", pady=(8, 0))
delete_button_frame.columnconfigure(0, weight=1)
delete_button_frame.columnconfigure(1, weight=1)
delete_button_frame.columnconfigure(2, weight=1)

start_delete_button = ttk.Button(
    delete_button_frame, text="Start Delete", command=start_auto_delete_schedule, style="Accent.TButton",
)
start_delete_button.grid(row=0, column=0, sticky="ew", padx=(0, 3))

stop_delete_button = ttk.Button(
    delete_button_frame, text="Stop Delete", command=stop_auto_delete_schedule, state="disabled",
)
stop_delete_button.grid(row=0, column=1, sticky="ew", padx=3)

manual_delete_button = ttk.Button(
    delete_button_frame, text="Manual Delete", command=manual_delete, style="Accent.TButton",
)
manual_delete_button.grid(row=0, column=2, sticky="ew", padx=(3, 0))

# Zone scrollable
delete_scroll_container, delete_inner, delete_canvas = _make_scrollable_area(delete_frame)
delete_scroll_container.pack(side="top", fill="both", expand=True)
delete_inner.columnconfigure(0, weight=1)
delete_inner.columnconfigure(1, weight=1)

# Titre section
delete_label = ttk.Label(
    delete_inner, text="Configuration de la suppression", style="Section.TLabel"
)
delete_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 8))

# Dossier à surveiller
ttk.Label(delete_inner, text="Dossier à surveiller:", font=("Segoe UI", 10)).grid(
    row=1, column=0, sticky="w", pady=(8, 3)
)
dir_frame = ttk.Frame(delete_inner)
dir_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 8))
dir_frame.columnconfigure(0, weight=1)

directory_entry = ttk.Entry(dir_frame)
directory_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

browse_delete_button = ttk.Button(
    dir_frame, text="Browse", command=browse_delete_folder, width=12, style="Accent.TButton",
)
browse_delete_button.pack(side="left")

# Paramètres de suppression
params_frame = ttk.LabelFrame(delete_inner, text="Paramètres", padding=10)
params_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))
params_frame.columnconfigure(1, weight=1)

ttk.Label(params_frame, text="Garder les backups depuis:", font=("Segoe UI", 10)).pack(
    anchor="w", pady=(0, 5)
)

days_frame = ttk.Frame(params_frame)
days_frame.pack(fill="x", pady=4)

days_entry = ttk.Entry(days_frame, width=5)
days_entry.insert(0, "30")
days_entry.pack(side="left", padx=5)

ttk.Label(days_frame, text="jour(s)", font=("Segoe UI", 10)).pack(side="left", padx=5)

# Planning de suppression
ttk.Label(params_frame, text="Planification quotidienne:", font=("Segoe UI", 10)).pack(
    anchor="w", pady=(8, 5)
)

schedule_frame = ttk.Frame(params_frame)
schedule_frame.pack(fill="x", pady=4)

ttk.Label(schedule_frame, text="À", font=("Segoe UI", 10)).pack(side="left", padx=5)
delete_hour_entry = ttk.Entry(schedule_frame, width=3)
delete_hour_entry.insert(0, "3")
delete_hour_entry.pack(side="left", padx=2)
ttk.Label(schedule_frame, text="h", font=("Segoe UI", 10)).pack(side="left", padx=2)
delete_minute_entry = ttk.Entry(schedule_frame, width=3)
delete_minute_entry.insert(0, "0")
delete_minute_entry.pack(side="left", padx=2)
ttk.Label(schedule_frame, text="min", font=("Segoe UI", 10)).pack(side="left", padx=2)

# Info labels
espace = ttk.Frame(delete_inner)
espace.grid(row=4, column=0, columnspan=2, sticky="ew", pady=8)

delete_backup_folder_label = ttk.Label(
    espace, text="Dossier de backup: -", foreground="#2E7D32", font=("Segoe UI", 9)
)
delete_backup_folder_label.pack(anchor="w", pady=5)


# Routage molette → bon canvas selon la zone survolée
def _setup_scroll_routing():
    scroll_areas = [
        (backup_scroll_container, backup_canvas, backup_scroll_container),
        (delete_scroll_container, delete_canvas, delete_scroll_container),
    ]

    # Map canvas → its scrollbar widget for visibility check
    canvas_to_scrollbar = {}
    for container, canvas, _ in scroll_areas:
        for child in container.winfo_children():
            if isinstance(child, ttk.Scrollbar):
                canvas_to_scrollbar[canvas] = child
                break

    def _find_canvas(widget):
        current = widget
        while current is not None:
            for container, canvas, _ in scroll_areas:
                if current is container:
                    return canvas
            try:
                current = current.master
            except AttributeError:
                break
        return None

    def _on_scroll(event):
        canvas = _find_canvas(event.widget)
        if canvas:
            vscroll = canvas_to_scrollbar.get(canvas)
            if vscroll and not vscroll.winfo_ismapped():
                return
            if event.num == 5 or event.delta < 0:
                canvas.yview_scroll(3, "units")
            elif event.num == 4 or event.delta > 0:
                canvas.yview_scroll(-3, "units")

    root.bind_all("<MouseWheel>", _on_scroll, add="+")
    root.bind_all("<Button-4>", _on_scroll, add="+")
    root.bind_all("<Button-5>", _on_scroll, add="+")


root.after(100, _setup_scroll_routing)

# Event bindings to update info displays
root_dirs_text.input_entry.bind("<KeyRelease>", lambda e: update_backup_info_display())
dest_dir_entry.bind("<KeyRelease>", lambda e: update_backup_info_display())
frequency_entry.bind("<KeyRelease>", lambda e: update_next_backup_display())
hour_entry.bind("<KeyRelease>", lambda e: update_next_backup_display())
minute_entry.bind("<KeyRelease>", lambda e: update_next_backup_display())

# Initial display update
root.after(500, update_backup_info_display)

# Démarrage interface
root.mainloop()

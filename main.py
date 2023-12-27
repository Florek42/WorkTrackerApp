import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json


class TaskTrackerApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Task Tracker")

    # Lista zadań
    self.tasks = []

    # Nazwa pliku do zapisu i wczytywania listy zadań
    self.filename = "tasks.json"

    # Nazwa pliku do zapisu i wczytywania ustawień
    self.settings_filename = "settings.json"

    # Domyślny motyw
    self.current_theme = tk.StringVar(value="Classic")
    self.load_settings()
    self.set_theme()

    # Tworzenie interfejsu
    self.create_ui()

    # Wczytanie listy zadań po uruchomieniu
    self.load_or_create_tasks()

  def create_ui(self):
    # Pasek nawigacyjny (menu)
    menu_bar = tk.Menu(self.root)
    self.root.config(menu=menu_bar)

    # Zakładka "Plik"
    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Plik", menu=file_menu)
    file_menu.add_command(label="Wczytaj", command=self.load_or_create_tasks)
    file_menu.add_command(label="Zapisz", command=self.save_tasks)
    file_menu.add_separator()
    file_menu.add_command(label="Wyjście", command=self.on_closing)

    # Zakładka "Motyw"
    theme_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Motyw", menu=theme_menu)
    theme_menu.add_radiobutton(label="Classic",
                               variable=self.current_theme,
                               value="Classic",
                               command=self.set_theme)
    theme_menu.add_radiobutton(label="Light",
                               variable=self.current_theme,
                               value="Light",
                               command=self.set_theme)
    theme_menu.add_radiobutton(label="Dark",
                               variable=self.current_theme,
                               value="Dark",
                               command=self.set_theme)

    # Etykieta i pole tekstowe dla nowego zadania
    tk.Label(self.root, text="Nowe zadanie:").pack(pady=5)
    self.new_task_entry = tk.Entry(self.root, width=30)
    self.new_task_entry.pack(pady=5)

    # Przycisk do dodawania nowego zadania
    tk.Button(self.root, text="Dodaj zadanie",
              command=self.add_task).pack(pady=5)

    # Ramka do wyświetlania zadań
    self.task_frame = tk.Frame(self.root)
    self.task_frame.pack(pady=5)

    # Pasek postępu
    self.progress_bar = ttk.Progressbar(self.root,
                                        orient="horizontal",
                                        length=300,
                                        mode="determinate")
    self.progress_bar.pack(pady=10)

    # Etykieta z informacją o postępie
    self.progress_label = tk.Label(self.root, text="Postęp: 0%")
    self.progress_label.pack(pady=5)

  def set_theme(self):
    theme = self.current_theme.get().lower()
    if theme == "light":
      bg_color = '#F0F0F0'
      fg_color = '#000000'
      active_bg_color = '#C0C0C0'
      active_fg_color = '#000000'
      checkbox_bg = '#F0F0F0'
    elif theme == "dark":
      bg_color = '#1E1E1E'
      fg_color = '#FFFFFF'
      active_bg_color = '#505050'
      active_fg_color = '#FFFFFF'
      checkbox_bg = '#1E1E1E'
    else:
      bg_color = '#D9D9D9'
      fg_color = '#000000'
      active_bg_color = '#BFBFBF'
      active_fg_color = '#000000'
      checkbox_bg = '#D9D9D9'

    self.root.tk_setPalette(background=bg_color,
                            foreground=fg_color,
                            activeBackground=active_bg_color,
                            activeForeground=active_fg_color)

    # Dostosowanie koloru tła dla checkboxów
    style = ttk.Style()
    style.map("TCheckbutton",
              background=[('selected', checkbox_bg)],
              foreground=[('selected', fg_color)])

    # Zapisanie ustawień
    self.save_settings()

  def add_task(self):
    task_text = self.new_task_entry.get()
    if task_text:
      task_number = len(self.tasks) + 1
      task_with_number = f"{task_number}. {task_text}"
      self.tasks.append({"text": task_with_number, "completed": False})

      # Tworzenie ramki dla zadania
      task_frame = tk.Frame(self.task_frame, bd=2, relief=tk.GROOVE)
      task_frame.pack(pady=5, fill=tk.X)

      # Etykieta z zadaniem
      task_label = tk.Label(task_frame, text=task_with_number, anchor="w")
      task_label.pack(side=tk.LEFT, padx=5)

      # Kwadracik do oznaczania wykonania zadania
      completion_checkbox = tk.Checkbutton(
          task_frame, command=lambda: self.toggle_completion(task_label))
      completion_checkbox.pack(side=tk.LEFT, padx=5)

      # Przycisk do usuwania zadania
      delete_button = tk.Button(task_frame,
                                text="Usuń",
                                command=lambda: self.remove_task(task_frame))
      delete_button.pack(side=tk.RIGHT, padx=5)

      # Przypisanie referencji do zadania
      task_frame.task_label = task_label
      task_frame.completion_checkbox = completion_checkbox
      task_frame.delete_button = delete_button

      self.new_task_entry.delete(0, tk.END)
      self.update_progress_bar()

  def toggle_completion(self, task_label):
    task_text = task_label["text"]
    task_index = int(task_text.split(".")[0]) - 1
    task = self.tasks[task_index]
    task["completed"] = not task["completed"]
    self.update_progress_bar()

  def remove_task(self, task_frame):
    task_text = task_frame.task_label["text"]
    task_index = int(task_text.split(".")[0]) - 1
    del self.tasks[task_index]
    task_frame.destroy()
    self.update_task_numbers()
    self.update_progress_bar()

  def update_task_numbers(self):
    for index, task_frame in enumerate(self.task_frame.winfo_children()):
      task_text = task_frame.task_label["text"]
      number, _ = task_text.split(". ", 1)
      task_frame.task_label["text"] = f"{index + 1}. {_}"

  def update_progress_bar(self):
    total_tasks = len(self.tasks)
    completed_tasks = sum(task["completed"] for task in self.tasks)
    progress_percentage = (completed_tasks /
                           total_tasks) * 100 if total_tasks > 0 else 0
    self.progress_bar["value"] = progress_percentage
    self.progress_label["text"] = f"Postęp: {int(progress_percentage)}%"

  def save_tasks(self):
    with open(self.filename, "w") as file:
      json.dump(self.tasks, file)
      messagebox.showinfo("Zapisano", "Lista zadań została zapisana.")

  def load_or_create_tasks(self):
    try:
      with open(self.filename, "r") as file:
        self.tasks = json.load(file)
        self.display_tasks()
        self.update_progress_bar()
        messagebox.showinfo("Wczytano", "Lista zadań została wczytana.")
    except FileNotFoundError:
      messagebox.showinfo(
          "Brak pliku",
          "Plik z listą zadań nie istnieje. Tworzenie nowej listy.")
      self.tasks = []

  def display_tasks(self):
    for task_frame in self.task_frame.winfo_children():
      task_frame.destroy()

    for task_dict in self.tasks:
      task_frame = tk.Frame(self.task_frame, bd=2, relief=tk.GROOVE)
      task_frame.pack(pady=5, fill=tk.X)

      task_label = tk.Label(task_frame, text=task_dict["text"], anchor="w")
      task_label.pack(side=tk.LEFT, padx=5)

      completion_checkbox = tk.Checkbutton(
          task_frame, command=lambda: self.toggle_completion(task_label))
      completion_checkbox.pack(side=tk.LEFT, padx=5)
      completion_checkbox.select(
      ) if task_dict["completed"] else completion_checkbox.deselect()

      delete_button = tk.Button(
          task_frame,
          text="Usuń",
          command=lambda frame=task_frame: self.remove_task(frame))
      delete_button.pack(side=tk.RIGHT, padx=5)

      task_frame.task_label = task_label
      task_frame.completion_checkbox = completion_checkbox
      task_frame.delete_button = delete_button

  def on_closing(self):
    self.save_tasks()
    self.root.destroy()

  def save_settings(self):
    settings = {"theme": self.current_theme.get()}
    with open(self.settings_filename, "w") as settings_file:
      json.dump(settings, settings_file)

  def load_settings(self):
    try:
      with open(self.settings_filename, "r") as settings_file:
        settings = json.load(settings_file)
        if "theme" in settings:
          self.current_theme.set(settings["theme"])
    except FileNotFoundError:
      pass


if __name__ == "__main__":
  root = tk.Tk()
  app = TaskTrackerApp(root)
  root.mainloop()

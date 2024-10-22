import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pygame
import time
from threading import Thread

class Node:
    def __init__(self, song, file_path):
        self.song = song
        self.file_path = file_path
        self.next = None
        self.prev = None

class DoublyLinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None

    def add_to_end(self, song, file_path):
        new_node = Node(song, file_path)
        if not self.head:
            self.head = new_node
            self.tail = new_node
            self.current = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node

    def delete_current(self):
        if self.current:
            if self.current == self.head and self.current == self.tail:
                self.head = None
                self.tail = None
                self.current = None
            elif self.current == self.head:
                self.head = self.current.next
                self.head.prev = None
                self.current = self.head
            elif self.current == self.tail:
                self.tail = self.current.prev
                self.tail.next = None
                self.current = self.tail
            else:
                self.current.prev.next = self.current.next
                self.current.next.prev = self.current.prev
                self.current = self.current.next

    def advance(self):
        if self.current and self.current.next:
            self.current = self.current.next

    def go_back(self):
        if self.current and self.current.prev:
            self.current = self.current.prev

    def get_current_song(self):
        if self.current:
            return self.current.song
        return None

    def get_current_song_file(self):
        if self.current:
            return self.current.file_path
        return None

class PlaylistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Lista de Reproducción de Canciones")
        self.root.geometry("500x400")
        self.root.config(bg="#222831")

        pygame.mixer.init()

        self.playlist = DoublyLinkedList()
        self.song_length = 0
        self.update_progress = False

        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 12), padding=5)
        self.style.configure("TLabel", font=("Helvetica", 12), background="#222831", foreground="#EEEEEE")
        self.style.configure("TScale", background="#222831", troughcolor="#00ADB5", sliderlength=20)

        self.add_button = ttk.Button(root, text="Agregar Canción", command=self.add_song)
        self.add_button.pack(pady=5)

        self.delete_button = ttk.Button(root, text="Eliminar Canción Actual", command=self.delete_current)
        self.delete_button.pack(pady=5)

        self.play_button = ttk.Button(root, text="Reproducir", command=self.play_song)
        self.play_button.pack(pady=5)

        self.pause_button = ttk.Button(root, text="Pausar", command=self.pause_song)
        self.pause_button.pack(pady=5)

        self.advance_button = ttk.Button(root, text="Siguiente", command=self.advance_song)
        self.advance_button.pack(pady=5)

        self.back_button = ttk.Button(root, text="Anterior", command=self.go_back_song)
        self.back_button.pack(pady=5)

        self.current_song_label = ttk.Label(root, text="Canción Actual: Ninguna")
        self.current_song_label.pack(pady=10)

        self.song_progress = ttk.Scale(root, from_=0, to=100, orient="horizontal", length=400, command=self.seek_song)
        self.song_progress.pack(pady=10)

    def add_song(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP3 files", "*.mp3"), ("WAV files", "*.wav")])
        if file_path:
            song_name = file_path.split("/")[-1]
            self.playlist.add_to_end(song_name, file_path)
            self.update_current_song()

    def delete_current(self):
        pygame.mixer.music.stop()
        self.update_progress = False
        self.playlist.delete_current()
        self.update_current_song()

    def play_song(self):
        file_path = self.playlist.get_current_song_file()
        if file_path:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

            self.song_length = pygame.mixer.Sound(file_path).get_length()
            self.song_progress.config(to=self.song_length)
            self.update_progress = True
            Thread(target=self.update_song_progress).start()

            self.update_current_song()

    def pause_song(self):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.update_progress = False

    def advance_song(self):
        self.update_progress = False
        self.playlist.advance()
        self.play_song()

    def go_back_song(self):
        self.update_progress = False
        self.playlist.go_back()
        self.play_song()

    def update_current_song(self):
        song = self.playlist.get_current_song()
        if song:
            self.current_song_label.config(text=f"Canción Actual: {song}")
        else:
            self.current_song_label.config(text="Canción Actual: Ninguna")

    def update_song_progress(self):
        while self.update_progress and pygame.mixer.music.get_busy():
            current_time = pygame.mixer.music.get_pos() / 1000
            self.song_progress.set(current_time)
            time.sleep(1)

    def seek_song(self, value):
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.rewind()
            pygame.mixer.music.set_pos(float(value))

if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False)
    app = PlaylistApp(root)
    root.mainloop()

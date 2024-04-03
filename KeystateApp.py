import tkinter as tk

class KeyStateApp:
    def __init__(self, root):
        self.root = root
        root.title("Key State Tracker")

        # Dictionary to keep track of key states
        self.keystate = {'w': False, 'a': False, 's': False, 'd': False}

        # Label to display key states
        self.label = tk.Label(root, text=self.get_keystate_string())
        self.label.pack()

        # Bind key press and release events
        root.bind('<KeyPress>', self.on_key_press)
        root.bind('<KeyRelease>', self.on_key_release)

    def on_key_press(self, event):
        if event.keysym.lower() in self.keystate:
            self.keystate[event.keysym.lower()] = True
            self.update_label()

    def on_key_release(self, event):
        if event.keysym.lower() in self.keystate:
            self.keystate[event.keysym.lower()] = False
            self.update_label()

    def get_keystate_string(self):
        return ' '.join(f"{key.upper()}: {'Pressed' if state else 'Released'}" for key, state in self.keystate.items())

    def update_label(self):
        self.label.config(text=self.get_keystate_string())

# Create the main window
root = tk.Tk()
app = KeyStateApp(root)

# Run the application
root.mainloop()

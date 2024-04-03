import tkinter as tk

def main():
    window = tk.Tk()
    window.title("Simple Circle")

    canvas_size = 400
    joy_center = canvas_size // 2
    canvas = tk.Canvas(window, width=canvas_size, height=canvas_size, bg='white')
    canvas.pack(pady=20)

    # Draw outer circle
    canvas.create_oval(joy_center - 50, joy_center - 50,
                       joy_center + 50, joy_center + 50, outline='black')

    # Draw inner circle (knob)
    canvas.create_oval(joy_center - 10, joy_center - 10,
                       joy_center + 10, joy_center + 10, fill='red')

    window.mainloop()

if __name__ == "__main__":
    main()

import tkinter
import customtkinter


class GUI:
    def __init__(self, run_fn, *args):

        customtkinter.set_appearance_mode("System")  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

        self.app = customtkinter.CTk()  # create CTk window like you do with the Tk window
        self.app.geometry("400x240")
        self.app.title("BLASTbeats")

        def button_function():
            run_fn(*args)

        # Use CTkButton instead of tkinter Button
        button = customtkinter.CTkButton(master=self.app, text="▶ Play", command=button_function)
        button.place(relx=0.5, rely=0.5, anchor=tkinter.CENTER)

        self.app.mainloop()

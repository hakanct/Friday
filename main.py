import customtkinter as ctk
from gui import JarvisGUI

def main():
    root = ctk.CTk()
    app = JarvisGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
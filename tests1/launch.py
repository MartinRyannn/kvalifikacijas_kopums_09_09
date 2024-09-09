import tkinter as tk
import customtkinter
import subprocess
from PIL import Image

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

def launchWindow():
    subprocess.Popen(["python", "mainWindow.py"])

app = customtkinter.CTk()
app.title("LAUNCHER")
app.geometry("300x230")

screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()

x_coordinate = int((screen_width) / 2)
y_coordinate = int((screen_height - 200) / 2)

app.geometry("+{}+{}".format(x_coordinate, y_coordinate))

mainFrame = customtkinter.CTkFrame(master=app, fg_color="#0E0E0E")
mainFrame.pack(pady=0, padx=0, fill="both", expand=False)

my_image = customtkinter.CTkImage(light_image=Image.open('images\goldLogo.png'),
    dark_image=Image.open('images\goldLogo.png'),
    size=(250, 35))
my_label = customtkinter.CTkLabel(mainFrame, text="", image=my_image)
my_label.pack(pady=14)

optionmenu = customtkinter.CTkOptionMenu(mainFrame, values=["1M", "5M", "15M", "30M"], width=200, height=40, text_color="white", anchor="center", font=("Arial", 17, "bold"))
optionmenu.pack(pady=10, padx=10)
optionmenu.set("TIMEFRAME")

button = customtkinter.CTkButton(master=mainFrame, anchor="center", width=250, height=45, font=("Arial", 23, "bold"), text="LAUNCH", fg_color="#080525", text_color="white", corner_radius=7, hover_color="#110A56", command=launchWindow)
button.pack(pady=30, padx=10)

app.mainloop()

import tkinter as tk
import instaloader
import json
from PIL import Image, ImageTk
import requests
import random
import os
import datetime
import threading
import time

class Main(tk.Frame):
    l = None
    user = None
    passwd = None
    image_num = 0
    image = None
    posts = []
    label = None
    isRunning = True

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()
        self.main(master)

    def getLogin(self):
        global user, passwd
        f = open("api.json", "r")
        j = json.load(f)
        f.close()
        user = j["insta"]["user"]
        passwd = j["insta"]["pass"]

    def getPosts(self):
        global l
        print("Getting posts...")
        count = 0
        for x in l.get_feed_posts():
            if(self.isRunning):
                if(x.typename == "GraphImage"):
                    count += 1
                    self.posts.append(x.url)
                elif(x.typename == "GraphSidecar"):
                    for y in x.get_sidecar_nodes():
                        if(not y.is_video):
                            self.posts.append(y.display_url)
                while(count % 20 == 0 and not self.image_num % 15 == 0 and self.isRunning):
                    time.sleep(0.001)
            else:
                break

    def getImage(self):
        global raw
        r = requests.get(self.posts[self.image_num])
        raw = r.content
        image = open("temp.jpg", "wb+")
        image.write(raw)
        image.close()
        r.close()
        self.image_num += 1
        img = self.processimage()
        return img

    def savePhoto(self):
        global raw
        if(not os.path.isdir("memes")):
            os.mkdir("memes")
        out = open("memes/" + datetime.datetime.now().strftime("%d-%m-%y %H-%M-%S") + str(random.randint(0, 100)) + ".jpg", "wb+")
        out.write(raw)
        out.close()
        self.ImageHandler()

    def processimage(self):
        max = (600, 600)
        img = Image.open("temp.jpg")
        img.thumbnail(max)
        img.save("temp.jpg")
        img.close()
        img = Image.open("temp.jpg")
        photo = ImageTk.PhotoImage(img)
        return photo

    def ImageHandler(self):
        photo = self.getImage()
        self.label = tk.Label(image=photo, width=600, height=600)
        self.label.image = photo
        self.label.grid(row=0, column=0, columnspan=3)

    def main(self, master):
        global posts
        global user, passwd, l
        self.getLogin()
        l = instaloader.Instaloader()
        l.login(user, passwd)
        x = threading.Thread(target=self.getPosts)
        x.start()
        left_arrow = tk.Button(text="Delete", command=self.ImageHandler)
        right_arrow = tk.Button(text="Save", command=self.savePhoto)
        left_arrow.grid(row=1, column=0)
        right_arrow.grid(row=1, column=2)
        time.sleep(5)
        y = threading.Thread(target=self.ImageHandler)
        y.start()
        self.mainloop()
        self.isRunning = False
        exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Instaviewer v0.6")
    root.geometry("600x640")
    root.resizable(False, False)
    app = Main(master=root)

from math import sqrt

from create_overlay_image import ChainInfoOverlay
import tkinter as tk
from PIL import ImageTk
import cv2
import numpy as np

class PuyoSpectatorAssist(tk.Tk):
    def __init__(self, puyo_skin='aqua'):
        tk.Tk.__init__(self)
        self.overlay_maker = ChainInfoOverlay(puyo_skin=puyo_skin, testmode=False)
        self.overlay_image = ImageTk.PhotoImage(file='img/green_bg.png')
        self.displayCanvas = tk.Label(self)
        self.displayCanvas.pack()
        self.test_image = ImageTk.PhotoImage(file='calibration_images/hartman_penglai.png')
        self.screenshot = None
        self.ticker = 0
        self.p1_masks = [np.zeros((1080, 1920), np.uint8)] * 4
        self.p2_masks = [np.zeros((1080, 1920), np.uint8)] * 4
        self.p1_next_BGRs = [[0, 0, 0]] * 4
        self.p2_next_BGRs = [[0, 0, 0]] * 4

        cv2.rectangle(self.p1_masks[0], (774, 356), (809, 371), (255, 255, 255), -1)
        cv2.rectangle(self.p1_masks[1], (774, 306), (809, 321), (255, 255, 255), -1)
        cv2.rectangle(self.p1_masks[2], (734, 256), (769, 271), (255, 255, 255), -1)
        cv2.rectangle(self.p1_masks[3], (734, 176), (769, 191), (255, 255, 255), -1)
        cv2.rectangle(self.p2_masks[0], (1100, 356), (1135, 371), (255, 255, 255), -1)
        cv2.rectangle(self.p2_masks[1], (1100, 306), (1135, 321), (255, 255, 255), -1)
        cv2.rectangle(self.p2_masks[2], (1150, 256), (1185, 271), (255, 255, 255), -1)
        cv2.rectangle(self.p2_masks[3], (1150, 176), (1185, 191), (255, 255, 255), -1)

    def detectPieceChange(self):
        self.screenshot = self.overlay_maker.captureScreen().screenshot

        new_p1_next_BGRs = [[]] * 4
        new_p2_next_BGRs = [[]] * 4

        p1_change = False
        p2_change = False

        for index, new_BGR in enumerate(new_p1_next_BGRs):
            new_BGR = cv2.mean(self.screenshot, mask=self.p1_masks[index])[:3]
            p1_change = self.isColorChanged(self.p1_next_BGRs[index], new_BGR, 0.01)
            self.p1_next_BGRs[index] = new_BGR

        for index, new_BGR in enumerate(new_p2_next_BGRs):
            new_BGR = cv2.mean(self.screenshot, mask=self.p2_masks[index])[:3]
            p2_change = self.isColorChanged(self.p2_next_BGRs[index], new_BGR, 0.01)
            self.p2_next_BGRs[index] = new_BGR

        if p1_change is True: print('P1 next piece changed.')
        if p2_change is True: print('P2 next piece changed.')
        self.changeOverlay(p1_change=p1_change, p2_change=p2_change)

    def changeOverlay(self, p1_change=False, p2_change=False):
        if p1_change is True: self.overlay_maker.display_p1 = True
        if p2_change is True: self.overlay_maker.display_p2 = True

        if p1_change or p2_change:
            self.overlay_maker.scrapeMatrices().analyzePops()
        overlay = self.overlay_maker.createOverlay().overlay

        self.overlay_image = ImageTk.PhotoImage(overlay)
        self.displayCanvas.config(image=self.overlay_image)

        self.after(17, self.detectPieceChange)

    def isColorChanged(self, old_BGR, new_BGR, percentage, use_old_check=False):
        if use_old_check:
            return True if new_BGR != old_BGR else False
        # Get max vector length in color cube (100% value)
        # where (0, 0, 0) - black, (255, 255, 255) - white
        max_length = sqrt(abs(255 ** 2 * 3))
        # Get vector length between old and new color
        color_diff_sum = 0
        for i in range(0, 3):
            color_diff_sum += (new_BGR[i] - old_BGR[i]) ** 2
        length = sqrt(abs(color_diff_sum))
        return True if length / max_length >= percentage else False
    
    def run(self):
        self.mainloop()

root = PuyoSpectatorAssist(puyo_skin='aqua')
root.title('PuyoSpectatorAssist Overlay')
root.geometry('1920x1080')
root.detectPieceChange()
root.run()

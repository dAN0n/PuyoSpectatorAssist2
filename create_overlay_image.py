import numpy as np
import os
from PIL import Image
from mss import mss
import cv2
import copy
from simulator import BruteForcePop, SimulatorSettings
from scrape_matrix import scrapeMatrix


# Test matrix
test_matrix = np.asarray([['0', '0', '0', '0', '0', '0'],
                          ['0', '0', '0', '0', '0', '0'],
                          ['0', '0', '0', '0', '0', '0'],
                          ['0', '0', '0', '0', '0', '0'],
                          ['0', '0', '0', '0', '0', '0'],
                          ['J', '0', '0', '0', '0', 'R'],
                          ['J', '0', '0', '0', '0', 'R'],
                          ['B', 'G', '0', '0', '0', 'R'],
                          ['G', 'Y', 'Y', '0', 'R', 'Y'],
                          ['G', 'G', 'Y', '0', 'J', 'Y'],
                          ['B', 'R', 'G', 'P', 'J', 'Y'],
                          ['B', 'B', 'R', 'G', 'P', 'P'],
                          ['R', 'R', 'G', 'G', 'P', 'Y']])

# Initialize Chainsim settings
settings = SimulatorSettings()

# Load images
cell_width = 64
cell_height = 60
cell_size = (cell_width, cell_height)

image_extension = '.png'
image_dir = 'img/'
cursor_file = '{}cursor/{{}}_cursor{}'.format(image_dir, image_extension)
numbers_file = '{}numbers/{{}}{}'.format(image_dir, image_extension)

green_bg = Image.open('{0}{2}{1}'.format(image_dir, image_extension, 'green_bg'))
reticules = {
    code: Image.open(cursor_file.format(name)).resize(cell_size)
    for code, name in [
        ('R', 'red'), ('G', 'green'), ('B', 'blue'), ('Y', 'yellow'), ('P', 'purple')
    ]
}
numbers = {
    code: Image.open(numbers_file.format(name)).resize(cell_size)
    for code, name in [(str(i), str(i) if i < 10 else 'omg') for i in range(2, 20)]
}


class ChainInfoOverlay:
    def __init__(self, puyo_skin='aqua', testmode=False):
        self.screenshot = None
        self.p1_matrix = [[]]
        self.p2_matrix = [[]]
        self.p1_analysis = None
        self.p2_analysis = None
        self.settings = SimulatorSettings()
        self.background = copy.copy(green_bg)
        self.overlay = copy.copy(self.background)
        self.testmode = testmode
        self.display_p1 = True
        self.display_p2 = True
        self.puyo_skin = puyo_skin


    def captureScreen(self):
        if self.testmode == True:
            PIL_img = Image.open('calibration_images/lagnus2.png')
            self.screenshot = cv2.cvtColor(np.array(PIL_img), cv2.COLOR_RGB2BGR)
        else:
            with mss() as sct:
                # Get information of monitor 1
                monitor_number = 1
                mon = sct.monitors[monitor_number]

                # The screen part to capture
                monitor = {
                    "top": -1080,
                    "left": -960,
                    "width": 1920,
                    "height": 1080,
                    "mon": monitor_number,
                }

                # Take screenshot and save to self.screenshot
                sct_img = sct.grab(monitor)
                PIL_img = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
                self.screenshot = cv2.cvtColor(np.array(PIL_img), cv2.COLOR_RGB2BGR)
        return self
    
    def scrapeMatrices(self):
        self.p1_matrix = scrapeMatrix(self.screenshot, 1, self.puyo_skin)
        self.p2_matrix = scrapeMatrix(self.screenshot, 2, self.puyo_skin)
        # Change game over cell to default value to prevent incorrect recognizing
        self.p1_matrix[self.settings.hidden_rows, 2] = '0'
        self.p2_matrix[self.settings.hidden_rows, 2] = '0'
        return self
    
    def analyzePops(self):
        self.p1_analysis = BruteForcePop(self.p1_matrix, self.settings, print_result=False)
        self.p2_analysis = BruteForcePop(self.p2_matrix, self.settings, print_result=False)

        if self.p1_analysis.already_popping is True: self.display_p1 = False
        if self.p2_analysis.already_popping is True: self.display_p2 = False

        return self
    
    def createOverlay(self):
        self.overlay = copy.copy(self.background)

        # Player 1
        if self.display_p1 is True:
            for chain in self.p1_analysis.popping_matrices:
                start_x = 279
                start_y = 159

                x = start_x + 64 * chain['col']
                y = start_y + 60 * (chain['row'] - 1)

                self.overlay.paste(reticules[chain['color']], (x, y), reticules[chain['color']])
                self.overlay.paste(numbers[str(chain['chain_length'])], (x, y), numbers[str(chain['chain_length'])])
        
        # Player 2
        if self.display_p2 is True:
            for chain in self.p2_analysis.popping_matrices:
                start_x = 1256
                start_y = 159

                x = start_x + 64 * chain['col']
                y = start_y + 60 * (chain['row'] - 1)

                self.overlay.paste(reticules[chain['color']], (x, y), reticules[chain['color']])
                self.overlay.paste(numbers[str(chain['chain_length'])], (x, y), numbers[str(chain['chain_length'])])
        
        return self

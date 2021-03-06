import numpy as np
import requests
import os
from PIL import Image, ImageOps
from pathlib import Path
from retrofy.configs import Filter_Configs
import retrofy.utils as utils

CONFIGS = Filter_Configs()

class Filter():

    MAX_SIZE = CONFIGS.MAXS["size"]

    def __init__(self, img_src):
        if isinstance(img_src, (str, Image.Image)) == False:
            raise TypeError("Parameter 'img_src' must be a string or a Pillow Image object.")

        self.__img_src = img_src
        self.__last_modifications = [] #list for all modifications that wasnt undoed
        self.__last_undos = []
        self.__load_image()



    @property
    def modified_img(self):
        return self.__modified_img

    @modified_img.setter
    def modified_img(self, img):
        if isinstance(img, Image.Image) == False:
            raise TypeError("Parameter 'modified_img' must be a Pillow Image object.")
        self.__modified_img = img
        self.__last_modifications.append(self.__modified_img)

    @property
    def original_img(self):
        return self.__original_img

    @property
    def last_modifications(self):
        return self.__last_modifications



    def __load_image(self):
        # if img_src alredy is a PIL Image object
        if isinstance(self.__img_src, Image.Image) == True:
            self.__original_img = self.__img_src
        else:
            if utils.is_url(self.__img_src) == True:
                try:
                    self.__img_src = requests.get(self.__img_src, stream=True).raw
                    self.__original_img = Image.open(self.__img_src).convert("RGB")
                except:
                    raise ValueError("Could not download image from URL '{}'.".format(self.__img_src))
            else:
                try:
                    self.__original_img = Image.open(self.__img_src).convert("RGB")
                except:
                    raise ValueError("Could not access image on file '{}'.".format(self.__img_src))
        #resize large images (with same aspect ratio)
        self.__original_img.thumbnail(self.MAX_SIZE)
        self.__modified_img = self.__original_img



    def undo(self, times=1):
        if isinstance(times, int) == False:
            raise TypeError("Parameter 'times' must be an integer.")

        if len(self.__last_modifications) > 0:
            for i in range(times):
                if len(self.__last_modifications) > 0:
                    self.__last_undos.append(self.__last_modifications[-1])
                    self.__last_modifications.pop(-1)
            if len(self.__last_modifications) == 0:
                self.reset()
            else:
                self.__modified_img = self.__last_modifications[-1]



    def redo(self, times=1):
        if isinstance(times, int) == False:
            raise TypeError("Parameter 'times' must be an integer.")

        if len(self.__last_undos) > 0:
            for i in range(times):
                if len(self.__last_undos) > 0:
                    self.modified_img = self.__last_undos[-1]
                    self.__last_undos.pop(-1)



    def reset(self):
        self.__modified_img = self.__original_img



    def show(self, original=False):
        if isinstance(original, bool) == False:
            raise TypeError("Parameter 'original' must be a boolean.")

        if original == False:
            self.__modified_img.show()
        else:
            self.__original_img.show()



    def save(self, path, original=False):
        if isinstance(original, bool) == False:
            raise TypeError("Parameter 'original' must be a boolean.")
        if isinstance(path, str) == False and isinstance(file_path, Path) == False:
            raise TypeError("Parameter 'path' must be a string or a Path object.")

        path = Path(path)
        if path.suffix == "":
            path = path.parent / Path(path.stem + ".png")
        if self.__modified_img.mode == "RGBA" and path.suffix != ".png":
            raise ValueError("RGBA Image must have 'png' file extension.")
        try:
            if original == False:
                self.__modified_img.save(path)
            else:
                self.__original_img.save(path)
        except:
            raise ValueError("Could not save image on especified path.")

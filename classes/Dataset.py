import os
import numpy as np
from PIL import Image
import time
import csv
import logging
from datetime import datetime
from PIL import Image
import io
from scipy import misc
logger = logging.getLogger(__name__)

class Dataset:
    def __init__(self, base="dataset/", filename="dataset.csv"):
        self.frame_count = 1
        self.cwd = os.getcwd() + "/"
        self.base = self.cwd + base
        self.directory = self.base + str(datetime.now()) + "/"
        self.csv_file_path = self.directory + filename
        self.images_rel_path = "images/" # Relative path
        self.images_path = self.directory + self.images_rel_path

        if not os.path.exists(self.images_path):
            os.makedirs(self.images_path)

        if not os.path.exists(self.csv_file_path):
            with open(self.csv_file_path, 'wb') as newFile:
                # file created.
                pass

        self.csv_file_writer = open(self.csv_file_path, 'ab')
        self.header = None

    def save_data(self, datavector, dataset_title):
        if self.header is None:
            self.header = dataset_title
            csv_writer = csv.writer(self.csv_file_writer)
            csv_writer.writerow(self.header)

        for key in datavector:
            frame = datavector[key]
            
            # save images
            if "camera" in key:
                name =  "img" + str(self.frame_count) + ".jpg"
                self.frame_count += 1
                #value = Image.open(io.BytesIO(value))
                path = self.images_path + name
                rel_path = self.images_rel_path + name
                misc.imsave(path, frame)
                #value.save(path)
                datavector[key] = rel_path
                
        self.add_data(datavector)

    def add_data(self, data):
        dict_writer = csv.DictWriter(self.csv_file_writer, self.header, -999)
        dict_writer.writerow(data)
        self.csv_file_writer.flush()

    def get_dataset(self):
        data = None
        return data
    
    def close(self):
        self.csv_file_writer.flush()
        self.csv_file_writer.close()
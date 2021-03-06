#! /usr/bin/env python
#coding=utf-8

import os
import time
import tornado.web
from models.entity import Upload, getSession

upload_path = os.path.join(os.path.abspath('.'), 'static/uploadfile/')

def nameRewrite(filename):
    file_timestamp = int(time.time())
    name_split = filename.split('.')
    if len(name_split) == 1:
        filename = filename + str(file_timestamp)
    else:
        filename = name_split[0] + str(file_timestamp) + '.' + name_split[1]
    return filename

def saveIntoDB(filename):
    session = getSession()
    session.add(Upload(filename, upload_path+filename))
    session.commit()

def fileUpload(path):
    if 'file' in self.request.files:
        file_dict_list = self.request.files['file']
        for file_dict in file_dict_list:
            filename = nameRewrite(file_dict["filename"]).encode('utf8')
            data = file_dict["body"]
            with open(upload_path + filename, 'w') as f:
                f.write(data)
        saveIntoDB(filename)
        self.write('success')

class FileUpload(tornado.web.RequestHandler):
    def get(self):
        self.render("upload.html")

    def post(self):
        #upload_path = os.path.join(os.path.dirname(__file__),"static"),
        if 'file' in self.request.files:
            file_dict_list = self.request.files['file']
            for file_dict in file_dict_list:
                filename = nameRewrite(file_dict["filename"]).encode('utf8')
                data = file_dict["body"]
                with open(upload_path + filename, 'w') as f:
                    f.write(data)
            saveIntoDB(filename)
            self.write('success')

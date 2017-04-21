# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 21:28:51 2017

@author: MartianMartin
"""

import pymongo
import gridfs
from bson.objectid import ObjectId
import os

class MongoController:
    
    def __init__(self):
        pass
    
    def open_db_connection(self):
        #uri = "mongodb://martin:pass1@74.79.252.194:27017/test_database"
        local_uri = "mongodb://martin:pass1@192.168.2.5:27017/test_database"
        client = pymongo.MongoClient(local_uri)
        self.db = client.get_database('test_database')
        self.fs = gridfs.GridFS(self.db)
        
    def close_db_connection(self):
        self.db.close()

    def upload_data(self, file_path=u'C:\\Users\\MartianMartin\\Desktop\\xdf-master\\xdf-master\\xdf_sample.xdf',
                    filename="misc_file",
                    user="misc_user",
                    channels="fz,oz,cz",
                    duration="10009",
                    rec_type="EEG",
                    notes="This is a test note"):
        metadata = {"user": user,
                    "name": filename,
                    "channels": channels,
                    "type": rec_type,
                    "duration": duration,
                    "notes": notes}
        xdfd = open(file_path,'rb').read()
        return self.fs.put(xdfd, **metadata)
        
    def download_data(self, object_id):
        ret = self.fs.get(ObjectId(object_id)).read()
        fp = os.getcwd()+'\\new_file_'+object_id+".xdf"
        new_file = open(fp,"wb")
        new_file.write(ret)
        new_file.close()
        return fp
        
    def test_upload(self, data):
        
        metadata = {"user": "martin",
                    "name": "arbitrary file name",
                    "channels": "0z,cz,fz",
                    "type": "EEG"}
        a = self.fs.put(b"hello world",  **metadata)
        return self.fs.get(a).read()

    def get_filenames(self):
        files = list(self.fs.fin())
        return [f.name for f in files]

    
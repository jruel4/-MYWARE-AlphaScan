# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 19:43:06 2017

@author: MartianMartin
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 21:28:51 2017

@author: MartianMartin
"""

import pymongo
import gridfs

class MongoController:
    
    def __init__(self):
        pass
    
    def open_db_connection(self):
        pass

# Connect
uri = "mongodb://martin:pass1@74.79.252.194:27017/test_database"
local_uri = "mongodb://martin:pass1@192.168.2.5:27017/test_database"
client = pymongo.MongoClient(local_uri)
db = client.get_database('test_database')

fs = gridfs.GridFS(db)
metadata = {"user": "martin",
            "name": "arbitrary file name",
            "channels": "0z,cz,fz",
            "type": "EEG"}
a = fs.put(b"hello world",  **metadata)
fs.get(a).read()

fname = u'C:\\Users\\MartianMartin\\Desktop\\xdf-master\\xdf-master\\xdf_sample.xdf'
xdfd = open(fname,'rb').read()
b = fs.put(xdfd, **metadata)
ret = fs.get(b).read()

'''
# Given the Object ID from the RoboMongo Viewer do :
>>> oid = ObjectId('58f77f348dc048108a587040')
>>> ret = fs.get(oid).read()
# Then dump to xdf
new_file = open("new_file.xdf","wb")
new_file.write(ret)
new_fil.close()
'''

# Create collection
collection_name = 'test_collection_2'
coll = db.get_collection(collection_name)

print(coll.find_one())

# Insert document
import datetime
post = {"author": "Mike",
         "text": "My first blog post!",
         "tags": ["mongodb", "python", "pymongo"],
         "date": datetime.datetime.utcnow()}

post_id = coll.insert_one(post).inserted_id

# Create test eeg data
import random
srate = 250
duration = 60 * 10 # seconds
N = srate * duration
data_large = [random.random() for i in range(N)]
data_small = [i for i in range(10)]

# Insert small
eeg_post = {'type': "EEG",
        'data': data_small,
        'user': 'martin',
        'timestamp': datetime.datetime.utcnow(),
}
        
post_id = coll.insert_one(eeg_post).inserted_id

# Insert large
eeg_post = {'type': "EEG",
        'data': data_large,
        'user': 'martin',
        'timestamp': datetime.datetime.utcnow(),
}
        
post_id = coll.insert_one(eeg_post).inserted_id

# Query post by id
from bson.objectid import ObjectId
thing1 = coll.find_one({'_id': ObjectId('58f77f348dc048108a587040') })
thing2 = coll.find_one({'_id': post_id })

# Query by user
things = coll.find({'user':'martin'})
things_list = list(things)
for l in things_list:
    print(len(l['data']))
    

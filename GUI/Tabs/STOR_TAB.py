# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 20:58:17 2017

@author: MartianMartin
"""

from PySide.QtCore import *
from PySide.QtGui import *
from Controller.Modules.MongoDB import MongoController

class STOR_TAB(QWidget):
    
    def __init__(self, Device, Debug, parent=None):
        super(STOR_TAB, self).__init__(parent)
        self._Debug = Debug
        self.db = MongoController()
        #######################################################################
        # Basic Init ##########################################################
        #######################################################################
        
        # Set layout
        self.layout = QGridLayout()
        self.setLayout(self.layout) # Does it matter when I do this?
        
        # Set layout formatting
        self.layout.setAlignment(Qt.AlignTop)
        
         #create available
        self.Text_f2upload = QLabel("No File Selected")   
        self.layout.addWidget(self.Text_f2upload, 0, 0)
        
        # Button to read network card and update avail and connected
        self.Button_CheckStatus = QPushButton("Select XDF File")
        self.layout.addWidget(self.Button_CheckStatus, 0, 1)
        self.Button_CheckStatus.clicked.connect(self.test_method)
        
        # add fields
        self.fields = ["user","channel","duration","rec_type","notes", "download id"]
        
        self.Line_arr = [QLineEdit(f) for f in self.fields]
        
        for i,l in enumerate(self.Line_arr):
            self.layout.addWidget(l, 2+i, 0)
            #self.layout.addWidget(QLabel(self.Line_arr[i]), 2+i, 1)
            self.cidx = 2+i+1
            
        # Button to upload
        self.Button_Upload= QPushButton("Upload")
        self.layout.addWidget(self.Button_Upload, self.nidx(), 1)
        self.Button_Upload.clicked.connect(self.upload_file)
        
        # Dowload button
        self.Button_Download= QPushButton("Download")
        self.layout.addWidget(self.Button_Download, self.nidx(), 1)
        self.Button_Download.clicked.connect(self.download_file)
            
    
        
    
    def nidx(self):
        self.cidx = self.cidx+1
        return self.cidx
        
    @Slot()
    def test_method(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file','C:')
        self.filename = fname
        self.Text_f2upload.setText(fname)
        self._Debug.append("Found file: "+fname)
        
    @Slot()
    def upload_file(self):
        self.db.open_db_connection()
        
        r = self.db.upload_data(file_path=self.filename,
                            user=self.Line_arr[0].text(),
                            channels=self.Line_arr[1].text(),
                            duration=self.Line_arr[2].text(),
                            rec_type=self.Line_arr[3].text(),
                            notes=self.Line_arr[4].text())
                            
        self._Debug.append("Uploaded file: "+str(r))
        self.db.close_db_connection()
                            
    @Slot()
    def download_file(self):
        self.db.open_db_connection()
        r = self.db.download_data(self.Line_arr[5].text())
        self._Debug.append("Downloaded to: "+r)
        self.db.close_db_connection()

    
 

        
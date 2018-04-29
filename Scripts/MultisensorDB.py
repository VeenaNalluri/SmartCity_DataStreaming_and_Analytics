#MultisensorDB.py
import logging
import pprint
from riaps.run.comp import Component
import datetime
import random
import time
#import csv
import os
import sys
sys.path.append("/home/riaps/Desktop/eclipse_workspace/sterling_ranch/python/")
from influxdb import client as influxdb
from databaseconfig import config


class MultisensorDB(Component):
    def __init__(self):
        super(MultisensorDB, self).__init__()            
        self.pid = os.getpid()
        self.logger.info("Starting the MultisensorDB component")
        
    #########Creating a local using influx#########################
        self.mydb= influxdb.InfluxDBClient(config.INFLUX_DBASE_HOST,
                                           config.INFLUX_DBASE_PORT,config.INFLUX_DBASE_USER,config.INFLUX_DBASE_PASSWORD,
                                           config.INFLUX_DBASE_NAME)
        self.mydb.create_database(config.INFLUX_DBASE_NAME)
        self.mydb.create_retention_policy(config.INFLUX_DBASE_RETENTION_POLICY,'3d',3,default=True)
        self.logger.info("Created a DB with name newone")
    #################################################################
        
     ##########on value sent from multisensor##############
        self.logger.info("Waiting for a msg update from sensor")


    def on_value_update(self):
        msg = self.value_update.recv_pyobj()
        self.logger.info("%s" %str(msg)) 
        now, home_id, node_id, parameter,readingvalue,units=msg
        
        lists = [{
            "measurement":"multisensor_values",
            "tags":{
                    "home_id": home_id,
                    "sensor_id":node_id,
                    "parameter":parameter,
                    
                    },
            "time":now,    
            "fields":{
                "parameter":parameter,    
                "value":readingvalue,
                "Units":units,
                 }
            }]
        self.mydb.write_points(lists)
        #self.logger.info("%s" %str(lists)) 
            
    
    def __destroy__(self):            
        self.logger.info("(PID %s) - stopping MultisensorDB",str(self.pid))                           

#config file for Influxdb

class Config:
    pass

config = Config()

config.INFLUX_DBASE_HOST= "localhost" 
config.INFLUX_DBASE_PORT=  "8086"
config.INFLUX_DBASE_USER= "distributed"
config.INFLUX_DBASE_PASSWORD=  "system"
config.INFLUX_DBASE_NAME= "newone"
config.INFLUX_DBASE_RETENTION_POLICY="my policy"


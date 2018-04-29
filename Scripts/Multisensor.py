#Multisensor.py
import logging
import sys, os
sys.path.append("/usr/local/lib/python2.7/dist-packages/openzwave-0.4.4-py2.7.egg")
import resource
from datetime import datetime
from riaps.run.comp import Component
import openzwave
from openzwave.node import ZWaveNode
from openzwave.value import ZWaveValue
from openzwave.controller import ZWaveController
from openzwave.network import ZWaveNetwork
from openzwave.option import ZWaveOption
import time
from pydispatch import dispatcher

device = "/dev/ttyACM0"

class Multisensor(Component):
    def __init__(self):
        super(Multisensor, self).__init__()            
        self.pid = os.getpid()
        self.logger.info("starting the Multisensor Component")
        self.logger.info("Opening the ZWave Stick at %s",device)
        self.log_level()
        self.logger.info("Starting the Openzwave Network")
        self.network.start()  # starting the openzwave network
        self.logger.info("Started the Openzwave Network")
        #self.my_network_states(self.network)
        self.my_network_status(self.network)  
        #self.node=ZWaveNode
        #self.ozw_debug(self.logger,self.network)
        
        
        
    def on_clock(self):
        self.logger.info("Periodical check for any refresh in values")
        self.connect_signals()
        
        
    def log_level(self):
        self.logger.info("Performing log level entries")
        options = ZWaveOption(device, config_path="/home/riaps/python-openzwave/openzwave/config", user_path=".", cmd_line="")
        options.set_log_file("OZW.log")
        options.set_append_log_file(False)
        options.set_save_log_level("Info")
        options.set_console_output(False)
        options.set_logging(True)
        options.lock()
        self.ZWaveOption=options
        self.network = ZWaveNetwork(options, log=None, autostart=False)
        self.logger.info("log level entries done")
        
    
    def my_network_status(self, network):
        for i in range(0, 100):
            if self.network.state >= self.network.STATE_AWAKED:
                self.logger.info("Network is awake ")
                break
            
        self.logger.info("------------------------------------------------------------")
        self.logger.info("---------Network Statistics if the network is awake---------")
        self.logger.info("Use openzwave library : {}".format(self.network.controller.ozw_library_version))
        self.logger.info("Use python library : {}".format(self.network.controller.python_library_version))
        self.logger.info("Use ZWave library : {}".format(self.network.controller.library_description))
        self.logger.info("Network home id : {}".format(self.network.home_id_str))
        #self.logger.info("Controller node id : {}".format(self.network.controller.node.node_id))
        #self.logger.info("Controller node version : {}".format(self.network.controller.node.version))
        self.logger.info("Nodes in network : {}".format(self.network.nodes_count))
        self.logger.info("------------------------------------------------------------")

        for i in range(0, 100):
            if self.network.state >= self.network.STATE_READY:
                self.logger.info("Network Ready")
                break
            else:
                time.sleep(0.01)
        
        if not network.is_ready:
            print("Can't start network......................")
            
        self.logger.info("------------------------------------------------------------")
        self.logger.info("--------Network Statistics after the network is ready--------")
        self.logger.info("Network home id : {}".format(self.network.home_id_str))
        self.logger.info("Nodes in network : {}".format(self.network.nodes_count))
        self.logger.info("-----------------------------------------------------------")
        
    def my_network_states(self, network):        
        cur_state = self.network.state
        cur_state_str = self.network.state_str
        while True:
            time.sleep(0.25)
            if cur_state != self.network.state:
                self.logger.info("%s ==> %s", cur_state_str, self.network.state_str)
                cur_state = self.network.state
                cur_state_str = self.network.state_str
            if cur_state is ZWaveNetwork.STATE_STOPPED:
               break
    

    def ozw_debug(self,logger, network):
        logger.info("------------------------------------------------------------")
        logger.info("Use openzwave library : {}".format(network.controller.ozw_library_version))
        logger.info("Use python library : {}".format(network.controller.python_library_version))
        logger.info("Use ZWave library : {}".format(network.controller.library_description))
        logger.info("Network home id : {}".format(network.home_id_str))
        #logger.info("Controller node id : {}".format(network.controller.node.node_id))
        #logger.info("Controller node version : {}".format(network.controller.node.version))
        logger.info("Nodes in network : {}".format(network.nodes_count))
        logger.info("------------------------------------------------------------")       

    def connect_signals(self):
        #self.logger.info("waiting for value refresh in network")
        dispatcher.connect(self.signal_network_ready, self.network.SIGNAL_NETWORK_READY)
        

    def signal_network_ready(self, network):  # Note -- the name of the network parameter must not change!
     
        if self.network is not network:
            return
        else:
            del network
            #ozw_debug(self.logger, self.network)
        self.logger.info("Network is working!")
        dispatcher.connect(self.signal_node_update, self.network.SIGNAL_NODE)
        dispatcher.connect(self.signal_value_refreshed, self.network.SIGNAL_VALUE)
        for nodeId, node in self.network.nodes.items():
            self.logger.info("Node %d has the following available configs", nodeId)
            for _, conf in node.get_configs().items():
                    self.logger.info(conf) 
        self.make_sensors_fast()
        

    def signal_value_refreshed(self, network, node, value):
        if self.network is not network:
            return
        else:
            del network
        self.logger.info("Received value refresh for node %d: %s", node.node_id, value)
        for valIndex, val in node.get_sensors().items():
            self.logger.info("Looking at sensor %s", str(val))
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            home_id=self.network.home_id_str
            node_id = val.id_on_network
            parameter = val.label
            readingvalue = val.data
            units = val.units
            msg = (now, str(home_id), str(node_id), str(parameter), str(readingvalue), str(units))
            self.logger.info("Message: %s", msg)
            #write_to_db()
            self.sterling.send_pyobj(msg)
        
    # Note -- the names of the network/node parameters must not change!
    def signal_node_update(self, network, node):
        if self.network is not network:
            return
        else:
            del network
        if not self.network.is_ready:
            return
        self.logger.info("Received notification of node %d update", node.node_id)
        
    def make_sensors_fast(self):
        for nodeId, node in self.network.nodes.items():
            if self.is_sensor(node):
                self.logger.info("Applying config for sensor node %s", nodeId)
                node.set_config(72057594081706753, 0b11111111)  # Activate all threshold reports
                node.set_config(72057594081707763,
                                30)  # Send the default report every 5 seconds, only applies if connected over USB power
                self.logger.info("Configs are now %d %d", node.get_config(72057594081706753),
                                 node.get_config(72057594081707763))   
    
        
    def __destroy__(self):            
        self.logger.info("Stopping the Multisensor Actor")      
        
    
    
    
        
    
    
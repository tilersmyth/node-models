import machine
import onewire 
import ds18x20 
import uasyncio as asyncio

from node.input import InputClient
from node.core.utils.logger import Log

class NodeClient(InputClient):
    # Required properties
    public_key = "23fb8c59-e61d-42fe-b32f-b7873ecb6b5e"
    
    # Node specific
    _pin = machine.Pin(4)
    _node =  ds18x20.DS18X20(onewire.OneWire(_pin))
    _period = None # measurement interval
    measurement_channels = {
        1: "temperature",
    }

    def on_settings(self, settings):
        # Validate expected settings here
        self._period = settings["node"]["period"]
    
    def __temperature(self):
        roms = NodeClient._node.scan()

        if not roms:
            Log.error("NodeClient.__temperature", "node sensor connection error!")
            return 'hardware_connection_error'
        
        NodeClient._node.convert_temp()

        for rom in roms:
            temp = NodeClient._node.read_temp(rom)
            if isinstance(temp, float):
                measurement = round(temp, 2)
                Log.info("NodeClient.__temperature", "data: {}".format(measurement))
                return str(measurement)
        return '0.0'

    async def on_active_state(self, channels):
        if self._period is None:
            Log.error("NodeClient.on_active_state", "period setting not set")

        while True:
            for channel_value in channels:
                measurement = self.measurement_channels[channel_value]
                if measurement == "temperature":
                    temperature = self.__temperature()
                    self.send_value(channel_value, temperature)
            await asyncio.sleep(int(self._period))

  

        

    
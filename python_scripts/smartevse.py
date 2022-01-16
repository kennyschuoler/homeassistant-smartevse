
import logging

from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.transaction import ModbusRtuFramer
from pymodbus.constants import Defaults

_LOGGER = logging.getLogger(__name__)

client = ModbusClient("10.0.5.19", "8888")
client.connect()

result = client.read_input_registers(0x0000, 12, unit=1)
if result.isError():
    _LOGGER.error(f"Attempt failed to fetch 'EVSE Status' {result}")
else:
    _LOGGER.error(f"'EVSE Status' fetched ! {result.registers}")

client.close()

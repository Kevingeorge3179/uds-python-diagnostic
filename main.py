import threading
import tester
from battery_ecu import BatteryECU
import can
from queue import Queue
import time



# data = bytes([0x10, 0x03, 0x14, 0x13, 0x30, 0x50, 0x65, 0x44, 0x55, 0x44])
# data = bytes([0x11])
# data = bytes([0x11, 0x01, 0xAA])
# 1. Enter Extended Session
data_1 = bytes([0x10, 0x03])

# 2. Request Security Seed
data_2 = bytes([0x27, 0x01])


data_3 = bytes([0x10, 0x01])

data_9 = bytes([0x19, 0x02, 0xFF])

# 4. Start Fault Injection Routine
data_4 = bytes([0x31, 0x01, 0xFF, 0x00])

# 5. Write 0x1234 to DID F1A0
data_5 = bytes([0x2E, 0xF1, 0xA0, 0x12, 0x34])

# 6. ECU Reset
data_6 = bytes([0x11, 0x01])

# 7. Read Session DID
data_7 = bytes([0x22, 0xF1, 0x86])

# 8. Read F1A0 to verify retained data
data_8 = bytes([0x22, 0xF1, 0xA0])

data_10 = bytes([0x19, 0x02, 0x08])

data_11 = bytes([0x19, 0x02, 0x01])

data_12 = bytes([0x14, 0xFF, 0xFF, 0xFF])


ecu = BatteryECU()



bus_tester = can.Bus(interface="virtual", channel="uds_virtual")

bus_ecu = can.Bus(interface="virtual", channel="uds_virtual")

stop_event = threading.Event()

inbox = Queue()


ecu_thread = threading.Thread(target=ecu.run_ecu, args=(bus_ecu,stop_event,inbox))
ecu_thread.start()

try:
    tester.run_tester(bus_tester=bus_tester, data=data_1)
    
    tester.run_tester(bus_tester=bus_tester, data=data_2)

    tester.run_tester(bus_tester=bus_tester, data=data_9)

    tester.run_tester(bus_tester=bus_tester, data=data_4)

    tester.run_tester(bus_tester=bus_tester, data=data_12)

    tester.run_tester(bus_tester=bus_tester, data=data_9)
    
    tester.run_tester(bus_tester=bus_tester, data=data_3)

    tester.run_tester(bus_tester=bus_tester, data=data_5)

    tester.run_tester(bus_tester=bus_tester, data=data_6)

    tester.run_tester(bus_tester=bus_tester, data=data_9)

    tester.run_tester(bus_tester=bus_tester, data=data_10)

    tester.run_tester(bus_tester=bus_tester, data=data_11)

    tester.run_tester(bus_tester=bus_tester, data=data_12)

    tester.run_tester(bus_tester=bus_tester, data=data_9)

    tester.run_tester(bus_tester=bus_tester, data=data_7)

    tester.run_tester(bus_tester=bus_tester, data=data_8)

finally:
    stop_event.set()
    ecu_thread.join()

    bus_tester.shutdown()
    bus_ecu.shutdown()
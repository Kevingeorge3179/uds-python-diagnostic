import threading
import tester
from battery_ecu import BatteryECU
import can
from queue import Queue
import time



data_1 = bytes([0x10, 0x03])

data_3 = bytes([0x27, 0x01])


ecu = BatteryECU()



bus_tester = can.Bus(interface="virtual", channel="uds_virtual")

bus_ecu = can.Bus(interface="virtual", channel="uds_virtual")

stop_event = threading.Event()

inbox = Queue()


ecu_thread = threading.Thread(target=ecu.run_ecu, args=(bus_ecu,stop_event,inbox))
ecu_thread.start()

try:
    
    tester.run_tester(bus_tester=bus_tester, data=data_1)

    tester.run_tester(bus_tester=bus_tester, data=data_3)

    print("\n--- ECU Internal State ---")
                
    print("Current Session:", hex(ecu.current_session))
    print("Security Unlocked:", ecu.security_unlocked)
    print("Security Seed:", ecu.security_seed)
    print("Routine Status:", ecu.routine_status)
    print("Fault Active:", ecu.fault_active)
    print("F1A0 Data:", ecu.did_data.get(0xF1A0))


  
finally:
    stop_event.set()
    ecu_thread.join()

    bus_tester.shutdown()
    bus_ecu.shutdown()
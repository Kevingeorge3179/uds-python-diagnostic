import threading
import tester
from battery_ecu import BatteryECU
import can
from queue import Queue, Empty

expected_payload = bytes([0x10, 0x03, 0x14, 0x13, 0x30, 0x50, 0x65, 0x44, 0x55, 0x44])


bus_tester = can.Bus(interface="virtual", channel="uds_virtual")

bus_ecu = can.Bus(interface="virtual", channel="uds_virtual")

ecu = BatteryECU()


bus_sniffer = can.Bus(interface="virtual", channel="uds_virtual")

check_event = threading.Event()

def sniffer_check(check_event):

    while not check_event.is_set():

        message_check = bus_sniffer.recv(timeout=1.0)

        if message_check is not None:
            print(f"{message_check.arbitration_id:X}")
            print(f"{message_check.data.hex(' ')}")


stop_event = threading.Event()

inbox = Queue()

sniffer_thread = None
ecu_thread = None

try:
    sniffer_thread = threading.Thread(target=sniffer_check, args=(check_event,))
    sniffer_thread.start()

    ecu_thread = threading.Thread(target=ecu.run_ecu, args=(bus_ecu,stop_event,inbox))
    ecu_thread.start()

    tester.run_tester(bus_tester=bus_tester, data=expected_payload)
    
    try:
        received_payload = inbox.get(timeout=2)

    except Empty:
        raise AssertionError("No payload received within 2 seconds")

    else:
        assert received_payload == expected_payload, "Payload mismatch"

            
finally:
    stop_event.set()
    if ecu_thread is not None:
        ecu_thread.join()

    check_event.set()
    if sniffer_thread is not None:
        sniffer_thread.join()

    bus_tester.shutdown()
    bus_ecu.shutdown()
    bus_sniffer.shutdown()

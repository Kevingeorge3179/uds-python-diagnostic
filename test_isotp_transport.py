import threading
import tester
from battery_ecu import BatteryECU
import can
from queue import Queue, Empty
import uuid

expected_payload = bytes([0x10, 0x03, 0x14, 0x13, 0x30, 0x50, 0x65, 0x44, 0x55, 0x44])

def sniffer_check(bus_sniffer, check_event):

    while not check_event.is_set():

        message_check = bus_sniffer.recv(timeout=1.0)

        if message_check is not None:
            print(f"{message_check.arbitration_id:X}")
            print(f"{message_check.data.hex(' ')}")

def test_isotp_transport():

    bus_tester = None
    bus_ecu = None
    bus_sniffer = None
    sniffer_thread = None
    check_event = None
    stop_event = None
    ecu_thread = None
    channel = f"uds_{uuid.uuid4().hex}"

    try:

        bus_tester = can.Bus(interface="virtual", channel=channel)
        bus_ecu = can.Bus(interface="virtual", channel=channel)
        bus_sniffer = can.Bus(interface="virtual", channel=channel)
    
        ecu = BatteryECU()
        stop_event = threading.Event()
        check_event = threading.Event()
        inbox = Queue()

        sniffer_thread = threading.Thread(target=sniffer_check, args=(bus_sniffer, check_event), daemon=True)
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

        if stop_event is not None:
            stop_event.set() 

        if check_event is not None:
            check_event.set()    
        
        try:
        
            if ecu_thread is not None:
                ecu_thread.join(3)

                if ecu_thread.is_alive():
                    raise RuntimeError("ECU thread failed to stop within timeout")
    
            if sniffer_thread is not None:
                sniffer_thread.join(3)

                if sniffer_thread.is_alive():
                    raise RuntimeError("Sniffer thread failed to stop within timeout")

        finally:

            if bus_tester is not None:
                bus_tester.shutdown()

            if bus_ecu is not None:
                bus_ecu.shutdown()

            if bus_sniffer is not None:
                bus_sniffer.shutdown()

import can
import isotp
import threading
import uuid

expected_payload = bytes([0x10, 0x03, 0x14, 0x13, 0x30, 0x50, 0x65, 0x44, 0x55, 0x44])

def sniffer_check(bus_sniffer, check_event):

    while not check_event.is_set():

        message_check = bus_sniffer.recv(timeout=1.0)

        if message_check is not None:
            print(f"{message_check.arbitration_id:X}")
            print(f"{message_check.data.hex(' ')}")


address_tester = isotp.Address(
    isotp.AddressingMode.Normal_11bits,
    txid=0x700,
    rxid=0x708
)

address_ecu = isotp.Address(
    isotp.AddressingMode.Normal_11bits,
    txid=0x708,
    rxid=0x700
)
def test_isotp_reverse():

    bus_tester = None
    bus_ecu = None
    bus_sniffer = None
    sniffer_thread = None
    check_event = None
    stack_tester = None
    stack_ecu = None
    channel = f"uds_{uuid.uuid4().hex}"

    try:
        bus_tester = can.Bus(interface="virtual", channel=channel)
        bus_ecu = can.Bus(interface="virtual", channel=channel)
        bus_sniffer = can.Bus(interface="virtual", channel=channel)

        stack_tester = isotp.CanStack(bus=bus_tester, address=address_tester)
        stack_ecu = isotp.CanStack(bus=bus_ecu, address=address_ecu)

        check_event = threading.Event()

        stack_tester.start()
        stack_ecu.start()

        sniffer_thread = threading.Thread(target=sniffer_check, args=(bus_sniffer, check_event), daemon=True)
        sniffer_thread.start()

        stack_ecu.send(data=expected_payload)


        received_payload = stack_tester.recv(block=True, timeout=2.0)

        assert received_payload is not None, "No response"
        assert received_payload == expected_payload, "Payload mismatch"
            
    finally:

        if stack_tester is not None:
            stack_tester.stop()

        if stack_ecu is not None:
            stack_ecu.stop()

        if check_event is not None:
            check_event.set()

        if sniffer_thread is not None:
            sniffer_thread.join()

        if bus_ecu is not None:
            bus_ecu.shutdown()

        if bus_tester is not None:
            bus_tester.shutdown()
        
        if bus_sniffer is not None:
            bus_sniffer.shutdown()


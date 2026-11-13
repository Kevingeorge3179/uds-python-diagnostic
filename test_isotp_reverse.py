import can
import isotp
import threading

expected_payload = bytes([0x10, 0x03, 0x14, 0x13, 0x30, 0x50, 0x65, 0x44, 0x55, 0x44])

bus_tester = can.Bus(interface="virtual", channel="uds_virtual")

bus_ecu = can.Bus(interface="virtual", channel="uds_virtual")

bus_sniffer = can.Bus(interface="virtual", channel="uds_virtual")

check_event = threading.Event()

def sniffer_check(check_event):

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

stack_tester = isotp.CanStack(bus=bus_tester, address=address_tester)

stack_ecu = isotp.CanStack(bus=bus_ecu, address=address_ecu)

sniffer_thread = None

try:
    stack_tester.start()
    stack_ecu.start()

    sniffer_thread = threading.Thread(target=sniffer_check, args=(check_event,))
    sniffer_thread.start()

    stack_ecu.send(data=expected_payload)


    received_payload = stack_tester.recv(block=True, timeout=2.0)

    assert received_payload is not None, "No response"
    assert received_payload == expected_payload, "Payload mismatch"
            
finally:
    stack_tester.stop()
    stack_ecu.stop()

    check_event.set()
    if sniffer_thread is not None:
        sniffer_thread.join()

    bus_ecu.shutdown()
    bus_tester.shutdown()
    bus_sniffer.shutdown()


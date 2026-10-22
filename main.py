import threading
import tester
import battery_ecu
import can


bus_tester = can.Bus(interface="virtual", channel="uds_virtual")

bus_ecu = can.Bus(interface="virtual", channel="uds_virtual")

stop_event = threading.Event()


ecu_thread = threading.Thread(target=battery_ecu.run_ecu, args=(bus_ecu,stop_event))
ecu_thread.start()

try:
    tester.run_tester(bus_tester=bus_tester)

finally:
    stop_event.set()
    ecu_thread.join()

    bus_tester.shutdown()
    bus_ecu.shutdown()




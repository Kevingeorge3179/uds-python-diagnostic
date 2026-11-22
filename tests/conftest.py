import threading
import pytest
from battery_ecu import BatteryECU
import can
from queue import Queue
import uuid

@pytest.fixture(scope="function")
def ecu_environment():

    bus_tester = None
    bus_ecu = None
    ecu_thread = None
    stop_event = None
    channel = f"uds_{uuid.uuid4().hex}"


    try:
        bus_tester = can.Bus(interface="virtual", channel=channel)

        bus_ecu = can.Bus(interface="virtual", channel=channel)

        stop_event = threading.Event()

        inbox = Queue()

        ecu = BatteryECU(s3_timeout=0.3)
        dispatch_table = ecu.dispatch_table

        called_handlers = []

        def make_handler_wrapper(dispatch_table, sid):

            original_handler = dispatch_table.get(sid)

            def wrapper(request):

                called_handlers.append(sid)
                response = original_handler(request=request)

                return response

            return wrapper

        for sid in dispatch_table.keys():

            dispatch_table[sid] = make_handler_wrapper(dispatch_table=dispatch_table, sid=sid)

        ecu_thread = threading.Thread(target=ecu.run_ecu, args=(bus_ecu,stop_event,inbox))
        ecu_thread.start()

        resources = {
        "ecu": ecu,
        "bus_tester": bus_tester,
        "inbox": inbox,
        "called_handlers": called_handlers
        }

        yield resources

    finally:

        if stop_event is not None:
            stop_event.set()

        try:

            if ecu_thread is not None:
                ecu_thread.join(2)

                if ecu_thread.is_alive():
                    raise RuntimeError("ECU thread failed to stop within timeout")

        finally:

            if bus_tester is not None:
                bus_tester.shutdown()

            if bus_ecu is not None:
                bus_ecu.shutdown()
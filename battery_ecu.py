import can


def run_ecu(bus_ecu, stop_event):
    while not stop_event.is_set():
        message = bus_ecu.recv(timeout=0.1)

        if message is not None:
            print(message)

            if message.arbitration_id == 0x700:

                if len(message.data) >= 3:

                    if message.data[0] == 0x02:

                        if message.data[1] == 0x10:
                            if message.data[2] == 0x03:

                                arbitration_id = 0x708
                                data = bytes([0x02, 0x50, 0x03])

                                response = can.Message(
                                    is_extended_id=False,
                                    arbitration_id=arbitration_id,
                                    data=data
                                )
                                
                                bus_ecu.send(msg=response)

                            else:

                                arbitration_id = 0x708
                                data = bytes([0x03, 0x7F, 0x10, 0x12])

                                response = can.Message(
                                    is_extended_id=False,
                                    arbitration_id=arbitration_id,
                                    data=data
                                )
                                
                                bus_ecu.send(msg=response)

                        elif message.data[1] == 0x22:

                            arbitration_id = 0x708
                            data = bytes([0x03, 0x7F, 0x22, 0x11])

                            response = can.Message(
                                is_extended_id=False,
                                arbitration_id=arbitration_id,
                                data=data
                            )
                            
                            bus_ecu.send(msg=response)


                    else:
                        print("Unexpected PCI/Length byte")
                
                else:
                    print("Short/malformed request received")
            
            else:
                print("Unexpected CAN ID received")

        else:
            continue
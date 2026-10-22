import can


def run_tester(bus_tester):
    arbitration_id = 0x700
    data = bytes([0x02, 0x10, 0x03])
    # data = bytes([0x02, 0x10, 0x04])
    # data = bytes([0x02, 0x22, 0x00])
    # data = bytes([0x02, 0x10])

    message = can.Message(
        is_extended_id=False,
        arbitration_id=arbitration_id,
        data=data
    )

    bus_tester.send(msg=message)

    response = bus_tester.recv(timeout=2.0)

    if response is not None:
        print(response)

        if response.arbitration_id == 0x708:

            if len(response.data) >= 3 and response.data[0] == 0x02:
                if response.data[1] == 0x50 and response.data[2] == 0x03:
                    print("Received positive response")

                else:
                    print("Unexpected UDS response")

            elif len(response.data) >= 4 and response.data[0] == 0x03:
                if response.data[1] == 0x7F:
                    if response.data[2] == message.data[1]:
                        print(f"Received negative response for requested service. NRC: 0x{response.data[3]:02X}")

                    else:
                        print("Negative response received for a different service.")

                else:
                    print("Unexpected UDS response")

            elif len(response.data) <=2:
                print("Short/malformed response")

            else:
                print("Unexpected UDS response")

        else:
            print("Unexpected CAN ID received")

    else:
        print("No response received from Battery ECU")


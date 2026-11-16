import isotp


def send_raw(bus_tester, data):

    address = isotp.Address(
        isotp.AddressingMode.Normal_11bits,
        txid=0x700,
        rxid=0x708
    )

    stack = None
    stack_started = False

    try:

        stack = isotp.CanStack(bus=bus_tester, address=address)

        stack.start()
        stack_started = True
        
        stack.send(data=data)

        response = stack.recv(block=True,timeout=2.0)

        return response

    finally:

        if  stack_started and stack is not None:
            stack.stop()

def run_tester(bus_tester, data):

    response = send_raw(bus_tester=bus_tester, data=data)

    if response is None:
        print("No response received from Battery ECU")

    elif len(response) == 0:
        print("Empty response received")

    else:

        if len(response) <=1 and data[0] != 0x14:
            print("Short/malformed response")

        elif response[0] == 0x7F:
            if len(response) >= 3:
                if response[1] == data[0]:
                    print(f"Received negative response for requested service. NRC: 0x{response[2]:02X}")

                else:
                    print("Negative response received for a different service.")

            else:
                print("Malformed negative response: missing NRC")

        elif response[0] == 0x50 and data[0] == 0x10:
            if len(response) == 6:
                if response[1] == data[1]:
                    print("Received positive response")
                    timing_1 = response[2] << 8 | response[3]
                    timing_2 = response[4] << 8 | response[5]
                    print(f"P2 Server Max: {timing_1}ms")
                    print(f"P2* Server Max: {timing_2*10}ms")
                    

                else:
                    print("Unexpected UDS response")

            else:
                print("Unexpected UDS response")

        elif response[0] == 0x51 and data[0] == 0x11:
            if len(response) == 2:
                if response[1] == data[1]:
                    print("Received positive response")
                    

                else:
                    print("Unexpected UDS response")

            else:
                print("Unexpected UDS response")

        elif response[0] == 0x62 and data[0] == 0x22:
            if len(response) >= 3:
                if data[1:3] == response[1:3]:
                    print("Received positive response")
                    print(f"{response.hex(' ')}")

                else:
                    print("Mismatch in DID")

            else:
                print("Unexpected UDS response")

        elif response[0] == 0x6E and data[0] == 0x2E:
            if len(response) >= 3:
                if data[1:3] == response[1:3]:
                    print("Received positive response")
                    print(f"{response.hex(' ')}")

                else:
                    print("Mismatch in DID")

            else:
                print("Unexpected UDS response")

        elif response[0] == 0x7E and data[0] == 0x3E:
            if len(response) == 2:
                if response[1] == 0x00:
                    print("Received positive response")
                    print(f"{response.hex(' ')}")

                else:
                    print("Unexpected UDS response")

            else:
                print("Unexpected UDS response")

        elif response[0] == 0x67 and data[0] == 0x27:
            if len(response) == 4:
                if response[1] == data[1]:

                    print(f"{response.hex(' ')}")
                    seed = response[2] << 8 | response[3]
                    key = seed ^ 0xFFFF
                    request_key = bytes([0x27, 0x02, key >>8, key & 0xFF])
                    response_key = send_raw(bus_tester=bus_tester, data=request_key)

                    if response_key is None:
                        print("No response received for Key request from Battery ECU")
            
                    elif len(response_key) == 0:
                        print("Empty response received for key request")

                    else:

                        if len(response_key) <=1:
                            print("Short/malformed response for key request")

                        elif response_key[0] == request_key[0] + 0x40:
                            if len(response_key) == 2:
                                if response_key[1] == request_key[1]:
                                
                                    print("Received positive response")
                                    print(f"{response_key.hex(' ')}")

                                else:

                                    print("Unexpected UDS response")

                            else:
                                print("Unexpected UDS response")

                        elif response_key[0] == 0x7F:
                            if len(response_key) >= 3:
                                if response_key[1] == request_key[0]:
                                    print(f"Received negative response for requested service. NRC: 0x{response_key[2]:02X}")
            
                                else:
                                    print("Negative response received for a different service.")
            
                            else:
                                print("Malformed negative response: missing NRC")

                        else:
                            print("Unexpected UDS response")

                else:
                    print("Unexpected UDS response")

            else:
                print("Unexpected UDS response")

        elif response[0] == 0x71 and data[0] == 0x31:
            if len(response) >= 4:
                if response[1] == 0x01:
                    if len(response) == 4:
                        RID = response[2] << 8 | response[3]
                        if RID == 0xFF00:
                            print("Received positive response")
                            print(f"{response.hex(' ')}")

                        else:
                            print("Unexpected UDS response")

                    else:
                        print("Unexpected UDS response")

                elif response[1] == 0x02:
                    if len(response) == 4:
                        RID = response[2] << 8 | response[3]
                        if RID == 0xFF00:
                            print("Received positive response")
                            print(f"{response.hex(' ')}")

                        else:
                            print("Unexpected UDS response")

                    else:
                        print("Unexpected UDS response")

                elif response[1] == 0x03:
                    if len(response) == 5:
                        RID = response[2] << 8 | response[3]
                        if RID == 0xFF00:
                            if response[4] == 0:
                                print("Received positive response, Status: RUNNING")
                                print(f"{response.hex(' ')}")

                            elif response[4] == 1:
                                print("Received positive response, Status: COMPLETED")
                                print(f"{response.hex(' ')}")

                            else:
                                print("Unexpected UDS response")

                        else:
                            print("Unexpected UDS response")

                    else:
                        print("Unexpected UDS response")

                else:
                    print("Unexpected UDS response")

            else:
                print("Unexpected UDS response")

        elif response[0] == 0x59 and data[0] == 0x19:

            if len(response) >= 3:
                if response[1] == 0x02:
                    if (len(response) - 3) % 4 == 0:
                        availability_mask = response[2]
                        print("Received positive response")
                        print(f"Availability Mask: {availability_mask}")

                        for i in range(3, len(response) - 3, 4):
                            dtc_code = response[i:i+3]
                            dtc_status = response[i+3]
                            print(f"DTC_code: {dtc_code.hex(' ')}")
                            print(f"Status: {dtc_status:02X}")

                    else:
                        print("Unexpected UDS response")

                else:
                    print("Unexpected UDS response")

            else:
                print("Unexpected UDS response")

        elif response[0] == 0x54 and data[0] == 0x14:
            if len(response) == 1:
                print("Received positive response")

            else:
                print("Unexpected UDS response")            

        else:
            print("Unexpected UDS response")

import isotp
from result_validation import validate_common_response,validate_session_response,validate_reset_response,\
validate_rdbi_response,validate_wdbi_response,validate_tester_present_response,validate_security_seed_response,\
validate_routine_response,validate_dtc_response,validate_clear_dtc_response
from result import Result


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

validators = {
    0x10: validate_session_response,
    0x11: validate_reset_response,
    0x22: validate_rdbi_response,
    0x2E: validate_wdbi_response,
    0x3E: validate_tester_present_response,
    0x31: validate_routine_response,
    0x19: validate_dtc_response,
    0x14: validate_clear_dtc_response,
}

def calculate_key(seed):

    key = seed ^ 0xFFFF
    return key

def unlock(bus_tester):

    request = bytes([0x27, 0x01])

    response = send_raw(bus_tester=bus_tester, data=request)

    common_response_seed = validate_common_response(request=request, response=response)

    if not common_response_seed.ok:
        return common_response_seed

    result_seed = validate_security_seed_response(request=request, response=response)

    if not result_seed.ok:
        return result_seed

    seed = result_seed.fields["seed"]
    key = calculate_key(seed=seed)
    request_key = bytes([0x27, 0x02, key >>8, key & 0xFF])
    response_key = send_raw(bus_tester=bus_tester, data=request_key)

    common_response_key = validate_common_response(request=request_key, response=response_key)

    if not common_response_key.ok:
        return common_response_key
    
    if len(response_key) != 2:
        return Result(ok=False, kind="malformed", message="Malformed key response")

    if response_key[1] != request_key[1]:
        return Result(ok=False, kind="malformed", message="Subfunction mismatch")

    return Result(ok=True, kind="positive", message="Security unlocked")

def run_tester(bus_tester, data):

    if not data:
        print("Empty UDS request")
        return

    if data == bytes([0x27, 0x01]):
        result = unlock(bus_tester)

        if result.ok:
            print(result.message)

        else:
            print(f"Security unlock failed:{result.message}")

        return
    
    elif data[0] == 0x27:
        print("Unsupported UDS request")
        return
    

    response = send_raw(bus_tester=bus_tester, data=data)

    common_response = validate_common_response(request=data, response=response)

    if not common_response.ok:
        print(common_response.message)

    else:
        validator = validators.get(data[0])

        if validator is not None:

            result = validator(request=data, response=response)
            print(result.message)

            if result.ok:

                if data[0] == 0x10:
                    print(f"P2_timing: {result.fields['p2_timing']} ms")
                    print(f"P2_star_timing: {result.fields['p2_star_timing']} ms")

                elif data[0] == 0x22:
                    print(f"Response: {result.fields['response']}")

                elif data[0] == 0x31:
                    print(f"Response: {result.fields['response']}")

                elif data[0] == 0x19:
                    print(f"Availability Mask: {result.fields['Availability Mask']}")

                    for dtc in result.fields["dtc_info"]:
                        dtc_code = dtc["dtc_code"]
                        dtc_status = dtc["dtc_status"]

                        print(f"DTC_code: {dtc_code}")
                        print(f"Status: {dtc_status:02X}")
        else:

            print("Unsupported UDS service")

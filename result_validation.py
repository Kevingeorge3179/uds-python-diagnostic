from result import Result

def validate_common_response(request, response):

    if response is None:
        result = Result(ok=False, kind="no_response", message="No response received from Battery ECU")
        return result

    elif len(response) == 0:
        result = Result(ok=False, kind="malformed", message="Empty response received")
        return result

    elif response[0] == 0x7F:
        if len(response) < 3:
            result = Result(ok=False, kind="malformed", message="Malformed negative response: missing NRC")
            return result

        if response[1] != request[0]:
            result = Result(ok=False, kind="malformed", message="Negative response received for a different service")
            return result
        
        result = Result(ok=False, kind="negative", message=f"Received negative response for requested service. NRC: 0x{response[2]:02X}",
                nrc=response[2])
        return result

    elif response[0] != request[0] + 0x40:
        result = Result(ok=False, kind="malformed", message="SID mismatch")
        return result
    
    else:
        result = Result(ok=True, kind="positive", message="Received positive response")
        return result

def validate_session_response(request, response):

    if len(response) != 6:
        result = Result(ok=False, kind="malformed", message="Incorrect response length")
        return result

    if response[0] != request[0] + 0x40:
        result = Result(ok=False, kind="malformed", message="SID mismatch")
        return result

    if response[1] != request[1]:
        result = Result(ok=False, kind="malformed", message="Subfunction mismatch")
        return result

    timing_1 = response[2] << 8 | response[3]
    timing_2 = response[4] << 8 | response[5]
    timing_2_ms = timing_2 * 10

    result = Result(ok=True, kind="positive", message="Received positive response",
        fields={
            "p2_timing": timing_1,
            "p2_star_timing": timing_2_ms
        }
    )

    return result

def validate_reset_response(request, response):

    if len(response) != 2:
        result = Result(ok=False, kind="malformed", message="Incorrect response length")
        return result

    if response[0] != request[0] + 0x40:
        result = Result(ok=False, kind="malformed", message="SID mismatch")
        return result

    if response[1] != request[1]:
        result = Result(ok=False, kind="malformed", message="Subfunction mismatch")
        return result

    result = Result(ok=True, kind="positive", message="Received positive response")
    return result

def validate_rdbi_response(request, response):

    if len(response) < 3:
        result = Result(ok=False, kind="malformed", message="Incorrect response length")
        return result

    if response[0] != request[0] + 0x40:
        result = Result(ok=False, kind="malformed", message="SID mismatch")
        return result

    if request[1:3] != response[1:3]:
        result = Result(ok=False, kind="malformed", message="Mismatch in DID")
        return result

    result = Result(ok=True, kind="positive", message="Received positive response",
        fields={
            "response": response.hex(' ')
        }
    )

    return result

def validate_wdbi_response(request, response):

    if len(response) < 3:
        result = Result(ok=False, kind="malformed", message="Incorrect response length")
        return result

    if response[0] != request[0] + 0x40:
        result = Result(ok=False, kind="malformed", message="SID mismatch")
        return result

    if request[1:3] != response[1:3]:
        result = Result(ok=False, kind="malformed", message="Mismatch in DID")
        return result
    
    result = Result(ok=True, kind="positive", message="Received positive response")
    return result

def validate_tester_present_response(request, response):

    if len(response) != 2:
        result = Result(ok=False, kind="malformed", message="Incorrect response length")
        return result

    if response[0] != request[0] + 0x40:
        result = Result(ok=False, kind="malformed", message="SID mismatch")
        return result

    if request[1] != response[1]:
        result = Result(ok=False, kind="malformed", message="Subfunction mismatch")
        return result

    result = Result(ok=True, kind="positive", message="Received positive response")
    return result

def validate_security_seed_response(request, response):

    if len(response) != 4:
        result = Result(ok=False, kind="malformed", message="Incorrect response length")
        return result

    if response[0] != request[0] + 0x40:
        result = Result(ok=False, kind="malformed", message="SID mismatch")
        return result

    if response[1] != request[1]:
        result = Result(ok=False, kind="malformed", message="Subfunction mismatch")
        return result

    seed = response[2] << 8 | response[3]

    result = Result(ok=True, kind="positive", message="Received positive response",
            fields={
                "seed": seed
            }
        )
    
    return result

def validate_routine_response(request, response):

    if len(response) < 4:
        result = Result(ok=False, kind="malformed", message="Incorrect response length")
        return result
    
    if response[0] != request[0] + 0x40:
        result = Result(ok=False, kind="malformed", message="SID mismatch")
        return result

    if response[1] != request[1]:
        result = Result(ok=False, kind="malformed", message="Subfunction mismatch")
        return result

    if request[2:4] != response[2:4]:
        result = Result(ok=False, kind="malformed", message="Mismatch in RID")
        return result

    if request[1] == 0x01:
        if len(response) != 4:
            result = Result(ok=False, kind="malformed", message="Incorrect response length")
            return result
        
        result = Result(ok=True, kind="positive", message="Received positive response",
                fields={
                    "response": response.hex(' ')
                }
            )
        
        return result

    elif request[1] == 0x02:
        if len(response) != 4:
            result = Result(ok=False, kind="malformed", message="Incorrect response length")
            return result
        
        result = Result(ok=True, kind="positive", message="Received positive response",
                fields={
                    "response": response.hex(' ')
                }
            )
        
        return result

    elif request[1] == 0x03:
        if len(response) != 5:
            result = Result(ok=False, kind="malformed", message="Incorrect response length")
            return result
        
        if response[4] == 0x00:
            result = Result(ok=True, kind="positive", message="Received positive response, Status: RUNNING",
                    fields={
                        "response": response.hex(' ')
                    }
                )
            
            return result

        elif response[4] == 0x01:
            result = Result(ok=True, kind="positive", message="Received positive response, Status: COMPLETED",
                    fields={
                        "response": response.hex(' ')
                    }
                )
            
            return result

        else:
            result = Result(ok=False, kind="malformed", message="Invalid status")
            return result

    else:
        result = Result(ok=False, kind="malformed", message="Invalid subfunction")
        return result

def validate_dtc_response(request, response):

    if len(response) < 3:
        result = Result(ok=False, kind="malformed", message="Incorrect response length")
        return result

    if response[0] != request[0] + 0x40:
        result = Result(ok=False, kind="malformed", message="SID mismatch")
        return result

    if response[1] != request[1]:
        result = Result(ok=False, kind="malformed", message="Subfunction mismatch")
        return result

    if response[1] != 0x02:
        result = Result(ok=False, kind="malformed", message="Unsupported subfunction")
        return result

    if (len(response) - 3) % 4 != 0:
        result = Result(ok=False, kind="malformed", message="Incorrect DTC response length")
        return result

    availability_mask = response[2]

    result = Result(ok=True, kind="positive", message="Received positive response",
            fields={
                "Availability Mask": availability_mask
            }
        )
    
    dtc_info = []
    for i in range(3, len(response), 4):
        dtc_code = response[i:i+3]
        dtc_status = response[i+3]
        info = {
            "dtc_code" : dtc_code.hex(' '),
            "dtc_status" : dtc_status
        }
        dtc_info.append(info)

    result.fields["dtc_info"] = dtc_info

    return result

def validate_clear_dtc_response(request, response):

    if len(response) != 1:
        result = Result(ok=False, kind="malformed", message="Incorrect response length")
        return result
    
    if response[0] != request[0] + 0x40:
        result = Result(ok=False, kind="malformed", message="SID mismatch")
        return result

    result = Result(ok=True, kind="positive", message="Received positive response")
    return result
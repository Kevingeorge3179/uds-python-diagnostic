from tester import send_raw
import time
import math


def initialize_ecu(ecu_environment):

    ecu = ecu_environment["ecu"]

    bus_tester = ecu_environment["bus_tester"]

    data = bytes([0x10, 0x01])
    expected_response = bytes([0x50, 0x01, 0x00, 0x32, 0x01, 0xF4])

    try:
        response = send_raw(bus_tester=bus_tester, data=data)

        assert response is not None
        assert response == expected_response

        assert ecu.current_session == 0x01
        assert ecu.security_unlocked is False
        assert ecu.security_seed is None

    except AssertionError as error:
        raise RuntimeError("ECU initialization failed: validation error.") from error

    else:

        return True

def enter_extended_session(ecu_environment):

    ecu = ecu_environment["ecu"]
    bus_tester = ecu_environment["bus_tester"]
            
    data = bytes([0x10, 0x03])
    expected_response = bytes([0x50, 0x03, 0x00, 0x32, 0x01, 0xF4])

    try:
        response = send_raw(bus_tester=bus_tester, data=data)

        assert response is not None
        assert response == expected_response

        assert ecu.current_session == 0x03
        assert ecu.security_unlocked is False
        assert ecu.security_seed is None

    except AssertionError as error:
        raise RuntimeError("ECU session change failed: validation error.") from error

    else:

        return True

def unlock_security(ecu_environment):

    ecu = ecu_environment["ecu"]
    bus_tester = ecu_environment["bus_tester"]

    data = bytes([0x27, 0x01])
    
    try:
        response_1 = send_raw(bus_tester=bus_tester, data=data)

        assert response_1 is not None
        assert len(response_1) == 4
        assert response_1[0] == 0x67
        assert response_1[1] == 0x01

    except AssertionError as error:
        raise RuntimeError("ECU seed request failed: validation error.") from error

    seed = response_1[2] << 8 | response_1[3]
    key = seed ^ 0xFFFF
    request_key = bytes([0x27, 0x02, key >>8, key & 0xFF])

    try:

        response_2 = send_raw(bus_tester=bus_tester, data=request_key)

        assert response_2 is not None
        assert len(response_2) == 2
        assert response_2[0] == 0x67
        assert response_2[1] == 0x02
        assert ecu.current_session == 0x03
        assert ecu.security_unlocked is True
        assert ecu.security_seed is None

    except AssertionError as error:
        raise RuntimeError("ECU key request failed: validation error.") from error

    else:

        return True


def prepare_preconditions(ecu_environment, session, security):

    valid_sessions = ["default", "extended", "any"]
    valid_security = ["locked", "unlocked", "any"]

    if session not in valid_sessions:
        raise ValueError("Invalid session value.")

    if security not in valid_security:
        raise ValueError("Invalid security value.")

    if session in ("default", "any") and security in ("locked", "any"):
        return True

    elif session == "extended" and security in ("locked", "any"):

        enter_extended_session(ecu_environment=ecu_environment)
        return True

    elif session in ("extended", "any") and security == "unlocked":

        enter_extended_session(ecu_environment=ecu_environment)
        unlock_security(ecu_environment=ecu_environment)
        return True

    elif session == "default" and security == "unlocked":
        raise ValueError("Invalid precondition: SecurityAccess requires Extended Session.")

    else:
        raise ValueError("Invalid precondition: invalid inputs.")

def validate_hex(value, field_name):

    try:
        return bytes.fromhex(value)
    
    except ValueError as error:
        raise ValueError(f"'{field_name}' must contain valid hexadecimal data.") from error

def build_request(data,context):

    request = bytearray()

    if not isinstance(data,list):
        raise TypeError("'data' must be a list.")

    for item in data:

        if isinstance(item,str):

            request.extend(validate_hex(value=item, field_name="item"))

        elif isinstance(item,dict) and "from_context" in item:

            if item["from_context"] not in context:
                raise KeyError("Referenced value not found in test context.")

            seed = context[item["from_context"]]

            if not isinstance(seed,(bytes, bytearray)):
                raise TypeError("Security seed must be bytes or bytearray.")

            if len(seed) != 2:
                raise ValueError("Security seed must contain exactly 2 bytes.")

            request.extend(seed)

        else:

            raise TypeError("Request item must be a string or context reference dictionary.")

    return bytes(request)

def execute_step(step, context,bus_tester):

    if not isinstance(step,dict):
        raise TypeError("'step' must be a dictionary")

    if "request" not in step or "expected" not in step:
        raise ValueError("Step must contain both 'request' and 'expected'.")

    if not isinstance(step["request"],list):
        raise TypeError("'request' must be a list")

    data_byte = build_request(data=step["request"],context=context)

    if not isinstance(step["expected"],dict):
        raise TypeError("'expected' must be a dictionary")

    if "type" not in step["expected"]:
        raise ValueError("'type' missing in expected")
    

    valid_types = ["exact", "pattern"]


    if step["expected"]["type"] not in valid_types:
        raise ValueError("Invalid 'type'")



    if step["expected"]["type"] == "exact":

        if "data" not in step["expected"]:
            raise ValueError("'data' missing in expected")

        if not isinstance(step["expected"]["data"],str):
            raise TypeError("'data' should a string")

        
        
        exp_data = step["expected"]["data"]
        expected_response = validate_hex(value=exp_data,field_name="data")

        try:
            response = send_raw(bus_tester=bus_tester, data=data_byte)

            if response is None:
                raise RuntimeError("UDS response is empty")
            
            assert response == expected_response
    
        except AssertionError as error:
            raise RuntimeError(f"UDS response validation failed. Response:{response.hex()} Expected response:{expected_response.hex()}") \
            from error

    elif step["expected"]["type"] == "pattern":

        if "prefix" not in step["expected"]:
            raise ValueError("'prefix' missing in expected")

        if not isinstance(step["expected"]["prefix"],str):
            raise TypeError("'prefix' should a string")
        
        if "length" not in step["expected"]:
            raise ValueError("'length' missing in expected")

        if isinstance(step["expected"]["length"], bool) or \
            not isinstance(step["expected"]["length"], int) or \
            step["expected"]["length"] <= 0:
            raise ValueError("'length' must be a positive integer.")

        
        exp_data = step["expected"]["prefix"]
        expected_prefix = validate_hex(value=exp_data, field_name="prefix")
        response_length = step["expected"]["length"]
        

        if len(expected_prefix) > response_length:
            raise ValueError("Pattern prefix cannot exceed expected response length.")

        if "capture" not in step["expected"]:
            raise ValueError("'capture' is required for pattern validation.")
        
        if not isinstance(step["expected"]["capture"],dict):
            raise TypeError("'capture' must be a dictionary")

        if "name" not in step["expected"]["capture"] or \
            "start" not in step["expected"]["capture"] or \
            "end" not in step["expected"]["capture"]:
            raise ValueError("'name' or 'start' or 'end' missing in capture")

        if isinstance(step["expected"]["capture"]["start"], bool) or \
            not isinstance(step["expected"]["capture"]["start"], int):
            raise ValueError("'start' must be a non-negative integer.")

        if isinstance(step["expected"]["capture"]["end"], bool) or \
            not isinstance(step["expected"]["capture"]["end"], int):
            raise ValueError("'end' must be a positive integer.")

        if step["expected"]["capture"]["name"] != "seed":
            raise ValueError("'name' should be 'seed'")

        start = step["expected"]["capture"]["start"]
        end = step["expected"]["capture"]["end"]

        if start < 0 or end - start != 2:
            raise ValueError("'seed' should have 2 bytes")

        if end > response_length:
            raise ValueError("'end' is out of  range")

        try:
            response = send_raw(bus_tester=bus_tester, data=data_byte)

            if response is None:
                raise RuntimeError("UDS response is empty")
            
            assert response[:len(expected_prefix)] == expected_prefix
            assert len(response) == response_length

            seed = response[start:end]
            context["seed"] = seed

        except AssertionError as error:
            raise RuntimeError(f"UDS response validation failed. Response:{response.hex()} Expected response:{expected_prefix.hex()}") \
            from error

def process_steps(list_steps,context,bus_tester,ecu):

    for step in list_steps:

        if not isinstance(step,dict):
            raise TypeError("'step' must be a dictionary")

        has_request = "request" in step
        has_action = "action" in step

        if has_request and has_action:
            raise ValueError("A step cannot contain both a request and an action.")

        elif has_request:
        
            execute_step(step=step,context=context, bus_tester=bus_tester)

        elif has_action:

            valid_action = ["wait", "check_state"]

            if not isinstance(step["action"], str):
                raise TypeError("'action' must be a string")

            if step["action"] not in valid_action:
                raise ValueError("Invalid action")

            if step["action"] == "wait":

                if "duration" not in step:
                    raise ValueError("Step must contain 'duration'")

                if isinstance(step["duration"], bool) or \
                not isinstance(step["duration"], (int, float)) or \
                not math.isfinite(step["duration"]) or step["duration"] < 0:
                    raise ValueError("'duration' must be a non-negative number.")
                
                duration = step["duration"]
                time.sleep(duration)

            elif step["action"] == "check_state":

                if not isinstance(step["expected"],dict):
                    raise TypeError("'expected' must be a dictionary")

                if "session" not in step["expected"] or "security" not in step["expected"]:
                    raise ValueError("'expected' must contain both 'session' and 'security'.")

                valid_session = [0x01, 0x03]

                if not isinstance(step["expected"]["session"], int) or \
                    isinstance(step["expected"]["session"], bool):
                    raise TypeError("'session' should be an integer")

                if step["expected"]["session"] not in valid_session:
                    raise ValueError("Invalid session")

                if not isinstance(step["expected"]["security"], bool):
                    raise TypeError("'security' should be a boolean")

                expected_session = step["expected"]["session"]
                expected_security = step["expected"]["security"]

                try:
                    assert ecu.current_session == expected_session
                    assert ecu.security_unlocked == expected_security

                except AssertionError as error:
                    raise RuntimeError("ECU transition failed: validation error.") from error
        else:
            raise ValueError("Invalid step definition.")

def validate_test_case(test_case):

    if not isinstance(test_case, dict):
        raise TypeError("Test case should be a dictionary")

    required_keys = ["test_id", "description", "session", "security", "setup_steps", 
                     "steps", "state_checks", "expected_handler_calls"]
    required_set = set(required_keys)

    missing_key = required_set - test_case.keys()
    unexpected_key = test_case.keys() - required_set

    if missing_key or unexpected_key:
        raise ValueError(f"Missing:{missing_key or 'None'}, Unexpected:{unexpected_key or 'None'}")

    if not isinstance(test_case["test_id"], str) or not test_case["test_id"].strip():
        raise TypeError("Test ID should be a String")

    if not isinstance(test_case["description"], str) or not test_case["description"].strip():
        raise TypeError("Test Description should be a String")

    if not isinstance(test_case["session"], str):
        raise TypeError("Session should be a String")

    if not isinstance(test_case["security"], str):
        raise TypeError("Security should be a String")

    if not isinstance(test_case["setup_steps"], list):
        raise TypeError("Setup_steps should be a List")

    if not isinstance(test_case["steps"], list):
        raise TypeError("Steps should be a List")

    if not isinstance(test_case["state_checks"], dict):
        raise TypeError("State_checks should be a Dictionary")

    if not isinstance(test_case["expected_handler_calls"], list):
        raise TypeError("Expected_handler_calls should be a List")

    for sid in test_case["expected_handler_calls"]:

        if not isinstance(sid, int) or isinstance(sid, bool):
            raise TypeError("'SID' should be an integer")

        if not (0x00 <= sid <= 0xFF):
            raise ValueError("Invalid SID")

    valid_sessions = ["default", "extended", "any"]
    valid_security = ["locked", "unlocked", "any"]

    if test_case["session"] not in valid_sessions:
        raise ValueError("Invalid session value.")

    if test_case["security"] not in valid_security:
        raise ValueError("Invalid security value.")

    if not test_case["state_checks"]:
        raise ValueError("State_check can not be empty")

    valid_ecu_states = ["session", "security", "security_seed", 
                        "routine_status", "fault_active", "did_values", "did_not_present"]

    valid_ecu_states_set = set(valid_ecu_states)
    unexpected_state = test_case["state_checks"].keys() - valid_ecu_states_set

    if unexpected_state:
        raise ValueError(f"Unexpected:{unexpected_state or 'None'}")

    if "session" in test_case["state_checks"]:

        allowed_session = [0x01, 0x03]

        if not isinstance(test_case["state_checks"]["session"], int) or \
            isinstance(test_case["state_checks"]["session"], bool):
            raise TypeError("'Session' should be an integer")

        if test_case["state_checks"]["session"] not in allowed_session:
            raise ValueError("Invalid session")

    if "security" in test_case["state_checks"]:

        if not isinstance(test_case["state_checks"]["security"], bool):
            raise TypeError("'Security' should be a boolean")

    if "security_seed" in test_case["state_checks"]:

        if not isinstance(test_case["state_checks"]["security_seed"], (bytes,type(None),bytearray)):
            raise TypeError("'security_seed' should be bytes or None")

        if test_case["state_checks"]["security_seed"] is not None and len(test_case["state_checks"]["security_seed"]) != 2:
            raise ValueError("Security seed should be two bytes")

    if "routine_status" in test_case["state_checks"]:

        if not isinstance(test_case["state_checks"]["routine_status"], str):
            raise TypeError("'Routine_status' should be a string")

        valid_routine_status = ["NOT_STARTED", "RUNNING", "COMPLETED", "STOPPED"]

        if test_case["state_checks"]["routine_status"] not in valid_routine_status:
            raise ValueError("Invalid routine status")

    if "fault_active" in test_case["state_checks"]:

        if not isinstance(test_case["state_checks"]["fault_active"], bool):
            raise TypeError("'Fault_active' should be a boolean")

    if "did_values" in test_case["state_checks"]:

        if not isinstance(test_case["state_checks"]["did_values"], dict):
            raise TypeError("'did_values' should be a dictionary")

        for key, value in test_case["state_checks"]["did_values"].items():

            if not isinstance(key, int) or isinstance(key, bool) or not (0 <= key <= 0xFFFF):
                raise ValueError("DID should be a valid 16-bit integer")

            if not isinstance(value, (bytes, bytearray)):
                raise TypeError("Value should be in bytes")

    if "did_not_present" in test_case["state_checks"]:

        if not isinstance(test_case["state_checks"]["did_not_present"], list):
            raise TypeError("'did_not_present' should be a list")

        for val in test_case["state_checks"]["did_not_present"]:

            if not isinstance(val, int) or isinstance(val, bool) or not (0 <= val <= 0xFFFF):
                raise ValueError("DID should be a valid 16-bit integer")

def verify_state_checks(ecu, state_checks):

    if "session" in state_checks:

        assert ecu.current_session == state_checks["session"], "Session mismatch"

    if "security" in state_checks:

        assert ecu.security_unlocked == state_checks["security"], "Security mismatch"

    if "security_seed" in state_checks:

        assert ecu.security_seed == state_checks["security_seed"], "Seed mismatch"

    if "routine_status" in state_checks:

        assert ecu.routine_status == state_checks["routine_status"], "Routine_status mismatch"

    if "fault_active" in state_checks:
    
        assert ecu.fault_active == state_checks["fault_active"], "Fault_active mismatch"

    if "did_values" in state_checks:
        
        for did, value in state_checks["did_values"].items():

            if did not in ecu.did_data:
                raise AssertionError("DID missing from ECU")

            assert value == ecu.did_data[did], "DID value mismatch"

    if "did_not_present" in state_checks:

        for did in state_checks["did_not_present"]:

            assert did not in ecu.did_data, "DID present in dictionary"

        
from test_helpers import initialize_ecu, prepare_preconditions, process_steps, validate_test_case, verify_state_checks
import pytest


test_case_1 = {
    "test_id" : "TC-3C-05",
    "description" : "Invalid SecurityAccess Key",
    "session" : "extended",
    "security" : "locked",
    "setup_steps" : [],
    "steps": [
        {
            "request": ["27", "01"],
            "expected": {
                "type": "pattern",
                "prefix": "67 01",
                "length": 4,
                "capture": {
                    "name": "seed",
                    "start": 2,
                    "end": 4
                }
            }
        },
        {
            "request": ["27", "02", {"from_context": "seed"}],
            "expected": {
                "type": "exact",
                "data": "7F 27 35"
            }
        }
    ],
    "state_checks": {
    "session": 0x03,
    "security": False,
    "security_seed": None
    },
    "expected_handler_calls" : [0x27, 0x27]
}

test_case_2 = {
    "test_id" : "TC-3C-06",
    "description" : "Key without seed",
    "session" : "extended",
    "security" : "locked",
    "setup_steps" : [],
    "steps": [
        {
            "request": ["27", "02", "12", "34"],
            "expected": {
                "type": "exact",
                "data": "7F 27 24"
            }
        }
    ],
    "state_checks": {
    "session": 0x03,
    "security": False,
    "security_seed": None
    },
    "expected_handler_calls" : [0x27]
}

test_case_3 = {
    "test_id" : "TC-3C-07",
    "description" : "Unsupported DID write",
    "session" : "extended",
    "security" : "unlocked",
    "setup_steps" : [],
    "steps": [
        {
            "request": ["2E", "F1", "B0", "12", "34"],
            "expected": {
                "type": "exact",
                "data": "7F 2E 31"
            }
        }
    ],
    "state_checks": {
    "session": 0x03,
    "security": True,
    "security_seed": None,
    "did_not_present": [0xF1B0]
    },
    "expected_handler_calls" : [0x2E]
}

test_case_4 = {
    "test_id" : "TC-3C-08",
    "description" : "RoutineControl with unsupported RID",
    "session" : "extended",
    "security" : "unlocked",
    "setup_steps" : [],
    "steps": [
        {
            "request": ["31", "01", "FF", "01"],
            "expected": {
                "type": "exact",
                "data": "7F 31 31"
            }
        }
    ],
    "state_checks": {
    "session": 0x03,
    "security": True,
    "security_seed": None,
    "routine_status" : "NOT_STARTED",
    "fault_active" : False
    },
    "expected_handler_calls" : [0x31]
}

test_case_5 = {
    "test_id" : "TC-3C-09",
    "description" : "StartRoutine when already completed",
    "session" : "extended",
    "security" : "unlocked",
    "setup_steps" : [
        {
            "request": ["31", "01", "FF", "00"],
            "expected": {
                "type": "exact",
                "data": "71 01 FF 00"
            }
        }
    ],
    "steps": [
        {
            "request": ["31", "01", "FF", "00"],
            "expected": {
                "type": "exact",
                "data": "7F 31 24"
            }
        }
    ],
    "state_checks": {
    "session": 0x03,
    "security": True,
    "security_seed": None,
    "routine_status" : "COMPLETED",
    "fault_active" : True
    },
    "expected_handler_calls" : [0x31]
}

test_case_6 = {
    "test_id" : "TC-2C-01",
    "description" : "DTC history after ECU Reset",
    "session" : "extended",
    "security" : "unlocked",
    "setup_steps" : [
        {
            "request": ["31", "01", "FF", "00"],
            "expected": {
                "type": "exact",
                "data": "71 01 FF 00"
            }
        },
        {
            "request": ["19", "02", "FF"],
            "expected": {
                "type": "exact",
                "data": "59 02 09 12 34 56 09"
            }
        },
        {
            "request": ["11", "01"],
            "expected": {
                "type": "exact",
                "data": "51 01"
            }
        },
    ],
    "steps": [
        {
            "request": ["19", "02", "FF"],
            "expected": {
                "type": "exact",
                "data": "59 02 09 12 34 56 08"
            }
        }        
    ],
    "state_checks": {
    "session": 0x01,
    "security": False,
    "security_seed": None,
    "routine_status" : "NOT_STARTED",
    "fault_active" : False
    },
    "expected_handler_calls" : [0x19]
}

test_case_7 = {
    "test_id" : "TC-3A-01",
    "description" : "Extended Session to Default Session",
    "session" : "extended",
    "security" : "unlocked",
    "setup_steps" : [],
    "steps": [
        {
            "request": ["10", "01"],
            "expected": {
                "type": "exact",
                "data": "50 01 00 32 01 F4"
            }
        }
    ],
    "state_checks": {
    "session": 0x01,
    "security": False,
    "security_seed": None
    },
    "expected_handler_calls" : [0x10]
}

test_case_8 = {
    "test_id" : "TC-3A-02",
    "description" : "ECU Reset while Extended and unlocked",
    "session" : "extended",
    "security" : "unlocked",
    "setup_steps" : [
        {
            "request": ["2E", "F1", "A0", "12", "34"],
            "expected": {
                "type": "exact",
                "data": "6E F1 A0"
            }
        }
    ],
    "steps": [
        {
            "request": ["11", "01"],
            "expected": {
                "type": "exact",
                "data": "51 01"
            }
        }
    ],
    "state_checks": {
    "session": 0x01,
    "security": False,
    "security_seed": None,
    "routine_status" : "NOT_STARTED",
    "fault_active" : False,
    "did_values": {0xF1A0: b"\x12\x34"}
    },
    "expected_handler_calls" : [0x11]
}

test_case_9 = {
    "test_id" : "TC-3B-01",
    "description" : "Protected service in Default Session",
    "session" : "default",
    "security" : "locked",
    "setup_steps" : [],
    "steps": [
        {
            "request": ["2E", "F1", "A0", "12", "34"],
            "expected": {
                "type": "exact",
                "data": "7F 2E 7F"
            }
        }
    ],
    "state_checks": {
    "session": 0x01,
    "security": False,
    "security_seed": None
    },
    "expected_handler_calls" : []
}

test_case_10 = {
    "test_id" : "TC-3B-02",
    "description" : "Protected service in Extended Session while locked",
    "session" : "extended",
    "security" : "locked",
    "setup_steps" : [],
    "steps": [
        {
            "request": ["2E", "F1", "A0", "12", "34"],
            "expected": {
                "type": "exact",
                "data": "7F 2E 33"
            }
        }
    ],
    "state_checks": {
    "session": 0x03,
    "security": False,
    "security_seed": None
    },
    "expected_handler_calls" : []
}

test_case_11 = {
    "test_id" : "TC-3B-03",
    "description" : "Successful protected write",
    "session" : "extended",
    "security" : "unlocked",
    "setup_steps" : [],
    "steps": [
        {
            "request": ["2E", "F1", "A0", "12", "34"],
            "expected": {
                "type": "exact",
                "data": "6E F1 A0"
            }
        }
    ],
    "state_checks": {
    "session": 0x03,
    "security": True,
    "security_seed": None,
    "did_values": {
        0xF1A0: bytes.fromhex("12 34")
        }
    },
    "expected_handler_calls" : [0x2E]
}

test_case_12 = {
    "test_id" : "TC-3B-04",
    "description" : "Unsupported Service",
    "session" : "default",
    "security" : "locked",
    "setup_steps" : [],
    "steps": [
        {
            "request": ["99", "01", "02"],
            "expected": {
                "type": "exact",
                "data": "7F 99 11"
            }
        }
    ],
    "state_checks": {
    "session": 0x01,
    "security": False,
    "security_seed": None
    },
    "expected_handler_calls" : []
}

test_case_13 = {
    "test_id" : "TC-3C-10",
    "description" : "Invalid WDBI length",
    "session" : "extended",
    "security" : "unlocked",
    "setup_steps" : [],
    "steps": [
        {
            "request": ["2E", "F1", "A0"],
            "expected": {
                "type": "exact",
                "data": "7F 2E 13"
            }
        }
    ],
    "state_checks": {
    "session": 0x03,
    "security": True,
    "security_seed": None,
    "did_not_present": [0xF1A0]
    },
    "expected_handler_calls" : [0x2E]
}

test_case_14 = {
    "test_id" : "TC-3C-04",
    "description" : "Late request after S3 expiry",
    "session" : "extended",
    "security" : "unlocked",
    "setup_steps": [
        {
            "action": "wait",
            "duration": 0.5
        }
    ],
    "steps": [
        {
            "request": ["2E", "F1", "A0", "12", "34"],
            "expected": {
                "type": "exact",
                "data": "7F 2E 7F"
            }
        }
    ],
    "state_checks": {
    "session": 0x01,
    "security": False,
    "security_seed": None
    },
    "expected_handler_calls" : []
}

test_case_15 = {
    "test_id" : "TC-3C-02",
    "description" : "TesterPresent refreshes S3",
    "session" : "extended",
    "security" : "unlocked",
    "setup_steps": [
        {
            "action": "wait",
            "duration": 0.2
        }
    ],
    "steps": [
        {
            "request": ["3E", "00"],
            "expected": {
                "type": "exact",
                "data": "7E 00"
            }
        },
        {
            "action": "wait",
            "duration": 0.15
        },
        {
            "action": "check_state",
            "expected": 
            {
                "session": 0x03,
                "security": True
            }
        },
        {
            "action": "wait",
            "duration": 0.5
        }
    ],
    "state_checks": {
    "session": 0x01,
    "security": False,
    "security_seed": None
    },
    "expected_handler_calls" : [0x3E]
}

test_case_16 = {
    "test_id" : "TC-3C-03",
    "description" : "Security re-lock on S3 expiry",
    "session" : "extended",
    "security" : "unlocked",
    "setup_steps": [
        {
            "action": "wait",
            "duration": 0.5
        }
    ],
    "steps": [],
    "state_checks": {
    "session": 0x01,
    "security": False,
    "security_seed": None
    },
    "expected_handler_calls" : []
}

test_case_17 = {
    "test_id" : "TC-4C-01",
    "description" : "ReadDTCInformation (0x19) - Incorrect request length",
    "session" : "default",
    "security" : "locked",
    "setup_steps": [],
    "steps": [
        {
            "request": ["19", "02"],
            "expected": {
                "type": "exact",
                "data": "7F 19 13"
            }
        }
    ],
    "state_checks": {
    "session": 0x01,
    "security": False,
    "security_seed": None
    },
    "expected_handler_calls" : [0x19]
}

test_case_18 = {
    "test_id" : "TC-4C-02",
    "description" : "ReadDTCInformation (0x19) - Unsupported sub-function",
    "session" : "default",
    "security" : "locked",
    "setup_steps": [],
    "steps": [
        {
            "request": ["19", "04", "FF"],
            "expected": {
                "type": "exact",
                "data": "7F 19 12"
            }
        }
    ],
    "state_checks": {
    "session": 0x01,
    "security": False,
    "security_seed": None
    },
    "expected_handler_calls" : [0x19]
}

test_case_19 = {
    "test_id" : "TC-4C-03",
    "description" : "ReadDTCInformation (0x19) - DTC status-mask filtering",
    "session" : "extended",
    "security" : "unlocked",
    "setup_steps": [
        {
            "request": ["31", "01", "FF", "00"],
            "expected": {
                "type": "exact",
                "data": "71 01 FF 00"
            }
        }
    ],
    "steps": [
        {
            "request": ["19", "02", "02"],
            "expected": {
                "type": "exact",
                "data": "59 02 09"
            }
        }
    ],
    "state_checks": {
    "session": 0x03,
    "security": True,
    "security_seed": None,
    "fault_active" : True
    },
    "expected_handler_calls" : [0x19]
}

test_case_20 = {
    "test_id" : "TC-4C-04",
    "description" : "ClearDiagnosticInformation (0x14) - Incorrect request length",
    "session" : "default",
    "security" : "locked",
    "setup_steps": [],
    "steps": [
        {
            "request": ["14", "FF", "FF"],
            "expected": {
                "type": "exact",
                "data": "7F 14 13"
            }
        }
    ],
    "state_checks": {
    "session": 0x01,
    "security": False,
    "security_seed": None
    },
    "expected_handler_calls" : [0x14]
}

test_case_21 = {
    "test_id" : "TC-4C-05",
    "description" : "ClearDiagnosticInformation (0x14) - Invalid DTC group",
    "session" : "default",
    "security" : "locked",
    "setup_steps": [],
    "steps": [
        {
            "request": ["14", "12", "34", "56"],
            "expected": {
                "type": "exact",
                "data": "7F 14 31"
            }
        }
    ],
    "state_checks": {
    "session": 0x01,
    "security": False,
    "security_seed": None
    },
    "expected_handler_calls" : [0x14]
}

test_case_22 = {
    "test_id" : "TC-4C-06",
    "description" : "ClearDiagnosticInformation (0x14) - Clear confirmed DTC when fault is inactive",
    "session" : "extended",
    "security" : "unlocked",
    "setup_steps": [
        {
            "request": ["31", "01", "FF", "00"],
            "expected": {
                "type": "exact",
                "data": "71 01 FF 00"
            }
        },
        {
            "request": ["19", "02", "FF"],
            "expected": {
                "type": "exact",
                "data": "59 02 09 12 34 56 09"
            }
        },
        {
            "request": ["11", "01"],
            "expected": {
                "type": "exact",
                "data": "51 01"
            }
        }
    ],
    "steps": [
        {
            "request": ["14", "FF", "FF", "FF"],
            "expected": {
                "type": "exact",
                "data": "54"
            }
        },
        {
            "request": ["19", "02", "FF"],
            "expected": {
                "type": "exact",
                "data": "59 02 09"
            }
        },
        {
            "action": "check_state",
            "expected": 
            {
                "session": 0x01,
                "security": False
            }
        }
    ],
    "state_checks": {
    "session": 0x01,
    "security": False,
    "security_seed": None,
    "routine_status" : "NOT_STARTED",
    "fault_active" : False
    },
    "expected_handler_calls" : [0x14, 0x19]
}

test_case_23 = {
    "test_id" : "TC-4C-07",
    "description" : "ClearDiagnosticInformation (0x14) - Clear DTC when fault is active and verify re-logging",
    "session" : "extended",
    "security" : "unlocked",
    "setup_steps": [
        {
            "request": ["31", "01", "FF", "00"],
            "expected": {
                "type": "exact",
                "data": "71 01 FF 00"
            }
        },
        {
            "request": ["19", "02", "FF"],
            "expected": {
                "type": "exact",
                "data": "59 02 09 12 34 56 09"
            }
        },
    ],
    "steps": [
        {
            "request": ["14", "FF", "FF", "FF"],
            "expected": {
                "type": "exact",
                "data": "54"
            }
        },
        {
            "request": ["19", "02", "FF"],
            "expected": {
                "type": "exact",
                "data": "59 02 09 12 34 56 09"
            }
        },
        {
            "action": "check_state",
            "expected": 
            {
                "session": 0x03,
                "security": True
            }
        }
    ],
    "state_checks": {
    "session": 0x03,
    "security": True,
    "security_seed": None,
    "routine_status" : "COMPLETED",
    "fault_active" : True
    },
    "expected_handler_calls" : [0x14, 0x19]
}

test_case_24 = {
    "test_id" : "TC-4C-08",
    "description" : "ReadDataByIdentifier (0x22) - Incorrect request length",
    "session" : "default",
    "security" : "locked",
    "setup_steps": [],
    "steps": [
        {
            "request": ["22", "F1"],
            "expected": {
                "type": "exact",
                "data": "7F 22 13"
            }
        }
    ],
    "state_checks": {
    "session": 0x01,
    "security": False,
    "security_seed": None
    },
    "expected_handler_calls" : [0x22]
}

test_case_25 = {
    "test_id" : "TC-4C-09",
    "description" : "ReadDataByIdentifier (0x22) - Unsupported DID",
    "session" : "default",
    "security" : "locked",
    "setup_steps": [],
    "steps": [
        {
            "request": ["22", "F1", "B0"],
            "expected": {
                "type": "exact",
                "data": "7F 22 31"
            }
        }
    ],
    "state_checks": {
    "session": 0x01,
    "security": False,
    "security_seed": None
    },
    "expected_handler_calls" : [0x22]
}

test_case_26 = {
    "test_id" : "TC-4C-10",
    "description" : "ReadDataByIdentifier (0x22) - Successful read of DID F186",
    "session" : "default",
    "security" : "locked",
    "setup_steps": [],
    "steps": [
        {
            "request": ["22", "F1", "86"],
            "expected": {
                "type": "exact",
                "data": "62 F1 86 01"
            }
        }
    ],
    "state_checks": {
    "session": 0x01,
    "security": False,
    "security_seed": None
    },
    "expected_handler_calls" : [0x22]
}

test_cases = [test_case_1, test_case_2, test_case_3, test_case_4, test_case_5, test_case_6, test_case_7,test_case_8,
            test_case_9, test_case_10, test_case_11, test_case_12, test_case_13, test_case_14, test_case_15, test_case_16,
            test_case_17, test_case_18, test_case_19, test_case_20, test_case_21, test_case_22, test_case_23, test_case_24,
            test_case_25, test_case_26]

def run_test_case(test_case, ecu_environment):

    ecu = ecu_environment["ecu"]
    bus_tester = ecu_environment["bus_tester"]
    handlers_called = ecu_environment["called_handlers"]
    context = {}

    validate_test_case(test_case=test_case)

    initialize_ecu(ecu_environment=ecu_environment)

    prepare_preconditions(
        ecu_environment=ecu_environment,
        session=test_case["session"],
        security=test_case["security"]
        )

    process_steps(list_steps=test_case["setup_steps"], context=context, bus_tester=bus_tester, ecu=ecu)

    handlers_called.clear()

    process_steps(list_steps=test_case["steps"], context=context, bus_tester=bus_tester, ecu=ecu)

    assert test_case["expected_handler_calls"] == handlers_called, "Missmatch in handlers called"

    verify_state_checks(ecu=ecu, state_checks=test_case["state_checks"])


@pytest.mark.parametrize("test_case", test_cases, ids= [tc["test_id"] for tc in test_cases])
def test_uds_regression(test_case, ecu_environment):
    run_test_case(test_case, ecu_environment)

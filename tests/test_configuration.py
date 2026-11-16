

def test_ecu_configuration(ecu_environment):

    ecu = ecu_environment["ecu"]

    assert set(ecu.dispatch_table) == set(ecu.gate_policy),(
    "Mismatch between dispatch_table and gate_policy \n"
    f"Keys missing in gate_policy: {set(ecu.dispatch_table) - set(ecu.gate_policy)} \n"
    f"Keys missing in dispatch_table: {set(ecu.gate_policy) - set(ecu.dispatch_table)} \n"
    )



def test_ecu_initial_state(ecu_environment):

    ecu = ecu_environment["ecu"]

    assert ecu.current_session == 0x01
    assert ecu.security_unlocked == False
    assert ecu.security_seed == None


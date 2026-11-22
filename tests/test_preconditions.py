from test_helpers import initialize_ecu, enter_extended_session, unlock_security, prepare_preconditions
import pytest

def test_initialize_ecu(ecu_environment):

    result = initialize_ecu(ecu_environment=ecu_environment)

    ecu = ecu_environment["ecu"]

    assert result is True
    assert ecu.current_session == 0x01
    assert ecu.security_unlocked == False
    assert ecu.security_seed == None

def test_enter_extended_session(ecu_environment):

    result = enter_extended_session(ecu_environment=ecu_environment)
    
    ecu = ecu_environment["ecu"]

    assert result is True
    assert ecu.current_session == 0x03
    assert ecu.security_unlocked == False
    assert ecu.security_seed == None

def test_unlock_security(ecu_environment):

    ecu = ecu_environment["ecu"]

    step_1 = initialize_ecu(ecu_environment=ecu_environment)

    step_2 = enter_extended_session(ecu_environment=ecu_environment)

    step_3 = unlock_security(ecu_environment=ecu_environment)

    assert step_1 is True
    assert step_2 is True
    assert step_3 is True
    assert ecu.current_session == 0x03
    assert ecu.security_unlocked == True
    assert ecu.security_seed == None

def test_prepare_preconditions_1(ecu_environment):

    ecu = ecu_environment["ecu"]

    step_1 = initialize_ecu(ecu_environment=ecu_environment)

    step_2 = prepare_preconditions(
        ecu_environment=ecu_environment,
        session="extended",
        security="unlocked"
    )

    assert step_1 is True
    assert step_2 is True
    assert ecu.current_session == 0x03
    assert ecu.security_unlocked == True
    assert ecu.security_seed == None

def test_prepare_preconditions_2(ecu_environment):

    ecu = ecu_environment["ecu"]

    step_1 = initialize_ecu(ecu_environment=ecu_environment)

    step_2 = prepare_preconditions(
        ecu_environment=ecu_environment,
        session="extended",
        security="locked"
    )

    assert step_1 is True
    assert step_2 is True
    assert ecu.current_session == 0x03
    assert ecu.security_unlocked == False
    assert ecu.security_seed == None

def test_prepare_preconditions_3(ecu_environment):

    ecu = ecu_environment["ecu"]

    step_1 = initialize_ecu(ecu_environment=ecu_environment)

    with pytest.raises(ValueError) as error:
        prepare_preconditions(
            ecu_environment=ecu_environment,
            session="default",
            security="unlocked"
        )

    assert step_1 is True
    assert str(error.value) == (
        "Invalid precondition: SecurityAccess requires Extended Session."
    )
    assert ecu.current_session == 0x01
    assert ecu.security_unlocked == False
    assert ecu.security_seed == None
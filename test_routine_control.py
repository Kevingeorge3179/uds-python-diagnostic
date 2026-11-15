from battery_ecu import BatteryECU


ecu_1 = BatteryECU()
ecu_2 = BatteryECU()
ecu_3 = BatteryECU()
ecu_4 = BatteryECU()
ecu_5 = BatteryECU()
ecu_6 = BatteryECU()
ecu_7 = BatteryECU()
ecu_8 = BatteryECU()
ecu_9 = BatteryECU()

ecu_1.routine_status = "COMPLETED"
ecu_1.fault_active = True

ecu_3.routine_status = "COMPLETED"
ecu_3.fault_active = True

ecu_5.routine_status = "COMPLETED"
ecu_5.fault_active = True

ecu_8.routine_status = "COMPLETED"
ecu_8.fault_active = True

ecu_9.routine_status = "COMPLETED"
ecu_9.fault_active = True

request_1 = bytes([0x31, 0x01, 0xFF, 0x00])

request_2 = bytes([0x31, 0x03, 0xFF, 0x00])

request_3 = bytes([0x31, 0x03, 0xFF, 0x01])

request_4 = bytes([0x31, 0x04, 0xFF, 0x00])

request_5 = bytes([0x31, 0x04, 0xFF])

request_6 = bytes([0x31, 0x01, 0xFF, 0x01])

request_7 = bytes([0x31, 0x02, 0xFF, 0x00])

request_8 = bytes([0x31, 0x02, 0xFF, 0x01])

response_1 = ecu_1.handle_routine_control(request=request_1)

response_2 = ecu_2.handle_routine_control(request=request_2)

response_3 = ecu_3.handle_routine_control(request=request_3)

response_4 = ecu_4.handle_routine_control(request=request_1)

response_5 = ecu_5.handle_routine_control(request=request_6)

response_6 = ecu_6.handle_routine_control(request=request_4)

response_7 = ecu_7.handle_routine_control(request=request_5)

response_8 = ecu_8.handle_routine_control(request=request_7)

response_9 = ecu_9.handle_routine_control(request=request_8)

assert response_1 == bytes([0x7F, 0x31, 0x24])
assert ecu_1.routine_status == "COMPLETED"
assert ecu_1.fault_active is True


assert response_2 == bytes([0x7F, 0x31, 0x24])
assert ecu_2.routine_status == "NOT_STARTED"
assert ecu_2.fault_active is False

assert response_3 == bytes([0x7F, 0x31, 0x31])
assert ecu_3.routine_status == "COMPLETED"
assert ecu_3.fault_active is True

assert response_4 == bytes([0x71, 0x01, 0xFF, 0x00])
assert ecu_4.routine_status == "COMPLETED"
assert ecu_4.fault_active is True

assert response_5 == bytes([0x7F, 0x31, 0x31])
assert ecu_5.routine_status == "COMPLETED"
assert ecu_5.fault_active is True

assert response_6 == bytes([0x7F, 0x31, 0x12])
assert ecu_6.routine_status == "NOT_STARTED"
assert ecu_6.fault_active is False

assert response_7 == bytes([0x7F, 0x31, 0x13])
assert ecu_7.routine_status == "NOT_STARTED"
assert ecu_7.fault_active is False

assert response_8 == bytes([0x7F, 0x31, 0x24])
assert ecu_8.routine_status == "COMPLETED"
assert ecu_8.fault_active is True

assert response_9 == bytes([0x7F, 0x31, 0x31])
assert ecu_9.routine_status == "COMPLETED"
assert ecu_9.fault_active is True
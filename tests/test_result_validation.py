from result_validation import validate_common_response,validate_session_response,validate_reset_response,\
validate_rdbi_response,validate_wdbi_response,validate_tester_present_response,validate_security_seed_response,\
validate_routine_response,validate_dtc_response,validate_clear_dtc_response



request_1 = bytes([0x22, 0xF1, 0x86])
request_2 = bytes([0x10, 0x03])
request_3 = bytes([0x11, 0x01])
request_4 = bytes([0x22, 0xF1, 0x86])
request_5 = bytes([0x2E, 0xF1, 0x86, 0x01])
request_6 = bytes([0x3E, 0x00])
request_7 = bytes([0x27, 0x01])
request_8 = bytes([0x31, 0x01, 0xFF, 0x00])
request_9 = bytes([0x31, 0x02, 0xFF, 0x00])
request_10 = bytes([0x31, 0x03, 0xFF, 0x00])
request_11 = bytes([0x31, 0x04, 0xFF, 0x00])
request_12 = bytes([0x19, 0x02, 0xFF])
request_13 = bytes([0x14, 0xFF, 0xFF, 0xFF])

response_1 = None
response_2 = bytes([])
response_3 = bytes([0x7F, 0x22, 0x31])
response_4 = bytes([0x7F, 0x10, 0x12])
response_5 = bytes([0x62, 0xF1, 0x86, 0x01])
response_6 = bytes([0x7F, 0x22])
response_7 = bytes([0x55, 0x01])

response_8 = bytes([0x50, 0x03, 0x00, 0x32, 0x01, 0xF4])
response_9 = bytes([0x50, 0x03, 0x00, 0x32, 0x01])
response_10 = bytes([0x51, 0x03, 0x00, 0x32, 0x01, 0xF4])
response_11 = bytes([0x50, 0x02, 0x00, 0x32, 0x01, 0xF4])

response_12 = bytes([0x51, 0x01])
response_13 = bytes([0x51, 0x02])
response_14 = bytes([0x51])

response_15 = bytes([0x62, 0xF1, 0x86, 0x01])
response_16 = bytes([0x62, 0xF1])
response_17 = bytes([0x55, 0xF1, 0x86, 0x01])
response_18 = bytes([0x62, 0xF1, 0xB0, 0x01])

response_19 = bytes([0x6E, 0xF1, 0x86])
response_20 = bytes([0x6E, 0xF1])
response_21 = bytes([0x55, 0xF1, 0x86])
response_22 = bytes([0x6E, 0xF1, 0xB0])

response_23 = bytes([0x7E, 0x00])
response_24 = bytes([0x7E])
response_25 = bytes([0x55, 0x00])
response_26 = bytes([0x7E, 0x01])

response_27 = bytes([0x67, 0x01, 0x12, 0x34])
response_28 = bytes([0x67, 0x01])
response_29 = bytes([0x65, 0x01, 0x12, 0x34])
response_30 = bytes([0x67, 0x02, 0x12, 0x34])

response_31 = bytes([0x71, 0x01, 0xFF, 0x00])
response_32 = bytes([0x71, 0x02, 0xFF, 0x00])
response_33 = bytes([0x71, 0x03, 0xFF, 0x00, 0x00])
response_34 = bytes([0x71, 0x03, 0xFF, 0x00, 0x01])
response_35 = bytes([0x72, 0x01, 0xFF, 0x00])
response_36 = bytes([0x71, 0x02, 0xFF, 0x00])
response_37 = bytes([0x71, 0x01, 0xFF, 0x03])
response_38 = bytes([0x71, 0x01, 0xFF])
response_39 = bytes([0x71, 0x03, 0xFF, 0x00, 0x02])
response_40 = bytes([0x71, 0x04, 0xFF, 0x00])
response_41 = bytes([0x71, 0x01, 0xFF, 0x00, 0xAA])
response_42 = bytes([0x71, 0x02, 0xFF, 0x00, 0xAA])
response_43 = bytes([0x71, 0x03, 0xFF, 0x00])

response_44 = bytes([0x59, 0x02, 0x09, 0x12, 0x34, 0x56, 0x09])
response_45 = bytes([0x59, 0x02, 0x09, 0x12, 0x34, 0x56, 0x09, 0xAA, 0xBB, 0xCC, 0x08])
response_46 = bytes([0x59, 0x02, 0x09, 0x12, 0x34, 0x56, 0x09, 0xAA, 0xBB, 0xCC])
response_47 = bytes([0x57, 0x02, 0x09, 0x12, 0x34, 0x56, 0x09, 0xAA, 0xBB, 0xCC])
response_48 = bytes([0x59, 0x01, 0x09, 0x12, 0x34, 0x56, 0x09, 0xAA, 0xBB, 0xCC])
response_49 = bytes([0x59, 0x02])
response_50 = bytes([0x59, 0x02, 0x09])

response_51 = bytes([0x54])
response_52 = bytes([])
response_53 = bytes([0x54, 0x00])
response_54 = bytes([0x55])

def test_common_response_no_response():
    test_1 = validate_common_response(request=request_1, response=response_1)
    assert not test_1.ok
    assert test_1.kind == "no_response"


def test_common_response_empty_malformed():
    test_2 = validate_common_response(request=request_1, response=response_2)
    assert not test_2.ok
    assert test_2.kind == "malformed"


def test_common_response_negative():
    test_3 = validate_common_response(request=request_1, response=response_3)
    assert not test_3.ok
    assert test_3.kind == "negative"
    assert test_3.nrc == 0x31


def test_common_response_mismatched_sid_malformed():
    test_4 = validate_common_response(request=request_1, response=response_4)
    assert not test_4.ok
    assert test_4.kind == "malformed"


def test_common_response_positive():
    test_5 = validate_common_response(request=request_1, response=response_5)
    assert test_5.ok
    assert test_5.kind == "positive"

def test_common_response_missing_nrc_malformed():
    test_6 = validate_common_response(request=request_1, response=response_6)
    assert not test_6.ok
    assert test_6.kind == "malformed"

def test_common_response_unexpected_response_malformed():
    test_7 = validate_common_response(request=request_1, response=response_7)
    assert not test_7.ok
    assert test_7.kind == "malformed"

def test_session_response_positive():
    test_8 = validate_session_response(request=request_2, response=response_8)
    assert test_8.ok
    assert test_8.kind == "positive"
    assert test_8.fields["p2_timing"] == 50
    assert test_8.fields["p2_star_timing"] == 5000


def test_session_response_malformed():
    test_9 = validate_session_response(request=request_2, response=response_9)
    assert not test_9.ok
    assert test_9.kind == "malformed"


def test_session_response_mismatched_sid_malformed():
    test_10 = validate_session_response(request=request_2, response=response_10)
    assert not test_10.ok
    assert test_10.kind == "malformed"


def test_session_response_mismatched_subfunction_malformed():
    test_11 = validate_session_response(request=request_2, response=response_11)
    assert not test_11.ok
    assert test_11.kind == "malformed"

def test_ecu_reset_response_positive():
    test_12 = validate_reset_response(request=request_3, response=response_12)
    assert test_12.ok
    assert test_12.kind == "positive"


def test_ecu_reset_response_mismatched_subfunction_malformed():
    test_13 = validate_reset_response(request=request_3, response=response_13)
    assert not test_13.ok
    assert test_13.kind == "malformed"


def test_ecu_reset_response_incorrect_length_malformed():
    test_14 = validate_reset_response(request=request_3, response=response_14)
    assert not test_14.ok
    assert test_14.kind == "malformed"

def test_read_did_response_positive():
    test_15 = validate_rdbi_response(request=request_4, response=response_15)
    assert test_15.ok
    assert test_15.kind == "positive"
    assert test_15.fields["response"] == "62 f1 86 01"


def test_read_did_response_incorrect_length_malformed():
    test_16 = validate_rdbi_response(request=request_4, response=response_16)
    assert not test_16.ok
    assert test_16.kind == "malformed"


def test_read_did_response_mismatched_sid_malformed():
    test_17 = validate_rdbi_response(request=request_4, response=response_17)
    assert not test_17.ok
    assert test_17.kind == "malformed"


def test_read_did_response_mismatched_did_malformed():
    test_18 = validate_rdbi_response(request=request_4, response=response_18)
    assert not test_18.ok
    assert test_18.kind == "malformed"

def test_write_did_response_positive():
    test_19 = validate_wdbi_response(request=request_5, response=response_19)
    assert test_19.ok
    assert test_19.kind == "positive"


def test_write_did_response_incorrect_length_malformed():
    test_20 = validate_wdbi_response(request=request_5, response=response_20)
    assert not test_20.ok
    assert test_20.kind == "malformed"


def test_write_did_response_mismatched_sid_malformed():
    test_21 = validate_wdbi_response(request=request_5, response=response_21)
    assert not test_21.ok
    assert test_21.kind == "malformed"


def test_write_did_response_mismatched_did_malformed():
    test_22 = validate_wdbi_response(request=request_5, response=response_22)
    assert not test_22.ok
    assert test_22.kind == "malformed"

def test_tester_present_response_positive():
    test_23 = validate_tester_present_response(request=request_6, response=response_23)
    assert test_23.ok
    assert test_23.kind == "positive"


def test_tester_present_response_incorrect_length_malformed():
    test_24 = validate_tester_present_response(request=request_6, response=response_24)
    assert not test_24.ok
    assert test_24.kind == "malformed"


def test_tester_present_response_mismatched_sid_malformed():
    test_25 = validate_tester_present_response(request=request_6, response=response_25)
    assert not test_25.ok
    assert test_25.kind == "malformed"


def test_tester_present_response_mismatched_subfunction_malformed():
    test_26 = validate_tester_present_response(request=request_6, response=response_26)
    assert not test_26.ok
    assert test_26.kind == "malformed"

def test_security_seed_response_positive():
    test_27 = validate_security_seed_response(request=request_7, response=response_27)
    assert test_27.ok
    assert test_27.kind == "positive"
    assert test_27.fields["seed"] == 0x1234


def test_security_seed_response_incorrect_length_malformed():
    test_28 = validate_security_seed_response(request=request_7, response=response_28)
    assert not test_28.ok
    assert test_28.kind == "malformed"


def test_security_seed_response_mismatched_sid_malformed():
    test_29 = validate_security_seed_response(request=request_7, response=response_29)
    assert not test_29.ok
    assert test_29.kind == "malformed"


def test_security_seed_response_mismatched_subfunction_malformed():
    test_30 = validate_security_seed_response(request=request_7, response=response_30)
    assert not test_30.ok
    assert test_30.kind == "malformed"

def test_routine_control_start_positive():
    test_31 = validate_routine_response(request=request_8, response=response_31)
    assert test_31.ok
    assert test_31.kind == "positive"
    assert test_31.fields["response"] == "71 01 ff 00"


def test_routine_control_stop_positive():
    test_32 = validate_routine_response(request=request_9, response=response_32)
    assert test_32.ok
    assert test_32.kind == "positive"
    assert test_32.fields["response"] == "71 02 ff 00"


def test_routine_control_results_running_positive():
    test_33 = validate_routine_response(request=request_10, response=response_33)
    assert test_33.ok
    assert test_33.kind == "positive"
    assert test_33.fields["response"] == "71 03 ff 00 00"
    assert test_33.message == "Received positive response, Status: RUNNING"


def test_routine_control_results_completed_positive():
    test_34 = validate_routine_response(request=request_10, response=response_34)
    assert test_34.ok
    assert test_34.kind == "positive"
    assert test_34.fields["response"] == "71 03 ff 00 01"
    assert test_34.message == "Received positive response, Status: COMPLETED"


def test_routine_control_mismatched_sid_malformed():
    test_35 = validate_routine_response(request=request_8, response=response_35)
    assert not test_35.ok
    assert test_35.kind == "malformed"


def test_routine_control_mismatched_subfunction_malformed():
    test_36 = validate_routine_response(request=request_8, response=response_36)
    assert not test_36.ok
    assert test_36.kind == "malformed"


def test_routine_control_mismatched_rid_malformed():
    test_37 = validate_routine_response(request=request_8, response=response_37)
    assert not test_37.ok
    assert test_37.kind == "malformed"


def test_routine_control_incorrect_length_malformed():
    test_38 = validate_routine_response(request=request_8, response=response_38)
    assert not test_38.ok
    assert test_38.kind == "malformed"


def test_routine_control_invalid_status_malformed():
    test_39 = validate_routine_response(request=request_10, response=response_39)
    assert not test_39.ok
    assert test_39.kind == "malformed"


def test_routine_control_unsupported_subfunction_malformed():
    test_40 = validate_routine_response(request=request_11, response=response_40)
    assert not test_40.ok
    assert test_40.kind == "malformed"

def test_routine_control_start_extra_bytes_malformed():
    test_41 = validate_routine_response(request=request_8, response=response_41)
    assert not test_41.ok
    assert test_41.kind == "malformed"


def test_routine_control_stop_extra_bytes_malformed():
    test_42 = validate_routine_response(request=request_9, response=response_42)
    assert not test_42.ok
    assert test_42.kind == "malformed"


def test_routine_control_results_missing_status_malformed():
    test_43 = validate_routine_response(request=request_10, response=response_43)
    assert not test_43.ok
    assert test_43.kind == "malformed"

def test_rdtci_positive_one_dtc_record_response():
    test_44 = validate_dtc_response(request=request_12, response=response_44)
    assert test_44.ok
    assert test_44.kind == "positive"
    assert test_44.fields["dtc_info"] == [
        {
            "dtc_code" : "12 34 56",
            "dtc_status" : 0x09
        }
    ]
    assert test_44.message == "Received positive response"

def test_rdtci_positive_two_dtc_record_response():
    test_45 = validate_dtc_response(request=request_12, response=response_45)
    assert test_45.ok
    assert test_45.kind == "positive"
    assert test_45.fields["dtc_info"] == [
        {
            "dtc_code" : "12 34 56",
            "dtc_status" : 0x09
        },
        {
            "dtc_code" : "aa bb cc",
            "dtc_status" : 0x08
        }
    ]

def test_rdtci_incorrect_payload_length_malformed_response():
    test_46 = validate_dtc_response(request=request_12, response=response_46)
    assert not test_46.ok
    assert test_46.kind == "malformed"

def test_rdtci_wrong_sid_malformed_response():
    test_47 = validate_dtc_response(request=request_12, response=response_47)
    assert not test_47.ok
    assert test_47.kind == "malformed"

def test_rdtci_wrong_sub_function_malformed_response():
    test_48 = validate_dtc_response(request=request_12, response=response_48)
    assert not test_48.ok
    assert test_48.kind == "malformed"

def test_rdtci_shorter_res_malformed_response():
    test_49 = validate_dtc_response(request=request_12, response=response_49)
    assert not test_49.ok
    assert test_49.kind == "malformed"

def test_rdtci_positive_zero_record_response():
    test_50 = validate_dtc_response(request=request_12, response=response_50)
    assert test_50.ok
    assert test_50.kind == "positive"
    assert test_50.fields["Availability Mask"] == 0x09
    assert test_50.fields["dtc_info"] == []

def test_clear_dtc_response_positive():
    test_51 = validate_clear_dtc_response(request=request_13, response=response_51)
    assert test_51.ok
    assert test_51.kind == "positive"


def test_clear_dtc_response_empty_malformed():
    test_52 = validate_clear_dtc_response(request=request_13, response=response_52)
    assert not test_52.ok
    assert test_52.kind == "malformed"


def test_clear_dtc_response_extra_byte_malformed():
    test_53 = validate_clear_dtc_response(request=request_13, response=response_53)
    assert not test_53.ok
    assert test_53.kind == "malformed"


def test_clear_dtc_response_mismatched_sid_malformed():
    test_54 = validate_clear_dtc_response(request=request_13, response=response_54)
    assert not test_54.ok
    assert test_54.kind == "malformed"
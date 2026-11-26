import tester


def fake_send_raw_reset_positive(bus_tester, data):
    return bytes([0x51, 0x01])

def fake_send_raw_reset_negative(bus_tester, data):
    return bytes([0x7F, 0x11, 0x12])

def fake_send_raw_reset_malformed(bus_tester, data):
    return bytes([0x52, 0x01])

def fake_send_raw_reset_wrong_sid(bus_tester, data):
    return bytes([0x7F, 0x10, 0x12])

def fake_send_raw_reset_missing_nrc(bus_tester, data):
    return bytes([0x7F, 0x11])

def fake_send_raw_reset_no_response(bus_tester, data):
    return None

def fake_send_raw_reset_empty_response(bus_tester, data):
    return bytes([])


def fake_send_raw_diagnostic_positive(bus_tester, data):
    return bytes([0x50, 0x03, 0x00, 0x32, 0x01, 0xF4])

def fake_send_raw_diagnostic_negative(bus_tester, data):
    return bytes([0x7F, 0x10, 0x12])

def fake_send_raw_diagnostic_malformed_positive(bus_tester, data):
    return bytes([0x50, 0x03, 0x00, 0x32])

def fake_send_raw_diagnostic_wrong_sid(bus_tester, data):
    return bytes([0x7F, 0x11, 0x12])


def fake_send_raw_rdbi_positive_response(bus_tester, data):
    return bytes([0x62, 0xF1, 0x86, 0x01])

def fake_send_raw_rdbi_negative_response(bus_tester, data):
    return bytes([0x7F, 0x22, 0x31])

def fake_send_raw_rdbi_malformed_response(bus_tester, data):
    return bytes([0x62, 0xF1, 0xB0, 0x01])

def fake_send_raw_wdbi_positive_response(bus_tester, data):
    return bytes([0x6E, 0xF1, 0x86])

def fake_send_raw_wdbi_negative_response(bus_tester, data):
    return bytes([0x7F, 0x2E, 0x31])

def fake_send_raw_wdbi_malformed_response(bus_tester, data):
    return bytes([0x6E, 0xF1, 0xB0])

def fake_send_raw_tester_present_positive_response(bus_tester, data):
    return bytes([0x7E, 0x00])

def fake_send_raw_tester_present_negative_response(bus_tester, data):
    return bytes([0x7F, 0x3E, 0x12])

def fake_send_raw_tester_present_malformed_response(bus_tester, data):
    return bytes([0x7E, 0x01])

def fake_send_raw_routine_control_positive_response(bus_tester, data):
    return bytes([0x71, 0x01, 0xFF, 0x00])

def fake_send_raw_routine_control_negative_response(bus_tester, data):
    return bytes([0x7F, 0x31, 0x12])

def fake_send_raw_routine_control_malformed_response(bus_tester, data):
    return bytes([0x71, 0x01, 0xFF, 0x04])

def fake_send_rdtci_positive_response(bus_tester, data):
    return bytes([0x59, 0x02, 0x09, 0x12, 0x34, 0x56, 0x01])

def fake_send_rdtci_positive_two_dtc_response(bus_tester, data):
    return bytes([0x59, 0x02, 0xFF, 0x12, 0x34, 0x56, 0x09, 0xAB, 0xCD, 0xEF, 0x08])

def fake_send_rdtci_negative_response(bus_tester, data):
    return bytes([0x7F, 0x19, 0x12])

def fake_send_rdtci_unsupported_subfunction_response(bus_tester, data):
    return bytes([0x59, 0x01, 0xFF])

def fake_send_rdtci_malformed_response(bus_tester, data):
    return bytes([0x59, 0x02, 0x09, 0x12, 0x34, 0x56])

def fake_send_raw_clear_dtc_positive_response(bus_tester, data):
    return bytes([0x54])

def fake_send_raw_clear_dtc_unexpected_response(bus_tester, data):
    return bytes([0x55])



def test_reset_positive_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_reset_positive)

    data = bytes([0x11, 0x01])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Received positive response"

def test_reset_negative_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_reset_negative)

    data = bytes([0x11, 0x01])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Received negative response for requested service. NRC: 0x12"

def test_reset_malformed_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_reset_malformed)

    data = bytes([0x11, 0x01])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "SID mismatch"

def test_reset_negative_wrong_sid(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_reset_wrong_sid)
    
    data = bytes([0x11, 0x01])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Negative response received for a different service"

def test_reset_negative_missing_nrc(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_reset_missing_nrc)
        
    data = bytes([0x11, 0x01])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Malformed negative response: missing NRC"

def test_reset_no_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_reset_no_response)
            
    data = bytes([0x11, 0x01])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "No response received from Battery ECU"

def test_reset_empty_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_reset_empty_response)
                
    data = bytes([0x11, 0x01])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Empty response received"

def test_diagnostic_positive_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_diagnostic_positive)

    data = bytes([0x10, 0x03])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert "Received positive response" in captured.out
    assert "P2_timing: 50 ms" in captured.out
    assert "P2_star_timing: 5000 ms" in captured.out

def test_diagnostic_negative_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_diagnostic_negative)

    data = bytes([0x10, 0x03])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Received negative response for requested service. NRC: 0x12"

def test_diagnostic_malformed_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_diagnostic_malformed_positive)

    data = bytes([0x10, 0x03])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Incorrect response length"

def test_diagnostic_negative_wrong_sid(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_diagnostic_wrong_sid)
    
    data = bytes([0x10, 0x03])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Negative response received for a different service"

def test_rdbi_positive_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_rdbi_positive_response)
    
    data = bytes([0x22, 0xF1, 0x86])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert "Received positive response" in captured.out
    assert "Response: 62 f1 86 01" in captured.out

def test_rdbi_negative_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_rdbi_negative_response)
    
    data = bytes([0x22, 0xF1, 0x86])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Received negative response for requested service. NRC: 0x31"

def test_rdbi_malformed_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_rdbi_malformed_response)
    
    data = bytes([0x22, 0xF1, 0x86])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Mismatch in DID"

def test_wdbi_positive_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_wdbi_positive_response)
    
    data = bytes([0x2E, 0xF1, 0x86, 0x01])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert "Received positive response" in captured.out

def test_wdbi_negative_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_wdbi_negative_response)
    
    data = bytes([0x2E, 0xF1, 0x86, 0x01])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Received negative response for requested service. NRC: 0x31"

def test_wdbi_malformed_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_wdbi_malformed_response)
    
    data = bytes([0x2E, 0xF1, 0x86, 0x01])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Mismatch in DID"

def test_tester_present_positive_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_tester_present_positive_response)
    
    data = bytes([0x3E, 0x00])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert "Received positive response" in captured.out

def test_tester_present_negative_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_tester_present_negative_response)
    
    data = bytes([0x3E, 0x00])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Received negative response for requested service. NRC: 0x12"

def test_tester_present_malformed_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_tester_present_malformed_response)
    
    data = bytes([0x3E, 0x00])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Subfunction mismatch"

def test_routine_control_positive_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_routine_control_positive_response)
    
    data = bytes([0x31, 0x01, 0xFF, 0x00])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert "Received positive response" in captured.out
    assert "71 01 ff 00" in captured.out

def test_routine_control_negative_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_routine_control_negative_response)
    
    data = bytes([0x31, 0x01, 0xFF, 0x00])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Received negative response for requested service. NRC: 0x12"

def test_routine_control_malformed_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_routine_control_malformed_response)
    
    data = bytes([0x31, 0x01, 0xFF, 0x00])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Mismatch in RID"

def test_rdtci_positive_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_rdtci_positive_response)
    
    data = bytes([0x19, 0x02, 0xFF])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert "Received positive response" in captured.out
    assert "Availability Mask: 9" in captured.out
    assert "DTC_code: 12 34 56" in captured.out
    assert "Status: 01" in captured.out

def test_rdtci_positive_two_dtc_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_rdtci_positive_two_dtc_response)
    
    data = bytes([0x19, 0x02, 0xFF])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert "Received positive response" in captured.out
    assert "Availability Mask: 255" in captured.out
    assert "DTC_code: 12 34 56" in captured.out
    assert "Status: 09" in captured.out
    assert "DTC_code: ab cd ef" in captured.out
    assert "Status: 08" in captured.out

def test_rdtci_negative_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_rdtci_negative_response)
    
    data = bytes([0x19, 0x02, 0xFF])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Received negative response for requested service. NRC: 0x12"

def test_rdtci_unsupported_subfunction_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_rdtci_unsupported_subfunction_response)
    
    data = bytes([0x19, 0x01, 0xFF])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Unsupported subfunction"

def test_rdtci_malformed_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_rdtci_malformed_response)
    
    data = bytes([0x19, 0x02, 0xFF])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Incorrect DTC response length"

def test_unlock_positive_response(monkeypatch, capsys):

    data = bytes([0x27, 0x01])
    bus_tester = None
    calls = []
    responses = [
        bytes([0x67, 0x01, 0x12, 0x34]),
        bytes([0x67, 0x02])
    ]

    def fake_send_unlock_positive_response(bus_tester, data):

        calls.append(data)
        response = responses.pop(0)

        return response

    monkeypatch.setattr(tester, "send_raw", fake_send_unlock_positive_response)
    
    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Security unlocked"
    assert len(calls) == 2
    assert calls[0] == bytes([0x27, 0x01])
    assert calls[1] == bytes([0x27, 0x02, 0xED, 0xCB])

def test_clear_dtc_positive_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_clear_dtc_positive_response)
    
    data = bytes([0x14, 0xFF, 0xFF, 0xFF])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Received positive response"

def test_clear_dtc_unexpected_response(monkeypatch, capsys):

    monkeypatch.setattr(tester, "send_raw", fake_send_raw_clear_dtc_unexpected_response)
    
    data = bytes([0x14, 0xFF, 0xFF, 0xFF])
    bus_tester = None

    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "SID mismatch"

def test_unlock_negative_seed_reject_response(monkeypatch, capsys):

    data = bytes([0x27, 0x01])
    bus_tester = None
    calls = []
    responses = [
        bytes([0x7F, 0x27, 0x35]),
    ]

    def fake_send_unlock_seed_rejected(bus_tester, data):

        calls.append(data)
        response = responses.pop(0)

        return response

    monkeypatch.setattr(tester, "send_raw", fake_send_unlock_seed_rejected)
    
    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Security unlock failed:Received negative response for requested service. NRC: 0x35"
    assert len(calls) == 1
    assert calls[0] == bytes([0x27, 0x01])

def test_unlock_negative_key_reject_response(monkeypatch, capsys):

    data = bytes([0x27, 0x01])
    bus_tester = None
    calls = []
    responses = [
        bytes([0x67, 0x01, 0x12, 0x34]),
        bytes([0x7F, 0x27, 0x35])
    ]

    def fake_send_unlock_key_rejected(bus_tester, data):

        calls.append(data)
        response = responses.pop(0)

        return response

    monkeypatch.setattr(tester, "send_raw", fake_send_unlock_key_rejected)
    
    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Security unlock failed:Received negative response for requested service. NRC: 0x35"
    assert len(calls) == 2
    assert calls[0] == bytes([0x27, 0x01])
    assert calls[1] == bytes([0x27, 0x02, 0xED, 0xCB])

def test_unlock_invalid_seed_request_response(monkeypatch, capsys):

    data = bytes([0x27, 0x01, 0xAA])
    bus_tester = None
    calls = []

    def fake_send_unlock_seed_request_rejected(bus_tester, data):

        calls.append(data)
        return

    monkeypatch.setattr(tester, "send_raw", fake_send_unlock_seed_request_rejected)
    
    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Unsupported UDS request"
    assert len(calls) == 0

def test_unlock_invalid_key_request_response(monkeypatch, capsys):

    data = bytes([0x27, 0x02, 0xAA, 0xBB])
    bus_tester = None
    calls = []

    def fake_send_unlock_key_request_rejected(bus_tester, data):

        calls.append(data)
        return

    monkeypatch.setattr(tester, "send_raw", fake_send_unlock_key_request_rejected)
    
    tester.run_tester(bus_tester=bus_tester, data=data)

    captured = capsys.readouterr()

    assert captured.out.strip() == "Unsupported UDS request"
    assert len(calls) == 0

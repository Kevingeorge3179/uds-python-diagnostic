import isotp
import time
import secrets


address = isotp.Address(
    isotp.AddressingMode.Normal_11bits,
    txid=0x708,
    rxid=0x700
)

class BatteryECU:

    def __init__(self):

        self.current_session = 0x01
        self.dispatch_table = {
            0x10: self.handle_diagnostic_session,
            0x22: self.handle_read_data_by_identifier,
            0x11: self.handle_ecu_reset,
            0x2E: self.handle_write_data_by_identifier,
            0x3E: self.handle_tester_present,
            0x27: self.handle_security_access,
            0x31: self.handle_routine_control,
            0x19: self.handle_read_dtc_information,
            0x14: self.handle_clear_diagnostic_information,
            }
        self.gate_policy = {
            0x10: {
                "sessions": [0x01, 0x03],
                "security_required": False
            },
            0x22:{
                "sessions": [0x01, 0x03],
                "security_required": False
            },
            0x11:{
                "sessions": [0x01, 0x03],
                "security_required": False
            },
            0x2E: {
                "sessions": [0x03],
                "security_required": True
            },
            0x3E:{
                "sessions": [0x01, 0x03],
                "security_required": False
            },
            0x27:{
                "sessions": [0x03],
                "security_required": False
            },
            0x31: {
                "sessions": [0x03],
                "security_required": True
            },
            0x19:{
                "sessions": [0x01, 0x03],
                "security_required": False
            },
            0x14:{
                "sessions": [0x01, 0x03],
                "security_required": False
            }
            }
        self.did_data = {
            0xF190: b"TESTVIN1234567890",
            }
        self.last_activity = time.monotonic()
        self.s3_timeout = 2.0
        self.security_seed = None
        self.security_unlocked = False
        self.routine_status = "NOT_STARTED"
        self.fault_active = False

        self.dtc_store = {}

    def relock_security(self):
        self.security_unlocked = False
        self.security_seed = None

    def reset_volatile_state(self):

        self.current_session = 0x01
        self.relock_security()
        self.routine_status = "NOT_STARTED"
        self.fault_active = False

    def monitor_faults(self):

        dtc_code = b"\x12\x34\x56"
        if self.fault_active:
            if dtc_code not in self.dtc_store:
                self.dtc_store[dtc_code] = {"confirmed" : True } 

    def check_s3_timeout(self):

        if self.current_session == 0x03:

            elapsed_time = time.monotonic() - self.last_activity

            if elapsed_time >= self.s3_timeout:

                self.current_session = 0x01
                self.relock_security()  

    def check_request_gates(self,sid):

        if self.current_session in self.gate_policy[sid]["sessions"]:

            if self.gate_policy[sid]["security_required"] and not self.security_unlocked:

                return 0x33

            else:

                return None
        else:

            return 0x7F

    def handle_diagnostic_session(self,request):

        if len(request) == 2:

            if request[0] == 0x10:

                if request[1] == 0x01:
                
                    self.current_session = 0x01
                    self.relock_security()
                    return bytes([0x50, 0x01, 0x00, 0x32, 0x01, 0xF4])
                 
                elif request[1] == 0x03:

                    self.current_session = 0x03
                    return bytes([0x50, 0x03, 0x00, 0x32, 0x01, 0xF4])                      

                else:

                    return bytes([0x7F, 0x10, 0x12])       
        
        else:

            return bytes([0x7F, 0x10, 0x13])


    def handle_read_data_by_identifier(self,request):

        if len(request) == 3:

            if request[0] == 0x22:

                DID = request[1] << 8 | request[2]

                if DID == 0xF186:
                    
                    response = bytes([0x62, DID >> 8, DID & 0xFF, self.current_session])
                    return response
                
                
                info = self.did_data.get(DID)

                if info is not None:

                    header = bytes([0x62, DID >> 8, DID & 0xFF])
                    response = header + info
                    return response

                else:

                    return bytes([0x7F, 0x22, 0x31])     
                        
        else:
            return bytes([0x7F, 0x22, 0x13]) 

    def handle_write_data_by_identifier(self,request):

        if len(request) >= 5:
        
            if request[0] == 0x2E:

                DID = request[1] << 8 | request[2]
                data = request[3:]
                
                if DID == 0xF1A0:

                    self.did_data[DID] = data                
                    response = bytes([0x6E, 0xF1, 0xA0])
                    return response

                else:
                    return bytes([0x7F, 0x2E, 0x31])

        else:
            return bytes([0x7F, 0x2E, 0x13])

    def handle_tester_present(self, request):

        if len(request) == 2:
        
            if request[0] == 0x3E:

                if request[1] == 0x00:
                
                    return bytes([0x7E, 0x00])                      

                else:

                    return bytes([0x7F, 0x3E, 0x12])       
        
        else:

            return bytes([0x7F, 0x3E, 0x13])


    def handle_ecu_reset(self,request):
        
        if len(request) == 2:
        
            if request[0] == 0x11:

                if request[1] == 0x01:

                    self.reset_volatile_state()
                    return bytes([0x51, 0x01])                      

                else:

                    return bytes([0x7F, 0x11, 0x12])       
            
        else:

            return bytes([0x7F, 0x11, 0x13])

    def handle_security_access(self,request):

        if len(request) >= 2:

            if request[0] == 0x27:

                if request[1] == 0x01:

                    if len(request) == 2:
                
                        self.security_unlocked = False
                        self.security_seed = secrets.token_bytes(2)
                        handler = bytes([0x67, 0x01])
                        response = handler + self.security_seed
                        return response

                    else:

                        return bytes([0x7F, 0x27, 0x13])

                elif request[1] == 0x02:

                    if len(request) == 4:

                        if self.security_seed is not None:
                        
                            expected_key = (self.security_seed[0] << 8 | self.security_seed[1]) ^ 0xFFFF
                            key = request[2] << 8 | request[3]

                            if expected_key == key:

                                self.security_unlocked = True
                                self.security_seed = None
                                return bytes([0x67, 0x02])  

                            else:

                                self.security_unlocked = False
                                self.security_seed = None
                                return bytes([0x7F, 0x27, 0x35]) 

                        else:

                            return bytes([0x7F, 0x27, 0x24])

                    else:

                        return bytes([0x7F, 0x27, 0x13])

                else:

                    return bytes([0x7F, 0x27, 0x12])
            
        else:
            
            return bytes([0x7F, 0x27, 0x13])


    def handle_routine_control(self, request):

        if len(request) == 4:
                
            if request[0] == 0x31:

                RID = request[2] << 8 | request[3]

                if request[1] == 0x01:

                    if RID == 0xFF00:
                        
                        if self.routine_status == "NOT_STARTED":

                            # The routine is simulated synchronously: it transitions from RUNNING to COMPLETED immediately, 
                            # rather than performing a real time-consuming operation.
                            self.routine_status = "RUNNING"
                            self.routine_status = "COMPLETED"

                            self.fault_active = True
                            return bytes([0x71, 0x01, 0xFF, 0x00])   

                        else:

                            return bytes([0x7F, 0x31, 0x24])                  

                    else:

                        return bytes([0x7F, 0x31, 0x31])

                elif request[1] == 0x02:

                    if RID == 0xFF00:

                        if self.routine_status == "RUNNING":

                            self.routine_status = "STOPPED"
                            return bytes([0x71, 0x02, 0xFF, 0x00])    

                        else:

                            return bytes([0x7F, 0x31, 0x24])                  

                    else:

                        return bytes([0x7F, 0x31, 0x31])

                elif request[1] == 0x03:

                    if RID == 0xFF00:

                        if self.routine_status == "COMPLETED":

                            return bytes([0x71, 0x03, 0xFF, 0x00, 0x01])

                        elif self.routine_status == "RUNNING":

                            return bytes([0x71, 0x03, 0xFF, 0x00, 0x00])                 

                        else:

                            return bytes([0x7F, 0x31, 0x24])

                    else:
                    
                        return bytes([0x7F, 0x31, 0x31])

                else:

                    return bytes([0x7F, 0x31, 0x12])       
            
        else:

            return bytes([0x7F, 0x31, 0x13])


    def handle_read_dtc_information(self, request):

        if len(request) == 3:
                        
            if request[0] == 0x19:

                if request[1] == 0x02:

                    response = []

                    for dtc_code, record in self.dtc_store.items():

                        test_failed = 0x01 if self.fault_active else 0x00
                        confirmed = 0x08 if record["confirmed"] else 0x00

                        status = test_failed | confirmed

                        if (status & request[2]) != 0:

                            dtc_record = dtc_code + bytes([status])
                            response.append(dtc_record)

                    return bytes([0x59, 0x02, 0x09]) + b"".join(response)

                else:
                
                    return bytes([0x7F, 0x19, 0x12])

        else:
        
            return bytes([0x7F, 0x19, 0x13])

    def handle_clear_diagnostic_information(self, request):

        if len(request) == 4:
                                
            if request[0] == 0x14:

                if request[1:] == b"\xFF\xFF\xFF":

                    self.dtc_store.clear()
                    return bytes([0x54])

                else:
                                
                    return bytes([0x7F, 0x14, 0x31])

        else:
                
            return bytes([0x7F, 0x14, 0x13])
    


       
    def run_ecu(self,bus_ecu, stop_event, inbox):

        stack = isotp.CanStack(bus=bus_ecu, address=address)

        try:
            stack.start()

            while not stop_event.is_set():
                
                payload = stack.recv(block=True, timeout=0.1)

                self.check_s3_timeout()

                if payload is not None:
                    
                    self.last_activity = time.monotonic()

                    inbox.put(payload)

                    sid = payload[0]
                    handler = self.dispatch_table.get(sid)

                    if handler is not None:

                        nrc = self.check_request_gates(sid=sid)

                        if nrc is not None:

                            data = bytes([0x7F, sid, nrc])
                            stack.send(data=data)

                        else:

                            data = handler(request=payload)
                            stack.send(data=data)

                    else:
                        data = bytes([0x7F, sid, 0x11])
                        stack.send(data=data)

                self.monitor_faults()

        finally:
            stack.stop()
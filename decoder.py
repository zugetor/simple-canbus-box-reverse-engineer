import serial

func_id_map = {
    # Response from box
    29: "RadarState (mode 0 front)",
    30: "RadarState (mode 1 back)",
    31: "OilEctricityInfo",
    32: "SWCKey",
    33: "BasicFlyInfo",
    34: "CurrentOilWear",
    35: "TravelOilInfo",
    36: "CarDoorInfo",
    37: "TPMSInfo",
    38: "CentralState",
    39: "FiftyOilWear",
    40: "ACState",
    41: "SWCAngle",
    47: "CommondKey",
    48: "CanVersion",
    49: "AMPState",
    50: "SystemInfo",
    65: "CarInfo",
    
    # Request from headunit
    192: "Media Settings",
    200: "Id3 Settings",
    130: "A/C Settings",
    144: "Data request",
}

def byte_arr_to_int(barr, offset, length, little_endian):
    if offset >= len(barr) - 1:
        return 0

    result = 0
    for i in range(length):
        val = barr[offset + i]
        if val < 0:
            val += 256  # only needed for signed bytes, usually not in Python
        shift = (i * 8) if little_endian else ((length - i - 1) * 8)
        result |= val << shift
    return result

def decode_basic_fly_info(data):
    if len(data) < 7:
        print("❌ Data too short for BasicFlyInfo")
        return

    mAverageSpeed = byte_arr_to_int(data, 0, 2, False) * 0.1
    mDriverTime1 = byte_arr_to_int(data, 2, 2, False)
    mCanDriverMileage = byte_arr_to_int(data, 4, 2, False)

    mileage_unit_byte = data[6]
    mileage_unit_map = {
        0: " ",
        1: "Mile",
        2: "Km",
    }
    mMileageUnit = mileage_unit_map.get(mileage_unit_byte, f"Unknown({mileage_unit_byte})")

    print("BasicFlyInfo decoded:")
    print(f"  Average Speed     : {mAverageSpeed} km/h")
    print(f"  Driver Time 1     : {mDriverTime1} (unit unknown)")
    print(f"  Driver Mileage    : {mCanDriverMileage} (unit unknown)")
    print(f"  Mileage Unit      : {mMileageUnit}")

def decode_car_door_info(data):
    if len(data) < 2:
        print("❌ Data too short for CarDoorInfo")
        return

    byte0 = data[0]
    byte1 = data[1]

    doorInfo = {}
    doorInfo['FrontRightDoor'] = (byte0 >> 7) & 1
    doorInfo['FrontLeftDoor'] = (byte0 >> 6) & 1
    doorInfo['BackRightDoor'] = (byte0 >> 5) & 1
    doorInfo['BackLeftDoor'] = (byte0 >> 4) & 1
    doorInfo['Trunk'] = (byte0 >> 3) & 1

    doorInfo['FrontCover'] = (byte1 >> 7) & 1
    doorInfo['SkyWindow'] = (byte1 >> 5) & 3  # 2 bits: values 0-3

    print("Car Door Info decoded:")
    for k, v in doorInfo.items():
        print(f"  {k}: {v}")
        
def get_left_and_right_temp(i, b):
    if b != 0:
        # Fahrenheit mode
        if i == 0:
            return "Low"
        elif i == 255:
            return "High"
        else:
            return f"{i}℉"
    else:
        # Celsius mode
        if i > 31:
            return f"{i * 2.0}℃"
        elif i == 0:
            return "Low"
        elif i == 31:
            return "High"
        else:
            return f"{(i / 2.0) + 17.5}℃"

def decode_ac_state(data):
    if len(data) < 8:
        print("❌ Data too short for AC State")
        return

    b0 = data[0]
    b1 = data[1]
    b2 = data[2]
    b3 = data[3]
    b4 = data[4]
    b5 = data[5]
    b6 = data[6]
    b7 = data[7]

    ac_state = {}

    # Byte 0 bits
    ac_state['ACSwitch'] = ((b0 >> 7) & 1) == 1
    ac_state['ACMode'] = ((b0 >> 6) & 1) == 1
    ac_state['InsideOrOutsideRoot'] = ((b0 >> 5) & 1) == 1
    ac_state['Auto'] = ((b0 >> 3) & 1) == 1
    ac_state['Dual'] = ((b0 >> 2) & 1) == 1
    ac_state['MaxAc'] = ((b0 >> 1) & 1) == 1
    ac_state['AutoDefog'] = (b0 & 1) == 1

    # Byte 1 bits
    ac_state['AirMode_Up'] = ((b1 >> 7) & 1) == 1
    ac_state['AirMode_Parallel'] = ((b1 >> 6) & 1) == 1
    ac_state['AirMode_Down'] = ((b1 >> 5) & 1) == 1
    ac_state['AirSpeedLevel'] = b1 & 0x0F

    # Byte 4 bits
    ac_state['FrontWindowDefog'] = ((b4 >> 7) & 1) == 1
    ac_state['BackWindowDefog'] = ((b4 >> 6) & 1) == 1
    ac_state['ECONMode'] = ((b4 >> 4) & 1) == 1

    # Byte 5 bits
    ac_state['LeftSeatHeat'] = b5 & 0x03
    ac_state['RightSeatHeat'] = (b5 >> 2) & 0x03

    # Byte 7 bits
    ac_state['BackAirState'] = ((b7 >> 7) & 1) == 1
    ac_state['BackAirMode_Parallel'] = ((b7 >> 6) & 1) == 1
    ac_state['BackAirMode_Down'] = ((b7 >> 5) & 1) == 1
    ac_state['BackAirMode_Auto'] = ((b7 >> 4) & 1) == 1
    ac_state['BackAirSpeedLevel'] = b7 & 0x0F

    # Temperature bytes with sign bit from bit 6 of byte 4
    sign_bit = (b4 >> 6) & 1
    ac_state['LeftSideTemperature'] = get_left_and_right_temp(b2, sign_bit)
    ac_state['RightSideTemperature'] = get_left_and_right_temp(b3, sign_bit)
    ac_state['BackSideTemperature'] = get_left_and_right_temp(b6, sign_bit)

    # Print result
    print("AC State decoded:")
    for k, v in ac_state.items():
        print(f"  {k}: {v}")
        
def get_tpms_value(raw_val, scale):
    if raw_val == 0 or raw_val == 255:
        return -1.0
    return raw_val * scale

def decode_tpms_info(data):
    if len(data) < 6:
        print("❌ Data too short for TPMSInfo")
        return

    first_byte = data[0]
    unit_bits = first_byte & 3
    unit = 0
    if unit_bits != 0 :
        if unit_bits == 1:
            unit = 1
            
        elif unit_bits == 2:
            unit = 0
            scale = 2.5
        scale = 1
    else:
        unit = 2
        scale = 0.1

    alarm_active = ((first_byte >> 6) & 1) == 1

    tpms_info = {
        "Unit": unit,
        "FrontLeftWheelPressureAlarm": 3 if alarm_active else 0,
        "FrontRightWheelPressureAlarm": 3 if alarm_active else 0,
        "BackLeftWheelPressureAlarm": 3 if alarm_active else 0,
        "BackRightWheelPressureAlarm": 3 if alarm_active else 0,
        "FrontLeftWheelPressure": get_tpms_value(data[1], scale),
        "FrontRightWheelPressure": get_tpms_value(data[2], scale),
        "BackLeftWheelPressure": get_tpms_value(data[3], scale),
        "BackRightWheelPressure": get_tpms_value(data[4], scale),
        "PrepareWheelPressure": get_tpms_value(data[5], scale),
    }

    print("TPMS Info decoded:")
    for k, v in tpms_info.items():
        print(f"  {k}: {v}")

def decode_travel_oil_info(data):
    if len(data) < 13:
        print("❌ Data too short for TravelOilInfo")
        return

    unit_map = {
        0: ("MPG", 60),
        1: ("Km/h", 30),
        2: ("L/100km", 30),
        16: ("mile/kWh", None),
        17: ("kWh/100mile", None),
        18: ("km/kWh", None),
        19: ("kWh/100km", None),
    }

    unit_code = data[0]
    unit_str, range_minutes = unit_map.get(unit_code, ("Unknown", None))

    oil_data = {
        "Unit": unit_str,
        "RangeOfMinuteOilConsumption": range_minutes,
        "CurrentOilConsumption": byte_arr_to_int(data, 1, 2, False) * 0.1,
        "AverageOilConsumption1": byte_arr_to_int(data, 3, 2, False) * 0.1,
        "AverageOilConsumption2": byte_arr_to_int(data, 5, 2, False) * 0.1,
        "AverageOilConsumption3": byte_arr_to_int(data, 7, 2, False) * 0.1,
        "AverageOilConsumption4": byte_arr_to_int(data, 9, 2, False) * 0.1,
        "AverageOilConsumption5": byte_arr_to_int(data, 11, 2, False) * 0.1,
    }

    print("Travel Oil Info decoded:")
    for k, v in oil_data.items():
        print(f"  {k}: {v}")

def decode_swc_angle(data):
    if len(data) < 2:
        print("❌ Data too short for SWCAngle")
        return

    lsb = data[0] & 0xFF
    msb = (data[1] & 0xFF) * 256
    value = lsb + msb

    is_negative = ((msb >> 3) & 1) == 1

    if is_negative:
        angle = (value ^ 0xFFF) + 1
    else:
        angle = -value

    print(f"SWC Angle: {angle}° (range ±380°)")
    return angle

def get_radar_level(b):
    return {
        1: 1,
        2: 4,
        3: 7,
        4: 10
    }.get(b, 0)


def decode_radar_state(data, is_rear=False):
    if len(data) < (5 if is_rear else 4):
        print("❌ Data too short for RadarState")
        return

    radar_state = {}

    if not is_rear:
        radar_state["FrontLeft"] = get_radar_level(data[0])
        radar_state["FrontLeftCenter"] = get_radar_level(data[1])
        radar_state["FrontRightCenter"] = get_radar_level(data[2])
        radar_state["FrontRight"] = get_radar_level(data[3])
    else:
        radar_state["BackLeft"] = get_radar_level(data[0])
        radar_state["BackLeftCenter"] = get_radar_level(data[1])
        radar_state["BackRightCenter"] = get_radar_level(data[2])
        radar_state["BackRight"] = get_radar_level(data[3])

        # CentralState decoding (only in rear radar packet)
        byte4 = data[4]
        central_state = {
            "BackRadarSwitch": (byte4 >> 7) & 0x01,
            "CentreSensorSensitivity": (byte4 >> 6) & 0x01,
            "RadarAlarmVolumeSwitch": (byte4 >> 4) & 0x01,
            "BackVolumeLevel": byte4 & 0x07,
        }

        print("CentralState:")
        for k, v in central_state.items():
            print(f"  {k}: {v}")

    print("RadarState:")
    for k, v in radar_state.items():
        print(f"  {k}: Level {v}")
        
def decode_oil_electricity_info(data):
    if len(data) < 2:
        print("❌ Data too short for OilElectricityInfo")
        return

    byte0 = data[0]
    byte1 = data[1]

    eCUInfo = {
        "BatteryCapacity": byte0 & 0b00000111,  # last 3 bits
        "OilElectricMixMotorcycle": (byte0 >> 7) & 0x01,

        "MotoDriveBattery": (byte1 >> 0) & 0x01,
        "MotoDriveWheel": (byte1 >> 1) & 0x01,
        "EngineDriveMoto": (byte1 >> 2) & 0x01,
        "EngineDriveWheel": (byte1 >> 3) & 0x01,
        "BatteryDriveMoto": (byte1 >> 4) & 0x01,
        "WheelDriveMoto": (byte1 >> 5) & 0x01,
    }

    print("OilElectricityInfo decoded:")
    for key, value in eCUInfo.items():
        print(f"  {key}: {value}")
    
    return eCUInfo

def decode_car_info(data):
    if len(data) < 7:
        print("❌ Data too short for CarInfo (mode 1)")
        return

    mode = data[0]
    print(f"CarInfo Mode: {mode}")

    if mode == 1:
        car_info = {
            "Handbrake":      (data[2] >> 4) & 1,
            "DippedHeadlight":(data[4] >> 7) & 1,
            "HighBeam":       (data[4] >> 6) & 1,
            "LampWidthLight": (data[4] >> 5) & 1,
            "BackLight":      (data[5] >> 7) & 1,
            "BrakeLight":     (data[5] >> 6) & 1,
            "RightTurnSignal":(data[5] >> 5) & 1,
            "LeftTurnSignal": (data[5] >> 4) & 1,
            "CautionLight":   (data[5] >> 3) & 1,
            "AfterFogLamps":  (data[5] >> 2) & 1,
            "BeforeFogLamps": (data[5] >> 1) & 1,
            "BackDoorLock":   (data[6] >> 2) & 0b11,
            "FrontRightDoorLock": (data[6] >> 1) & 1,
            "FrontLeftDoorLock": data[6] & 1,
        }

        print("CarInfo (Mode 1) decoded:")
        for k, v in car_info.items():
            print(f"  {k}: {v}")

    elif mode == 2:
        if len(data) < 16:
            print("❌ Data too short for CarInfo (mode 2)")
            return

        car_info = {
            "DrivingMile":         byte_arr_to_int(data, 1, 3, False),
            "CanDriverMileage":    byte_arr_to_int(data, 4, 2, False),
            "TRIPAMile":           byte_arr_to_int(data, 6, 3, False) * 0.1,
            "TRIPBMile":           byte_arr_to_int(data, 9, 3, False) * 0.1,
            "InstantanSpeed":      int(byte_arr_to_int(data, 12, 2, False) * 0.01),
            "EquallySpeed":        int(byte_arr_to_int(data, 14, 2, False) * 0.1),
        }

        print("CarInfo (Mode 2) decoded:")
        for k, v in car_info.items():
            print(f"  {k}: {v}")

    elif mode == 3:
        if len(data) < 8:
            print("❌ Data too short for CarInfo (mode 3)")
            return

        car_info = {
            "EngineSpeed": byte_arr_to_int(data, 1, 2, False),
            "OutsideTemp": f"{data[7]}℃",
        }

        print("CarInfo (Mode 3) decoded:")
        for k, v in car_info.items():
            print(f"  {k}: {v}")

    else:
        print(f"❌ Unknown CarInfo mode: {mode}")

def decode_data_request(data):
    if len(data) < 2:
        print("❌ Data too short for data request")
        return

    byte0 = data[0]
    byte1 = data[1]

    print("Date request decoded:")
    if byte0 == 37 :
        print("request tpms info")
    if byte0 == 38 :
        print("request central state")
    if byte0 == 40 :
        print("request A/C state")
    if byte0 == 49 :
        print("request amp state")
    if byte0 == 33 :
        print("request basic fly info")
    if byte0 == 35 :
        print("request travel oil info")
    if byte0 == 39 :
        print("request fifty oil wear")

def decode_ac_setting(data):
    if len(data) < 2:
        print("❌ Data too short for A/C Setting")
        return

    byte0 = data[0]
    byte1 = data[1]

    print("A/C setting decoded:")
    if byte0 == 1 :
        print("ON/OFF")
    if byte0 == 2 :
        print("Temp down")
    if byte0 == 3 :
        print("Temp up")
    if byte0 == 9 :
        print("fan down")
    if byte0 == 10 :
        print("fan up")
    if byte0 == 19 :
        print("windshield defog")
    if byte0 == 20 :
        print("rear defog")
    if byte0 == 21:
        print("auto mode")
    if byte0 == 25 :
        print("mode")

last_package = ""
def decode_packet(packet):
    try:
        global last_package
        packet = [int(x, 16) for x in packet]
        
        func_id = packet[1]
        func_name = func_id_map.get(func_id, "Unknown Function ID")
        if func_name == last_package:
            return
        last_package = func_name
        data_len = int(packet[2])

        data = packet[3:3 + data_len]
        checksum = packet[-1]
        
        checksum_calc = (sum(packet[1:-1])&0xFF) ^ 0xFF

        print(f"Decoded Packet:")
        print(f"  Start       : 0x{packet[0]:02X}")
        print(f"  Function ID : 0x{func_id:02X} {func_name}")
        print(f"  Data Length : {data_len}")
        print(f"  Data        : {' '.join(f'0x{b:02X}' for b in data)}")
        print(f"  Checksum    : 0x{checksum:02X} {checksum == checksum_calc}")
        print()
        
        if func_id == 29:
            decode_radar_state(data, False)
        if func_id == 30:
            decode_radar_state(data, True)
        if func_id == 31:
            decode_oil_electricity_info(data)
        if func_id == 33:
            decode_basic_fly_info(data)
        if func_id == 35:
            decode_travel_oil_info(data)
        if func_id == 36:
            decode_car_door_info(data)
        if func_id == 37:
            decode_tpms_info(data)
        if func_id == 40:
            decode_ac_state(data)
        if func_id == 41:
            decode_swc_angle(data)
        if func_id == 130:
            decode_ac_setting(data)
        if func_id == 65:
            decode_car_info(data)
        print()
    except Exception:
        print(packet)

# Open COM7 at 38400 baudrate
ser = serial.Serial('COM4', 38400, timeout=1)

try:
    buffer = []
    while True:
        byte = ser.read(1)
        if not byte:
            continue

        val = ord(byte)
        #print(val)
        if val == 0x2E:
            if buffer:
                decode_packet(buffer)
            buffer = [f"0x{val:02x}"]  # start new packet with this 0x2E
        else:
            buffer.append(f"0x{val:02x}")

except KeyboardInterrupt:
    print("Stopped by user.")
finally:
    ser.close()

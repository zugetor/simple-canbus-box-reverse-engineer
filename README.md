# 📊 CAN Function ID & Data Structure Reference

This document outlines the CAN function IDs and the structure of their associated data payloads.

---

## 🔢 Function ID Map

| ID (Dec) | ID (Hex) | Direction       | Function Name           |
|----------|----------|------------------|--------------------------|
| 29       | `0x1D`   | Response         | RadarState (Front)       |
| 30       | `0x1E`   | Response         | RadarState (Back)        |
| 31       | `0x1F`   | Response         | OilElectricityInfo       |
| 32       | `0x20`   | Response         | SWCKey                   |
| 33       | `0x21`   | Response         | BasicFlyInfo             |
| 34       | `0x22`   | Response         | CurrentOilWear           |
| 35       | `0x23`   | Response         | TravelOilInfo            |
| 36       | `0x24`   | Response         | CarDoorInfo              |
| 37       | `0x25`   | Response         | TPMSInfo                 |
| 38       | `0x26`   | Response         | CentralState             |
| 39       | `0x27`   | Response         | FiftyOilWear             |
| 40       | `0x28`   | Response         | ACState                  |
| 41       | `0x29`   | Response         | SWCAngle                 |
| 47       | `0x2F`   | Response         | CommondKey               |
| 48       | `0x30`   | Response         | CanVersion               |
| 49       | `0x31`   | Response         | AMPState                 |
| 50       | `0x32`   | Response         | SystemInfo               |
| 130      | `0x82`   | Request (HU → Box)| A/C Settings             |
| 144      | `0x90`   | Request (HU → Box)| Data Request             |
| 192      | `0xC0`   | Request (HU → Box)| Media Settings           |
| 200      | `0xC8`   | Request (HU → Box)| ID3 Settings             |

---

## 📐 Data Structures by Function ID

### 🛞 `0x1F` – OilElectricityInfo

| Byte | Field                         | Description                        |
|------|-------------------------------|------------------------------------|
| 0    | BatteryCapacity (bits 0–2)    | Battery level                      |
| 0    | OilElectricMixMotorcycle (bit 7)| Hybrid mode flag                  |
| 1    | MotoDriveBattery (bit 0)      | Battery driving motor              |
| 1    | MotoDriveWheel (bit 1)        | Motor drives wheels                |
| 1    | EngineDriveMoto (bit 2)       | Engine drives motor                |
| 1    | EngineDriveWheel (bit 3)      | Engine drives wheels               |
| 1    | BatteryDriveMoto (bit 4)      | Battery to motor path              |
| 1    | WheelDriveMoto (bit 5)        | Wheel-to-motor regen               |

---

### 🚘 `0x21` – BasicFlyInfo

| Byte Range | Field             | Description                   |
|------------|------------------|-------------------------------|
| 0–1        | AverageSpeed      | (×0.1) km/h                   |
| 2–3        | DriverTime1       | Minutes? (unit unspecified)   |
| 4–5        | DriverMileage     | Integer value                 |
| 6          | MileageUnit       | 0=blank, 1=Mile, 2=Km         |

---

### ⛽ `0x23` – TravelOilInfo

| Byte Range | Field                     | Description                |
|------------|--------------------------|----------------------------|
| 0          | Unit Code                | e.g. 2 = L/100km           |
| 1–2        | CurrentOilConsumption    | (×0.1)                     |
| 3–4        | AvgOilConsumption1       | (×0.1)                     |
| 5–6        | AvgOilConsumption2       | (×0.1)                     |
| 7–8        | AvgOilConsumption3       | (×0.1)                     |
| 9–10       | AvgOilConsumption4       | (×0.1)                     |
| 11–12      | AvgOilConsumption5       | (×0.1)                     |

---

### 🚪 `0x24` – CarDoorInfo

| Byte | Field           | Description           |
|------|----------------|-----------------------|
| 0    | FrontRightDoor | Bit 7                 |
| 0    | FrontLeftDoor  | Bit 6                 |
| 0    | BackRightDoor  | Bit 5                 |
| 0    | BackLeftDoor   | Bit 4                 |
| 0    | Trunk          | Bit 3                 |
| 1    | FrontCover     | Bit 7                 |
| 1    | SkyWindow      | Bits 5–6              |

---

### 🌡️ `0x28` – ACState

| Byte | Field                     | Description                      |
|------|--------------------------|----------------------------------|
| 0    | ACSwitch, ACMode, etc.   | Bits 7–0 various states          |
| 1    | AirMode & FanSpeed       | Bits 7–5 mode, bits 3–0 speed    |
| 2    | LeftTempRaw              | Raw temp byte                    |
| 3    | RightTempRaw             | Raw temp byte                    |
| 4    | Defog flags              | Bits 7,6 = front/back defog      |
| 5    | Left/Right Seat Heat     | Bits 1–0, 3–2                    |
| 6    | BackTempRaw              | Raw temp byte                    |
| 7    | BackAir states           | Bits 7–4 = auto/mode/speed       |

---

### 🔧 `0x25` – TPMSInfo

| Byte | Field                         | Description            |
|------|-------------------------------|------------------------|
| 0    | Unit & Alarm flags            | Unit in bits 0–1       |
| 1–5  | Wheel Pressures               | FL, FR, BL, BR, Spare  |

---

### 📡 `0x1D` / `0x1E` – RadarState

#### Front (`0x1D`):
| Byte | Position          | Level Mapping |
|------|-------------------|----------------|
| 0    | FrontLeft         | 1–4 mapped to 1–10 |
| 1    | FrontLeftCenter   |                |
| 2    | FrontRightCenter  |                |
| 3    | FrontRight        |                |

#### Rear (`0x1E`):
| Byte | Position          | Level Mapping |
|------|-------------------|----------------|
| 0    | BackLeft          | 1–4 mapped to 1–10 |
| 1    | BackLeftCenter    |                |
| 2    | BackRightCenter   |                |
| 3    | BackRight         |                |
| 4    | CentralState      | See below      |

**CentralState Fields (Byte 4):**
| Bit | Field                    |
|-----|--------------------------|
| 7   | BackRadarSwitch          |
| 6   | CentreSensorSensitivity  |
| 4   | RadarAlarmVolumeSwitch   |
| 2–0 | BackVolumeLevel (0–7)    |

---

### 🔄 `0x29` – SWCAngle

| Byte | Description                      |
|------|----------------------------------|
| 0–1  | 12-bit value with sign in MSB    |
|      | Range: ±380 degrees              |

---

### ❄️ `0x82` – A/C Settings (Command)

| Byte 0 | Action                 |
|--------|------------------------|
| 1      | ON/OFF Toggle          |
| 2      | Temp Down              |
| 3      | Temp Up                |
| 9      | Fan Speed Down         |
| 10     | Fan Speed Up           |
| 19     | Windshield Defog       |
| 20     | Rear Defog             |
| 21     | Auto Mode              |
| 25     | Mode Change            |

---

### 📥 `0x90` – Data Request

| Byte 0 | Request Item           |
|--------|------------------------|
| 33     | BasicFlyInfo           |
| 35     | TravelOilInfo          |
| 37     | TPMSInfo               |
| 38     | CentralState           |
| 39     | FiftyOilWear           |
| 40     | ACState                |
| 49     | AMPState               |

---

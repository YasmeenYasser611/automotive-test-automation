from time import sleep


class ECUCommunicationError(Exception):
    """Raised when ECU communication fails."""


class AutomotiveLibrary:
    ROBOT_LIBRARY_SCOPE = "SUITE"

    def __init__(self):
        self.voltage = 12.0
        self.failures_left = 0
        self.last_frame = None

    def set_supply_voltage(self, voltage):
        voltage = float(voltage)
        if voltage < 5.0 or voltage > 18.0:
            raise ValueError(
                f"Supply voltage {voltage}V is outside allowed range 5.0V-18.0V"
            )
        self.voltage = voltage


    def ecu_model_reacts_to(self, volts):
        """Stand-in for the real ECU voltage behaviour on a test bench."""
        volts = float(volts)

        if volts < 5.0 or volts > 18.0:
            raise ValueError(
                f"UNSAFE: {volts:g} V is outside the 5-18 V safe range. Not applied."
            )

        if volts < 9.0:
            return "UNDERVOLTAGE"
        if volts <= 14.0:
            return "NORMAL"
        return "OVERVOLTAGE"

    def voltage_should_be_in_range(self, minimum, maximum):
        minimum = float(minimum)
        maximum = float(maximum)
        if not minimum <= self.voltage <= maximum:
            raise AssertionError(
                f"Voltage {self.voltage}V is outside expected range {minimum}V-{maximum}V"
            )

    def validate_can_frame(self, can_id, dlc, *data):
        can_id = int(str(can_id), 0)
        dlc = int(dlc)
        data = [int(str(byte), 0) for byte in data]

        if not 0 <= can_id <= 0x7FF:
            raise AssertionError(f"Invalid CAN ID: {hex(can_id)}")
        if not 0 <= dlc <= 8:
            raise AssertionError(f"DLC must be 0-8, got {dlc}")
        if len(data) != dlc:
            raise AssertionError(f"DLC is {dlc} but got {len(data)} data bytes")

        for byte in data:
            if not 0 <= byte <= 0xFF:
                raise AssertionError(f"CAN data byte out of range: {byte}")

        self.last_frame = {"id": can_id, "dlc": dlc, "data": data}

    def can_overvoltage_flag_should_be(self, expected):
        self._can_flag_should_be(expected, 0x02, "overvoltage")

    def can_undervoltage_flag_should_be(self, expected):
        self._can_flag_should_be(expected, 0x10, "undervoltage")

    def _can_flag_should_be(self, expected, mask, name):
        if self.last_frame is None:
            raise AssertionError("No CAN frame has been received")
        if self.last_frame["dlc"] < 4:
            raise AssertionError("CAN frame does not contain byte 4")

        byte4 = self.last_frame["data"][3]
        actual = (byte4 & mask) != 0
        expected = str(expected).lower() in ("true", "1", "yes", "on")

        if actual != expected:
            raise AssertionError(f"{name} flag expected {expected}, got {actual}")

    def configure_ecu_failures(self, count):
        self.failures_left = int(count)

    def get_device_status(self):
        try:
            if self.failures_left > 0:
                self.failures_left -= 1
                raise ConnectionError("ECU communication failed")
            return "OK"
        except ConnectionError as error:
            raise ECUCommunicationError(
                f"Failed to communicate with ECU: {error}"
            ) from error

    def get_device_status_with_retry(self, attempts, delay):
        attempts = int(attempts)
        delay = float(delay)

        if attempts <= 0:
            raise ValueError("attempts must be greater than zero")

        last_error = None

        for attempt in range(attempts):
            try:
                return self.get_device_status()
            except ECUCommunicationError as error:
                last_error = error
                if attempt < attempts - 1:
                    print(f"Retrying in {delay:g}s...")
                    sleep(delay)

        raise last_error
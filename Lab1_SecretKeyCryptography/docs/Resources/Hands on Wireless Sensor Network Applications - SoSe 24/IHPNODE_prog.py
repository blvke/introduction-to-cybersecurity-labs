import binascii
import functools
import struct
import sys
import time
import serial
import logging


BSL_RX_DATA_BLOCK = 0x10    # Write to boot loader
BSL_RX_DATA_BLOCK_FAST = 0x1b    # Write to boot loader
BSL_RX_PASSWORD = 0x11    # Receive password to unlock commands
BSL_ERASE_SEGMENT = 0x12    # Erase one segment
BSL_LOCK_INFO = 0x13    # Toggle INFO_A lock bit
BSL_MASS_ERASE = 0x15    # Erase complete FLASH memory
BSL_CRC_CHECK = 0x16    # Run 16 bit CRC check over given area
BSL_LOAD_PC = 0x17    # Load PC and start execution
BSL_TX_DATA_BLOCK = 0x18    # Read from boot loader
BSL_VERSION = 0x19    # Get BSL version
BSL_BUFFER_SIZE = 0x1a    # Get BSL buffer size

BSL_GET_VERSION = 0x80
# Adres komendy do zmiany prędkości transmisji
BSL_CHANGE_BAUD_RATE = 0x52
BSL5_ACK = 0x00

# Baudrate dla komunikacji z MSP430
BSL_BAUD_RATE_D1 = {
    9600: 0x02,
    19200: 0x03,
    38400: 0x04,
    57600: 0x05,
    115200: 0x06,
}

def three_bytes(address):
    """Convert a 24-bit address to a bytes string with 3 bytes"""
    return bytes([(address & 0xff), ((address >> 8) & 0xff), ((address >> 16) & 0xff)])
#
def crc_update(crc, byte):
    x = ((crc >> 8) ^ byte) & 0xFF
    x ^= x >> 4
    return ((crc << 8) ^ (x << 12) ^ (x << 5) ^ x) & 0xFFFF

# Klasa obsługująca BSL5
class BSL5:
    def __init__(self):
        self.logger = logging.getLogger('BSL')
        self.start_time = None
        self.data_size =0
        print("Preparing device ...")

    def start_timer(self):
        self.start_time = time.time()

    # Metoda kończąca timer i zwracająca czas działania
    def stop_timer(self):
        end_time = time.time()
        elapsed_time = end_time - self.start_time
        return elapsed_time

    def open(self, port, baudrate=9600):
        self.serial = serial.Serial(
            port,
            baudrate=baudrate,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE,
            timeout=5,)
        self.telosI2CWriteCmd(0, 0)
        time.sleep(0.05)
        self.serial.flushInput()
        self.serial.flushOutput()

    def close(self):
        """Closes the used serial port.
        This function must be called at the end of a program,
        otherwise the serial port might not be released and can not be
        used in other programs.
        Returns zero if the function is successful."""
        print(self.data_size,"bytes programmed")
        print("Reset device ...")
        self.telosI2CWriteCmd(0,0)
        time.sleep(0.05)
        self.bslReset(0)
        self.serial.close()

    def __del__(self):
        if self.serial.is_open:
            self.serial.close()


    def telosSetSCL(self, level):
        self.serial.setRTS(not level)

    def telosSetSDA(self, level):
        self.serial.setDTR(not level)

    def telosI2CStart(self):
        self.telosSetSDA(1)
        self.telosSetSCL(1)
        self.telosSetSDA(0)

    def telosI2CStop(self):
        self.telosSetSDA(0)
        self.telosSetSCL(1)
        self.telosSetSDA(1)

    def telosI2CWriteBit(self, bit):
        self.telosSetSCL(0)
        self.telosSetSDA(bit)
        time.sleep(2e-6)
        self.telosSetSCL(1)
        time.sleep(1e-6)
        self.telosSetSCL(0)

    def telosI2CWriteByte(self, byte):
        self.telosI2CWriteBit(byte & 0x80);
        self.telosI2CWriteBit(byte & 0x40);
        self.telosI2CWriteBit(byte & 0x20);
        self.telosI2CWriteBit(byte & 0x10);
        self.telosI2CWriteBit(byte & 0x08);
        self.telosI2CWriteBit(byte & 0x04);
        self.telosI2CWriteBit(byte & 0x02);
        self.telosI2CWriteBit(byte & 0x01);
        self.telosI2CWriteBit(0);  # "acknowledge"

    def telosI2CWriteCmd(self, addr, cmdbyte):
        self.telosI2CStart()
        self.telosI2CWriteByte(0x90 | (addr << 1))
        self.telosI2CWriteByte(cmdbyte)
        self.telosI2CStop()
        time.sleep(0.020)

    def bslReset(self, invokeBSL=0):


        if invokeBSL:

            self.telosI2CWriteCmd(0, 1)
            time.sleep(0.05)
            self.telosI2CWriteCmd(0, 3)
            time.sleep(0.05)
            self.telosI2CWriteCmd(0, 1)
            time.sleep(0.05)
            self.telosI2CWriteCmd(0, 3)
            time.sleep(0.05)
            self.telosI2CWriteCmd(0, 2)
            time.sleep(0.05)
            self.telosI2CWriteCmd(0, 0)
            time.sleep(0.05)
        else:
            self.telosI2CWriteCmd(0, 0)
            self.telosI2CWriteCmd(0, 1)
            self.telosI2CWriteCmd(0, 0)
        time.sleep(0.250)  # give MSP430's oscillator time to stabilize
        self.serial.flushInput()  # clear buffers
        self.serial.flushOutput()  # clear buffers

    def __del__(self):
        if self.serial.is_open:
            self.serial.close()

    def calcChecksum(self,data, length):
        """Calculates a checksum of "data"."""
        checksum = 0xffff

        for i in range(length):
            x = ((checksum >> 8) ^ (ord(data[i]))) & 0xff
            x = x ^ (x >> 4)
            checksum = (checksum << 8) ^ (x << 12) ^ (x << 5) ^ x
        return 0xffff & checksum

    def bsl(self, cmd, message=b''):
        """\
        Low level access to the serial communication.

        This function sends a command and waits until it receives an answer
        (including timeouts). It will return a string with the data part of
        the answer. In case of a failure read timeout or rejected commands by
        the slave, it will raise an exception.

        If the parameter "expect" is not None, "expect" bytes are expected in
        the answer, an exception is raised if the answer length does not match.
        If "expect" is None, the answer is just returned.

        Frame format:
        +-----+----+----+-----------+----+----+
        | HDR | LL | LH | D1 ... DN | CL | CH |
        +-----+----+----+-----------+----+----+
        """
        header = struct.pack('<BH', 0x80, 1+len(message))
        command =  struct.pack('<B', cmd)
        checksum_data = command + message
        byte_list = [bytes([byte]) for byte in checksum_data]
        checksum = self.calcChecksum(byte_list,len(byte_list))
        txdata = header + command + message + struct.pack('<BB', checksum & 0xFF, (checksum >> 8) & 0xFF)
        #print(txdata)

        self.serial.write(txdata)
        if self.serial.baudrate == 9600:
            time.sleep(0.1)
        elif self.serial.baudrate == 115200:
            time.sleep(0.0001)

    def BSL_MASS_ERASE(self):
        print("Mass Erase...")
        self.bsl(BSL_MASS_ERASE)
        print("Mass Erase complete")

    def BSL_RX_PASSWORD(self, password):
        self.bsl(BSL_RX_PASSWORD, password)
        print("Transmit default password ...")

    def BSL_RX_DATA_BLOCK(self, address, data):
        packet = three_bytes(address) + data
        self.bsl(BSL_RX_DATA_BLOCK, packet)
        self.data_size += len(data)
        print("Sending data", hex(address), len(data), "bytes")

    def BSL_CHANGE_BAUD_RATE(self, multiply):
        packet = struct.pack('<B', multiply)
        self.bsl(BSL_CHANGE_BAUD_RATE, packet)


    def parse_ti_txt(self,filename):
        segments = []
        with open(filename, 'r') as file:
            current_address = None
            current_data = []

            for line in file:
                if line.startswith('@'):
                    if current_address is not None:
                        segments.append((current_address, bytes(current_data)))
                        current_data = []

                    current_address = int(line[1:], 16)
                elif line.strip() == 'q':
                    break
                else:
                    current_data.extend(int(byte, 16) for byte in line.split())

            if current_address is not None and current_data:
                segments.append((current_address, bytes(current_data)))

        return segments

    def program_ti_txt(self, filename, block_size=250):
        segments = self.parse_ti_txt(filename)
        total_bytes = sum(len(data) for _, data in segments)
        sent_bytes = 0
        for address, data in segments:
            for offset in range(0, len(data), block_size):
                block_data = data[offset:offset + block_size]
                self.BSL_RX_DATA_BLOCK(address + offset, block_data)
                sent_bytes += len(block_data)

                time.sleep(0.1)

    def set_baudrate(self, baudrate):
        print(f'Changing baud rate to {baudrate}')
        try:
            multiply = BSL_BAUD_RATE_D1[baudrate]
        except KeyError:
            raise ValueError(f'Unsupported baud rate {baudrate}')
        else:
            self.BSL_CHANGE_BAUD_RATE(multiply)
            time.sleep(0.010)
            self.serial.baudrate = baudrate

# def testmain():
#     bsl_target = BSL5()
#     # bsl_target.start_timer()
#     bsl_target.open(port='COM9', baudrate=9600)
#
#     bsl_target.bslReset(1)
#     # bsl_target.BSL_RX_PASSWORD(b"\xff" * 32)
#     bsl_target.BSL_MASS_ERASE()
#     bsl_target.BSL_RX_PASSWORD(b"\xff" * 32)
#
#     new_baudrate = 115200
#     bsl_target.set_baudrate(new_baudrate)
#
#     bsl_target.program_ti_txt("IHPOSv3_SA.txt")
#
#     # #bsl_target.program_hex("IHPOSv3_SA.hex")
#     # #sys.stderr.flush()
#     # bsl_target.program_hex("msp430_LED.hex")
#     # elapsed_time = bsl_target.stop_timer()
#     # print(f"Total execution time: {elapsed_time} seconds")
#     bsl_target.close()

def main(com_port, filename):
    bsl_target = BSL5()
    bsl_target.start_timer()
    bsl_target.open(port=com_port, baudrate=9600)

    bsl_target.bslReset(1)
    # bsl_target.BSL_RX_PASSWORD(b"\xff" * 32)
    bsl_target.BSL_MASS_ERASE()
    bsl_target.BSL_RX_PASSWORD(b"\xff" * 32)

    new_baudrate = 115200
    bsl_target.set_baudrate(new_baudrate)

    bsl_target.program_ti_txt(filename)

    # #bsl_target.program_hex("IHPOSv3_SA.hex")
    # #sys.stderr.flush()
    # bsl_target.program_hex("msp430_LED.hex")
    elapsed_time = bsl_target.stop_timer()
    print(f"Total execution time: {elapsed_time} seconds")
    bsl_target.close()



if __name__ == '__main__':
    #testmain()
    # Sprawdź, czy podano odpowiednią liczbę argumentów
    if len(sys.argv) != 3:
        print("Usage: python program.py <COM port> <filename>")
        sys.exit(1)

    # Pobierz argumenty z linii poleceń
    com_port = sys.argv[1]
    filename = sys.argv[2]
    print("using serial port",com_port)
    # Wywołaj funkcję główną programu
    main(com_port, filename)
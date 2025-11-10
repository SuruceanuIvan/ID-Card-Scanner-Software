import time
import spidev
import gpiod

# Define chip and lines
chip = gpiod.Chip('gpiochip4')  # For Raspberry Pi 5
rst_line = chip.get_line(25)  # GPIO25 for RST1


# Configure lines
rst_line.request(consumer="MFRC522", type=gpiod.LINE_REQ_DIR_OUT)

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Bus 0, Device 0
spi.max_speed_hz = 1000000  # 1MHz

# MFRC522 registers
CommandReg = 0x01
ComIEnReg = 0x02
DivIEnReg = 0x03
ComIrqReg = 0x04
DivIrqReg = 0x05
ErrorReg = 0x06
Status2Reg = 0x08
FIFODataReg = 0x09
FIFOLevelReg = 0x0A
ControlReg = 0x0C
BitFramingReg = 0x0D
ModeReg = 0x11
TxControlReg = 0x14
TxASKReg = 0x15

# MFRC522 commands
PCD_IDLE = 0x00
PCD_AUTHENT = 0x0E
PCD_RECEIVE = 0x08
PCD_TRANSMIT = 0x04
PCD_TRANSCEIVE = 0x0C
PCD_RESETPHASE = 0x0F
PCD_CALCCRC = 0x03

# MFRC522 response codes
MI_OK = 0
MI_NOTAGERR = 1
MI_ERR = 2

# Mifare constants
PICC_REQIDL = 0x26
PICC_REQALL = 0x52
PICC_ANTICOLL = 0x93
PICC_SElECTTAG = 0x93
PICC_AUTHENT1A = 0x60
PICC_AUTHENT1B = 0x61
PICC_READ = 0x30
PICC_WRITE = 0xA0
PICC_DECREMENT = 0xC0
PICC_INCREMENT = 0xC1
PICC_RESTORE = 0xC2
PICC_TRANSFER = 0xB0
PICC_HALT = 0x50

def write_register(address, value):
    spi.xfer2([((address << 1) & 0x7E), value])

def read_register(address):
    return spi.xfer2([((address << 1) & 0x7E) | 0x80, 0])[1]

def set_bit_mask(address, mask):
    current_value = read_register(address)
    write_register(address, current_value | mask)

def clear_bit_mask(address, mask):
    current_value = read_register(address)
    write_register(address, current_value & (~mask))

def antenna_on():
    temp = read_register(TxControlReg)
    if ~(temp & 0x03):
        set_bit_mask(TxControlReg, 0x03)

def reset():
    write_register(CommandReg, PCD_RESETPHASE)
    time.sleep(0.05)  # Give it time to reset

def init():
    reset()
    
    # Configure the MFRC522
    write_register(TModeReg, 0x8D)        # TAuto=1; timer starts automatically at the end of the transmission
    write_register(TPrescalerReg, 0x3E)    # 0x3E 0x0A - Timer frequency 
    write_register(TReloadRegL, 30)        # Timer reload value
    write_register(TReloadRegH, 0)         # Timer reload value
    write_register(TxASKReg, 0x40)         # Force 100% ASK modulation
    write_register(ModeReg, 0x3D)          # CRC preset value to 0x6363
    
    antenna_on()  # Turn on the antenna

def request(req_mode):
    write_register(BitFramingReg, 0x07)  # Transmit the last byte completely
    
    buf = [req_mode]
    (status, backData, backLen) = to_card(PCD_TRANSCEIVE, buf)
    
    if (status != MI_OK) or (backLen != 0x10):
        status = MI_ERR
        
    return (status, backData)

def to_card(command, send_data):
    backData = []
    backLen = 0
    status = MI_ERR
    irq_en = 0x00
    wait_irq = 0x00
    
    if command == PCD_AUTHENT:
        irq_en = 0x12
        wait_irq = 0x10
    elif command == PCD_TRANSCEIVE:
        irq_en = 0x77
        wait_irq = 0x30
    
    write_register(ComIEnReg, irq_en | 0x80)  # Enable interrupt request
    clear_bit_mask(ComIrqReg, 0x80)          # Clear all interrupt request bits
    set_bit_mask(FIFOLevelReg, 0x80)         # FlushBuffer=1, FIFO initialization
    
    write_register(CommandReg, PCD_IDLE)     # No action, cancel the current command
    
    # Write data to the FIFO
    for i in range(len(send_data)):
        write_register(FIFODataReg, send_data[i])
    
    # Execute the command
    write_register(CommandReg, command)
    
    if command == PCD_TRANSCEIVE:
        set_bit_mask(BitFramingReg, 0x80)    # StartSend=1, transmission of data starts
    
    # Wait for the command to complete
    i = 100  # Wait timeout
    while True:
        n = read_register(ComIrqReg)
        i -= 1
        if i == 0 or (n & 0x01) or (n & wait_irq):
            break
    
    clear_bit_mask(BitFramingReg, 0x80)      # StartSend=0
    
    if i != 0:
        if (read_register(ErrorReg) & 0x1B) == 0x00:  # BufferOvfl Collerr CRCErr ProtocolErr
            status = MI_OK
            
            if n & irq_en & 0x01:
                status = MI_NOTAGERR
            
            if command == PCD_TRANSCEIVE:
                n = read_register(FIFOLevelReg)
                last_bits = read_register(ControlReg) & 0x07
                
                if last_bits != 0:
                    backLen = (n - 1) * 8 + last_bits
                else:
                    backLen = n * 8
                
                if n == 0:
                    n = 1
                if n > 16:
                    n = 16
                
                # Read the data from FIFO
                for i in range(n):
                    backData.append(read_register(FIFODataReg))
        else:
            status = MI_ERR
    
    return (status, backData, backLen)

def anticoll():
    serNum = []
    
    write_register(BitFramingReg, 0x00)    # TxLastBits = 0, RxAlign = 0
    
    serNum = [PICC_ANTICOLL, 0x20]
    
    (status, backData, backBits) = to_card(PCD_TRANSCEIVE, serNum)
    
    if status == MI_OK:
        if len(backData) == 5:
            serNum_check_sum = 0
            for i in range(4):
                serNum_check_sum ^= backData[i]
            
            if serNum_check_sum != backData[4]:
                status = MI_ERR
        else:
            status = MI_ERR
    
    return (status, backData)

def calculate_crc(data):
    clear_bit_mask(DivIrqReg, 0x04)  # CRCIrq = 0
    set_bit_mask(FIFOLevelReg, 0x80)  # Clear the FIFO pointer
    
    # Write data to the FIFO
    for i in range(len(data)):
        write_register(FIFODataReg, data[i])
    
    write_register(CommandReg, PCD_CALCCRC)
    
    # Wait for CRC calculation to complete
    i = 255
    while True:
        n = read_register(DivIrqReg)
        i -= 1
        if i == 0 or (n & 0x04):  # CRCIrq bit set
            break
    
    # Read CRC calculation result
    crc_result = [read_register(0x22), read_register(0x21)]
    
    return crc_result

def select_tag(uid):
    buf = [PICC_SElECTTAG, 0x70]
    
    for i in range(5):
        buf.append(uid[i])
    
    crc = calculate_crc(buf)
    buf.append(crc[0])
    buf.append(crc[1])
    
    (status, backData, backLen) = to_card(PCD_TRANSCEIVE, buf)
    
    if (status == MI_OK) and (backLen == 0x18):
        return backData[0]
    else:
        return 0

def auth(auth_mode, block_addr, key, uid):
    buff = [auth_mode, block_addr]
    
    # First byte should be the block address
    for i in range(len(key)):
        buff.append(key[i])
    
    # Now we need to append the first 4 bytes of the UID
    for i in range(4):
        buff.append(uid[i])
    
    (status, backData, backLen) = to_card(PCD_AUTHENT, buff)
    
    if status != MI_OK or not (read_register(Status2Reg) & 0x08):
        status = MI_ERR
    
    return status

def stop_crypto():
    clear_bit_mask(Status2Reg, 0x08)

def read(block_addr):
    recv_data = []
    buff = [PICC_READ, block_addr]
    crc = calculate_crc(buff)
    buff.append(crc[0])
    buff.append(crc[1])
    (status, backData, backLen) = to_card(PCD_TRANSCEIVE, buff)
    
    if status == MI_OK:
        for i in range(16):
            recv_data.append(backData[i])
    else:
        recv_data = []
    
    return (status, recv_data)

def write(block_addr, data):
    buff = [PICC_WRITE, block_addr]
    crc = calculate_crc(buff)
    buff.append(crc[0])
    buff.append(crc[1])
    
    (status, backData, backLen) = to_card(PCD_TRANSCEIVE, buff)
    
    if status == MI_OK and backLen == 4 and (backData[0] & 0x0F) == 0x0A:
        # Data confirmed, now write data to the card
        buff = []
        for i in range(16):
            buff.append(data[i])
        
        crc = calculate_crc(buff)
        buff.append(crc[0])
        buff.append(crc[1])
        (status, backData, backLen) = to_card(PCD_TRANSCEIVE, buff)
        
        if status != MI_OK or backLen != 4 or (backData[0] & 0x0F) != 0x0A:
            status = MI_ERR
    else:
        status = MI_ERR
    
    return status

# Missing registers
TModeReg = 0x2A
TPrescalerReg = 0x2B
TReloadRegL = 0x2C
TReloadRegH = 0x2D

# Reset the RFID reader
rst_line.set_value(0)  # LOW
time.sleep(0.1)
rst_line.set_value(1)  # HIGH
time.sleep(0.1)

# Initialize the RFID reader
init()

def obtainUID():
    while True:
        # Check for cards
        (status, backData) = request(PICC_REQIDL)
        
        if status == MI_OK:
            print("Card detected!")
            
            # Anti-collision, return card serial number
            (status, uid) = anticoll()
            
            if status == MI_OK:
                print("Card UID:", end=' ')
                uid_str = ""
                for i in range(0, len(uid)):
                    print(f"{uid[i]:02X}", end=' ')
                    uid_str += f"{uid[i]:02X}"
                print()

                return uid_str
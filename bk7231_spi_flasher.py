

import sys
import os
import argparse
import os
import sys
import platform
import spidev
import time
import RPi.GPIO as GPIO

def ChipReset():
    # set CEN low for 1s
    GPIO.setup(CENGPIO, GPIO.OUT)
    GPIO.output(CENGPIO, GPIO.LOW)
    time.sleep(1)
    GPIO.output(CENGPIO, GPIO.HIGH)

def BK_EnterSPIMode(spi):
    ChipReset()
    print("Send 250 'D2'")
    send_buf = bytearray(250)
    for x in range(250):
        send_buf[x] = 0xD2
    a = spi.xfer2(send_buf)


    for x in range(250):
        print(hex(a[x]), end = '')
        print(" ", end = '')
    
    time.sleep(0.1)

    print("Test by sending get ID")
    cmd_id = bytearray(4)
    cmd_id[0] = 0x9F
    cmd_id[1] = 0x0
    cmd_id[2] = 0x0
    cmd_id[3] = 0x0
    
    a = spi.xfer2(cmd_id)

    for x in range(4):
        print(hex(a[x]), end = '')
        print(" ", end = '')
        
    if a[0] == 0x00 and a[1] == 0x1c and a[2] == 0x70 and a[3] == 0x15:
        print("ID OK")
        return 1
        
    print("ID bad")
    return 0

SPI_CHIP_ERASE_CMD		= 0xc7
SPI_CHIP_ENABLE_CMD		= 0x06
SPI_READ_PAGE_CMD   	= 0x03
SPI_WRITE_PAGE_CMD   	= 0x02
SPI_SECTRO_ERASE_CMD	= 0x20
SPI_SECUR_SECTOR_ERASE	= 0x44
SPI_ID_READ_CMD			= 0x9F
SPI_STATU_WR_LOW_CMD	= 0x01
SPI_STATU_WR_HIG_CMD	= 0x31
SPI_READ_REG        	= 0x05

def Wait_Busy_Down():
    while True:
        send_buf = bytearray(2)
        send_buf[0] = SPI_READ_REG
        send_buf[1] = 0x00
        out_buf = spi.xfer2(send_buf)
        if not (out_buf[1] & 0x01):
            break
        time.sleep(0.01)

def CHIP_ENABLE_Command():
    send_buf = bytearray(1)
    send_buf[0] = SPI_CHIP_ENABLE_CMD
    spi.xfer(send_buf)
    Wait_Busy_Down()
    
def WriteImage(startaddr,filename, maxSize):
    print("WriteImage "+filename)
    statinfo = os.stat(filename)
    # size = statinfo.st_size
    # size = (size+255)//256*256
    size = maxSize;

    count = 0
    addr = startaddr
    f = open(filename, "rb")

    while count < size:
        print("count "+str(count) +"/"+str(size))
        if 1:
            if 0 == (addr & 0xfff):
                CHIP_ENABLE_Command()
                send_buf = bytearray(4)
                send_buf[0] = 0x20
                send_buf[1] = (addr & 0xFF0000) >> 16
                send_buf[2] = (addr & 0xFF00) >> 8
                send_buf[3] = addr & 0xFF
                spi.xfer(send_buf)
                Wait_Busy_Down()

        buf = f.read(256)
        if buf:
            CHIP_ENABLE_Command()
            send_buf = bytearray(4+256)
            send_buf[0] = 0x02
            send_buf[1] = (addr & 0xFF0000) >> 16
            send_buf[2] = (addr & 0xFF00) >> 8
            send_buf[3] = addr & 0xFF
            send_buf[4:4+256] = buf
            spi.xfer(send_buf)
        count += 256
        addr += 256
        
    f.close()

    return True
    
def ReadStart(startaddr, filename, readlen):
    count = 0
    addr = startaddr
    f = open(filename, "wb")
    size = readlen
    size = (size+255)//256*256
    print("Reading")

    while count < size:
        print("count "+str(count) +"/"+str(size))
        send_buf = bytearray(4+256)
        send_buf[0] = 0x03
        send_buf[1] = (addr & 0xFF0000) >> 16
        send_buf[2] = (addr & 0xFF00) >> 8
        send_buf[3] = addr & 0xFF
        result = spi.xfer2(send_buf)
        count += 256
        addr += 256
        part = bytearray(result[4:4+256])
        for x in range(256):
            print(hex(part[x]), end = '')
            print(" ", end = '')
        f.write(part)

    f.close()

    ChipReset()
    return True
   
# Adjust it for your pin
CENGPIO = GPIO.PB+21
# also adjust it
GPIO.setmode(GPIO.RAW)

spi = spidev.SpiDev()
spi.open(0, 0)
# SPI mode 3
spi.mode = 0b11
# it will fail to read ID with higher speeds (at least it fails for me)
spi.max_speed_hz = 30000

if BK_EnterSPIMode(spi) == 0:
    print("Failed to read flash id")
    exit();
    
# this will allow you to write directly bootloader + app
#WriteImage(0,"OpenBK7231T_App_QIO_35a81303.bin", 0x200000)
# if you have an app that was loaded by bkWriter 1.60 with offs 0x11000,
# and you have broke your bootloader, you can take bootloader from OBK build
# and then restore an app
WriteImage(0,"OpenBK7231T_App_QIO_35a81303.bin", 0x11000)
WriteImage(0x11000,"REST.bin", 0x200000)
# I used this to verify my code and it work
#ReadStart(0,"tstReadS.bin", 0x1100)




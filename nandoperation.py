import time
import struct
import sys
import traceback
import flashdevice_defs
from array import array as Array
from pyftdi import ftdi


class IO:
    def __init__(self, do_slow = False, debug = 0, simulation_mode = False):
       self.Debug = debug
       self.PageSize = 0
       self.Status = 0xFF  #Invalid Status
       self.Slow = do_slow
       self.WriteProtect = False
        
       try:
          self.ftdi = ftdi.Ftdi()
          self.ftdi.show_devices() # Detect FTDI device
       except:
          print("Error opening FTDI device")
          self.ftdi = None
          
       if self.ftdi is not None:
            try:
                self.ftdi.open(0x0403, 0x6011, interface = 1)# 403 is a vendor id, 6011 is product ID for 4232 and there are multiple interfaces (multiple communication channel) in this case we have selected interface = 1
            except:
                traceback.print_exc(file = sys.stdout)

            if self.ftdi.is_connected:
                self.ftdi.set_bitmode(0, self.ftdi.BitMode.MCU)# configured to MCU mode
                print('FTDI is set to MCU mode')
                
                # if self.Slow:
                #     # Clock FTDI chip at 12MHz instead of 60MHz
                #     self.ftdi.write_data(Array('B', [ftdi.Ftdi.ENABLE_CLK_DIV5]))
                # else:
                #     self.ftdi.write_data(Array('B', [ftdi.Ftdi.DISABLE_CLK_DIV5]))

                # self.ftdi.set_latency_timer(self.ftdi.LATENCY_MIN)
                # self.ftdi.purge_buffers()
                # self.ftdi.write_data(Array('B', [ftdi.Ftdi.SET_BITS_HIGH, 0x0, 0x1]))
                
            Status = self.__get_status()  
            print(f"NAND STATUS Before Initialization: {Status:#04x}") 
            self.__wait_ready()
            self.__initialization()  
            self.__wait_ready() # Waiting for chip_initialization operation to complete DEBUG:: Potential issue
            self.Status = self.__get_status()
            print(f"NAND STATUS After Initialization: {self.Status:#04x}") 
            self.__get_id()
        
    def __get_id(self):
        self.Name = ''
        self.ID = 0
        self.PageSize = 0
        self.ChipSizeMB = 0
        self.EraseSize = 0
        self.Options = 0
        self.AddrCycles = 0

        self.__send_cmd(flashdevice_defs.NAND_CMD_READID)
        self.__send_address(0, 1)
        flash_identifiers = self.__read_data(5)# read_id command followed by 00h address returns 5 bytes

        if not flash_identifiers:
            print("Error Getting NAND device ID")
            return False

        for i,manufacture_information in flash_identifiers:
            print(f"NAND Information Byte_{i}: {manufacture_information:#04x}") 
            
        # for device_description in flashdevice_defs.DEVICE_DESCRIPTIONS:
        #     if device_description[1] == flash_identifiers[0]:
        #         (self.Name, self.ID, self.PageSize, self.ChipSizeMB, self.EraseSize, self.Options, self.AddrCycles) = device_description
        #         self.Identified = True
        #         break

        # if not self.Identified:
        #     return False
         
        return True

                
    def is_slow_mode(self):
        return self.Slow 
       
    def __wait_ready(self):
        if self.ftdi is None or not self.ftdi.is_connected:
            return

        while 1:
            self.ftdi.write_data(Array('B', [ftdi.Ftdi.GET_BITS_HIGH]))
            data = self.ftdi.read_data_bytes(1)
            if not data or len(data) <= 0:
                raise Exception('FTDI device Not ready. Try restarting it.')

            if  data[0] & 2 == 0x2:
                return

            if self.Debug > 0:
                print('Not Ready', data)

        return
    def __initialization(self):
        self.__send_cmd(0xFF)
        return
         
    def __write(self, cl, al, data):
        cmds = []
        cmd_type = 0
        if cl == 1:
            cmd_type |= flashdevice_defs.ADR_CL
        if al == 1:
            cmd_type |= flashdevice_defs.ADR_AL
        if not self.WriteProtect:
            cmd_type |= flashdevice_defs.ADR_WP

        cmds += [ftdi.Ftdi.WRITE_EXTENDED, cmd_type, 0, ord(data[0])]
        for i in range(1, len(data), 1):
            #if i == 256:
            #    cmds += [Ftdi.WRITE_SHORT, 0, ord(data[i])]
            cmds += [ftdi.Ftdi.WRITE_SHORT, 0, ord(data[i])]

        if self.ftdi is None or not self.ftdi.is_connected:
            return

        self.ftdi.write_data(Array('B', cmds))
        
    def __send_cmd(self, cmd):
        self.__write(1, 0, chr(cmd))

    def __send_address(self, addr, count):
        data = ''

        for _ in range(0, count, 1):
            data += chr(addr & 0xff)
            addr = addr>>8

        self.__write(0, 1, data)

    def __get_status(self):
        self.__send_cmd(0x70)
        status = self.__read_data(1)[0]
        return status

    def __read_data(self, count):
        return self.__read(0, 0, count)
    
    def __read(self, cl, al, count):
        cmds = []
        cmd_type = 0
        if cl == 1:
            cmd_type |= flashdevice_defs.ADR_CL
        if al == 1:
            cmd_type |= flashdevice_defs.ADR_AL

        cmds += [ftdi.Ftdi.READ_EXTENDED, cmd_type, 0]

        for _ in range(1, count, 1):
            cmds += [ftdi.Ftdi.READ_SHORT, 0]

        cmds.append(ftdi.Ftdi.SEND_IMMEDIATE)

        if self.ftdi is None or not self.ftdi.is_connected:
            return

        self.ftdi.write_data(Array('B', cmds))
        if self.is_slow_mode():
            data = self.ftdi.read_data_bytes(count*2)
            data = data[0:-1:2]
        else:
            data = self.ftdi.read_data_bytes(count)
        return bytes(data)

      
nandOperation = IO()

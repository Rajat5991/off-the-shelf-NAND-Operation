# NANDOperation
Executing read, write, and erase operations on Micron TSOP-48 using FTDI-FT2232H configured in MCU Host Bus Emulation mode.

# Setup
1) Purchase FT2232H Mini Module, TSOP-48 Pin NAND Flash and TSOP-48 Pin Socket.

   <img width="224" alt="image" src="https://github.com/Rajat5991/off-the-shelf-NAND-Operation/assets/154459536/e275ba37-766d-4fdc-a322-bfbfc4fc0d5d">
   <img width="235" alt="image" src="https://github.com/Rajat5991/off-the-shelf-NAND-Operation/assets/154459536/76f8ed64-b37f-4858-ac8a-cffb266f3b1d">
   <img width="289" alt="image" src="https://github.com/Rajat5991/off-the-shelf-NAND-Operation/assets/154459536/becf4e97-cfab-4dd3-8a18-688ce8cb417a">

2) Install D2xx driver to communicate with FT2232H from https://ftdichip.com/drivers/d2xx-drivers/
3) Install pyftdi and pyusb library.
         pip install pyftdi
         pip install pyusb        
4) Install zadig to use generic USB driver. Follow installation instruction guide in the link: - https://eblot.github.io/pyftdi/installation.html
5) Micron Datasheet for deeper understanding of the command can be found in the link: https://datasheetspdf.com/pdf-file/843441/Micron/MT29F8G08ABACA/1
3)FT2232H can be used in various configurations but for our setup we need to use it in MCU (mimics 8048 or 8051 microprocessor) host bus emulation mode.
6) 

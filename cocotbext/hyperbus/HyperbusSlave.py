import cocotb
from cocotb_bus.drivers import BusDriver
from cocotb.triggers import RisingEdge, FallingEdge, ReadOnly, Timer, ReadWrite, Lock



class HyperbusSlave(BusDriver):
     _signals=['cs', 'rwds', 'dq', 'clk', 'memory']
     _optional_signals=['clk_']

    def __init__(self, cs, rwds, dq, clk, memory):
      self.bus.cs=cs
      self.bus.rwds=rwds
      self.bus.dq=dq
      self.bus.clk=clk
      self.bus.memory=memory 
    
      self.memory_model = memory_model
      self.rwds_mask = 0xFF
    
    async def driver_send(self, data):
       await RisingEdge(self.clk)  
  
       self.bus.dq.value = data  # Driver data onto output signals
   
       self.bus.tx_complete.value = 1  # Example completion signal
       
    def write(self, address, data):
      '''
      Writes data to the slave memory based on address, considering burst transfers.
    Parameters:
    address: The target address to write to.
    data: The data to be written as a byte string.
      '''
        burst_length = self._calc_burst(data)

        for i in range(burst_length):
           self.memory_model[address + i] = data[i]
            
    def read(self, address, length):
      '''
       Reads data from the slave memory based on address
      Parameters:
      address: The target address to read from.
      length: The number of bytes to read.
      '''
      read_data = bytearray(length)

        for i in range(length):
            
            if address + i in self.memory_model:
                read_data[i] = self.memory_model[address + i]
            else:
                
                read_data[i] = 0
                

            # Apply RDWS mask 
            read_data[i] &= self.rwds_mask

            # Send data to output signals 
            self.bus.dq.value = read_data[i]
           
        return read_data

     def _calc_burst(self, data):
           burst_length_map = {
            128: None,  # 00 for infinite burst
            64: 1,     # 01 for 64 bytes
            16: 2,     # 10 for 16 bytes
            32: 3,     # 11 for 32 bytes
        }

        for length, code in burst_length_map.items():
            if len(data) % length == 0:
                return code
            else 
                return 1



   
        
    async def handle_transaction(self):
        await RisingEdge(self.clk)

        if self.bus.cs.value == 0:  # Chip select asserted
            command = await self.decode_command()
            if command == "write":
                await self.write(address, data)
            elif command == "read":
                data = await self.read(address, length)
            else:
                # Handle unsupported commands

            self.bus.cs.value = 1  # Deassert chip select

    async def decode_command(self):
        '''
        using the ca bit assignment logic for(read/write/address space/burst type/latency)
        '''
        await RisingEdge(self.bus.clk)
        
        
   async def process_latency(self, latency):
       '''
       Implement logic to wait for required number of clock cycles based on latency
       '''
       wait_time = latency * self.clk.period  #calculate wait time

   
       await Timer(wait_time, units='ns')


      

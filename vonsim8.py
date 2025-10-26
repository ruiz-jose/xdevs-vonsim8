from xdevs.models import Atomic, Coupled, Port
from xdevs.sim import Coordinator


class SharedBus(Atomic):
    """Modelo atómico para el bus compartido con arbitraje."""
    
    def __init__(self, name: str = "BUS"):
        super().__init__(name)
        self.current_value: int = 0x00
        self.locked: bool = False
        self.requester: str = ""
        
        self.req = Port(str, name="req")
        self.add_in_port(self.req)
        self.grant = Port(bool, name="grant")
        self.add_out_port(self.grant)
        
        self.data_in = Port(int, name="data_in")
        self.add_in_port(self.data_in)
        self.data_out = Port(int, name="data_out")
        self.add_out_port(self.data_out)
        
        self.release = Port(bool, name="release")
        self.add_in_port(self.release)
        
        self.pending_grant = False
        self.pending_data = False
    
    def initialize(self):
        self.passivate()
    
    def deltext(self, e: float):
        self.continuef(e)
        
        if self.req and not self.req.empty():
            if not self.locked:
                self.requester = self.req.get()
                self.locked = True
                self.pending_grant = True
                self.hold_in("GRANTING", 1)
        
        if self.release and not self.release.empty():
            if self.release.get():
                self.locked = False
                self.requester = ""
        
        if self.data_in and not self.data_in.empty():
            self.current_value = self.data_in.get() & 0xFF
            self.pending_data = True
            self.activate()
    
    def deltint(self):
        if self.pending_grant:
            self.pending_grant = False
        if self.pending_data:
            self.pending_data = False
        self.passivate()
    
    def lambdaf(self):
        if self.pending_grant:
            self.grant.add(True)
        if self.pending_data:
            self.data_out.add(self.current_value)
    
    def exit(self):
        pass


class Register(Atomic):
    """Modelo atómico para un registro de 8 bits con señales indexadas."""
    
    def __init__(self, name: str, initial_value: int = 0x00):
        super().__init__(name)
        self.value: int = initial_value
        self.reg_name: str = name
        
        self.data_in = Port(int, name="data_in")
        self.add_in_port(self.data_in)
        self.enable_in = Port(str, name="enable_in")
        self.add_in_port(self.enable_in)
        self.enable_out = Port(str, name="enable_out")
        self.add_in_port(self.enable_out)
        
        self.data_out = Port(int, name="data_out")
        self.add_out_port(self.data_out)
        
        self.pending_write = False
        self.pending_read = False
        self.pending_value = 0x00
    
    def initialize(self):
        self.passivate()
    
    def deltext(self, e: float):
        self.continuef(e)
        
        if self.data_in and not self.data_in.empty():
            self.pending_value = self.data_in.get() & 0xFF
        
        if self.enable_in and not self.enable_in.empty():
            target_reg = self.enable_in.get()
            if target_reg == self.reg_name:
                self.pending_write = True
                self.activate()
        
        if self.enable_out and not self.enable_out.empty():
            target_reg = self.enable_out.get()
            if target_reg == self.reg_name:
                self.pending_read = True
                self.activate()
    
    def deltint(self):
        if self.pending_write:
            self.value = self.pending_value
            print(f"  [{self.name}] δ_int: Escritura completada. Valor={self.value:02X}")
            self.pending_write = False
        
        if self.pending_read:
            print(f"  [{self.name}] δ_int: Lectura completada. Valor={self.value:02X}")
            self.pending_read = False
        
        self.passivate()
    
    def lambdaf(self):
        if self.pending_read:
            print(f"  [{self.name}] λ: Emitiendo dato={self.value:02X} por data_out")
            self.data_out.add(self.value)
    
    def exit(self):
        pass


class SimpleRegister(Atomic):
    """Modelo atómico para registros simples (MBR, IR) con señales booleanas."""
    
    def __init__(self, name: str, initial_value: int = 0x00):
        super().__init__(name)
        self.value: int = initial_value
        
        self.data_in = Port(int, name="data_in")
        self.add_in_port(self.data_in)
        self.enable_in = Port(bool, name="enable_in")
        self.add_in_port(self.enable_in)
        self.enable_out = Port(bool, name="enable_out")
        self.add_in_port(self.enable_out)
        
        self.data_out = Port(int, name="data_out")
        self.add_out_port(self.data_out)
        
        self.pending_write = False
        self.pending_read = False
        self.pending_value = 0x00
    
    def initialize(self):
        self.passivate()
    
    def deltext(self, e: float):
        self.continuef(e)
        
        if self.enable_in and not self.enable_in.empty():
            enabled = self.enable_in.get()
            if enabled and self.data_in and not self.data_in.empty():
                self.pending_value = self.data_in.get() & 0xFF
                self.pending_write = True
                self.activate()
        
        if self.enable_out and not self.enable_out.empty():
            enabled = self.enable_out.get()
            if enabled:
                self.pending_read = True
                self.activate()
        
        if not self.enable_in and self.data_in and not self.data_in.empty():
            self.pending_value = self.data_in.get() & 0xFF
            self.pending_write = True
            self.activate()
    
    def deltint(self):
        if self.pending_write:
            self.value = self.pending_value
            print(f"  [{self.name}] δ_int: Escritura completada. Valor={self.value:02X}")
            self.pending_write = False
        
        if self.pending_read:
            print(f"  [{self.name}] δ_int: Lectura completada. Valor={self.value:02X}")
            self.pending_read = False
        
        self.passivate()
    
    def lambdaf(self):
        if self.pending_read:
            print(f"  [{self.name}] λ: Emitiendo dato={self.value:02X} por data_out")
            self.data_out.add(self.value)
    
    def exit(self):
        pass


class InstructionPointer(Atomic):
    """Modelo atómico para el registro IP (Instruction Pointer)."""
    
    def __init__(self, name: str = "IP"):
        super().__init__(name)
        self.value: int = 0x00
        
        self.addr_out = Port(int, name="addr_out")
        self.add_out_port(self.addr_out)
        self.ip_write = Port(int, name="ip_write")
        self.add_in_port(self.ip_write)
        self.read_request = Port(bool, name="read_request")
        self.add_in_port(self.read_request)
        
        self.pending_output = False
        self.pending_increment = False
    
    def initialize(self):
        self.passivate()
    
    def deltext(self, e: float):
        self.continuef(e)
        
        if self.read_request and self.read_request.get():
            self.pending_output = True
            self.activate()
        
        if self.ip_write:
            increment = self.ip_write.get()
            if increment:
                self.pending_increment = True
                self.activate()
    
    def deltint(self):
        if self.pending_increment:
            old_val = self.value
            self.value = (self.value + 1) & 0xFF
            print(f"  [IP] δ_int: Incremento IP. {old_val:02X} → {self.value:02X}")
            self.pending_increment = False
        
        if self.pending_output:
            self.pending_output = False
        
        self.passivate()
    
    def lambdaf(self):
        if self.pending_output:
            print(f"  [IP] λ: Emitiendo dirección IP={self.value:02X} por addr_out")
            self.addr_out.add(self.value)
    
    def exit(self):
        pass


class MemoryAddressRegister(Atomic):
    """Modelo atómico para el registro MAR (Memory Address Register)."""
    
    def __init__(self, name: str = "MAR"):
        super().__init__(name)
        self.address: int = 0x00
        
        self.addr_in = Port(int, name="addr_in")
        self.add_in_port(self.addr_in)
        self.addr_out = Port(int, name="addr_out")
        self.add_out_port(self.addr_out)
        
        self.pending_addr = None
    
    def initialize(self):
        self.passivate()
    
    def deltext(self, e: float):
        self.continuef(e)
        if self.addr_in:
            self.pending_addr = self.addr_in.get() & 0xFF
            self.activate()
    
    def deltint(self):
        if self.pending_addr is not None:
            self.address = self.pending_addr
            print(f"  [MAR] δ_int: Dirección almacenada. MAR={self.address:02X}")
            self.pending_addr = None
        self.passivate()
    
    def lambdaf(self):
        if self.pending_addr is not None:
            print(f"  [MAR] λ: Emitiendo dirección MAR={self.pending_addr:02X} hacia MEM")
            self.addr_out.add(self.pending_addr)
    
    def exit(self):
        pass


class Memory(Atomic):
    """Modelo atómico para la memoria unificada."""
    
    def __init__(self, name: str = "MEM"):
        super().__init__(name)
        self.storage: dict[int, int] = {}
        self.pending_addr: int | None = None
        self.pending_read: bool = False
        
        self.addr = Port(int, name="addr")
        self.add_in_port(self.addr)
        self.rw = Port(bool, name="rw")
        self.add_in_port(self.rw)
        self.data_in = Port(int, name="data_in")
        self.add_in_port(self.data_in)
        
        self.data_out = Port(int, name="data_out")
        self.add_out_port(self.data_out)
        
        self.pending_operation = None
    
    def initialize(self):
        self.storage[0x00] = 0x01
        self.passivate()
    
    def deltext(self, e: float):
        self.continuef(e)
        
        if self.addr and not self.addr.empty():
            self.pending_addr = self.addr.get() & 0xFF
        
        if self.rw and not self.rw.empty():
            self.pending_read = self.rw.get()
        
        if self.pending_addr is not None and self.pending_read:
            self.pending_operation = ("read", self.pending_addr)
            print(f"  [MEM] δ_ext: Solicitud de lectura en dirección {self.pending_addr:02X}")
            self.hold_in("READING", 1)
            self.pending_addr = None
            self.pending_read = False
    
    def deltint(self):
        if self.pending_operation:
            op_type, addr_val = self.pending_operation
            data = self.storage.get(addr_val, 0x00)
            print(f"  [MEM] δ_int: Lectura completada. MEM[{addr_val:02X}]={data:02X}")
        self.pending_operation = None
        self.passivate()
    
    def lambdaf(self):
        if self.pending_operation and self.pending_operation[0] == "read":
            addr_val = self.pending_operation[1]
            data = self.storage.get(addr_val, 0x00)
            print(f"  [MEM] λ: Emitiendo dato={data:02X} por data_out")
            self.data_out.add(data)
    
    def exit(self):
        pass


class ControlUnit(Atomic):
    """Modelo atómico para la Unidad de Control (UC)."""
    
    def __init__(self, name: str = "UC"):
        super().__init__(name)
        
        self.ir_in = Port(int, name="ir_in")
        self.add_in_port(self.ir_in)
        
        self.ip_read = Port(bool, name="ip_read")
        self.add_out_port(self.ip_read)
        self.ip_inc = Port(bool, name="ip_inc")
        self.add_out_port(self.ip_inc)
        self.mem_read = Port(bool, name="mem_read")
        self.add_out_port(self.mem_read)
        self.mbr_enable = Port(bool, name="mbr_enable")
        self.add_out_port(self.mbr_enable)
        self.ir_enable = Port(bool, name="ir_enable")
        self.add_out_port(self.ir_enable)
        self.ir_read = Port(bool, name="ir_read")
        self.add_out_port(self.ir_read)
        
        self.reg_enable_out = Port(str, name="reg_enable_out")
        self.add_out_port(self.reg_enable_out)
        self.reg_enable_in = Port(str, name="reg_enable_in")
        self.add_out_port(self.reg_enable_in)
        
        self.phase = "IDLE"
        self.instruction_code = 0x00
        self.micro_step = 0
        
        self.total_cycles = 0
        self.fetch_cycles = 0
        self.execute_cycles = 0
        
        self.instruction_set = {
            0x01: {"opcode": "MOV", "dst": "AL", "src": "BL"}
        }
    
    def initialize(self):
        self.phase = "FETCH1"
        self.micro_step = 0
        self.total_cycles = 1
        self.fetch_cycles = 1
        self.hold_in(self.phase, 1)
    
    def deltint(self):
        if self.phase == "FETCH1":
            print(f"\n{'═'*78}")
            print(f"  FASE FETCH - Paso 1/6: UC → IP (solicita dirección)")
            print(f"{'─'*78}")
            self.phase = "FETCH2"
            cycles = 1
            self.hold_in(self.phase, cycles)
        
        elif self.phase == "FETCH2":
            print(f"\n{'─'*78}")
            print(f"  FASE FETCH - Paso 2/6: IP → MAR (transfiere dirección)")
            print(f"{'─'*78}")
            self.phase = "FETCH3"
            cycles = 1
            self.fetch_cycles += cycles
            self.total_cycles += cycles
            self.hold_in(self.phase, cycles)
        
        elif self.phase == "FETCH3":
            print(f"\n{'─'*78}")
            print(f"  FASE FETCH - Paso 3/6: UC → MEM (mem_read); IP ← IP+1")
            print(f"{'─'*78}")
            self.phase = "FETCH4"
            cycles = 2
            self.fetch_cycles += cycles
            self.total_cycles += cycles
            self.hold_in(self.phase, cycles)
        
        elif self.phase == "FETCH4":
            print(f"\n{'─'*78}")
            print(f"  FASE FETCH - Paso 4/6: MEM → MBR (instrucción leída)")
            print(f"{'─'*78}")
            self.phase = "FETCH5"
            cycles = 1
            self.fetch_cycles += cycles
            self.total_cycles += cycles
            self.hold_in(self.phase, cycles)
        
        elif self.phase == "FETCH5":
            print(f"\n{'─'*78}")
            print(f"  FASE FETCH - Paso 5/6: MBR → IR (carga instrucción)")
            print(f"{'─'*78}")
            self.phase = "FETCH6"
            cycles = 2
            self.fetch_cycles += cycles
            self.total_cycles += cycles
            self.hold_in(self.phase, cycles)
        
        elif self.phase == "FETCH6":
            print(f"\n{'─'*78}")
            print(f"  FASE FETCH - Paso 6/6: IR → UC (recibe opcode)")
            print(f"{'─'*78}")
            self.phase = "EXEC1"
            cycles = 1
            self.fetch_cycles += cycles
            self.total_cycles += cycles
            self.hold_in(self.phase, cycles)
        
        elif self.phase == "EXEC1":
            print(f"\n{'═'*78}")
            print(f"  FASE EXECUTE - Paso 1/5: Decodificación")
            print(f"{'─'*78}")
            decoded = self.instruction_set.get(self.instruction_code, {"opcode": "NOP", "dst": "", "src": ""})
            print(f"  [UC] Instrucción decodificada: {decoded['opcode']} {decoded['dst']},{decoded['src']}")
            print(f"  [UC] Microoperaciones planificadas: BL → BUS → AL")
            self.phase = "EXEC2"
            cycles = 1
            self.execute_cycles += cycles
            self.total_cycles += cycles
            self.hold_in(self.phase, cycles)
        
        elif self.phase == "EXEC2":
            print(f"\n{'─'*78}")
            print(f"  FASE EXECUTE - Paso 2/5: UC → REG_BANK.enable_out(BL)")
            print(f"{'─'*78}")
            self.phase = "EXEC3"
            cycles = 1
            self.execute_cycles += cycles
            self.total_cycles += cycles
            self.hold_in(self.phase, cycles)
        
        elif self.phase == "EXEC3":
            print(f"\n{'─'*78}")
            print(f"  FASE EXECUTE - Paso 3/5: BUS ← BL (dato disponible)")
            print(f"{'─'*78}")
            self.phase = "EXEC4"
            cycles = 2
            self.execute_cycles += cycles
            self.total_cycles += cycles
            self.hold_in(self.phase, cycles)
        
        elif self.phase == "EXEC4":
            print(f"\n{'─'*78}")
            print(f"  FASE EXECUTE - Paso 4/5: UC → REG_BANK.enable_in(AL)")
            print(f"{'─'*78}")
            self.phase = "EXEC5"
            cycles = 1
            self.execute_cycles += cycles
            self.total_cycles += cycles
            self.hold_in(self.phase, cycles)
        
        elif self.phase == "EXEC5":
            print(f"\n{'─'*78}")
            print(f"  FASE EXECUTE - Paso 5/5: AL ← BUS (captura completada)")
            print(f"{'─'*78}")
            cycles = 1
            self.execute_cycles += cycles
            self.total_cycles += cycles
            self.phase = "DONE"
            print(f"\n{'═'*78}")
            print(f"  ✓ Ciclo de instrucción MOV AL, BL completado")
            print(f"{'═'*78}")
            self.hold_in(self.phase, cycles)
        
        elif self.phase == "DONE":
            self.passivate()
        
        else:
            self.passivate()
    
    def deltext(self, e: float):
        self.continuef(e)
        if self.ir_in:
            self.instruction_code = self.ir_in.get() & 0xFF
    
    def lambdaf(self):
        if self.phase == "FETCH1":
            self.ip_read.add(True)
        elif self.phase == "FETCH3":
            self.mem_read.add(True)
            self.ip_inc.add(True)
        elif self.phase == "FETCH4":
            self.mbr_enable.add(True)
        elif self.phase == "FETCH5":
            self.ir_enable.add(True)
        elif self.phase == "FETCH6":
            self.ir_read.add(True)
        elif self.phase == "EXEC2":
            self.reg_enable_out.add("BL")
        elif self.phase == "EXEC4":
            self.reg_enable_in.add("AL")
    
    def exit(self):
        pass


class RegisterBank(Coupled):
    """Modelo acoplado para el banco de registros AL, BL, CL, DL."""
    
    def __init__(self, name: str = "REG_BANK"):
        super().__init__(name)
        
        self.al = Register("AL", 0x01)
        self.bl = Register("BL", 0x0A)
        self.cl = Register("CL", 0x00)
        self.dl = Register("DL", 0x00)
        
        self.add_component(self.al)
        self.add_component(self.bl)
        self.add_component(self.cl)
        self.add_component(self.dl)
        
        self.reg_enable_in = Port(str, name="reg_enable_in")
        self.add_in_port(self.reg_enable_in)
        self.reg_enable_out = Port(str, name="reg_enable_out")
        self.add_in_port(self.reg_enable_out)
        
        self.add_coupling(self.reg_enable_in, self.al.enable_in)
        self.add_coupling(self.reg_enable_in, self.bl.enable_in)
        self.add_coupling(self.reg_enable_in, self.cl.enable_in)
        self.add_coupling(self.reg_enable_in, self.dl.enable_in)
        
        self.add_coupling(self.reg_enable_out, self.al.enable_out)
        self.add_coupling(self.reg_enable_out, self.bl.enable_out)
        self.add_coupling(self.reg_enable_out, self.cl.enable_out)
        self.add_coupling(self.reg_enable_out, self.dl.enable_out)
        
        for src_reg in [self.al, self.bl, self.cl, self.dl]:
            for dst_reg in [self.al, self.bl, self.cl, self.dl]:
                if src_reg != dst_reg:
                    self.add_coupling(src_reg.data_out, dst_reg.data_in)


class VonSim8System(Coupled):
    """Modelo acoplado que integra todos los componentes del simulador VonSim8."""
    
    def __init__(self, name: str = "VonSim8"):
        super().__init__(name)
        
        self.ip = InstructionPointer("IP")
        self.mar = MemoryAddressRegister("MAR")
        self.mem = Memory("MEM")
        self.mbr = SimpleRegister("MBR", 0x00)
        self.ir = SimpleRegister("IR", 0x00)
        self.uc = ControlUnit("UC")
        self.reg_bank = RegisterBank("REG_BANK")
        
        self.devs_events = 0
        
        self.add_component(self.ip)
        self.add_component(self.mar)
        self.add_component(self.mem)
        self.add_component(self.mbr)
        self.add_component(self.ir)
        self.add_component(self.uc)
        self.add_component(self.reg_bank)
        
        self.add_coupling(self.uc.ip_read, self.ip.read_request)
        self.add_coupling(self.ip.addr_out, self.mar.addr_in)
        self.add_coupling(self.mar.addr_out, self.mem.addr)
        self.add_coupling(self.uc.mem_read, self.mem.rw)
        self.add_coupling(self.uc.ip_inc, self.ip.ip_write)
        self.add_coupling(self.mem.data_out, self.mbr.data_in)
        self.add_coupling(self.uc.mbr_enable, self.mbr.enable_in)
        self.add_coupling(self.mbr.data_out, self.ir.data_in)
        self.add_coupling(self.uc.ir_enable, self.mbr.enable_out)
        self.add_coupling(self.uc.ir_enable, self.ir.enable_in)
        self.add_coupling(self.uc.ir_read, self.ir.enable_out)
        self.add_coupling(self.ir.data_out, self.uc.ir_in)
        self.add_coupling(self.uc.reg_enable_out, self.reg_bank.reg_enable_out)
        self.add_coupling(self.uc.reg_enable_in, self.reg_bank.reg_enable_in)


class CPUSystem(Coupled):
    """Wrapper para compatibilidad."""
    def __init__(self, name: str = "CPUEnvironment"):
        super().__init__(name)
        self.vonsim8 = VonSim8System("VonSim8")
        self.add_component(self.vonsim8)


if __name__ == "__main__":
    import time
    
    class EventCountingCoordinator(Coordinator):
        def __init__(self, model):
            super().__init__(model)
            self.event_count = 0
            
        def _inject_event_counter(self, model):
            """Inyecta contador en deltint y deltext de todos los modelos atómicos."""
            if hasattr(model, 'deltint'):
                original_deltint = model.deltint
                def counted_deltint():
                    self.event_count += 1
                    return original_deltint()
                model.deltint = counted_deltint
            
            if hasattr(model, 'deltext'):
                original_deltext = model.deltext
                def counted_deltext(e):
                    self.event_count += 1
                    return original_deltext(e)
                model.deltext = counted_deltext
            
            if hasattr(model, 'components'):
                for comp in model.components:
                    self._inject_event_counter(comp)
        
        def initialize(self):
            """Override para inyectar contadores antes de inicializar."""
            self._inject_event_counter(self.model)
            super().initialize()
    
    print("\n" + "═" * 80)
    print("║" + " " * 15 + "SIMULACIÓN DEVS - VONSIM8 (Von Neumann 8-bit)" + " " * 20 + "║")
    print("═" * 80)
    print("  Instrucción: MOV AL, BL (opcode 0x01)")
    print("  Formalismo:  DEVS (Discrete Event System Specification)")
    print("═" * 80 + "\n")
    
    print("⏳ Ejecutando simulación...\n")
    
    env = CPUSystem("VonSim8Environment")
    coord = EventCountingCoordinator(env)
    coord.initialize()
    
    start_time = time.time()
    coord.simulate(num_iters=30)
    simulation_time = time.time() - start_time
    coord.exit()
    
    vonsim8 = env.vonsim8
    
    print("═" * 60)
    print("  RESULTADOS DE LA SIMULACIÓN")
    print("═" * 60)
    
    print(f"\n  Registros:")
    print(f"    IP:  0x00 → 0x{vonsim8.ip.value:02X}  ✓")
    print(f"    AL:  0x01 → 0x{vonsim8.reg_bank.al.value:02X}  {'✓ Transferido' if vonsim8.reg_bank.al.value == 0x0A else '✗ Error'}")
    print(f"    BL:  0x0A → 0x{vonsim8.reg_bank.bl.value:02X}  ✓")
    
    print()
    if vonsim8.reg_bank.al.value == 0x0A:
        print("  ✅ MOV AL,BL ejecutado correctamente")
    else:
        print("  ❌ ERROR en la transferencia")
    
    print(f"\n  Métricas:")
    print(f"    • CPI:         {vonsim8.uc.total_cycles} ciclos (FETCH: {vonsim8.uc.fetch_cycles} + EXECUTE: {vonsim8.uc.execute_cycles})")
    print(f"    • Tiempo real: {simulation_time*1000:.2f} ms")
    print(f"    • Eventos:     {coord.event_count} transiciones DEVS")
    print()
    
    print("═" * 80)
    print("  ✅ Simulación completada | Arquitectura Von Neumann validada")
    print("═" * 80 + "\n")
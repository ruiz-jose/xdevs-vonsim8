# VonSim8 - Simulador DEVS de Arquitectura Von Neumann 8-bit

## 📋 Descripción

**VonSim8** es un simulador de arquitectura Von Neumann de 8 bits implementado utilizando el formalismo **DEVS** (Discrete Event System Specification). El proyecto modela una CPU simplificada que ejecuta instrucciones básicas, demostrando los principios fundamentales de la arquitectura Von Neumann mediante eventos discretos.

El simulador implementa una instrucción `MOV AL, BL` completa con sus ciclos de **FETCH** y **EXECUTE**, modelando detalladamente cada componente hardware y las señales de control que los interconectan.

## 🏗️ Arquitectura del Sistema

El sistema VonSim8 está compuesto por los siguientes componentes modelados como sistemas DEVS:

### Componentes Atómicos

- **IP (Instruction Pointer)**: Registro contador de programa
- **MAR (Memory Address Register)**: Registro de direcciones de memoria
- **MBR (Memory Buffer Register)**: Registro buffer de memoria
- **IR (Instruction Register)**: Registro de instrucción
- **Memory (MEM)**: Memoria unificada de programa y datos
- **Control Unit (UC)**: Unidad de control con máquina de estados
- **Register**: Registros de propósito general (AL, BL, CL, DL)
- **SharedBus**: Bus compartido con arbitraje

### Componentes Acoplados

- **RegisterBank (REG_BANK)**: Banco de 4 registros de 8 bits (AL, BL, CL, DL) con bus interno
- **VonSim8System**: Sistema completo que integra todos los componentes

## 🔄 Ciclo de Instrucción

### Fase FETCH (6 pasos - 8 ciclos)
1. UC → IP (solicita dirección)
2. IP → MAR (transfiere dirección)
3. UC → MEM (mem_read); IP++ (incremento)
4. MEM → MBR (lectura completada)
5. MBR → IR (carga instrucción)
6. IR → UC (recibe opcode)

### Fase EXECUTE (5 pasos - 6 ciclos)
1. Decodificación de instrucción
2. UC → REG_BANK (enable_out BL)
3. BUS ← BL (dato disponible en bus)
4. UC → REG_BANK (enable_in AL)
5. AL ← BUS (transferencia completada)

**Total**: 14 ciclos de reloj para instrucción MOV

## 🚀 Instalación

### Requisitos

- Python >= 3.9
- xDEVS framework v3.0.0

### Pasos de Instalación

1. **Clonar el repositorio**:
```bash
git clone https://github.com/ruiz-jose/xdevs-vonsim8.git
cd xdevs-vonsim8
```

2. **Instalar la librería xDEVS**:

El proyecto incluye el framework xDEVS en el subdirectorio `xdevs.py/`. Para instalarlo:

```powershell
cd xdevs.py
pip install -e .
```

O instalar desde PyPI:
```powershell
pip install xdevs
```

## 💻 Uso

### Ejecución Básica

Para ejecutar la simulación del sistema VonSim8:

```powershell
python vonsim8.py
```

### Salida Esperada

La simulación muestra:

```
═══════════════════════════════════════════════════════════════════════════════
║               SIMULACIÓN DEVS - VONSIM8 (Von Neumann 8-bit)                 ║
═══════════════════════════════════════════════════════════════════════════════
  Instrucción: MOV AL, BL (opcode 0x01)
  Formalismo:  DEVS (Discrete Event System Specification)
═══════════════════════════════════════════════════════════════════════════════

⏳ Ejecutando simulación...

  FASE FETCH - Paso 1/6: UC → IP (solicita dirección)
  ...
  FASE EXECUTE - Paso 1/5: Decodificación
  ...

═══════════════════════════════════════════════════════════════════════════════
  RESULTADOS DE LA SIMULACIÓN
═══════════════════════════════════════════════════════════════════════════════

  Registros:
    IP:  0x00 → 0x01  ✓
    AL:  0x01 → 0x0A  ✓ Transferido
    BL:  0x0A → 0x0A  ✓

  ✅ MOV AL,BL ejecutado correctamente

  Métricas:
    • CPI:         14 ciclos (FETCH: 8 + EXECUTE: 6)
    • Tiempo real: 3.01 ms
    • Eventos:     45 transiciones DEVS
```

## 📊 Características Técnicas

- **Ancho de palabra**: 8 bits
- **CPI (Ciclos Por Instrucción)**: 14 ciclos para MOV
- **Arquitectura**: Von Neumann (memoria unificada)
- **Señalización**: Indexada para registros (AL, BL, CL, DL)
- **Bus**: Compartido con arbitraje temporal
- **Formalismo**: DEVS (eventos discretos)

## 🧪 Estructura del Código

```
vonsim8.py              # Simulador principal
xdevs.py/               # Framework xDEVS (incluido)
  xdevs/
    models.py           # Clases base Atomic y Coupled
    sim.py              # Coordinador y simulador
    factory.py          # Factorías de modelos
    abc/                # Clases abstractas
    celldevs/           # Modelos Cell-DEVS
    examples/           # Ejemplos de uso
    plugins/            # Plugins (CSV, MQTT, SQL, etc.)
```

## 🔬 Componentes xDEVS Utilizados

### Clases Base
- `xdevs.models.Atomic`: Modelos atómicos (componentes individuales)
- `xdevs.models.Coupled`: Modelos acoplados (sistemas jerárquicos)
- `xdevs.models.Port`: Puertos de entrada/salida
- `xdevs.sim.Coordinator`: Coordinador de simulación

### Métodos DEVS Implementados
- `initialize()`: Inicialización del modelo
- `deltint()`: Función de transición interna
- `deltext(e)`: Función de transición externa
- `lambdaf()`: Función de salida
- `exit()`: Finalización del modelo

## 📈 Métricas de Simulación

El simulador proporciona:
- **Ciclos totales**: Total de ciclos de reloj
- **Ciclos FETCH**: Ciclos en fase de búsqueda
- **Ciclos EXECUTE**: Ciclos en fase de ejecución
- **Eventos DEVS**: Número de transiciones de estado
- **Tiempo real**: Tiempo de ejecución de la simulación

## 🎯 Objetivos del Proyecto

1. **Didáctico**: Demostrar arquitectura Von Neumann mediante simulación DEVS
2. **Fidelidad**: Modelar ciclos de reloj y señales de control reales
3. **Modularidad**: Componentes reutilizables y jerárquicos
4. **Verificación**: Validar corrección de transferencias de datos

## 🛠️ Extensiones Futuras

- [ ] Implementar más instrucciones (ADD, SUB, JMP, etc.)
- [ ] Añadir ALU (Unidad Aritmético-Lógica)
- [ ] Implementar flags de estado (Zero, Carry, Overflow)
- [ ] Soporte para interrupciones
- [ ] Modo de memoria separada (Harvard)
- [ ] Visualización gráfica de la ejecución

## 📚 Referencias

- **xDEVS Framework**: [https://github.com/iscar-ucm/xdevs.py](https://github.com/iscar-ucm/xdevs.py)
- **DEVS Formalism**: Zeigler, B.P. (1976). Theory of Modelling and Simulation
- **Von Neumann Architecture**: Von Neumann, J. (1945). First Draft of a Report on the EDVAC

## 👥 Autores

- José L. Ruiz - Implementación del simulador VonSim8
- xDEVS Framework por: Román Cárdenas, Óscar Fernández Sebastián, Kevin Henares, José L. Risco-Martín

## 📄 Licencia

Este proyecto utiliza el framework xDEVS. Consulta `xdevs.py/LICENSE.txt` para más detalles sobre la licencia de xDEVS.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu característica (`git checkout -b feature/NuevaCaracteristica`)
3. Commit tus cambios (`git commit -m 'Añadir nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abre un Pull Request

## 📧 Contacto

Para preguntas o sugerencias sobre VonSim8, abre un issue en el repositorio.
Para consultas sobre xDEVS, visita: [https://github.com/iscar-ucm/xdevs.py](https://github.com/iscar-ucm/xdevs.py)
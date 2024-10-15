# CVSW-TPO-Backend

## Base de datos

### Poblar la base

Listar los "seeders":
```bash
python -m flask seed list
```

Ejecutar seeders:
```bash
python -m flask seed run "<nombre-seeder>"
```

Ejemplo:
```bash
python -m flask seed run Servicios
```

Salida:
```
...
Agregando Servicio: <Servicio None - Medicina General>
Agregando Servicio: <Servicio None - Cardiología>
Agregando Servicio: <Servicio None - Odontología>
Agregando Servicio: <Servicio None - Pediatría>
Agregando Servicio: <Servicio None - Obstetricia>
Agregando Servicio: <Servicio None - Radiología>
Agregando Servicio: <Servicio None - Laboratorio>
Servicios...    [OK]
Committing to database!
```

**¡¡¡Importante!!!** utilizar el siguiente orden:
1. Establecimientos
2. Servicios
3. Empleados

### Restablecer la base

Ejecutar:
```bash
python -m flask seed run Truncar
```

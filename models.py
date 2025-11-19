import json
from datetime import datetime, timedelta

#Excepciones personalizadas para busquedas y operaciones en el sistema

class ClienteInhabilitadoError(Exception):
    pass

class SalaOcupadaError(Exception):
    pass

class PagoRechazadoError(Exception):
    pass

class ProductoAgotadoError(Exception):
    pass

class StockInsuficienteError(Exception):
    pass

# Clase base para las membresías

class MembresiaBase:
    def __init__(self, tipo, precio, entradas_mes, descuento_productos=0, limite_deuda=100):
        self.tipo = tipo
        self.precio = precio
        self.entradas_mes = entradas_mes
        self.descuento_productos = descuento_productos
        self.limite_deuda = limite_deuda
    
    def puede_entrar(self, entradas_usadas):
        return entradas_usadas < self.entradas_mes
    
    def calcular_descuento_producto(self, precio_producto):
        return precio_producto * (self.descuento_productos / 100)
    
    def __str__(self):
        return f"Membresia tipo:{self.tipo} - Precio: {self.precio}$/mes y {self.entradas_mes} entradas"


#Cambiar precios y beneficios
class MembresiaBasica(MembresiaBase):
    def __init__(self):
        super().__init__("Basica", 100, 10, 5, 100)

class MembresiaEstandar(MembresiaBase):
    def __init__(self):
        super().__init__("Estandar", 200, 30, 10, 200)

class MembresiaPremium(MembresiaBase):
    def __init__(self):
        super().__init__("Premium", 350, 80, 15, 350)

class MembresiaEstudiante(MembresiaBase):
    def __init__(self):
        super().__init__("Estudiante", 70, 15, 10, 70)

#Clase para productos

class Producto:
    def __init__(self, id_producto, nombre, precio, stock):
        self.id_producto = id_producto
        self.nombre = nombre
        self.precio = precio
        self.stock = stock
    
    def reducir_stock(self, cantidad):
        if cantidad > self.stock:
            raise StockInsuficienteError(f"Stock insuficiente de {self.nombre}. Stock disponible: {self.stock}")
        self.stock -= cantidad

    def reponer_stock(self, cantidad):
        self.stock += cantidad
    
    def __str__(self):
        return f"Producto: {self.nombre} - ID: {self.id_producto}  - ${self.precio} (Stock: {self.stock})"
    

#Clase para clientes

class Cliente:
    def __init__(self, id_cliente, nombre, correo, membresia):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.correo = correo
        self.membresia = membresia
        self.activo = True
        self.entradas_usadas = 0
        self.deuda_renovacion = 0
        self.reservas = []
        self.compras = []
        self.fecha_ultimo_uso = datetime.now()

    def puede_entrar(self):
        if not self.activo:
            return False, "Cliente inactivo"
        
        if self.deuda_renovacion >= self.membresia.limite_deuda:
            self.activo = False
            return False, "Membresia suspendida por deuda"
        
        if not self.membresia.puede_entrar(self.entradas_usadas):
            return False, "Limite de entradas alcanzado"
        
        return True, "Puede entrar"
    
    #Mejorar uso de mensaje
    def usar_entrada(self):
        puede, mensaje = self.puede_entrar()
        if not puede:
            return False, mensaje
        
        self.entradas_usadas += 1
        self.fecha_ultimo_uso = datetime.now()
        return True, "Entrada registrada"
    
    def comprar_producto(self, producto, cantidad):
        if producto.stock < cantidad:
            raise ProductoAgotadoError(f"Producto {producto.nombre} agotado o stock insuficiente")
        
        descuento = self.membresia.calcular_descuento_producto(producto.precio)
        precio_final = (producto.precio - descuento) * cantidad
        
        producto.reducir_stock(cantidad)

        compra = {
            "fecha": datetime.now(),
            "producto": producto.nombre,
            "cantidad": cantidad,
            "precio_unitario": producto.precio,
            "descuento": descuento * cantidad,
            "total": precio_final
        }
        self.compras.append(compra)
        
        return compra
    
    def renovar_membresia(self):
        self.deuda_renovacion += self.membresia.precio
        
        if self.deuda_renovacion >= self.membresia.limite_deuda:
            self.activo = False
            return "Membresia suspendida por deuda acumulada"
        
        return f"Renovacion registrada. Deuda: ${self.deuda_renovacion}"
    
    def pagar_renovacion(self, monto):
        if monto <= 0:
            raise PagoRechazadoError("Monto debe ser positivo")
        
        if monto > self.deuda_renovacion:
            raise PagoRechazadoError(f"Monto excede la deuda. Deuda actual: ${self.deuda_renovacion}")
        
        self.deuda_renovacion -= monto

        if not self.activo and self.deuda_renovacion < self.membresia.limite_deuda:
            self.activo = True
        
        return f"Pago aplicado. Deuda restante: ${self.deuda_renovacion}"
    
    def cancelar_membresia(self):
        if not self.activo:
            return "La membresia ya esta inactiva"
        
        self.activo = False
        self.deuda_renovacion += self.membresia.precio
        return "Membresia cancelada. Se cobro el mes corriente"
    
    def __str__(self):
        estado = "Activo" if self.activo else "Inactivo"

        return f"Nombre: {self.nombre} ID: ({self.id_cliente}) - {self.membresia.tipo} - Entradas: {self.entradas_usadas}/{self.membresia.entradas_mes} - Deuda: ${self.deuda_renovacion} - {estado}"
    

#Clase para salas de reuniones

class Sala:
    def __init__(self, id_sala, nombre, capacidad):
        self.id_sala = id_sala
        self.nombre = nombre
        self.capacidad = capacidad
        self.reservas = []
    
    def esta_disponible(self, fecha_hora, duracion_horas):
        fin_reserva = fecha_hora + timedelta(hours=duracion_horas)
        
        for reserva in self.reservas:
            if (fecha_hora < reserva.fin and fin_reserva > reserva.inicio):
                return False
        return True
    
    def __str__(self):
        return f"ID Sala: {self.id_sala} - {self.nombre}. (Capacidad: {self.capacidad})"
    

#Clase para reservas de salas

class Reserva:
    def __init__(self, id_reserva, cliente, sala, inicio, duracion_horas):
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.sala = sala
        self.inicio = inicio
        self.duracion_horas = duracion_horas
        self.fin = inicio + timedelta(hours=duracion_horas)
    
    def __str__(self):
        return f"Reserva {self.id_reserva}: {self.cliente.nombre} - {self.sala.nombre} - {self.inicio.strftime('%d/%m %H:%M')}"
    
#Clase para gestionar el coworking

class Coworking:
    def __init__(self):
        self.clientes = {}
        self.salas = {}
        self.reservas = {}
        self.productos = {}
        self.prox_id_reserva = 1
        
    
    def inicializar_datos_default(self):
        self._crear_salas_si_no_existen()
        self._crear_productos_si_no_existen()
    
    def _crear_salas_si_no_existen(self):
        if not self.salas:
            salas = [
                Sala("S1", "Sala Pequena", 4),
                Sala("S2", "Sala Mediana", 8),
                Sala("S3", "Sala Grande", 15),
                Sala("S4", "Sala Reuniones", 6),
                Sala("S5", "Oficina Privada", 2)
            ]
            for sala in salas:
                self.agregar_sala(sala)
            print("Salas por defecto creadas")

    def _crear_productos_si_no_existen(self):
        if not self.productos:  
            productos = [
                Producto("P1", "Cafe", 2, 100),
                Producto("P2", "Te", 1.5, 100),
                Producto("P3", "Agua", 1, 200),
                Producto("P4", "Snack", 3, 50),
                Producto("P5", "Sandwich", 5, 30),
                Producto("P6", "Refresco", 2.5, 80),
                Producto("P7", "Ensalada", 8, 20)
            ]
            for producto in productos:
                self.agregar_producto(producto)
            print("Productos por defecto creados")


    #Registro de ventas
    def _registrar_venta(self, tipo_venta, cliente_id, descripcion, monto):
        """Registra una venta en el historial del negocio"""
        venta = {
            "fecha": datetime.now().isoformat(),  # Ya es string, no datetime
            "tipo": tipo_venta,
            "cliente_id": cliente_id,
            "descripcion": descripcion,
            "monto": monto
        }
        
        try:
            with open("datos/ventas.json", "r", encoding='utf-8') as f:
                ventas = json.load(f)
        except FileNotFoundError:
            ventas = []
        
        ventas.append(venta)
        
        with open("datos/ventas.json", "w", encoding='utf-8') as f:
            json.dump(ventas, f, indent=2, ensure_ascii=False)
        
        return venta
    
    def obtener_historial_ventas(self):
        """Obtiene el historial completo de ventas"""
        try:
            with open("datos/ventas.json", "r", encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return []
        
    def agregar_cliente(self, cliente):
        if cliente.id_cliente in self.clientes:
            raise ClienteInhabilitadoError("Cliente ya existe")
        self.clientes[cliente.id_cliente] = cliente
    
    def agregar_sala(self, sala):
        if sala.id_sala in self.salas:
            print(f"Sala {sala.id_sala} ya existe, omitiendo")
            return
        self.salas[sala.id_sala] = sala
    
    def agregar_producto(self, producto):
        if producto.id_producto in self.productos:
            print(f"Producto {producto.id_producto} ya existe, omitiendo")
            return
        self.productos[producto.id_producto] = producto
    
    def buscar_cliente(self, id_cliente):
        return self.clientes.get(id_cliente)
    
    def buscar_sala(self, id_sala):
        return self.salas.get(id_sala)
    
    def buscar_producto(self, id_producto):
        return self.productos.get(id_producto)
    
    def reservar_sala(self, id_cliente, id_sala, fecha_hora, duracion_horas=1):
        cliente = self.buscar_cliente(id_cliente)
        if not cliente:
            raise ClienteInhabilitadoError("Cliente no encontrado")
        
        puede, mensaje = cliente.usar_entrada()
        if not puede:
            raise ClienteInhabilitadoError(mensaje)
        
        sala = self.buscar_sala(id_sala)
        if not sala:
            raise SalaOcupadaError("Sala no encontrada")
        
        if not sala.esta_disponible(fecha_hora, duracion_horas):
            raise SalaOcupadaError("Sala no disponible")
        
        reserva = Reserva(f"R{self.prox_id_reserva}", cliente, sala, fecha_hora, duracion_horas)
        
        self.reservas[reserva.id_reserva] = reserva
        cliente.reservas.append(reserva)
        sala.reservas.append(reserva)
        self.prox_id_reserva += 1
        
        return reserva
    
    def comprar_producto(self, id_cliente, id_producto, cantidad=1):
        cliente = self.buscar_cliente(id_cliente)
        if not cliente:
            raise ClienteInhabilitadoError("Cliente no encontrado")
        
        producto = self.buscar_producto(id_producto)
        if not producto:
            raise ProductoAgotadoError("Producto no encontrado")
        
        compra = cliente.comprar_producto(producto, cantidad)
        
        # Registrar en historial de ventas del negocio
        self._registrar_venta(
            tipo_venta="producto",
            cliente_id=id_cliente,
            descripcion=f"{producto.nombre} x{cantidad}",
            monto=compra['total']
        )
        
        return compra
    
    def reponer_stock(self, id_producto, cantidad):
        producto = self.buscar_producto(id_producto)
        if not producto:
            raise ProductoAgotadoError("Producto no encontrado")
        
        producto.reponer_stock(cantidad)
        return f"Stock de {producto.nombre} repuesto: {producto.stock} unidades"
    
    def renovar_membresias_automatico(self):
        resultados = []
        for cliente in self.clientes.values():
            if cliente.activo:
                resultado = cliente.renovar_membresia()
                
                # Registrar en historial de ventas si se renovo
                if "Renovacion registrada" in resultado:
                    self._registrar_venta(
                        tipo_venta="membresia",
                        cliente_id=cliente.id_cliente,
                        descripcion=f"Renovacion {cliente.membresia.tipo}",
                        monto=cliente.membresia.precio
                    )
                
                resultados.append(f"{cliente.nombre}: {resultado}")
        return resultados
    
    def cancelar_membresia(self, id_cliente):
        cliente = self.buscar_cliente(id_cliente)
        if not cliente:
            raise ClienteInhabilitadoError("Cliente no encontrado")
        
        resultado = cliente.cancelar_membresia()
        
        # Registrar en historial de ventas
        self._registrar_venta(
            tipo_venta="membresia",
            cliente_id=id_cliente,
            descripcion=f"Cancelacion {cliente.membresia.tipo}",
            monto=cliente.membresia.precio
        )
        
        return resultado
    
    def pagar_renovacion(self, id_cliente, monto):
        cliente = self.buscar_cliente(id_cliente)
        if not cliente:
            raise PagoRechazadoError("Cliente no encontrado")
        
        resultado = cliente.pagar_renovacion(monto)
        
        # Registrar en historial de ventas
        self._registrar_venta(
            tipo_venta="pago_renovacion",
            cliente_id=id_cliente,
            descripcion=f"Pago deuda renovacion",
            monto=monto
        )
        
        return resultado
    
    def obtener_estadisticas(self):
        stats = {
            "total_clientes": len(self.clientes),
            "clientes_activos": sum(1 for c in self.clientes.values() if c.activo),
            "total_reservas": len(self.reservas),
            "membresias_por_tipo": {},
            "valor_inventario": 0,
            "productos_bajo_stock": [],
            "ventas_totales": 0,
            "ventas_por_tipo": {}
        }
        
        for cliente in self.clientes.values():
            tipo = cliente.membresia.tipo
            stats["membresias_por_tipo"][tipo] = stats["membresias_por_tipo"].get(tipo, 0) + 1
        
        for producto in self.productos.values():
            stats["valor_inventario"] += producto.precio * producto.stock
            if producto.stock < 10:
                stats["productos_bajo_stock"].append(producto.nombre)
        
        # Estadísticas de ventas
        historial_ventas = self.obtener_historial_ventas()
        for venta in historial_ventas:
            stats["ventas_totales"] += venta["monto"]
            tipo = venta["tipo"]
            stats["ventas_por_tipo"][tipo] = stats["ventas_por_tipo"].get(tipo, 0) + venta["monto"]
        
        return stats
    def __len__(self):
        return len(self.clientes)
    
    def __iter__(self):
        return iter(self.clientes.values())
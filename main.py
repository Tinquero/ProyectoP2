from models import *
from persistencia import *
from datetime import datetime, timedelta
import os

def main():
    coworking = Coworking()
    os.makedirs("datos", exist_ok=True)
    
    cargar_datos(coworking)
    
    tipos_membresia = {
        "1": MembresiaBasica(),
        "2": MembresiaEstandar(),
        "3": MembresiaPremium(),
        "4": MembresiaEstudiante()
    }
    
    while True:
        print("\n=== SISTEMA DE COWORKING ===")
        print("1. Registrar cliente")
        print("2. Listar clientes")
        print("3. Reservar sala")
        print("4. Comprar producto")
        print("5. Pagar renovacion")
        print("6. Cancelar membresia")
        print("7. Reponer stock")
        print("8. Ver estadisticas")
        print("9. Renovar membresias (simulacion)")
        print("10. Ver historial de ventas")
        print("11. Salir")

        opcion = input("\nSeleccione una opcion: ")
        
        if opcion == "1":
            registrar_cliente(coworking, tipos_membresia)
        elif opcion == "2":
            listar_clientes(coworking)
        elif opcion == "3":
            reservar_sala(coworking)
        elif opcion == "4":
            comprar_producto(coworking)
        elif opcion == "5":
            pagar_renovacion(coworking)
        elif opcion == "6":
            cancelar_membresia(coworking)
        elif opcion == "7":
            reponer_stock(coworking)
        elif opcion == "8":
            ver_estadisticas(coworking)
        elif opcion == "9":
            renovar_membresias(coworking)
        elif opcion == "10":
            ver_historial_ventas(coworking)
        elif opcion == "11":
            guardar_datos(coworking)
            print("Datos guardados. Sesion finalizada")
            break
        else:
            print("Opcion no valida")

def registrar_cliente(coworking, tipos_membresia):
    print("\n--- REGISTRAR CLIENTE ---")
    id_cliente = input("ID del cliente: ")
    nombre = input("Nombre: ")
    correo = input("Correo: ")
    
    print("\nTipos de membresia:")
    for key, mem in tipos_membresia.items():
        print(f"{key}. {mem}")
    
    tipo = input("Seleccione membresia (1-4): ")
    membresia = tipos_membresia.get(tipo, MembresiaBasica())
    
    cliente = Cliente(id_cliente, nombre, correo, membresia)
    try:
        coworking.agregar_cliente(cliente)
        print(f"Cliente {nombre} registrado exitosamente con membresia {membresia}.")
    except ClienteInhabilitadoError as e:
        print(f"Error: {e}")

def listar_clientes(coworking):
    print("\n--- LISTA DE CLIENTES ---")
    if len(coworking) == 0:
        print("No hay clientes registrados.")
    else:
        for cliente in coworking:
            print(cliente)

def reservar_sala(coworking):
    print("\n--- RESERVAR SALA ---")
    id_cliente = input("ID del cliente: ")
    
    print("\nSalas disponibles:")
    for sala in coworking.salas.values():
        print(sala)
    
    id_sala = input("ID de la sala: ")
    
    try:
        horas_desde_ahora = int(input("Horas hasta la reserva: "))
        duracion = int(input("Duración en horas: "))
        
        fecha_reserva = datetime.now() + timedelta(hours=horas_desde_ahora)
        reserva = coworking.reservar_sala(id_cliente, id_sala, fecha_reserva, duracion)
        
        print(f"Reserva exitosa: {reserva}")
        
    except (ClienteInhabilitadoError, SalaOcupadaError, ValueError) as e:
        print(f"Error: {e}")

def comprar_producto(coworking):
    print("\n--- COMPRAR PRODUCTO ---")
    id_cliente = input("ID del cliente: ")
    
    print("\nProductos disponibles:")
    for producto in coworking.productos.values():
        print(producto)
    
    id_producto = input("ID del producto: ")
    cantidad = int(input("Cantidad: "))
    
    try:
        compra = coworking.comprar_producto(id_cliente, id_producto, cantidad)
        print(f"Compra exitosa: {compra['producto']} x{compra['cantidad']} - Total: ${compra['total']}")
    except (ClienteInhabilitadoError, ProductoAgotadoError, ValueError) as e:
        print(f"Error: {e}")

def pagar_renovacion(coworking):
    print("\n--- PAGAR RENOVACION ---")
    id_cliente = input("ID del cliente: ")
    monto = float(input("Monto a pagar: $"))
    
    try:
        resultado = coworking.pagar_renovacion(id_cliente, monto)
        print(resultado)
    except (PagoRechazadoError, ValueError) as e:
        print(f"Error: {e}")

def cancelar_membresia(coworking):
    print("\n--- CANCELAR MEMBRESÍA ---")
    id_cliente = input("ID del cliente: ")
    
    try:
        resultado = coworking.cancelar_membresia(id_cliente)
        print(resultado)
    except ClienteInhabilitadoError as e:
        print(f"Error: {e}")

def reponer_stock(coworking):
    print("\n--- REPONER STOCK ---")
    print("Productos disponibles:")
    for producto in coworking.productos.values():
        print(producto)
    
    id_producto = input("ID del producto: ")
    cantidad = int(input("Cantidad a reponer: "))
    
    try:
        resultado = coworking.reponer_stock(id_producto, cantidad)
        print(resultado)
    except ProductoAgotadoError as e:
        print(f"Error: {e}")

def ver_estadisticas(coworking):
    print("\n--- ESTADISTICAS DEL SISTEMA ---")
    stats = coworking.obtener_estadisticas()
    
    print(f"Total clientes: {stats['total_clientes']}")
    print(f"Clientes activos: {stats['clientes_activos']}")
    print(f"Total reservas: {stats['total_reservas']}")
    print(f"Valor del inventario: ${stats['valor_inventario']}")
    print(f"Ventas totales: ${stats['ventas_totales']}")
    
    print("\nMembresias por tipo:")
    for tipo, cantidad in stats['membresias_por_tipo'].items():
        print(f"  {tipo}: {cantidad}")
    
    print("\nVentas por tipo:")
    for tipo, monto in stats['ventas_por_tipo'].items():
        print(f"  {tipo}: ${monto}")
    
    if stats['productos_bajo_stock']:
        print(f"\nProductos con stock bajo: {', '.join(stats['productos_bajo_stock'])}")

def renovar_membresias(coworking):
    print("\n--- RENOVACION AUTOMATICA DE MEMBRESIAS ---")
    resultados = coworking.renovar_membresias_automatico()
    if resultados:
        for resultado in resultados:
            print(resultado)
    else:
        print("No hay clientes activos para renovar")

def ver_historial_ventas(coworking):
    print("\n--- HISTORIAL DE VENTAS DEL NEGOCIO ---")
    ventas = coworking.obtener_historial_ventas()
    
    if not ventas:
        print("No hay ventas registradas")
        return
    
    ventas_ordenadas = sorted(ventas, key=lambda x: x['fecha'], reverse=True)
    
    total_general = 0
    print("\nUltimas ventas:")
    print("-" * 80)
    for venta in ventas_ordenadas[:20]:
        fecha = datetime.fromisoformat(venta['fecha']).strftime('%d/%m/%Y %H:%M')
        print(f"{fecha} | {venta['tipo']:15} | {venta['cliente_id']:10} | {venta['descripcion']:30} | ${venta['monto']:>8}")
        total_general += venta['monto']
    
    print("-" * 80)
    print(f"Total general en historial: ${total_general}")
    
    ventas_por_tipo = {}
    for venta in ventas:
        tipo = venta['tipo']
        ventas_por_tipo[tipo] = ventas_por_tipo.get(tipo, 0) + venta['monto']
    
    print("\nResumen por tipo de venta:")
    for tipo, total in ventas_por_tipo.items():
        print(f"  {tipo}: ${total}")

if __name__ == "__main__":
    main()
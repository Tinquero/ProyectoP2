import json
from datetime import datetime
from models import MembresiaBasica, MembresiaEstandar, MembresiaPremium, MembresiaEstudiante, Cliente, Producto

def guardar_datos(coworking, archivo_clientes="datos/clientes.json", archivo_productos="datos/productos.json"):
    datos_clientes = []
    for cliente in coworking.clientes.values():
        # Convertir datetime a string ISO
        compras_serializables = []
        for compra in cliente.compras:
            compra_serializable = compra.copy()
            compra_serializable['fecha'] = compra['fecha'].isoformat()  # Convertir fecha
            compras_serializables.append(compra_serializable)
        
        datos_clientes.append({
            'id_cliente': cliente.id_cliente,
            'nombre': cliente.nombre,
            'correo': cliente.correo,
            'membresia_tipo': cliente.membresia.tipo,
            'activo': cliente.activo,
            'entradas_usadas': cliente.entradas_usadas,
            'deuda_renovacion': cliente.deuda_renovacion,
            'fecha_ultimo_uso': cliente.fecha_ultimo_uso.isoformat(),  # Convertir fecha
            'compras': compras_serializables  # Usar la versión con fechas convertidas
        })
    
    with open(archivo_clientes, 'w', encoding='utf-8') as f:
        json.dump(datos_clientes, f, indent=2, ensure_ascii=False)
    
    datos_productos = []
    for producto in coworking.productos.values():
        datos_productos.append({
            'id_producto': producto.id_producto,
            'nombre': producto.nombre,
            'precio': producto.precio,
            'stock': producto.stock
        })
    
    with open(archivo_productos, 'w', encoding='utf-8') as f:
        json.dump(datos_productos, f, indent=2, ensure_ascii=False)

def cargar_datos(coworking, archivo_clientes="datos/clientes.json", archivo_productos="datos/productos.json"):
    """Carga los datos del sistema desde archivos JSON"""
    
    tipos_membresia = {
        "Basica": MembresiaBasica(),
        "Estandar": MembresiaEstandar(),
        "Premium": MembresiaPremium(),
        "Estudiante": MembresiaEstudiante()
    }
    
    # Bandera para saber si cargamos datos existentes
    datos_existen = False
    
    # Cargar clientes
    try:
        with open(archivo_clientes, 'r', encoding='utf-8') as f:
            datos_clientes = json.load(f)
        
        for datos in datos_clientes:
            membresia = tipos_membresia.get(datos['membresia_tipo'], MembresiaBasica())
            cliente = Cliente(
                datos['id_cliente'],
                datos['nombre'],
                datos['correo'],
                membresia
            )
            cliente.activo = datos['activo']
            cliente.entradas_usadas = datos['entradas_usadas']
            cliente.deuda_renovacion = datos['deuda_renovacion']
            cliente.fecha_ultimo_uso = datetime.fromisoformat(datos['fecha_ultimo_uso'])
            
            compras_cargadas = []
            for compra in datos['compras']:
                compra_cargada = compra.copy()
                if 'fecha' in compra_cargada:
                    compra_cargada['fecha'] = datetime.fromisoformat(compra_cargada['fecha'])
                compras_cargadas.append(compra_cargada)
            cliente.compras = compras_cargadas
            
            coworking.agregar_cliente(cliente)
        
        datos_existen = True
    
    except FileNotFoundError:
        print("No se encontraron datos de clientes.")
    
    # Cargar productos
    try:
        with open(archivo_productos, 'r', encoding='utf-8') as f:
            datos_productos = json.load(f)
        
        for datos in datos_productos:
            producto = Producto(
                datos['id_producto'],
                datos['nombre'],
                datos['precio'],
                datos['stock']
            )
            coworking.agregar_producto(producto)
        
        datos_existen = True
    
    except FileNotFoundError:
        print("No se encontraron datos de productos.")
    
    # Si NO cargamos datos existentes, crear datos por defecto
    if not datos_existen:
        print("Creando datos por defecto...")
        coworking.inicializar_datos_default()
    else:
        print("Datos existentes cargados correctamente")
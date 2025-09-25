from models.cliente import Cliente
from models.factura import Factura
from extensions import db

from flask import Blueprint, render_template, request, jsonify
from sqlalchemy import func, extract, and_, or_
from datetime import datetime, timedelta
from collections import defaultdict
import calendar



reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@reportes_bp.route('/')
def menu_reportes():
    """Página principal de reportes"""
    return render_template('reportes/menu_reportes.html')

@reportes_bp.route('/facturas_por_cliente')
def facturas_por_cliente():
    cliente_id = request.args.get('cliente_id', type=int)
    estado = request.args.get('estado', '')

    clientes = Cliente.query.order_by(Cliente.nombre).all()
    
    query = Factura.query.join(Cliente)
    if cliente_id:
        query = query.filter(Cliente.id_cliente == cliente_id)
    if estado:
        query = query.filter(Factura.estado == estado)
    
    facturas = query.all()
    
    datos_reporte = None
    if facturas:
        if cliente_id:
            cliente = Cliente.query.get(cliente_id)
            total_facturas = len(facturas)
            total_monto = sum(float(f.total) for f in facturas)
            total_pagadas = sum(1 for f in facturas if f.estado == 'pagada')
            
            datos_reporte = {
                'modo': 'detalle',
                'cliente': cliente,
                'facturas': facturas,
                'total_facturas': total_facturas,
                'total_monto': total_monto,
                'total_pagadas': total_pagadas
            }
        else:
            from collections import defaultdict
            clientes_dict = defaultdict(lambda: {
                'cliente': None,
                'total_facturas': 0,
                'total_monto': 0,
                'pendientes': 0,
                'pagadas': 0,
                'anuladas': 0
            })
            
            for factura in facturas:
                cliente_key = factura.id_cliente
                cliente_data = clientes_dict[cliente_key]
                
                if cliente_data['cliente'] is None:
                    cliente_data['cliente'] = factura.cliente
                
                cliente_data['total_facturas'] += 1
                cliente_data['total_monto'] += float(factura.total)
                
                if factura.estado == 'pendiente':
                    cliente_data['pendientes'] += 1
                elif factura.estado == 'pagada':
                    cliente_data['pagadas'] += 1
                elif factura.estado == 'cancelada':
                    cliente_data['anuladas'] += 1
            
            clientes_data = list(clientes_dict.values())
            clientes_data.sort(key=lambda x: x['total_monto'], reverse=True)
            
            datos_reporte = {
                'modo': 'general',
                'clientes': clientes_data
            }
    
    return render_template(
        'reportes/facturas_por_cliente.html',
        clientes=clientes,
        datos_reporte=datos_reporte
    )


@reportes_bp.route('/detalle-cliente-ajax')
def detalle_cliente_ajax():
    """Endpoint AJAX para obtener el detalle de facturas de un cliente"""
    cliente_id = request.args.get('cliente_id', type=int)
    
    if not cliente_id:
        return jsonify({'error': 'Cliente no especificado'}), 400
    
    cliente = Cliente.query.get_or_404(cliente_id)
    facturas = Factura.query.filter_by(cliente_id=cliente_id)\
                            .order_by(Factura.fecha_creacion.desc()).all()

    html = f"""
    <div class="table-responsive">
        <table class="table table-sm">
            <thead>
                <tr>
                    <th>Número</th>
                    <th>Fecha</th>
                    <th>Estado</th>
                    <th class="text-right">Total</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for factura in facturas:
        estado_class = {
            'pendiente': 'warning',
            'pagada': 'success',
            'anulada': 'danger'
        }.get(factura.estado, 'secondary')
        
        html += f"""
                <tr>
                    <td>#{factura.numero}</td>
                    <td>{factura.fecha_creacion.strftime('%d/%m/%Y')}</td>
                    <td><span class="badge badge-{estado_class}">{factura.estado.title()}</span></td>
                    <td class="text-right">${factura.total:.2f}</td>
                </tr>
        """
    
    if not facturas:
        html += """
                <tr>
                    <td colspan="4" class="text-center text-muted">No hay facturas registradas</td>
                </tr>
        """
    
    html += """
            </tbody>
        </table>
    </div>
    """
    
    return jsonify({
        'cliente_nombre': f"{cliente.nombre} {cliente.apellido}",
        'html': html
    })

@reportes_bp.route('/ventas-por-periodo')
def ventas_por_periodo():
    """Reporte de ventas por período"""
    fecha_inicio_str = request.args.get('fecha_inicio', '')
    fecha_fin_str = request.args.get('fecha_fin', '')
    estado = request.args.get('estado', '')

    hoy = datetime.now()
    if not fecha_inicio_str:
        fecha_inicio = datetime(hoy.year, hoy.month, 1)
    else:
        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d')
    
    if not fecha_fin_str:
        if hoy.month == 12:
            fecha_fin = datetime(hoy.year + 1, 1, 1) - timedelta(days=1)
        else:
            fecha_fin = datetime(hoy.year, hoy.month + 1, 1) - timedelta(days=1)
    else:
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d')

    query = Factura.query.filter(
        Factura.fecha_creacion >= fecha_inicio,
        Factura.fecha_creacion <= fecha_fin
    )

    if estado:
        query = query.filter(Factura.estado == estado)

    facturas = query.order_by(Factura.fecha_creacion.desc()).all()
    
    datos_reporte = None
    if facturas:
        periodos_dict = defaultdict(lambda: {
            'total_facturas': 0,
            'total_ventas': 0,
            'pendientes': 0,
            'pagadas': 0,
            'anuladas': 0,
            'fecha': None
        })
        
        for factura in facturas:
            fecha_clave = factura.fecha_creacion.date()
            clave = fecha_clave.strftime('%Y-%m-%d')
            
            # Acumular datos
            periodos_dict[clave]['total_facturas'] += 1
            periodos_dict[clave]['total_ventas'] += float(factura.total)
            periodos_dict[clave]['fecha'] = fecha_clave

            if factura.estado == 'pendiente':
                periodos_dict[clave]['pendientes'] += 1
            elif factura.estado == 'pagada':
                periodos_dict[clave]['pagadas'] += 1
            elif factura.estado == 'cancelada':
                periodos_dict[clave]['anuladas'] += 1

        periodos_list = []
        for clave in sorted(periodos_dict.keys(), reverse=True):
            periodo = periodos_dict[clave]
            periodos_list.append(periodo)

        total_facturas = sum(p['total_facturas'] for p in periodos_list)
        total_ventas = sum(p['total_ventas'] for p in periodos_list)
        mayor_venta = max(p['total_ventas'] for p in periodos_list) if periodos_list else 0
        promedio_diario = total_ventas / len(periodos_list) if periodos_list else 0
        
        datos_reporte = {
            'periodos': periodos_list,
            'total_facturas': total_facturas,
            'total_ventas': total_ventas,
            'mayor_venta': mayor_venta,
            'promedio_diario': promedio_diario,
            'total_pendientes': sum(p['pendientes'] for p in periodos_list),
            'total_pagadas': sum(p['pagadas'] for p in periodos_list),
            'total_anuladas': sum(p['anuladas'] for p in periodos_list)
        }
    
    return render_template('reportes/ventas_por_periodo.html',
                            datos_reporte=datos_reporte)

def obtener_nombre_mes(numero_mes):
    """Obtener el nombre del mes en español"""
    meses = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    return meses[numero_mes - 1] if 1 <= numero_mes <= 12 else str(numero_mes)
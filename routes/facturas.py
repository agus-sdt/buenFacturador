from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.factura import Factura
from models.detalle_factura import DetalleFactura
from models.cliente import Cliente
from models.producto import Producto
from datetime import datetime, timezone
from decimal import Decimal

facturas_bp = Blueprint("facturas", __name__, url_prefix="/facturas")

@facturas_bp.route("/")
@login_required
def lista_facturas():
    facturas = Factura.query.order_by(Factura.fecha.desc()).all()
    return render_template("facturas/lista_facturas.html", facturas=facturas)

@facturas_bp.route("/nueva", methods=["GET", "POST"])
@login_required
def nueva_factura():
    if request.method == "POST":
        try:
            id_cliente = request.form["id_cliente"]
            observaciones = request.form.get("observaciones", "")

            ultimo_numero = db.session.query(db.func.max(Factura.numero_factura)).scalar()
            if ultimo_numero:
                numero = int(ultimo_numero.split('-')[1]) + 1
            else:
                numero = 1
            numero_factura = f"FAC-{numero:06d}"

            factura = Factura(
                numero_factura=numero_factura,
                id_cliente=id_cliente,
                observaciones=observaciones,
                id_usuario_creador=current_user.id_usuario
            )

            db.session.add(factura)
            db.session.flush()

            productos = request.form.getlist("id_producto[]")
            cantidades = request.form.getlist("cantidad[]")
            precios = request.form.getlist("precio[]")

            for i, id_producto in enumerate(productos):
                if id_producto and cantidades[i] and precios[i]:
                    producto = Producto.query.get(id_producto)
                    cantidad = int(cantidades[i])
                    precio = Decimal(str(precios[i]))
                    subtotal_calculado = Decimal(str(precio)) * Decimal(str(cantidad))

                    detalle = DetalleFactura(
                        id_factura=factura.id_factura,
                        id_producto=id_producto,
                        descripcion_producto=producto.descripcion,
                        precio_unitario=precio,
                        cantidad=cantidad,
                        subtotal=subtotal_calculado
                    )
                    db.session.add(detalle)

                    producto.stock -= cantidad

            db.session.flush()
            factura.calcular_totales()
            db.session.add(factura)

            db.session.commit()
            flash(f"Factura {factura.numero_factura} creada correctamente", "success")
            return redirect(url_for("facturas.ver_factura", id=factura.id_factura))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear la factura: {e}", "error")

    clientes = Cliente.query.all()
    productos = Producto.query.filter(Producto.stock > 0).all()
    return render_template("facturas/nueva_factura.html", clientes=clientes, productos=productos)

@facturas_bp.route("/ver/<int:id>")
@login_required
def ver_factura(id):
    factura = Factura.query.get_or_404(id)
    return render_template("facturas/ver_factura.html", factura=factura)

@facturas_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_factura(id):
    factura = Factura.query.get_or_404(id)

    if factura.estado != 'pendiente':
        flash("Solo se pueden editar facturas pendientes", "error")
        return redirect(url_for("facturas.ver_factura", id=id))
    
    if request.method == "POST":
        try:
            factura.id_cliente = request.form["id_cliente"]
            factura.observaciones = request.form.get("observaciones", "")

            detalles_actuales = db.session.query(DetalleFactura).filter_by(id_factura=factura.id_factura).all()

            for detalle in detalles_actuales:
                producto = db.session.query(Producto).get(detalle.id_producto)
                if producto:
                    producto.stock += detalle.cantidad

            db.session.query(DetalleFactura).filter_by(id_factura=factura.id_factura).delete()
            db.session.flush()

            productos = request.form.getlist("id_producto[]")
            cantidades = request.form.getlist("cantidad[]")
            precios = request.form.getlist("precio[]")

            for i, id_producto in enumerate(productos):
                if id_producto and cantidades[i] and precios[i]:
                    producto = Producto.query.get(id_producto)
                    cantidad = int(cantidades[i])
                    precio = Decimal(str(precios[i]))
                    subtotal_calculado = Decimal(str(precio)) * Decimal(str(cantidad))
                    
                    detalle = DetalleFactura(
                        id_factura=factura.id_factura,
                        id_producto=id_producto,
                        descripcion_producto=producto.descripcion,
                        precio_unitario=precio,
                        cantidad=cantidad,
                        subtotal=subtotal_calculado
                    )
                    db.session.add(detalle)
                    
                    producto.stock -= cantidad

            db.session.flush()

            db.session.refresh(factura)

            factura.calcular_totales()
            db.session.add(factura)
            
            db.session.commit()
            flash("Factura actualizada correctamente", "success")
            return redirect(url_for("facturas.ver_factura", id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar la factura: {e}", "error")
    
    clientes = Cliente.query.all()
    productos = Producto.query.all()
    return render_template("facturas/editar_factura.html", factura=factura, clientes=clientes, productos=productos)

@facturas_bp.route("/eliminar/<int:id>")
@login_required
def eliminar_factura(id):
    factura = Factura.query.get_or_404(id)
    
    try:
        for detalle in factura.detalles:
            producto = detalle.producto
            producto.stock += detalle.cantidad
        
        db.session.delete(factura)
        db.session.commit()
        
        flash(f'Factura {factura.numero_factura} eliminada correctamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar factura: {e}', 'error')
    
    return redirect(url_for('facturas.lista_facturas'))

@facturas_bp.route("/cambiar-estado/<int:id>/<nuevo_estado>")
@login_required
def cambiar_estado(id, nuevo_estado):
    factura = Factura.query.get_or_404(id)
    
    if nuevo_estado in ['pendiente', 'pagada', 'cancelada']:
        factura.estado = nuevo_estado
        db.session.add(factura)
        db.session.commit()
        flash(f'Estado de factura actualizado a: {nuevo_estado}', 'success')
    else:
        flash('Estado inválido', 'error')
    
    return redirect(url_for('facturas.ver_factura', id=id))

@facturas_bp.route("/api/producto/<int:id>")
@login_required
def api_producto(id):
    producto = Producto.query.get_or_404(id)
    return jsonify({
        'id': producto.id_producto,
        'descripcion': producto.descripcion,
        'precio': float(producto.precio),
        'stock': producto.stock
    })
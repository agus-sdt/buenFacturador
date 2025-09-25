from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.producto import Producto
from sqlalchemy import DECIMAL

productos_bp = Blueprint("productos", __name__, url_prefix="/productos")

@productos_bp.route("/")
def lista_productos():
    productos = Producto.query.all()
    return render_template("productos/listaProductos.html", productos=productos)

@productos_bp.route("/nuevoProducto", methods=["GET", "POST"])
def nuevo_producto():
    if request.method == "POST":
        descripcion = request.form["descripcion"]
        precio = float(request.form["precio"])
        stock = int(request.form["stock"]) if request.form["stock"] else 0

        producto = Producto(
            descripcion=descripcion,
            precio=precio,
            stock=stock
        )
        
        try:
            db.session.add(producto)
            db.session.commit()
            flash("Producto creado correctamente", "success")
            return redirect(url_for("productos.lista_productos"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear producto: {e}", "error")

    return render_template("productos/nuevoProducto.html")

@productos_bp.route("/editarProducto/<int:id>", methods=["GET", "POST"])
def editar_producto(id):
    producto = Producto.query.get_or_404(id)

    if request.method == "POST":
        producto.descripcion = request.form["descripcion"]
        producto.precio = float(request.form["precio"])
        producto.stock = int(request.form["stock"]) if request.form["stock"] else 0

        try:
            db.session.commit()
            flash("Producto actualizado correctamente", "success")
            return redirect(url_for("productos.lista_productos"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar producto: {e}", "error")

    return render_template("productos/editarProducto.html", producto=producto)

@productos_bp.route("/eliminar/<int:id>")
def eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    
    try:
        db.session.delete(producto)
        db.session.commit()
        flash(f'Producto "{producto.descripcion}" eliminado correctamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar producto: {e}', 'error')
    
    return redirect(url_for('productos.lista_productos'))


@productos_bp.route("/verProducto/<int:id>", methods=["GET", "POST"])
def ver_producto(id):
    producto = Producto.query.get_or_404(id)
    return render_template("productos/verProducto.html", producto=producto)
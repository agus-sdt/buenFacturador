from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from extensions import db
from models.cliente import Cliente
from decoradores import role_required 

clientes_bp = Blueprint("clientes", __name__, url_prefix="/clientes")

@clientes_bp.route("/")
@role_required('admin')
def lista_clientes():
    clientes = Cliente.query.all()
    return render_template("clientes/lista.html", clientes=clientes)

@clientes_bp.route("/nuevo", methods=["GET", "POST"])
@role_required('admin')
def nuevo_cliente():
    if request.method == "POST":
        nombre = request.form["nombre"]
        direccion = request.form["direccion"]
        telefono = request.form["telefono"]
        email = request.form["email"]

        cliente = Cliente(
            nombre=nombre,
            direccion=direccion,
            telefono=telefono,
            email=email
        )
        try:
            db.session.add(cliente)
            db.session.commit()
            flash("Cliente creado correctamente", "success")
            return redirect(url_for("clientes.lista_clientes"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear cliente: {e}", "error")

    return render_template("clientes/nuevo.html")

@clientes_bp.route("/editar/<int:id>", methods=["GET", "POST"])
@role_required('admin')
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)

    if request.method == "POST":
        cliente.nombre = request.form["nombre"]
        cliente.direccion = request.form["direccion"]
        cliente.telefono = request.form["telefono"]
        cliente.email = request.form["email"]

        try:
            db.session.commit()
            flash("Cliente actualizado correctamente", "success")
            return redirect(url_for("clientes.lista_clientes"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar: {e}", "error")

    return render_template("clientes/editar.html", cliente=cliente)

@clientes_bp.route("/eliminar/<int:id>")
@role_required('admin')
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    try:
        db.session.delete(cliente)
        db.session.commit()
        flash('Cliente eliminado exitosamente', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error al eliminar el cliente: {e}', 'error')

    return redirect(url_for("clientes.lista_clientes"))

@clientes_bp.route("/ver/<int:id>")
@role_required('admin')
def ver_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    return render_template("clientes/ver.html", cliente=cliente)
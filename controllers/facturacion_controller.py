from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response
from datetime import datetime
from extensions import db, PDFSHIFT_API_KEY
from decorators import login_required
import requests
from models import facturacion
 

facturacion_bp = Blueprint('facturacion', __name__)

@facturacion_bp.route('/facturar', methods=['GET', 'POST'])
@login_required
def facturacion_page():
    if request.method == 'POST':
        facturacion.guardar_factura(request.form)
        return redirect(url_for('facturacion.facturacion_page'))
    numero_factura = facturacion.obtener_numero_factura()
    clientes_ref = db.collection('clientes').stream()
    clientes = [{"id": c.id, "nombre": c.to_dict().get("nombre")} for c in clientes_ref]
    return render_template('facturar.html', numero_factura=numero_factura, clientes=clientes)

@facturacion_bp.route('/consultar_facturas')
@login_required
def consultar_facturas():
    query = request.args.get('query', '')
    fecha = request.args.get('fecha', '')
    if not fecha:
        fecha = datetime.today().strftime('%Y-%m-%d')
    facturas = facturacion.obtener_facturas_filtradas(query=query, fecha=fecha)
    total_ventas_hoy = (facturacion.obtener_total_ventas_hoy()
                        if fecha == datetime.today().strftime('%Y-%m-%d')
                        else sum(f.get('total', 0) for f in facturas))
    for f in facturas:
        for d in f.get('detalles', []):
            d.setdefault('producto', {'id':'N/A','nombre':'Desconocido'})
            d.setdefault('total', 0)
    return render_template('consultar_facturas.html',
                           facturas=facturas,
                           total_ventas_hoy=total_ventas_hoy,
                           fecha=fecha)

@facturacion_bp.route('/factura/<factura_id>')
@login_required
def detalle_factura(factura_id):
    ref = db.collection('facturas').document(factura_id).get()
    if not ref.exists:
        return "Factura no encontrada", 404
    factura = ref.to_dict()
    cliente = db.collection('clientes').document(factura['cliente_id']).get().to_dict()
    detalles = []
    for item in factura.get('detalles', []):
        p = db.collection('productos').document(item.get('producto_id')).get()
        pd = p.to_dict() if p.exists else {}
        detalles.append({
            'nombre': pd.get('descripcion','Desconocido'),
            'cantidad': item.get('cantidad',0),
            'precio_unitario': pd.get('valor_unitario',0),
            'subtotal': item.get('cantidad',0)*pd.get('valor_unitario',0)
        })
    vendedor = {}
    if factura.get('vendedor_id'):
        v = db.collection('vendedores').document(factura['vendedor_id']).get()
        if v.exists: vendedor = v.to_dict()
    return render_template('facturas_detalles.html',
                           factura=factura,
                           cliente=cliente,
                           detalles=detalles,
                           factura_id=factura_id)

@facturacion_bp.route('/eliminar_factura/<factura_id>', methods=['POST'])
@login_required
def eliminar_factura(factura_id):
    try:
        facturacion.eliminar_factura_por_id(factura_id)
        flash('Factura eliminada correctamente.','success')
    except Exception as e:
        flash(f'Error al eliminar factura: {e}','danger')
    return redirect(url_for('facturacion.consultar_facturas'))

@facturacion_bp.route('/descargar_factura/<id>')
@login_required
def descargar_factura(id):
    factura = facturacion.obtener_factura_por_id(id)
    cliente = facturacion.obtener_cliente_por_factura(factura)
    detalles = facturacion.obtener_detalles_por_factura(id)
    html = render_template('factura_pdf.html',
                           factura=factura,
                           cliente=cliente,
                           detalles=detalles)
    try:
        resp = requests.post(
            'https://api.pdfshift.io/v3/convert/pdf',
            auth=('api',PDFSHIFT_API_KEY),
            json={"source":html}
        )
        resp.raise_for_status()
        pdf = resp.content
        response = make_response(pdf)
        response.headers['Content-Type']='application/pdf'
        response.headers['Content-Disposition']=f'inline; filename=factura_{id}.pdf'
        return response
    except Exception as e:
        return f"Error generando PDF: {e}",500

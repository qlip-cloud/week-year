import frappe
from frappe import _
import requests
import json
from frappe.utils import getdate, formatdate
from datetime import datetime
from gp_integration.gp_integration.service.connection import execute_send
from gp_integration.gp_integration.service.utils import get_master_setup
from gp_integration.gp_integration.constant.api_setup import INTGVENT


MSG_ERROR = _("There was an error in the process to connect to GP, contact the administrator")

# NOTA: Es creado exclusivamente para modificar la fecha de envío (delivery_date) para corregir un bug en los registros
def send_sales_order_for_delivery_date(sales_order):

    res = {'name': '', 'msg': 'Fail', 'result': 400, 'body_data': '', 'response': ''}

    title = _("Send Sales Order for Delivery Date")

    so_json = None

    so_respose = None

    try:

        sales_order_temp = frappe.get_doc("Sales Order", sales_order)

        # TODO: Verificar ajustes cuando se incluya modificar compañía en un Sales Order
        company = sales_order_temp.company

        master_name = __get_master_setup(company)

        if not master_name:

            res["msg"] = _('The recordset of Master Setup is empty')

            return res

        so_upd = sales_order_temp.qp_gp_sales_order

        so_json = __prepare_petition(master_name, sales_order, so_upd)

        print("so_json--->", so_json)

        res['body_data'] = so_json

        # so_respose = execute_send(company_name=company, endpoint_code=INTGVENT, json_data=so_json)

        # mock
        # so_respose = {'Estado': 'Falla', 'Detalle': ''}
        so_respose =  {'Estado': 'Exitoso', 'Detalle': 'PRB-003'}

        print("so_respose-->", so_respose)

        res['response'] = so_respose

        print("so_respose.get(Estado)", so_respose.get("Estado"))

        if so_respose.get("Estado") == "Exitoso":

            res['name'] = sales_order

            res['msg'] = 'Success'

            res['result'] = 200

            frappe.log_error(message='\n'.join((str(sales_order), str(so_json), str(so_respose))), title=_("Call GP - UPD Exito"))

            return res

        else:

            frappe.log_error(message='\n'.join((str(sales_order), str(so_json), str(so_respose))), title=_("Call GP - UPD Error"))

    except Exception as error:

        frappe.log_error(message='\n'.join((sales_order, frappe.get_traceback())), title=title)

        pass

    return res


def __get_master_setup(company):

    master_name = frappe.db.get_list('qp_GP_MasterSetup',
        filters={
            'company': company 
        },
        fields=['name', 'store_main', 'order_id', 'customer_class'],
        order_by="creation desc"
    )

    return master_name and master_name[0] or {}


def __prepare_petition(master_name, sales_order, so_update):

    so_json = {}

    so_obj = frappe.get_doc("Sales Order", sales_order)

    customer_email = frappe.db.get_value("Customer", so_obj.customer, "email_id")

    customer_group = frappe.db.get_value("Customer", so_obj.customer, "customer_group")

    customer_addr = frappe.get_doc('Address', so_obj.customer_address)

    item_list = []

    Bdga_Default = ""

    for item in so_obj.items:

        currency_company = frappe.db.get_value("Company", so_obj.company, "default_currency")

        Bdga_Default = item.warehouse.split(" - ")[0]

        item_list.append(
            {
                "Id": item.item_code,
                "Cant": item.qty,
                "Precio": item.base_price_list_rate if so_obj.currency == currency_company else item.price_list_rate,
                "Bdga_linea": Bdga_Default, # Tomarlo del producto
                "shipping_method": so_obj.qp_shipping_type,
                "shipping_date": so_obj.delivery_date.strftime("%Y-%m-%d"),
                "Itemdespor": item.discount_percentage,
                "itemdesc": item.discount_amount
            }
        )


    # store_main = __get_value_master(master_name, 'store_main')

    order_id = __get_value_master(master_name, 'order_id')

    id_clase = customer_group # __get_value_master(master_name, 'customer_class')

    bdg_alter = [{"Id": ""}]

    year_week = so_obj.qp_year_week.split('-')

    nro_semana = int(year_week[1])

    so_json['Id_Pedido'] = order_id
    so_json['Id_Pedido_Esp'] = so_update
    so_json['Tipo_Pedido'] = "5" # "5" pedidos en espera | "2" = Pedidos (reserva inventario)
    so_json['moneda'] = so_obj.currency
    so_json['tasa'] = so_obj.conversion_rate
    so_json['NumeroSemana'] = "WK {}".format(nro_semana)
    so_json['Lote_Cab'] = so_obj.qp_shipping_type
    so_json['Bdga_Default'] = Bdga_Default # "" # store_main
    so_json['Bdg_Alter'] = bdg_alter
    so_json['Articulo'] = item_list
    so_json['Id_Cliente'] = so_obj.customer
    so_json['Nom_Cliente'] = so_obj.customer_name
    so_json['Apell_Cliente'] = ""
    so_json['Id_Clase'] = id_clase
    so_json['Direc_Cliente'] = customer_addr.address_line1
    so_json['Ciudad_Cliente'] = customer_addr.city
    so_json['Pais_Cliente'] = customer_addr.country
    so_json['Telefono_Cliente'] = customer_addr.phone
    so_json['Correo_Cliente'] = customer_email
    so_json['Direc_Entrega'] = customer_addr.address_line1
    so_json['Ciudad_Entrega'] = customer_addr.city
    so_json['Pais_entrega'] = customer_addr.country
    so_json['compania'] = so_obj.company
    so_json['referencia1'] = so_obj.qp_reference1
    so_json['referencia2'] = so_obj.qp_reference2 or ""
    so_json['referencia3'] = so_obj.qp_reference3 or ""

    return json.dumps(so_json)

def __get_value_master(master_name, field_conf):

    res = master_name.get(field_conf).split('-')

    return res and res[0] or ''

import frappe
from frappe import _
from frappe.utils.background_jobs import get_jobs
from frappe.utils import flt, cint

from temporal_table.temporal_table.use_case.import_sales_order import __transform_year_week


@frappe.whitelist()
def updt_delivery_date(company):

    try:

        processing_delivery_date(company)

        return "okay"


    except Exception as error:

        frappe.log_error(message=frappe.get_traceback(), title="updt_delivery_date")

        pass

    return "error"


def processing_delivery_date(company):

    # Validar duplicacion de ejecución de proceso
    enqueued_method = 'ball_customization.ball_customization.uses_cases.update_delivery_date.get_updt_list'
    jobs = get_jobs()

    if not jobs or enqueued_method not in jobs[frappe.local.site]:

        frappe.enqueue(enqueued_method, data=company, queue='long', is_async=True, timeout=54000)


def get_updt_list(data):

    # Consultar ordenes de venta a procesar

    sql_str = """
        select delivery_date, qp_year_week, name, customer
        from  `tabSales Order`
        where company = '{0}' and qp_year_week >= '2025-01'
        order by qp_year_week asc
    """.format(data)

    so_list = frappe.db.sql(sql_str, as_dict=1)

    for rec in so_list:

        so_obj = frappe.get_doc("Sales Order", rec.name)

        upd_delivery_date = __transform_year_week(rec.get('qp_year_week'))

        if upd_delivery_date != so_obj.delivery_date:

            print("Diferente -->", rec.name)

            so_obj.delivery_date = upd_delivery_date

            for item_so in so_obj.items:

                item_so.delivery_date = upd_delivery_date            

            so_obj.save()

    return

def update_delivery_from_so(rec):

    try:
        print("update_delivery_from_so rec.name", rec.name)

        so_obj = None

        so_obj = frappe.get_doc("Sales Order", rec.name)

        print("so_obj.delivery_date", so_obj.delivery_date)

        upd_delivery_date = __transform_year_week(rec.get('qp_year_week'))

        print("upd_delivery_date", upd_delivery_date)

        if upd_delivery_date != so_obj.delivery_date:

            print("Diferente -->", rec.name)

            so_obj.delivery_date = upd_delivery_date

            so_obj.save()

            frappe.db.commit()

            print("DESPUES so_obj.delivery_date", so_obj.delivery_date)

    except Exception as error:

        frappe.db.rollback()

        frappe.log_error(message=frappe.get_traceback(), title="update_delivery_from_so: {0}".format(so_obj.name))

        pass

    return


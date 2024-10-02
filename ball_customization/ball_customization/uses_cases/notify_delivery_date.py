import frappe
from frappe import _
from frappe.utils.background_jobs import get_jobs
from frappe.utils import flt, cint

from temporal_table.temporal_table.use_case.import_sales_order import __transform_year_week
from ball_customization.ball_customization.uses_cases.gp_service_ball import send_sales_order_for_delivery_date


@frappe.whitelist()
def notify_delivery_date(company):

    try:

        processing_notify_delivery_date(company)

        return "okay"


    except Exception as error:

        frappe.log_error(message=frappe.get_traceback(), title="notify_delivery_date")

        pass

    return "error"


def processing_notify_delivery_date(company):

    # Validar duplicacion de ejecución de proceso
    enqueued_method = 'ball_customization.ball_customization.uses_cases.notify_delivery_date.get_notify_list'
    jobs = get_jobs()

    if not jobs or enqueued_method not in jobs[frappe.local.site]:

        frappe.enqueue(enqueued_method, data=company, queue='long', is_async=True, timeout=54000)


def get_notify_list(data):

    # Consultar ordenes de venta a procesar

    sql_str = """
        select delivery_date, qp_year_week, name, customer
        from  `tabSales Order`
        where company = '{0}' and qp_year_week >= '2025-01' and qp_gp_status != 'registered'
        order by qp_year_week asc
    """.format(data)

    so_list = frappe.db.sql(sql_str, as_dict=1)

    for rec in so_list:
        print("notify_delivery_date_2gp rec", rec.name)
        res = send_sales_order_for_delivery_date(rec.name)
        print("result", res)

    return

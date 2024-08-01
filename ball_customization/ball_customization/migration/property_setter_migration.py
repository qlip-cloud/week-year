import frappe
from var_dump import var_dump

NAME_01 = "Sales Order-per_delivered-in_list_view"
NAME_02 = "Sales Order-per_billed-in_list_view"
PROPERTY_SETTER = "Property Setter"

global_naming_series_01 = None
global_naming_series_02 = None

def before_migrate(doc = None, method = None):

    global global_naming_series_01
    global global_naming_series_02

    # Sales Order-per_delivered-in_list_view

    global_naming_series_01 = naming_backup(PROPERTY_SETTER,NAME_01)

    # Sales Order-per_billed-in_list_view

    global_naming_series_02 = naming_backup(PROPERTY_SETTER,NAME_02)


def naming_backup(origin_namng_Series, name):

    list_search = (origin_namng_Series, name)

    if frappe.db.exists(*list_search):

        return frappe.get_doc(*list_search)
    
    return


def after_migrate(doc = None, method = None):
    
    global global_naming_series_01
    global global_naming_series_02

    # Sales Order-per_delivered-in_list_view

    naming_restore(PROPERTY_SETTER, global_naming_series_01, NAME_01)

    del global_naming_series_01

    # Sales Order-per_billed-in_list_view

    naming_restore(PROPERTY_SETTER, global_naming_series_02, NAME_02)

    del global_naming_series_02


def naming_restore(origin_namng_Series, global_naming_series, name):

    if global_naming_series:

        backup_create(origin_namng_Series, global_naming_series, name)


def backup_create(origin_namng_Series, global_naming_series, name):
    
    list_search = (origin_namng_Series, name)

    if frappe.db.exists(*list_search):

        old_naming_series = frappe.get_doc(*list_search)
        old_naming_series.value = global_naming_series.value
        old_naming_series.default_value = global_naming_series.default_value
        old_naming_series.save(ignore_permissions=True)

    else:

        global_naming_series.insert()

    frappe.db.commit()

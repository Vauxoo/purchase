# -*- coding: utf-8 -*-
############################################################################
#    Module Writen For Odoo, Open Source Management Solution
#
#    Copyright (c) 2011 Vauxoo - http://www.vauxoo.com
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
#    coded by: Nhomar Hernandez <nhomar@vauxoo.com>
#    planned by: Nhomar Hernandez <nhomar@vauxoo.com>
############################################################################

{
    "name": "Purchase Console",
    "summary": "Manage your purchase planning wasn't so simple ever.",
    "version": "1.0.0",
    "author": "Vauxoo",
    "sequence": 100,
    "website": "http://www.vauxoo.com/",
    "category": "",
    "depends": [
        "board",  # Just because we need some graphic stuff from here
        "message_post_model",  # Just because log properly some +2many
        "purchase_requisition",  # To have this concept available.
        "procurement_jit_stock",  # Because the analysis include automatic
        # procurement.
        "purchase_double_validation",  # Because the process need this 2 steps.
        "forecasting_smoothing_techniques",
        # computation process here
        "stock_landed_costs_segmentation",  # Because last cost is from here.
        # "purchase_requisition_department",
        # "purchase_requisition_incoterms",
        # "purchase_requisition_line_description",
        # "purchase_requisition_line_plan",
        # "purchase_requisition_line_price_unit",
        # "purchase_requisition_line_uom_check",
        # "purchase_requisition_line_view",
        # "purchase_requisition_priority",
        # "purchase_requisition_remarks",
        # "purchase_requisition_supplier_list",
        # "purchase_requisition_type",
    ],
    "data": [
        'views/assets_backend.xml',
        'views/purchase_requisition_view.xml',
    ],
    "demo": [
    ],
    "test": [],
    "qweb": [
        'static/xml/console.xml',
        'static/xml/web_widget_one2many_console.xml',
    ],
    "js": [
    ],
    "css": [
        'static/css/console.css',
    ],
    "installable": True,
    "application": True,
    'auto_install': False,
}

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
        # PRODUCT HELPERS.
        # Conceptually the master product management starts here.
        "product_lifecycle",
        # serial management unfucked.
        "product_unique_serial",
        # necessary to use it as filter and analysis.
        "product_manufacturer",
        # To have a correct and consistent management of codes in product.
        "product_unique_default_code",
        # Important tool to manage better the set of products
        "product_properties_by_category",
        # Stock modules.
        # Because the analysis include automatic.
        "procurement_jit_stock",
        # Proper cost management.
        "stock_landed_costs_segmentation",
        # Stock
        "purchase_rfq_xls",  # We need the original report in xls
        # Because the process need this 2 steps.
        "purchase_double_validation",
        # To ensure a proper costing method configurable for all products.
        "costing_method_settings",
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
        # Technical tools.
        "message_post_model",  # Just because log properly some +2many
        # computation process here
        "forecasting_smoothing_techniques"
    ],
    "data": [
        'views/assets_backend.xml',
        'views/purchase_requisition_view.xml',
        'views/layout.xml',
        'wizard/fill_products_wizard_view.xml',
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

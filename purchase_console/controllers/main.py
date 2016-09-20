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

from openerp import http


class Console(http.Controller):

    def get_help(self, record, fields=None):
        if fields is None:
            fields = []
        fields_info = record.fields_get(fields, attributes=['help', 'string'])
        return fields_info

    @http.route(
        '/purchase/console/<model("purchase.requisition"):requisition>',
        auth='user', type="http")
    def console(self, requisition):
        # Because is a basic algorithm to be used just for rendering.
        max_po_line_ids = len(requisition.supplier_ids)
        po_lines_width = int(12.00/max_po_line_ids)

        return http.request.render('purchase_console.requisition', {
            'requisition': requisition,
            'po_lines_width': po_lines_width,
            'po_lines_number': max_po_line_ids,
            'get_help': self.get_help,
        })

    @http.route(
        '/purchase/console/<model("purchase.requisition"):requisition>/<action>',  # noqa
        type='json',
        auth="public")
    def action(self, requisition, action, **data):
        """Controller to manage the front end actions:
            Procure: 'procure_products_from_suppliers',
            Send RFQ: 'sent_suppliers',
            Open Bid: 'open_bid',
            Generate PO: 'generate_po',
            Cancel all: 'cancel_requisition'
        """
        if hasattr(requisition, action):
            getattr(requisition, action)()
        return bool(requisition)

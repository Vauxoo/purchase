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
from openerp.http import request


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
        max_po_line_ids = 0
        po_lines_width = 0
        if requisition.supplier_ids:
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
        type='json', auth="public")
    def action(self, requisition, action, **data):
        """Controller to manage the front end actions:
            Procure: 'procure_products_from_suppliers',
            Send RFQ: 'sent_suppliers',
            Confirm Call: 'confirm_call',
            Open Bid: 'open_bid',
            Generate PO: 'generate_po',
            Cancel all: 'cancel_requisition'
        """
        res = {'result': False}
        if hasattr(requisition, action):
            try:
                res['message'] = getattr(requisition, action)()
                res['result'] = True
            except Exception as e:
                res['result'] = False
                res['message'] = {'title': e[0],
                                  'msg': e[1]}
        return res

    @http.route(
        '/update/line/<model("purchase.order.line"):line>',
        auth='user', type="json")
    def update_line(self, line, **data):
        pol = request.registry('purchase.order.line')
        cr, uid, context = request.cr, request.uid, request.context
        res = {'result': False}
        try:
            pol.update_line(cr, uid, line.id, data, context=context)
            res['result'] = True
        except ValueError as e:
            res['result'] = False
            res['message'] = e.message
        return res

    @http.route(
        '/purchase_console/order_approve/',
        auth='user', type="json")
    def purchase_order_approve(self, order_id, **data):
        cr, uid, context = request.cr, request.uid, request.context
        purchase_obj = request.registry('purchase.order')
        res = {'result': False}
        try:
            purchase_obj.signal_workflow(
                cr, uid, [order_id], 'purchase_approve', context=context)
            res['result'] = True
        except ValueError as e:
            res['result'] = False
            res['message'] = e.message
        return res

    @http.route(
        '/purchase_console/action-line/',
        auth='user', type="json")
    def purchase_order_line_confirm(self, line_id, **data):
        cr, uid, context = request.cr, request.uid, request.context
        pol = request.registry('purchase.order.line')
        res = {'result': False}
        try:
            pol.update_line(cr, uid, line_id, data, context=context)
            res['result'] = True
        except ValueError as e:
            res['result'] = False
            res['message'] = e.message
        return res

    @http.route(
        '/purchase_console/remove-line/',
        auth='user', type="json")
    def purchase_order_line_unlik(self, line_id, **data):
        cr, uid, context = request.cr, request.uid, request.context
        pol = request.registry('purchase.order.line')
        return pol.unlink(cr, uid, [line_id], context=context)

    @http.route(
        ['/shop/purchase_order_modal/<model("purchase.order"):order>'],
        type='json', auth="public", methods=['POST'], website=True)
    def modal(self, order, **data):
        return request.website._render(
            "purchase_console.purchase_order_modal",
            {'order': order,
             })

    @http.route(
        ['/shop/modal_msg_error/'],
        type='json', auth="public", methods=['POST'], website=True)
    def modal_message(self, message, **data):
        return request.website._render(
            "purchase_console.message_modal",
            {'message': message,
             })

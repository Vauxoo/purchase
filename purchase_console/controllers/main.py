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

    @http.route(
        '/purchase/console/<model("purchase.requisition"):requisition>/',
        auth='user'
        )
    def teacher(self, requisition):
        return http.request.render('purchase_console.requisition', {
            'requisition': requisition,
        })

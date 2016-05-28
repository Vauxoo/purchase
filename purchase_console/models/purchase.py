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
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def print_quotation_xls(self):
        '''This function prints the request for quotation and mark it as sent, so
        that we can see more easily the next step of the workflow
        '''
        self.ensure_one()
        context = dict(self._context)
        context['xls_report'] = True
        self.signal_workflow('send_rfq')
        action = self.env['report'].with_context(context).get_action(
                        self, 'purchase.report_purchasequotation')
        print action
        return action

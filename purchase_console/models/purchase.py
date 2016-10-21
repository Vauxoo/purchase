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
from openerp import api, models


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    @api.multi
    def print_quotation_xls(self):
        """This function prints the request for quotation and mark it as sent, so
        that we can see more easily the next step of the workflow
        """
        self.ensure_one()
        context = dict(self._context)
        context['xls_report'] = True
        self.signal_workflow('send_rfq')
        action = self.env['report'].with_context(context).get_action(
            self, 'purchase.report_purchasequotation')
        return action

    @api.multi
    def force_rfq_send(self):
        for order in self:
            # email_act = order.with_context({'send_rfq': True}).wkf_send_rfq()
            email_act = order.with_context(
                {'send_rfq': True}).action_rfq_send()
            if email_act and email_act.get('context'):
                composer_obj = self.env['mail.compose.message']
                composer_values = {}
                email_ctx = email_act['context']
                template_values = [
                    email_ctx.get('default_template_id'),
                    email_ctx.get('default_composition_mode'),
                    email_ctx.get('default_model'),
                    email_ctx.get('default_res_id'),
                ]
                composer_values.update(composer_obj.onchange_template_id(
                    *template_values).get('value', {}))
                if not composer_values.get('email_from'):
                    composer_values['email_from'] = order.company_id.email
                for key in ['attachment_ids', 'partner_ids']:
                    if composer_values.get(key):
                        composer_values[key] = [(6, 0, composer_values[key])]
                composer = composer_obj.with_context(email_ctx).create(
                    composer_values)
                composer.with_context(email_ctx).send_mail()
                order.signal_workflow('send_rfq')
        return True

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
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class FillProducts(models.TransientModel):
    _name = 'fill.products'

    name = fields.Many2one('res.partner', string='Partner', required=True,
                           help='Lood all products related to this partner')
    procure = fields.Boolean(help='Use the procurement rule to set the '
                                  'quantity on lines, False if you will '
                                  ' fill manually the quantities.')

    @api.model
    def create_lines(self, products):
        lines = []
        req = self.env['purchase.requisition']
        req = req.search([('id', '=', self.env.context['active_id'])], limit=1)
        # Just in case new products in the requisition to avoid at least
        # automatically add twice the same product.
        products = products - req.line_ids.mapped('product_id')
        for product in products:
            line = (0, 0, {
                'product_id': product.id,
            })
            lines.append(line)
        req.write({'line_ids': lines})

    @api.multi
    def fill(self):
        self.ensure_one()
        supplierinfo = self.env['product.supplierinfo']
        supplierinfo = supplierinfo.search([('name', '=', self.name.id)])
        templates = supplierinfo.mapped('product_tmpl_id')
        template_ids = templates.mapped('id')
        products = self.env['product.product'].search([('product_tmpl_id',
                                                        'in', template_ids)])
        self.create_lines(products)

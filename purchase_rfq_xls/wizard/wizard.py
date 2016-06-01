# coding: utf-8
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#    Copyright (C) Vauxoo (<http://vauxoo.com>).
#    All Rights Reserved
# #############Credits#########################################################
#    Coded by: Jose Suniaga <josemiguel@vauxoo.com>
###############################################################################
#    This program is free software: you can redistribute it and/or modify it
#    under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or (at your
#    option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import ValidationError, Warning as UserError
import base64

import logging
_logger = logging.getLogger(__name__)

try:
    import xlrd
except ImportError:
    _logger.info('You have purchase_rfq_xls from '
                 'addons-vauxoo declared in your '
                 'system you will need xlrd library '
                 'in order to use this module')


class PurchaseQuotationWizard(models.TransientModel):
    _description = 'Purchase Quotation'
    _name = 'purchase.quotation.wizard'
    _col_start = "ID"

    @api.depends()
    def _get_purchase(self):
        context = dict(self._context)
        active_ids = context['active_ids'][0]
        self.purchase = self.env['purchase.order'].browse(active_ids)

    template_action = fields.Selection([
        ('export', "Get a quotation template without prices"),
        ('import', "Update a quotation prices"),
    ], default='import', help='Get a quotation template without prices: '
                              'Simply download the template xls. \n '
                              'Update a quotation: Given a '
                              'filled template upload it and update the '
                              'prices sent by supplier')
    xls_file = fields.Binary('Valid XLS file')
    xls_name = fields.Char()
    state = fields.Selection([('form', 'form'),
                              ('success', 'success'),
                              ('success2', 'success2')], default='form')
    line_ids = fields.One2many(
        'purchase.quotation.wizard.line', 'wizard_id')
    purchase = fields.Many2one('purchase.order', compute='_get_purchase')

    @api.multi
    @api.constrains('xls_name', 'xls_file')
    def _check_xls(self):
        if self.template_action != 'import':
            return True
        if not self.xls_file:
            raise ValidationError(_("Load a Valid XLS File"))
        if self.template_action == 'import' and \
                not self.xls_name.endswith('.xls'):
            raise ValidationError(_("The file must be a Valid Excel xls file"))
        purchase = self.purchase
        fname = '/tmp/%s' % (self.xls_name)
        with open(fname, 'w') as tmp_fname:
            tmp_fname.write(base64.b64decode(self.xls_file))
            tmp_fname.close()
        sheet = xlrd.open_workbook(fname).sheet_by_index(0)
        if sheet.cell_type(2, 5) not in \
                (xlrd.XL_CELL_EMPTY, xlrd.XL_CELL_BLANK) and \
                sheet.cell_value(2, 6) != purchase.name:
            raise UserError(' '.join([
                _('Is not a valid template for Quotation'),
                str(purchase.name)]))

    @api.model
    def _update_price(self, order_line, price, qty):
        data = {}
        if isinstance(price, float) and isinstance(qty, float):
            data.update({'price_unit': price, 'product_qty': qty})
            return order_line.write(data)
        return False

    @api.model
    def get_xls_eof(self, sheet):
        """Search for the last row of a Spreadsheet
        @return: return int
        """
        row = 0
        while True:
            try:
                sheet.cell_value(row, 0)
                row += 1
            except IndexError:
                break
        return row

    @api.multi
    def import_xls(self):
        """Validate and read xls file to update quotation
        """
        self.ensure_one()
        context = dict(self._context)
        fname = '/tmp/%s' % (self.xls_name)
        # I go directly to the sheet, because the contraint already validated
        # which is the proper format for the sheet.
        sheet = xlrd.open_workbook(fname).sheet_by_index(0)
        eof = self.get_xls_eof(sheet)
        # First col header on Qweb report: template.xml
        can_start = False
        done_ids = self.env['purchase.order.line']
        new_products = []
        for row in range(eof):
            if self._col_start == sheet.cell_value(row, 0):
                can_start = True
                continue
            if not can_start:
                continue
            # Proposed product Quantity
            order_line = self.env['purchase.order.line']
            product = self.env['product.supplierinfo']
            prod = self.env['product.product']
            values = dict(identifier=sheet.cell_value(row, 0),
                          internal_code=sheet.cell_value(row, 1),
                          vendor_code=sheet.cell_value(row, 2),
                          description=sheet.cell_value(row, 3),
                          date_planned=sheet.cell_value(row, 4),
                          product_qty=sheet.cell_value(row, 5),
                          # cell on column 6 is the price that I know, then
                          # just ignoring it.
                          price_unit=sheet.cell_value(row, 7))
            # Using the External ID I try to get the order
            if values['identifier']:
                # If identifier: we will try the line as it is (no code and/or
                # any other check more than the qty and price).
                order_line = done_ids.search([('id', '=',
                                               int(values['identifier']))],
                                             limit=1)
            if values['vendor_code'] and not values['identifier']:
                # If no identifier: we will try to look by internal code.
                product = product.search([('product_code', '=',
                                           values['vendor_code'])])
            if values['internal_code'] and not values['identifier']:
                prod = prod.search([('default_code', '=',
                                     values['internal_code'])])
            if order_line:
                self._update_price(order_line,
                                   values['price_unit'],
                                   values['product_qty'])
                done_ids += order_line
            if not order_line:
                new_products.append((0, 0, {
                    'product': prod,
                    'product_tmpl': product,
                    'vendor_code': values['vendor_code'],
                    'internal_code': values['internal_code'],
                    'description': values['description'],
                    'cost': values['price_unit'],
                    'product_qty': values['product_qty'],
                }))
        # if done_ids:
            # intersect objects and unlink diff
            # order_line_diff = purchase.order_line - done_ids
            # TODO: I think they should not be deleted.
            # order_line_diff.unlink()
        self.write({'state': 'success2'})
        if new_products:
            self.write({
                'state': 'success',
                'line_ids': new_products
                })
        action = self.env.ref('purchase_rfq_xls.action_purchase_quotation')
        return action.with_context(context).read([])

    @api.multi
    def print_report(self):
        """Print the report
        @return : return report
        """
        ctx = dict(self._context)
        ctx['xls_report'] = True
        purchase = self.env['purchase.order'].browse(ctx['active_ids'])[0]
        return self.env['report'].with_context(ctx).get_action(
            purchase,
            'purchase_rfq_xls.report_template',
            data={'ids': purchase.id})


class PurchaseQuotationWizardLine(models.TransientModel):
    _description = 'Purchase Quotation Details'
    _name = 'purchase.quotation.wizard.line'
    _rec_name = 'description'

    description = fields.Char()
    vendor_code = fields.Char()
    internal_code = fields.Char()
    wizard_id = fields.Many2one('purchase.quotation.wizard')
    product = fields.Many2one('product.product')
    product_tmpl = fields.Many2one('product.template')
    cost = fields.Float()
    product_qty = fields.Float()

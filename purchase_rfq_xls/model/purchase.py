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
import base64
from openerp import api, fields, models, _
try:
    from openerp.addons.controller_report_xls.controllers.main \
            import get_xls
except ImportError:
    print 'Dear Future Me.... Please do not do this'


class MailComposer(models.TransientModel):

    _name = 'mail.compose.message'
    _inherit = 'mail.compose.message'

    def get_mail_values(self, cr, uid, wizard, res_ids, context=None):
        extra_attachments = context.get('extra_attachments')
        if extra_attachments:
            assert isinstance(extra_attachments, list), '''Extra Attachments
                                                        to be copied
                                                        must be a list of ids
                                                        '''
            att_ids = context.get('extra_attachments')
            wizard.write({'attachment_ids': [(4, i) for i in att_ids]})
        return super(MailComposer, self).get_mail_values(cr, uid, wizard, res_ids, context=context)


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @api.multi
    def _get_received_quote(self):
        att = self.env['ir.attachment']
        for purchase in self:
            # TODO: Check if it was loaded marking it.
            att = att.search([('res_id', '=', purchase.id),
                              ('res_model', '=', 'purchase.order'),
                              ('name', 'ilike', '.xls')],
                             limit=1)
            if not att:
                purchase.supplier_quote = self._get_xls()
            if att:
                purchase.supplier_quote = att
            purchase.received_quote = bool(purchase.supplier_quote)

    received_quote = fields.Boolean(help="We have at least one xls file as"
                                         "attachment already loaded.",
                                    compute="_get_received_quote")
    supplier_quote = fields.Many2one("ir.attachment",
                                     help="Attachment considered the one from"
                                          " supplier",
                                     compute="_get_received_quote")

    @api.model
    def _get_xls(self):
        html = self.env['report'].get_html(
            self,
            'purchase_rfq_xls.report_template',
            data={'ids': self.ids, 'form': {}}
        )
        # convert html to xls
        xls = get_xls(html)
        # create attachment
        return self.env['ir.attachment'].create({
            'name': 'RFQ_' + str(self.name) + '.xls',
            'datas': base64.b64encode(xls),
            'datas_fname': 'RFQ_' + str(self.name) + '.xls',
            'type': 'binary',
            'res_model': 'purchase.order',
            'res_id': self.ids[0],
            'user_id': self._uid,
        })

    @api.multi
    def action_rfq_send(self):
        '''
        This function opens a window to compose an email, with the edi purchase
        template message loaded by default
        backported from v9.0.
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            if self.env.context.get('send_rfq', False):
                template_id = ir_model_data.get_object_reference(
                        'purchase', 'email_template_edi_purchase')[1]
            else:
                template_id = ir_model_data.get_object_reference(
                        'purchase', 'email_template_edi_purchase_done')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(
                        'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_model': 'purchase.order',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'extra_attachments': [self.supplier_quote.id],
        })
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    @api.multi
    def open_rfw_web(self):
        self.ensure_one()
        rep_url = "/report/html/purchase_rfq_xls.report_template/%i" % self.id
        action = {
            'type': 'ir.actions.act_url',
            'name': "Web RFQ",
            'target': "new",
            'context': self._context,
            'url': rep_url,
            }
        return action

    @api.multi
    def receive_rfq_xls(self):
        self.ensure_one()
        action = self.env.ref(
                'purchase_rfq_xls.action_purchase_quotation').read([])[0]
        action.update({'target': 'new'})
        context = dict(self._context)
        context.update({
            'purchase': self.id
            })

        return action


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.multi
    def _compute_external_id(self):
        for record in self:
            xml_id = record.get_external_id()[record.id]
            xml_id = len(xml_id) and xml_id or \
                record._BaseModel__export_xml_id()
            record.xml_id = xml_id

    @api.multi
    def _compute_vendor_code(self):
        for record in self:
            domain = [('product_tmpl_id', '=',
                       record.product_id.product_tmpl_id.id),
                      ('name', '=', record.order_id.partner_id.id)]
            supplierinf = self.env['product.supplierinfo'].search(domain)
            record.vendor_code = supplierinf.product_code

    xml_id = fields.Char(compute=_compute_external_id,
                         store=False,
                         size=128,
                         string='External ID',
                         help="ID of the view defined in xml file")

    vendor_code = fields.Char(compute=_compute_vendor_code,
                              store=False,
                              size=128,
                              string='Vendor Code',
                              help="Supplier product code")

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
from operator import attrgetter

import openerp.addons.decimal_precision as dp
from openerp import _, api, fields, models


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'
    _excluded_states_po = ['cancel']

    @api.model
    def _get_suppliers(self):
        """Partners involved are the ones present as sellers in product and the
        ones manually added in purchase orders.
        :return: recordset of suppliers
        """
        products = self.env['product.product']
        purchases = self.purchase_ids.filtered(
            lambda rec: rec.state not in self._excluded_states_po)
        suppliers_pur = purchases.mapped('partner_id')
        # If there is already some purchase better use the partners there.
        if purchases:
            return suppliers_pur
        products = self.line_ids.mapped('product_id')
        suppliers_prod = self.env['res.partner']
        for product in products:
            suppliers_prod += product.seller_ids.mapped('name')
        partners = self.supplier_ids | suppliers_pur | suppliers_prod
        # Always sorted in order to ensure a consistent behavior in the console
        # when iterated.
        return partners.sorted(key=attrgetter('name'))

    @api.depends('exclusive', 'purchase_ids', 'line_ids')
    def _compute_suppliers(self):
        """Given a set of purchase products in a bid, compute the partners that
        should be called on such bid.
        """
        for order in self:
            order.supplier_ids = self._get_suppliers()

    @api.model
    def _inverse_suppliers(self):
        """When add a partner we assume you will ask for prices,
        then a PO is created. :return:
        """
        supplier_on_orders = self.purchase_ids.mapped('partner_id')
        new_suppliers = supplier_on_orders - self.supplier_ids
        # If there is a new supplier then new purchase orders are created.
        for supplier in new_suppliers:
            self.make_purchase_order(supplier.id)

    see_left_column = fields.Boolean()
    user_id = fields.Many2one(help="User in charge of give follow up to this"
                                   "requisition process.")
    supplier_ids = fields.Many2many('res.partner',
                                    compute="_compute_suppliers",
                                    copy=False,
                                    domain=[('supplier', '=', True)],
                                    inverse='_inverse_suppliers')
    line_ids = fields.One2many('purchase.requisition.line',
                               'requisition_id',
                               'Products to Purchase',
                               states={'done': [('readonly', True)]},
                               copy=True)
    advantage_discount = fields.Float(default=0.02,
                                      help="When you start negociate, may be"
                                      "you want to show a price a little less"
                                      "than the effectively computed one in "
                                      "the system, here you can set such "
                                      "discount to conceptually just show it "
                                      "in the RFQ to the supplier.")
    stock_to = fields.Char(readonly=True, help="Technical field: How much time"
                                               " do you have of stock.")

    @api.model
    def check_rfq(self):
        """Check if can generate Purchases quotes
        if multiple_rfq_per_supplier is False and exists any purchase order
        with partner of any in supplier_ids can not generate more rfq
        """
        self.ensure_one()
        for supplier in self.supplier_ids:
            if not self.multiple_rfq_per_supplier and supplier.id in \
                    self.purchase_ids.mapped(
                        lambda x: x.state != 'cancel' and x.partner_id.id):
                return False
        return True

    @api.multi
    def procure_products_from_suppliers(self):
        """Given a set of products compute procurements for products where
        those partners are suppliers.
        And change requisition state to in_progress state.
        """
        self.ensure_one()
        for supplier in self.supplier_ids:
            self.make_purchase_order(supplier.id)
        self.signal_workflow('sent_suppliers')
        return True

    @api.multi
    def confirm_call(self):
        self.ensure_one()
        self.tender_in_progress()
        return True

    @api.multi
    def sent_suppliers(self):
        """this method will send all rfq to all suppliers
        """
        self.ensure_one()
        for order in self.purchase_ids:
            order.force_rfq_send()
        return True

    @api.multi
    def open_bid(self):
        """this method will Finish Call of bids
        """
        self.ensure_one()
        self.tender_open()
        return True

    @api.multi
    def cancel_requisition(self):
        """this method will Cancel the requisition.
        """
        self.ensure_one()
        self.tender_cancel()
        return True

    @api.multi
    def group_tenders(self):
        """TODO: This method is a little wired in order to respect only this
        specified set of rules to group tenders.

        1. Given a set of tender lists it will cancel them and join all
        line_ids.
        2. No Filter about any other topic is used to check it.
        3. We should have a method called split-tenders when you need once it
        is merged split them with some other logic.
        4. It will close all the other Purchase Orders and Requisitions done
        before and related with the merged ones.
        """
        pass

    @api.multi
    def open_fill(self):
        """This opens the fill wizard
        @return: the RFQ tree view
        """
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('purchase_console.action_fill_wizard')
        form_view_id = imd.xmlid_to_res_id(
            'purchase_console.view_fill_products_form')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[form_view_id, 'form'],
                      [False, 'graph'],
                      [False, 'kanban'],
                      [False, 'calendar'],
                      [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        # result = {'type': 'ir.actions.act_window_close'}
        return result

    @api.multi
    def open_console_web(self):
        self.ensure_one()
        rep_url = "/purchase/console/%i" % self.id
        action = {
            'type': 'ir.actions.act_url',
            'name': "Web Tender",
            'target': "new",
            'context': self._context,
            'url': rep_url,
        }
        return action


class ProcurementOrder(models.Model):
    _inherit = 'procurement.order'

    # TODO: Use new api here?
    def _run(self, cr, uid, procurement, context=None):
        requisition_obj = self.pool.get('purchase.requisition')
        warehouse_obj = self.pool.get('stock.warehouse')
        if procurement.rule_id and procurement.rule_id.action == 'buy' \
                and procurement.product_id.purchase_requisition:
            # Not done yet anything, TODO: logic to select the warehouse, it
            # cannot be just the first.
            warehouse_id = warehouse_obj.search(
                cr, uid, [('company_id', '=', procurement.company_id.id)],
                context=context)
            requisition_id = requisition_obj.create(cr, uid, {
                'origin': procurement.origin,
                'date_end': procurement.date_planned,
                'warehouse_id': warehouse_id and warehouse_id[0] or False,
                'company_id': procurement.company_id.id,
                'procurement_id': procurement.id,
                'picking_type_id': procurement.rule_id.picking_type_id.id,
                'line_ids': [(0, 0, {
                    'product_id': procurement.product_id.id,
                    'product_uom_id': procurement.product_uom.id,
                    'product_qty': procurement.product_qty

                })],
            })
            self.message_post(cr, uid, [procurement.id], body=_(
                "Purchase Requisition created"), context=context)
            return self.write(cr, uid, [procurement.id],
                              {'requisition_id': requisition_id},
                              context=context)
        return super(ProcurementOrder, self)._run(
            cr, uid, procurement, context=context)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    precision = dp.get_precision('Product Unit of Measure')

    @api.multi
    def update_line(self, data):
        """This method will update the values line showed in front end:
           * product_qty
           * last_price
           * price_bid
           * price_unit
           * accounting_cost
           * state

        @data: Dictionary that contains the values to update
            {'id': id, 'name': name, 'value': 'value'}
            id: line id
            name: field name to update
            value: new value
        """
        self.ensure_one()
        pol = self.pool.get('purchase.order.line')
        line, parent = self, self.order_id
        if data.get('name') == 'product_qty':
            values = pol.onchange_product_id(
                self.env.cr, self.env.uid, self.id,
                parent.pricelist_id.id,
                line.product_id.id, float(data.get('value')),
                line.product_uom.id, parent.partner_id.id, parent.date_order,
                parent.fiscal_position.id, line.date_planned, line.name,
                False, parent.state, self.env.context).get('value')
            line.write(values)

        if data.get('name') == 'state':
            if not data.get('value'):
                pol.action_draft(
                    self.env.cr, self.env.uid, [line.id],
                    context=self.env.context)
            if data.get('value', False):
                pol.action_confirm(
                    self.env.cr, self.env.uid, [line.id],
                    context=self.env.context)

    def get_last_inv_line(self):
        """Last price is the last price paid for this product invoice based or
        the last price this supplier gave us the
        less of both.
        :return:
        """
        # Using SQL just to be sure all is really fast.
        # TODO: This should be pointing to account_invoice_report.
        query = """(SELECT l.id, l.price_unit, i.date_invoice
                        FROM account_invoice_line as l
                    INNER JOIN account_invoice as i ON i.id=l.invoice_id
                    INNER JOIN res_partner as r ON r.id=i.partner_id
                        WHERE (l.product_id = %(product_id)s
                            AND i.partner_id = %(partner_id)s)
                            AND i.state in ('open', 'paid')
                    LIMIT 1)
                    UNION
                    (SELECT l.id, l.price_unit, i.date_invoice
                        FROM account_invoice_line as l
                    INNER JOIN account_invoice as i ON i.id=l.invoice_id
                    INNER JOIN res_partner as r ON r.id=i.partner_id
                        WHERE (l.product_id = %(product_id)s
                            AND i.partner_id != %(partner_id)s)
                            AND i.state in ('open', 'paid')
                    ORDER BY date_invoice DESC
                    LIMIT 1)"""
        self._cr.execute(query, dict(
            product_id=self.product_id.id,
            partner_id=self.order_id.partner_id.id))
        elements = [row for row in self._cr.fetchall()]
        return sorted(elements, key=lambda il: il[1])

    @api.multi
    @api.depends(
        'product_id', 'last_price',
        'order_id.requisition_id.advantage_discount')
    def _compute_prices(self):
        """Get the values computed for prices
        :return:
        """
        for line in self:
            ils = line.get_last_inv_line()
            line.last_invoice_id = ils and ils[0][0] or False
            line.last_price = ils and ils[0][1] or 0.00
            line.accounting_cost = line.product_id.standard_price
            line.price_bid = line.last_price * \
                (1 - line.order_id.requisition_id.advantage_discount)

    price_bid = fields.Float(digits_compute=precision,
                             help="Technical field: for not loosing the price"
                             "used for the bid, which can be generally a"
                             "little percentage less than the actual computed"
                             "one.",
                             compute="_compute_prices")
    last_price = fields.Float(digits_compute=precision,
                              help="Technical field: It will represent the "
                              "more little one between the last purchase  "
                              "to this supplier and the last purchase actually"
                              " done. If never bought to this  supplier this "
                              "will be the same than the last one, if never"
                              " bought at all this will be 0",
                              compute="_compute_prices")
    accounting_cost = fields.Float('Acc', digits_compute=precision,
                                   help="Technical field: it will represent "
                                   "the more the actual standard cost in the "
                                   "product (the accounting one) used as"
                                   "reference ",
                                   compute="_compute_prices")
    last_invoice_id = fields.Many2one('account.invoice.line',
                                      help="Technical field: it will represent"
                                      " the last account invoice line done "
                                      "to this supplier  or simply the last "
                                      "invoice the one with the littlest "
                                      "price.",
                                      compute="_compute_prices")

    # def action_draft(self, cr, uid, ids, context=None):
    #     self.write(cr, uid, ids, {'state': 'draft'}, context=context)
    #
    # def action_confirm(self, cr, uid, ids, context=None):
    #     super(purchase_order_line,
    # self).action_confirm(cr, uid, ids, context=context)
    #     for element in self.browse(cr,
    # uid, ids, context=context):
    #         if not element.quantity_bid:
    #             self.write(cr, uid, ids,
    #      {'quantity_bid': element.product_qty}, context=context)
    #     return True
    #
    # def generate_po(self, cr, uid, tender_id, context=None):
    #     #call generate_po from tender with active_id. Called from js widget
    # return self.pool.get('purchase.requisition').generate_po(cr, uid,
    # [tender_id], context=context)


class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    def _get_consolidated_price(self, req):
        product = req.product_id
        cost = product.material_cost + \
            product.landed_cost + \
            product.production_cost + \
            product.subcontracting_cost
        return cost

    @api.multi
    def _compute_line_fields(self):
        for req in self:
            req.consolidated_price = self._get_consolidated_price(req)

    @api.multi
    @api.depends('requisition_id', 'requisition_id.po_line_ids')
    def _compute_po_line(self):
        """In order to return purchase_order_lines filtered by
            product_id = requisition_line.product_id
        """
        excluded = self.env['purchase.requisition']._excluded_states_po
        for line in self:
            # Requisition_id.po_line_ids already has all purchases_order_lines
            # of all purchase orders related to requisition_id
            po_line_ids = line.requisition_id.po_line_ids.filtered(
                lambda r: r.product_id == line.product_id and
                r.order_id.state not in excluded)
            line.po_line_ids = po_line_ids

    @api.model
    def get_po_line_render(self):
        """For render reasons we need have a False record per line if the
        partner did not quote this element in order to render properly always a
        correct number of columns per line."""
        self.ensure_one()
        lines = self.po_line_ids
        res = []
        for supp in self.requisition_id.supplier_ids.sorted():
            line = lines.filtered(
                lambda rec, k=supp: rec.order_id.partner_id == k)
            res.append(line.id)
        po_lines = self.po_line_ids.browse(res)
        return po_lines

    po_line_ids = fields.One2many('purchase.order.line',
                                  help="Technical field: the purchase orders "
                                  "lines related to a line.",
                                  compute="_compute_po_line")
    consolidated_price = fields.Float(string="Consolidated",
                                      help="Technical field: The cost price"
                                      "including the landing costs for "
                                      "supplier in order to have a comparative"
                                      " price including all the impacts of "
                                      "logistic for example: Landing costs, "
                                      "Time to arrival, accounting impacts, "
                                      "other expenses.",
                                      compute="_compute_line_fields")
    # TODO: Put this in the stock_forecast module.
    forecast_qty = fields.Float('Projected', readonly=True,
                                help="Technical field: The quantity "
                                "projected with the forecast module by any"
                                " mean.")
    stock = fields.Float(readonly=True,
                         help="Technical field: Stock when the forecast "
                         " was computed, necessary to know if you really"
                         " can live with stock actual or not.")

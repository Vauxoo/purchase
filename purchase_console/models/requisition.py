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
from openerp.exceptions import ValidationError, Warning as UserError


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'

    @api.model
    def _get_suppliers(self):
        """Partners involved are the ones present as sellers in product and the ones manually added in purchase orders.
        :return:
        """
        supplier_orders_ids = []
        if self.purchase_ids:
            supplier_orders_ids = [order.partner_id.id for order in self.purchase_ids if not order.state in ['cancel']]
        products = []
        if self.line_ids:
            products = [line.product_id for line in self.line_ids]
        suppliers = []
        for product in products:
            if product.seller_ids:
                suppliers = suppliers + [supplier for supplier in product.seller_ids]
        supplier_on_products_ids = [supplier.name.id for supplier in suppliers]
        return supplier_orders_ids + supplier_on_products_ids

    @api.one
    @api.depends('exclusive', 'purchase_ids', 'line_ids')
    def _get_partners_related(self):
        """Given a set of purchase products in a bid, compute the partners that can be called on such bid.
        :return:
        """
        # If it was not forced to be only one.
        if not self.supplier_ids:
            if self.exclusive!='exclusive':
                self.supplier_ids = self._get_suppliers()

    @api.one
    def _create_po_given_partner(self):
        """When add a partner we assume you will ask for prices, then a PO is created.
        :return:
        """
        supplier_on_orders_ids = []
        if self.purchase_ids:
            supplier_on_orders_ids = [order.partner_id.id for order in self.purchase_ids]
        for supplier in self.supplier_ids:
            if not supplier.id in supplier_on_orders_ids:
                self.make_purchase_order(supplier.id)

    supplier_ids = fields.Many2many('res.partner', compute="_get_partners_related", string='Suppliers Involved',
                                     track_visibility='always', copy=False, inverse='_create_po_given_partner')

    @api.model
    def procure_products_from_suppliers(self):
        """Given a set of products compute procurements for products where those partners are suppliers.
        :return:
        """
        return True
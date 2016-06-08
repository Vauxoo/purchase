# coding: utf-8

import time
from datetime import datetime

from openerp.report import report_sxw
from openerp.osv import osv


class RequestForQuotation(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(RequestForQuotation,
              self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'int': int,
            'datetime': datetime,
        })


class RequestForQuotationReport(osv.AbstractModel):
    _name = 'report.aging_due_report.aging_due_report_qweb'
    _inherit = 'report.abstract_report'
    _template = 'purchase_console.report_purchase_order_xls_qweb'
    _wrapped_report_class = RequestForQuotation

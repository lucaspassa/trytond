# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from .account import *
from .sale import *
from .purchase import *


def register():
    Pool.register(
        TaxRuleLineTemplate,
        TaxRuleLine,
        InvoiceLine,
        Sale,
        SaleLine,
        PurchaseLine,
        module='account_tax_rule_country', type_='model')

============================
Production Rounding Scenario
============================

Imports::

    >>> from decimal import Decimal
    >>> from proteus import Model, Wizard
    >>> from trytond.tests.tools import activate_modules
    >>> from trytond.modules.company.tests.tools import create_company, \
    ...     get_company

Install production Module::

    >>> config = activate_modules('production')

Create company::

    >>> _ = create_company()
    >>> company = get_company()

Create product::

    >>> ProductUom = Model.get('product.uom')
    >>> unit, = ProductUom.find([('name', '=', 'Unit')])
    >>> ProductTemplate = Model.get('product.template')
    >>> Product = Model.get('product.product')
    >>> product = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'product'
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.producible = True
    >>> template.list_price = Decimal(30)
    >>> template.cost_price = Decimal(20)
    >>> template.save()
    >>> product.template = template
    >>> product.save()

Create component::

    >>> component = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'component'
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.list_price = Decimal(5)
    >>> template.cost_price = Decimal(1)
    >>> template.save()
    >>> component.template = template
    >>> component.save()

Create residual::

    >>> residual = Product()
    >>> template = ProductTemplate()
    >>> template.name = 'residual'
    >>> template.default_uom = unit
    >>> template.type = 'goods'
    >>> template.list_price = Decimal(0)
    >>> template.cost_price = Decimal(0)
    >>> template.save()
    >>> residual.template = template
    >>> residual.save()

Create Bill of Material with rational ratio::

    >>> BOM = Model.get('production.bom')
    >>> bom = BOM(name='product')
    >>> input = bom.inputs.new()
    >>> input.product = component
    >>> input.quantity = 4
    >>> output = bom.outputs.new()
    >>> output.product = product
    >>> output.quantity = 9
    >>> output = bom.outputs.new()
    >>> output.product = residual
    >>> output.quantity = 8
    >>> bom.save()

Make a production with rounding::

    >>> Production = Model.get('production')
    >>> production = Production()
    >>> production.product = product
    >>> production.bom = bom
    >>> production.quantity = 3

Check component is ceiled::

    >>> input, = production.inputs
    >>> input.quantity
    2.0

Check product quantity::

    >>> output, = [o for o in production.outputs if o.product == product]
    >>> output.quantity
    3.0

Check residual is floored::

    >>> output, = [o for o in production.outputs if o.product == residual]
    >>> output.quantity
    2.0

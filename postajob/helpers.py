from postajob.models import Invoice, InvoiceProduct


def create_invoice_for_purchased_products(purchased_products, **invoice_kwargs):
    """
    Creates an invoice from a list of purchased_product instances.

    """
    invoice = Invoice.objects.create(**invoice_kwargs)
    for purchased_product in purchased_products:
        kwargs = {
            'product_name': purchased_product.product.name,
            'product_expiration_date': purchased_product.expiration_date,
            'num_jobs_allowed': purchased_product.num_jobs_allowed,
            'purchase_amount': purchased_product.purchase_amount,
        }
        invoiced_product = InvoiceProduct.objects.create(**kwargs)
        invoice.invoiced_products.add(invoiced_product)
    return invoice


def create_invoice_for_products(products, **invoice_kwargs):
    """
    Creates an invoice from a list of products.

    """
    invoice = Invoice.objects.create(**invoice_kwargs)
    for product in products:
        kwargs = {
            'product_name': product.name,
            'product_expiration_date': product.expiration_date(),
            'num_jobs_allowed': product.num_jobs_allowed,
            'purchase_amount': product.cost,
        }
        invoiced_product = InvoiceProduct.objects.create(**kwargs)
        invoice.invoiced_products.add(invoiced_product)
    return invoice
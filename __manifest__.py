# -*- coding: utf-8 -*-
{
    'name': "Ticket POS MX",

    'summary': """ Desarrollo de ticket """,

    'description': """
        Ticket personalizado para el punto de venta
    """,

    'author': "JS",
    'website': "",

    'category': 'Uncategorized',
    'version': '0.1',

    'depends': ['point_of_sale'],

    'data': [
        #'views/templates.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            # XML
            'pos_ticket_mx/static/src/app/screens/receipt_screen/receipt/receipt_header/receipt_header.xml',
            'pos_ticket_mx/static/src/app/screens/receipt_screen/receipt/order_receipt.xml',
            'pos_ticket_mx/static/src/app/screens/receipt_screen/receipt/order_receipt.js',
            'pos_ticket_mx/static/src/js/pos_receipt_cfdi.js',
            'pos_ticket_mx/static/src/js/payment_cfdi_fetch.js',
            'pos_ticket_mx/static/src/xml/pos_ticket_cfdi.xml',
        ],
    },
    'license': 'LGPL-3',

    'installable': True,
    'auto_install': False,
}


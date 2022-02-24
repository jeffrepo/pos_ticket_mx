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
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/pos.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
    'auto_install': False,
}

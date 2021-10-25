# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import logging
import pytz
from datetime import datetime

class Picking(models.Model):
    _inherit = "pos.order"

    def letras_numeros (self, id_pedido):
        pedido = self.env['pos.order'].search([('id','=',id_pedido)])
        string_to = self.env['account.move'].l10n_mx_edi_amount_to_text(pedido)
        logging.warn("Pedido")
        logging.warn(string_to)
        # string_total = pedido.l10n_mx_edi_amount_to_text()
        # self.env['account.move'].nombre_funcion(tu parametro en este caso tu pedido)
        logging.warn("Total letras a numeros :D")

        return string_to

    def texto_total (self, total):
        currency = self.env.company.currency_id.name.upper()
        # M.N. = Moneda Nacional (National Currency)
        # M.E. = Moneda Extranjera (Foreign Currency)
        currency_type = 'M.N' if currency == 'MXN' else 'M.E.'
        # Split integer and decimal part
        cliente_id = self.env['res.partner'].search([('id','=',1)])
        amount_i, amount_d = divmod(total, 1)
        amount_d = round(amount_d, 2)
        amount_d = int(round(amount_d * 100, 2))
        words = self.env.company.currency_id.with_context(lang= cliente_id.lang or 'es_ES').amount_to_text(amount_i).upper()
        invoice_words = '%(words)s %(amount_d)02d/100 %(curr_t)s' % dict(
            words=words, amount_d=amount_d, curr_t=currency_type)
        logging.warn("invoice_words")
        logging.warn(invoice_words)
        return invoice_words


    def buscar_pedido(self, referencia):
        pedido = self.env['pos.order'].search([('pos_reference','=',referencia)])
        if pedido:
            logging.warn("Pedido")
            logging.warn(pedido)
            return pedido
        else:
            return False

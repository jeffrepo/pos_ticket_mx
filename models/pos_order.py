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
        # string_total = pedido.l10n_mx_edi_amount_to_text()
        # self.env['account.move'].nombre_funcion(tu parametro en este caso tu pedido)

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
        return invoice_words


    def buscar_pedido(self, referencia):
        pedido = self.env['pos.order'].search([('pos_reference','=',referencia)])
        if pedido:
            return pedido
        else:
            return False


class PosOrder(models.Model):
    _inherit = "pos.order"
    
    def descuento_lineas(self,pedido_id,lines):
        precio_total_descuento = 0
        precio_total_positivo = 0
        logging.warning('Otra funcion heredada')
        for linea in lines:
            if linea.price_unit > 0:
                precio_total_positivo += linea.price_subtotal_incl
            elif linea.price_unit < 0:
                precio_total_descuento += linea.price_subtotal_incl
                linea.price_unit = 0

        posicion = 0
        for linea in lines:
            if lines[posicion].price_unit > 0:
                descuento = ((precio_total_descuento / precio_total_positivo)*100)*-1
                pedido_id.write({ 'lines': [[1, pedido_id.lines[posicion].id, { 'discount': descuento }]] })
            posicion += 1

        # linea.unlink()
        for linea1 in lines:
            if linea1.price_subtotal < 0:
                linea1.unlink()

        return True

    def lineas_eliminadas(self, lines, order):
        precio_total_descuento = 0
        precio_total_positivo = 0
        logging.warning('ORDERS')
        logging.warning(order)
        for linea in lines['lines']:
            for elemento_linea in linea:
                if elemento_linea != 0:
                    if elemento_linea['price_unit'] > 0:
                        precio_total_positivo += elemento_linea['price_subtotal_incl']
                    elif elemento_linea['price_unit'] < 0:
                        precio_total_descuento += elemento_linea['price_subtotal_incl']
                        elemento_linea['price_unit'] = 0

        posicion = 0
        i=0
        logging.warning('primera linea')
        for linea0 in lines['lines']:
            for elemento_linea1 in linea0:
                if elemento_linea1 !=0:
                    if elemento_linea1['price_unit'] > 0:
                        descuento = ((precio_total_descuento / precio_total_positivo)*100)*-1
                        order['data']['lines'][i][2]['discount'] = descuento
                    posicion += 1
            i+=1

        # linea.unlink()
        dele=0
        logging.warning('segunda linea')
        for linea1 in order['data']['lines']:
            for elemento_linea2 in linea1:
                if elemento_linea2 != 0:
                    if elemento_linea2['price_subtotal'] < 0:
                        order['data']['lines'][dele].clear()
            dele+=1

        order1 = order
        logging.warning('tercer linea')
        for i in order1['data']['lines']:
            if [] in order1['data']['lines']:
                order['data']['lines'].remove([])
        logging.warning('termina')
        return True

    # @api.model
    # def _process_order(self, order, draft, existing_order):
    #     # for o in self: 
    #     #     logging.warning(o)
    #     #     self.lineas_eliminadas(order['data'], order)


    #     # if existencia_orden:
    #     #     pedido_id = self.env['pos.order'].search([('id','=', existencia_orden)])
    #     #     logging.warning('Si se esta creando el pedido');
    #     #     if pedido_id:
    #     #         logging.warning('Linea 89')
    #     #         self.descuento_lineas(pedido_id,pedido_id.lines)
    #     res = super(PosOrder, self)._process_order(order, draft, existing_order)
    #     return res

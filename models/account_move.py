# -*- coding: utf-8 -*-
import base64
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError
import logging
import pytz
from datetime import datetime

class Picking(models.Model):
    _inherit = "account.move"

    @api.model
    def obtener_valores_factura_mx(self, id_factura):
        factura_id = self.env['account.move'].search([('id','=',id_factura)])
        logging.warn("factura_id");
        logging.warn(factura_id)
        cfdi=None
        sello_sat = None
        # factura_id = None
        Emisor = None
        xml = None
        regimen_fiscal = None
        sello_digital_emisor = None
        tfd = None
        total_letras = ''
        certificado_sat = None
        fecha_certificacion = None
        folio_fiscal = None
        cadena_original = None
        if factura_id:
            logging.warn("Primera parte factura_id si trae algo")
            logging.warn(factura_id)
            cfdi = base64.decodestring(factura_id.l10n_mx_edi_cfdi)
            xml = factura_id.l10n_mx_edi_get_xml_etree()
            tfd = factura_id.l10n_mx_edi_get_tfd_etree(xml)
            sello_sat = tfd.get('selloSAT', tfd.get('SelloSAT', 'No identificado'))
            certificado_sat = tfd.get('NoCertificadoSAT')
            folio_fiscal = tfd.get('UUID')
            
        logging.warn("El xml")
        logging.warn(xml)
        logging.warn("-----------------")
        logging.warn("Que es tfd ?")
        logging.warn(tfd)



        if xml:
            regimen_fiscal = xml.Emisor.get('RegimenFiscal', '')
            fecha_certificacion = xml.get('fecha', xml.get('Fecha', '')).replace('T', ' ')
            sello_digital_emisor = xml.get('sello', xml.get('Sello', 'No identificado'))


        if factura_id:
            cadena_original = factura_id._get_l10n_mx_edi_cadena()
            total_letras = factura_id.l10n_mx_edi_amount_to_text()
            cadena_factura_id = factura_id.l10n_mx_edi_cfdi_uuid
            extraer_ultimos_digitos = cadena_factura_id[-8:]


        datos_factura = {
            'total_string': total_letras,
            'regimen_fiscal': regimen_fiscal,
            'certificado_sat': certificado_sat,
            'fecha_certificacion': fecha_certificacion,
            'folio_fiscal': folio_fiscal,
            'cadena_original': cadena_original,
            'sello_sat': sello_sat,
            'sello_digital_emisor': sello_digital_emisor,
        }
        return datos_factura

    def letras_numeros (self, id_pedido):
        pedido = self.env['pos.order'].search([('id','=',id_pedido)])
        string_to = self.env['account.move'].l10n_mx_edi_amount_to_text(pedido)
        logging.warn("Pedido")
        logging.warn(string_to)
        # string_total = pedido.l10n_mx_edi_amount_to_text()
        # self.env['account.move'].nombre_funcion(tu parametro en este caso tu pedido)
        logging.warn("Total letras a numeros :D")
        hola = "Hola"
        return string_to

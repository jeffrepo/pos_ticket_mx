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
            cfdi_values1 = self._l10n_mx_edi_get_invoice_cfdi_values(base64.decodebytes(factura_id))

            cfdi1 = self.env.ref('l10n_mx_edi.cfdiv33')._render(cfdi_values1)

            decoded_cfdi_values = invoice._l10n_mx_edi_decode_cfdi(cfdi_data=cfdi1)
            cfdi = invoice._l10n_mx_edi_decode_cfdi(cfdi_data=cfdi1)
            # cfdi = base64.decodestring((factura_id.l10n_mx_edi_cfdi_uuid))
            xml = factura_id.l10n_mx_edi_get_xml_etree()
            tfd = factura_id.l10n_mx_edi_get_tfd_etree(xml)
            sello_sat = tfd.get('selloSAT', tfd.get('SelloSAT', 'No identificado'))
            certificado_sat = tfd.get('NoCertificadoSAT')
            folio_fiscal = tfd.get('UUID')

        logging.warning("El xml")
        logging.warning(xml)
        logging.warning("-----------------")
        logging.warning("Que es tfd ?")
        logging.warning(tfd)



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

        return string_to

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
        logging.warning('obtener_valores_factura_mx')
        logging.warning(id_factura)
        sello_sat = None
        # factura_id = None
        regimen_fiscal = None
        sello_digital_emisor = None
        sello_digital_cfdi = None
        total_letras = ''
        certificado_sat = None
        fecha_certificacion = None
        folio_fiscal = None
        cadena_original = None
        vat_empresa = None
        monto_total = None
        vat_usuario = None
        if factura_id:
            if factura_id.state == 'posted':
                factura_id._l10n_mx_edi_decode_cfdi()
                logging.warning(factura_id._l10n_mx_edi_decode_cfdi())
                if factura_id._l10n_mx_edi_decode_cfdi():
                    regimen_fiscal = factura_id._l10n_mx_edi_decode_cfdi()['fiscal_regime']
                    sello_sat = factura_id._l10n_mx_edi_decode_cfdi()['sello_sat']
                    certificado_sat = factura_id._l10n_mx_edi_decode_cfdi()['certificate_sat_number']
                    fecha_certificacion = factura_id._l10n_mx_edi_decode_cfdi()['emission_date_str']
                    folio_fiscal = factura_id._l10n_mx_edi_decode_cfdi()['uuid']
                    cadena_original = factura_id._l10n_mx_edi_decode_cfdi()['cadena']
                    sello_digital_cfdi = factura_id._l10n_mx_edi_decode_cfdi()['sello']
                    logging.warning('Pago total en texto')
                    logging.warning(factura_id._l10n_mx_edi_cfdi_amount_to_text())
                    total_letras = factura_id._l10n_mx_edi_cfdi_amount_to_text()
                    vat_empresa = factura_id._l10n_mx_edi_decode_cfdi()['supplier_rfc']
                    vat_usuario = factura_id._l10n_mx_edi_decode_cfdi()['customer_rfc']
                    monto_total = factura_id._l10n_mx_edi_decode_cfdi()['amount_total']
        # if factura_id:
        #     cadena_original = factura_id._get_l10n_mx_edi_cadena()
        #     total_letras = factura_id.l10n_mx_edi_amount_to_text()
        #     cadena_factura_id = factura_id.l10n_mx_edi_cfdi_uuid
        #     extraer_ultimos_digitos = cadena_factura_id[-8:]


        datos_factura = {
            'vat_empresa': vat_empresa,
            'vat_usuario': vat_usuario,
            'total_string': total_letras,
            'regimen_fiscal': regimen_fiscal,
            'certificado_sat': certificado_sat,
            'fecha_certificacion': fecha_certificacion,
            'folio_fiscal': folio_fiscal,
            'cadena_original': cadena_original,
            'sello_sat': sello_sat,
            'sello_digital_cfdi': sello_digital_cfdi,
            'monto_total': monto_total,
        }
        return datos_factura

    def _post(self, soft=True):
        #Funcion heredada y creada para activar el boton de "process now"
        logging.warning('POST')
        res = super()._post(soft)
        logging.warning('intentar _POST')
        res.action_process_edi_web_services();
        return res


    def letras_numeros (self, id_pedido):
        pedido = self.env['pos.order'].search([('id','=',id_pedido)])
        string_to = self.env['account.move'].l10n_mx_edi_amount_to_text(pedido)

        return string_to

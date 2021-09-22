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
        cfdi = base64.decodestring(factura_id.l10n_mx_edi_cfdi)
        logging.warn(cfdi)
        # cfdi = factura_id.l10n_mx_edi_get_xml_etree(cfdi)
        # logging.warn(cfdi)
        xml = factura_id.l10n_mx_edi_get_xml_etree();
        logging.warn("El xml")
        logging.warn(xml);
        logging.warn("-----------------")
        tfd = factura_id.l10n_mx_edi_get_tfd_etree(xml)
        sello_sat = tfd.get('selloSAT', tfd.get('SelloSAT', 'No identificado'));
        regimen_fiscal = xml.Emisor.get('RegimenFiscal', '');
        certificado_sat = tfd.get('NoCertificadoSAT');
        fecha_certificacion = xml.get('fecha', xml.get('Fecha', '')).replace('T', ' ');
        folio_fiscal = tfd.get('UUID');
        cadena_original = factura_id._get_l10n_mx_edi_cadena();
        total_letras = factura_id.l10n_mx_edi_amount_to_text();
        sello_digital_emisor = xml.get('sello', xml.get('Sello', 'No identificado'));
        cadena_factura_id = factura_id.l10n_mx_edi_cfdi_uuid;
        logging.warn("cadena_factura_id")
        logging.warn(cadena_factura_id)
        extraer_ultimos_digitos = cadena_factura_id[-8:]
        logging.warn("extraer_ultimos_digitos")
        logging.warn(extraer_ultimos_digitos)
        logging.warn(factura_id.currency_id.decimal_places + factura_id.l10n_mx_edi_cfdi_amount)
        # string = quote_plus('https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?' + keep_query(
        # re=factura_id.l10n_mx_edi_cfdi_supplier_rfc, rr=factura_id.l10n_mx_edi_cfdi_customer_rfc,
        # tt='%.*f' % (factura_id.currency_id.decimal_places, factura_id.l10n_mx_edi_cfdi_amount), id=factura_id.l10n_mx_edi_cfdi_uuid)
        # + '&amp;fe=%s' % quote_plus( sello, 'utf-8', 'strict', '=/').replace('%2B', '+'));
        # string_unificado = ("https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?re="+
        # factura_id.l10n_mx_edi_cfdi_supplier_rfc+
        # "rr="+factura_id.l10n_mx_edi_cfdi_customer_rfc+
        # "tt="+ 25 +
        # "id="+str(factura_id.l10n_mx_edi_cfdi_uuid));
        datos_factura = {
            'total_string': total_letras,
            'regimen_fiscal': regimen_fiscal,
            'certificado_sat': certificado_sat,
            'fecha_certificacion': fecha_certificacion,
            'folio_fiscal': folio_fiscal,
            'cadena_original': cadena_original,
            'sello_sat': sello_sat,
            'sello_digital_emisor': sello_digital_emisor,
            # 'string_unificado': string_unificado,
        }
        return datos_factura

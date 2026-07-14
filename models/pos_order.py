# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
import re
from urllib.parse import urlencode, quote_plus



class PosOrder(models.Model):
    _inherit = 'pos.order'

    delivery_note_custom = fields.Boolean(string="Nota de remisión", default=False, copy=False, tracking=True)
    amount_total_words = fields.Char(string="Total en letras", default=False, copy=False)
    mx_invoice_online = fields.Boolean(string="Factura en línea", default=False, copy=False)

    @api.model
    def _get_pos_order_for_cfdi_ticket(self, identifier):
        if not identifier:
            _logger.warning("[pos_ticket_mx][cfdi] empty identifier")
            return self.browse()

        identifier = str(identifier)
        _logger.warning("[pos_ticket_mx][cfdi] searching pos.order identifier=%s", identifier)
        order = self.search([
            "|", "|",
            ("uuid", "=", identifier),
            ("pos_reference", "=", identifier),
            ("name", "=", identifier),
        ], limit=1, order="id desc")
        if order:
            _logger.warning(
                "[pos_ticket_mx][cfdi] found by reference id=%s uuid=%s pos_reference=%s name=%s",
                order.id, order.uuid, order.pos_reference, order.name,
            )
            return order

        if isinstance(identifier, int) or (isinstance(identifier, str) and identifier.isdigit()):
            order = self.browse(int(identifier)).exists()
            if order:
                _logger.warning(
                    "[pos_ticket_mx][cfdi] found by numeric id=%s uuid=%s pos_reference=%s name=%s",
                    order.id, order.uuid, order.pos_reference, order.name,
                )
                return order

        _logger.warning("[pos_ticket_mx][cfdi] pos.order not found identifier=%s", identifier)
        return self.browse()

    # def get_qr_link(self):
    #     self.ensure_one()
    #     cfdi_infos = self.env['l10n_mx_edi.document']._decode_cfdi_attachment(self.l10n_mx_edi_cfdi_attachment_id.raw)
    #     if not cfdi_infos:
    #         return {}

    #     barcode_value_params = keep_query(
    #         id=cfdi_infos['uuid'],
    #         re=cfdi_infos['supplier_rfc'],
    #         rr=cfdi_infos['customer_rfc'],
    #         tt=cfdi_infos['amount_total'],
    #     )
    #     barcode_sello = url_quote_plus(cfdi_infos['sello'][-8:], safe='=/').replace('%2B', '+')
    #     barcode_value = url_quote_plus(f'https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?{barcode_value_params}&fe={barcode_sello}')
    #     barcode_src = f'/report/barcode/?barcode_type=QR&value={barcode_value}&width=180&height=180'

    #     return barcode_src

    def _get_mx_cfdi_barcode_src(self, move, cfdi_value):
        barcode_value_params = urlencode({
            "id": move.l10n_mx_edi_cfdi_uuid or "",
            "re": (move.company_id.vat or "").strip(),
            "rr": (move.partner_id.vat or "").strip(),
            "tt": "%.6f" % move.amount_total,
        })
        barcode_sello = quote_plus((cfdi_value.get("sello") or "")[-8:], safe="=/").replace("%2B", "+")
        barcode_value = quote_plus(
            "https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?%s&fe=%s"
            % (barcode_value_params, barcode_sello)
        )
        return "/report/barcode/?barcode_type=QR&value=%s&width=180&height=180" % barcode_value

    def _get_mx_cfdi_amount_to_text(self, order, move):
        amount_text = (
            getattr(move, "amount_total_words", False)
            or getattr(order, "amount_total_words", False)
            or ""
        )
        if amount_text:
            return amount_text

        amount_to_text = getattr(move, "_l10n_mx_edi_cfdi_amount_to_text", None)
        if amount_to_text:
            try:
                return amount_to_text()
            except Exception:
                _logger.exception("[pos_ticket_mx][cfdi] amount_to_text from CFDI helper failed")

        try:
            return move.currency_id.amount_to_text(move.amount_total).replace(",", "")
        except Exception:
            _logger.exception("[pos_ticket_mx][cfdi] amount_to_text from currency failed")
            return ""
    
    @api.model
    def get_mx_cfdi_ticket_data_by_uuid(self, uuid):
        _logger.warning("[pos_ticket_mx][cfdi] get_mx_cfdi_ticket_data_by_uuid identifier=%s", uuid)
        order = self._get_pos_order_for_cfdi_ticket(uuid)
        _logger.warning(
            "[pos_ticket_mx][cfdi] order=%s account_move=%s",
            order.id if order else False,
            order.account_move.id if order and order.account_move else False,
        )
        if not order or not order.account_move:
            _logger.warning(
                "[pos_ticket_mx][cfdi] return empty: no order/account_move identifier=%s", uuid
            )
            return {}
        order = order.sudo()
        move = order.account_move.sudo()
        if not move.l10n_mx_edi_cfdi_uuid:
            _logger.warning(
                "[pos_ticket_mx][cfdi] return empty: move has no CFDI uuid move=%s state=%s cfdi_state=%s",
                move.id, move.state, getattr(move, "l10n_mx_edi_cfdi_state", None),
            )
            return {}

        decoded_cfdi = {}
        try:
            decoded_cfdi = move._l10n_mx_edi_decode_cfdi() or {}
        except Exception:
            _logger.exception("[pos_ticket_mx][cfdi] decode CFDI failed move=%s", move.id)

        try:
            cfdi_value = move._l10n_mx_edi_get_extra_invoice_report_values() or {}
        except Exception:
            _logger.exception(
                "[pos_ticket_mx][cfdi] extra invoice values failed move=%s", move.id
            )
            cfdi_value = {}
        if not isinstance(cfdi_value, dict):
            cfdi_value = {}
        cfdi_value.setdefault("sello", decoded_cfdi.get("sello") or "")
        cfdi_value.setdefault("sello_sat", decoded_cfdi.get("sello_sat") or "")
        cfdi_value.setdefault("cadena", decoded_cfdi.get("cadena") or "")
        cfdi_value.setdefault(
            "certificate_sat_number", decoded_cfdi.get("certificate_sat_number") or ""
        )
        cfdi_value.setdefault("stamp_date", decoded_cfdi.get("emission_date_str") or "")
        _logger.warning(
            "[pos_ticket_mx][cfdi] extra invoice values keys=%s",
            list(cfdi_value.keys()) if isinstance(cfdi_value, dict) else cfdi_value,
        )
        if not cfdi_value:
            _logger.warning("[pos_ticket_mx][cfdi] return empty: no extra invoice values")
            return {}
        partner = move.partner_id.sudo()
        no_cert_sat = getattr(move, "l10n_mx_edi_sat_cert_number", False) or ""
        no_cert_emisor = getattr(move, "l10n_mx_edi_cfdi_cert_number", False) or ""
        fecha_certificacion = cfdi_value.get("stamp_date") or ""
        # Datos “forma/metodo/uso/moneda” (ajusta a tus campos reales)
        forma_pago = getattr(move, "l10n_mx_edi_payment_method_id", False)
        metodo_pago = getattr(move, "l10n_mx_edi_payment_policy", False)
        uso_cfdi = getattr(move, "l10n_mx_edi_usage", False)
        no_cert_emisor = cfdi_value.get("certificate_number") or no_cert_emisor
        no_cert_sat = cfdi_value.get("certificate_sat_number") or no_cert_sat
        # “Cadena digital” depende de implementación; a veces está en un campo EDI o en el XML
        cadena_digital = cfdi_value.get("cadena") or ""
        sello_digital_cfdi = cfdi_value.get("sello") or ""
        sello_digital_sat = cfdi_value.get("sello_sat") or ""
        forma = ""
        cantidad_letra = self._get_mx_cfdi_amount_to_text(order, move)
        try:
            extra_values = move._l10n_mx_edi_get_extra_common_report_values()
        except Exception:
            _logger.exception("[pos_ticket_mx][cfdi] extra common values failed move=%s", move.id)
            extra_values = {}
        extra_values = extra_values if isinstance(extra_values, dict) else {}
        extra_values["barcode_src"] = (
            extra_values.get("barcode_src") or self._get_mx_cfdi_barcode_src(move, cfdi_value)
        )
        _logger.warning(
            "[pos_ticket_mx][cfdi] extra common values keys=%s has_barcode=%s",
            list(extra_values.keys()) if isinstance(extra_values, dict) else extra_values,
            bool(extra_values.get("barcode_src")) if isinstance(extra_values, dict) else False,
        )
        if not extra_values or not extra_values.get("barcode_src"):
            _logger.warning("[pos_ticket_mx][cfdi] return empty: no barcode_src")
            return {}
        _logger.warning(
            "[pos_ticket_mx][cfdi] return data order=%s move=%s cfdi_uuid=%s invoice=%s",
            order.id, move.id, move.l10n_mx_edi_cfdi_uuid, move.name,
        )
        # aquí devuelves lo que quieras imprimir (uuid, fecha timbrado, certificados, cadena, etc.)
        return {
            "invoice_name": move.name or "",
            "folio_ref": order.pos_reference or "",
            "fecha_emision": move.invoice_date.strftime("%d/%m/%Y") if move.invoice_date else "",
            "fecha_certificacion": fecha_certificacion,
            "expedido_en": (move.company_id.city or "") + (", " + (move.company_id.state_id.name or "") if move.company_id.state_id else ""),
            "cliente_nombre": partner.name or "",
            "cliente_rfc": partner.vat or "",
            "cliente_domicilio": partner.contact_address or "",
            "uuid": move.l10n_mx_edi_cfdi_uuid,
            "no_cert_sat": no_cert_sat,
            "no_cert_emisor": no_cert_emisor,
            "forma_pago_cliente": forma_pago.display_name if forma_pago else "",
            "metodo_pago": metodo_pago or "",
            "uso_cfdi": uso_cfdi or "",
            "moneda": move.currency_id.name or "",
            "cadena_digital": cadena_digital or "",
            "cantidad_letra": cantidad_letra or "",
            "sello_digital_cfdi": sello_digital_cfdi or "",
            "sello_digital_sat": sello_digital_sat or "",
            "barcode_src": extra_values["barcode_src"],
            "extra_values": extra_values or "",
        }
    
    @api.model
    def get_amount_total_words(self, total, currency_id):
        """Convierte un monto a letras usando la moneda indicada"""
        print(f"el total {total}, el id de la moneda {currency_id}")
        currency = self.env['res.currency'].browse(currency_id)
        print(f"la moneda {currency}")
        self.amount_total_words = currency.amount_to_text(total).replace(',', '')
        return currency.amount_to_text(total).replace(',', '')

    # @api.model
    # def get_mx_cfdi_ticket_data_by_uid(self, uid):
    #     order = self.search([("uid", "=", uid)], limit=1)
    #     if not order:
    #         return {}

    #     move = order.account_move  # factura del POS (ajusta si la guardas en otro campo)
    #     if not move:
    #         return {}

    #     # Si aún no está timbrada, probablemente no hay UUID
    #     uuid = getattr(move, "l10n_mx_edi_cfdi_uuid", False)
    #     if not uuid:
    #         return {}

    #     partner = move.partner_id

    #     # Campos típicos l10n_mx_edi (pueden variar según tu módulo)
    #     no_cert_sat = getattr(move, "l10n_mx_edi_sat_cert_number", False) or ""
    #     no_cert_emisor = getattr(move, "l10n_mx_edi_cfdi_cert_number", False) or ""

    #     # “Cadena digital” depende de implementación; a veces está en un campo EDI o en el XML
    #     cadena_digital = getattr(move, "l10n_mx_edi_cfdi_cadena_original", False) or ""

    #     # Datos “forma/metodo/uso/moneda” (ajusta a tus campos reales)
    #     forma_pago = getattr(move, "l10n_mx_edi_payment_method_id", False)
    #     metodo_pago = getattr(move, "l10n_mx_edi_payment_policy", False)
    #     uso_cfdi = getattr(move, "l10n_mx_edi_usage", False)

    #     return {
    #         "invoice_name": move.name or "",
    #         "folio_ref": order.pos_reference or "",
    #         "fecha_emision": move.invoice_date.strftime("%d/%m/%Y") if move.invoice_date else "",
    #         "fecha_certificacion": move.l10n_mx_edi_cfdi_datetime.strftime("%Y-%m-%dT%H:%M:%S") if getattr(move, "l10n_mx_edi_cfdi_datetime", False) else "",
    #         "expedido_en": (move.company_id.city or "") + (", " + (move.company_id.state_id.name or "") if move.company_id.state_id else ""),
    #         "cliente_nombre": partner.name or "",
    #         "cliente_rfc": partner.vat or "",
    #         "cliente_domicilio": partner.contact_address or "",
    #         "uuid": uuid,
    #         "no_cert_sat": no_cert_sat,
    #         "no_cert_emisor": no_cert_emisor,
    #         "forma_pago_cliente": forma_pago.display_name if forma_pago else "",
    #         "metodo_pago": metodo_pago or "",
    #         "uso_cfdi": uso_cfdi or "",
    #         "moneda": move.currency_id.name or "",
    #         "cadena_digital": cadena_digital or "",
    #     }


    # @api.model
    # def _process_order(self, order, existing_order):
    #     res = super()._process_order(order, existing_order)

    #     # res puede ser int (id) o recordset según el super en tu stack
    #     pos_order = self.browse(res) if isinstance(res, int) else res

    #     # --- tu lógica de timbrado aquí ---
    #     if (
    #         pos_order
    #         and pos_order.company_id.country_id.code == "MX"
    #         and pos_order.to_invoice
    #         and pos_order.account_move
    #     ):
    #         move = pos_order.account_move
    #         if move.state != "posted":
    #             move.action_post()

    #         try:
    #             move._l10n_mx_edi_cfdi_invoice_try_send()
    #         except Exception as e:
    #             # Si necesitas forzar timbrado:
    #             raise UserError(_("No se pudo timbrar automáticamente la factura. Detalle: %s") % str(e))

    #     # 🔥 CLAVE: devolver EXACTAMENTE lo que devolvió super()
    #     return res




    @api.model
    def sync_from_ui(self, orders):
        data = super().sync_from_ui(orders)

        pos_rows = (data or {}).get("pos.order", [])
        if not pos_rows:
            _logger.warning("POS autostamp: sin pos.order en retorno; no se timbra nada.")
            return data

        # ⚠️ IMPORTANTÍSIMO: solo órdenes que en ESTE retorno tienen account_move
        # y todavía no tienen uuid CFDI
        move_ids = []
        for row in pos_rows:
            # row viene como dict (como en tu log)
            if row.get("account_move") and not row.get("l10n_mx_edi_cfdi_uuid"):
                move_ids.append(row["account_move"])

        if not move_ids:
            _logger.warning("POS autostamp: no hay account_move nuevos/pendientes en este retorno; no se timbra.")
            return data

        moves = self.env["account.move"].browse(move_ids)

        for move in moves:
            # Ya timbrada por otro proceso
            if move.l10n_mx_edi_cfdi_uuid:
                continue

            if move.state != "posted":
                move.action_post()

            partner = move.partner_id
            vat = (partner.vat or "").strip().upper()
            name = (partner.name or "").strip().upper()
            
            # Decide tu política:
            # - si el POS es mostrador y normalmente es público general:
            #if vat == "XAXX010101000" or "PUBLICO EN GENERAL" in name:
            move.l10n_mx_edi_cfdi_to_public = True
            move._l10n_mx_edi_cfdi_invoice_try_send()
            doc = self.env["l10n_mx_edi.document"].search(
                [("move_id", "=", move.id)], order="id desc", limit=1
            )
            
            _logger.warning(
                "RESULTADO TIMBRADO POS -> %s uuid=%s cfdi_state=%s doc_state=%s msg=%s",
                move.name,
                move.l10n_mx_edi_cfdi_uuid,
                move.l10n_mx_edi_cfdi_state,
                getattr(doc, "state", None),
                (doc.message or "")[:200],
)
            if not move.l10n_mx_edi_cfdi_uuid:
                doc = self.env["l10n_mx_edi.document"].search(
                    [("move_id", "=", move.id)],
                    order="id desc",
                    limit=1
                )
                msg = doc.message if doc and doc.message else _("Sin detalle de error.")
                raise UserError(_("No se pudo timbrar la factura %s.\nDetalle: %s") % (move.name, msg))

        return data

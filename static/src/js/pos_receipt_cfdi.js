/** @odoo-module **/

import { PosOrder } from "@point_of_sale/app/models/pos_order";
import { patch } from "@web/core/utils/patch";

patch(PosOrder.prototype, {
    setup(vals) {
        super.setup(...arguments);
        this.mx_invoice_online = Boolean(vals?.mx_invoice_online);
    },

    setMxInvoiceOnline(value) {
        this.assertEditable();
        this.mx_invoice_online = Boolean(value);
        this._markDirty();
    },

    isMxInvoiceOnline() {
        return Boolean(this.mx_invoice_online);
    },

    getOnlineInvoicePortalUrl() {
        const baseUrl = this.config?._base_url || window.location.origin;
        return `${baseUrl}/portal/facturacion`;
    },

    getOnlineInvoiceBarcodeSrc() {
        const barcodeValue = encodeURIComponent(this.getOnlineInvoicePortalUrl());
        return `/report/barcode/?barcode_type=QR&value=${barcodeValue}&width=180&height=180`;
    },

    serializeForORM(opts = {}) {
        const data = super.serializeForORM(...arguments);
        data.mx_invoice_online = this.isMxInvoiceOnline();
        return data;
    },

    export_for_printing(baseUrl, headerData) {
        return {
            ...super.export_for_printing(...arguments),
            mx_cfdi: this.mx_cfdi || null,
            mx_invoice_online: this.isMxInvoiceOnline(),
            mx_invoice_online_barcode_src: this.getOnlineInvoiceBarcodeSrc(),
            mx_invoice_online_url: this.getOnlineInvoicePortalUrl(),
        };
    },
});

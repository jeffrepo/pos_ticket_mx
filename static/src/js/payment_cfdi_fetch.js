/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PaymentScreen.prototype, {
    toggleMxInvoiceOnline() {
        const enableOnlineInvoice = !this.currentOrder.isMxInvoiceOnline();
        this.currentOrder.setMxInvoiceOnline(enableOnlineInvoice);
        if (enableOnlineInvoice && this.currentOrder.isToInvoice()) {
            this.currentOrder.setToInvoice(false);
            this.currentOrder.mx_cfdi = null;
        }
    },

    isMxInvoiceOnline() {
        return this.currentOrder.isMxInvoiceOnline();
    },

    async toggleIsToInvoice() {
        await super.toggleIsToInvoice(...arguments);
        if (this.currentOrder.isToInvoice() && this.currentOrder.isMxInvoiceOnline()) {
            this.currentOrder.setMxInvoiceOnline(false);
        }
        if (!this.currentOrder.isToInvoice()) {
            this.currentOrder.mx_cfdi = null;
        }
    },

    async _finalizeValidation() {
        await super._finalizeValidation(...arguments);
        try {
            const order = this.currentOrder;
            if (!order?.isToInvoice?.() || order.isMxInvoiceOnline?.()) {
                order.mx_cfdi = null;
                return;
            }
            const data = await this.env.services.orm.call(
                "pos.order",
                "get_mx_cfdi_ticket_data_by_uuid",
                [order.uuid]
            );
            order.mx_cfdi = data || null;
        } catch (e) {
            // No rompas el flujo si falla obtener datos.
        }
    },
});

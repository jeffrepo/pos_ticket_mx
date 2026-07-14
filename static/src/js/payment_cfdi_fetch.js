/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";

patch(PaymentScreen.prototype, {
    toggleMxInvoiceOnline() {
        this.currentOrder.setMxInvoiceOnline(!this.currentOrder.isMxInvoiceOnline());
    },

    isMxInvoiceOnline() {
        return this.currentOrder.isMxInvoiceOnline();
    },

    async _finalizeValidation() {
        await super._finalizeValidation(...arguments);

        // Ya con la orden sincronizada, pide los datos CFDI cuando aplica.
        try {
            const order = this.currentOrder;
            const uuid = order.uuid;
            const data = await this.env.services.orm.call(
                "pos.order",
                "get_mx_cfdi_ticket_data_by_uuid",
                [uuid]
            );
            order.mx_cfdi = data || null;
        } catch (e) {
            // No rompas el flujo si falla obtener datos
            // (el ticket se imprimirá sin los extras)
        }

    },
});

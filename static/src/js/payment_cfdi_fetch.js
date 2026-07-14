/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import OrderPaymentValidation from "@point_of_sale/app/utils/order_payment_validation";

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

patch(PaymentScreen.prototype, {
    toggleMxInvoiceOnline() {
        this.currentOrder.setMxInvoiceOnline(!this.currentOrder.isMxInvoiceOnline());
    },

    isMxInvoiceOnline() {
        return this.currentOrder.isMxInvoiceOnline();
    },

});

patch(OrderPaymentValidation.prototype, {
    async afterOrderValidation() {
        await this.loadMxCfdiTicketData();
        return await super.afterOrderValidation(...arguments);
    },

    async loadMxCfdiTicketData() {
        const order = this.order;
        if (!order?.isToInvoice() || order.isMxInvoiceOnline?.()) {
            return;
        }

        for (let attempt = 0; attempt < 8; attempt++) {
            try {
                const data = await this.pos.data.call(
                    "pos.order",
                    "get_mx_cfdi_ticket_data_by_uuid",
                    [order.uuid]
                );
                if (data?.barcode_src || data?.extra_values?.barcode_src) {
                    order.mx_cfdi = data;
                    return;
                }
                order.mx_cfdi = data || null;
            } catch (e) {
                // No rompas el flujo si falla obtener datos.
            }
            await wait(1000);
        }
    },
});

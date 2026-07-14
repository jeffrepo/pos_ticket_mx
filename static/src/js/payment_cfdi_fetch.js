/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { PosStore } from "@point_of_sale/app/services/pos_store";
import OrderPaymentValidation from "@point_of_sale/app/utils/order_payment_validation";

const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function loadMxCfdiTicketData(pos, order) {
    if (!order || order.isMxInvoiceOnline?.()) {
        return;
    }

    for (let attempt = 0; attempt < 4; attempt++) {
        try {
            const data = await pos.data.call(
                "pos.order",
                "get_mx_cfdi_ticket_data_by_uuid",
                [order.uuid]
            );
            if (data?.barcode_src || data?.extra_values?.barcode_src) {
                order.mx_cfdi = data;
                return;
            }
            if (data && Object.keys(data).length) {
                order.mx_cfdi = data;
            }
        } catch (e) {
            // No rompas el flujo si falla obtener datos.
        }
        await wait(700);
    }
}

patch(PaymentScreen.prototype, {
    toggleMxInvoiceOnline() {
        this.currentOrder.setMxInvoiceOnline(!this.currentOrder.isMxInvoiceOnline());
    },

    isMxInvoiceOnline() {
        return this.currentOrder.isMxInvoiceOnline();
    },

    async _finalizeValidation() {
        if (super._finalizeValidation) {
            await super._finalizeValidation(...arguments);
        }
        await loadMxCfdiTicketData(this.pos, this.currentOrder);
    },
});

patch(OrderPaymentValidation.prototype, {
    async afterOrderValidation() {
        await loadMxCfdiTicketData(this.pos, this.order);
        return await super.afterOrderValidation(...arguments);
    },
});

patch(PosStore.prototype, {
    async printReceipt({ order = this.getOrder(), ...options } = {}) {
        await loadMxCfdiTicketData(this, order);
        return await super.printReceipt({ order, ...options });
    },
});

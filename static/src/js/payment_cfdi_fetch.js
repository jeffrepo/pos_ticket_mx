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
    if (!order.isToInvoice?.()) {
        return;
    }

    const identifiers = [
        order.uuid,
        order.pos_reference,
        order.name,
        order.server_id,
        order.id,
    ].filter((identifier, index, array) => identifier && array.indexOf(identifier) === index);

    for (let attempt = 0; attempt < 10; attempt++) {
        for (const identifier of identifiers) {
            try {
                const orm = pos.env?.services?.orm;
                const data = orm
                    ? await orm.call("pos.order", "get_mx_cfdi_ticket_data_by_uuid", [identifier])
                    : await pos.data.call("pos.order", "get_mx_cfdi_ticket_data_by_uuid", [identifier]);
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
        }
        await wait(800);
    }
}

patch(PaymentScreen.prototype, {
    toggleMxInvoiceOnline() {
        const enableOnlineInvoice = !this.currentOrder.isMxInvoiceOnline();
        this.currentOrder.setMxInvoiceOnline(enableOnlineInvoice);
        if (enableOnlineInvoice && this.currentOrder.isToInvoice()) {
            this.currentOrder.setToInvoice(false);
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

/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import OrderPaymentValidation from "@point_of_sale/app/utils/order_payment_validation";

const logCfdi = (...args) => console.warn("[pos_ticket_mx][cfdi]", ...args);

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
        logCfdi("toggleIsToInvoice before", {
            uuid: this.currentOrder?.uuid,
            isToInvoice: this.currentOrder?.isToInvoice?.(),
            isMxInvoiceOnline: this.currentOrder?.isMxInvoiceOnline?.(),
            hasMxCfdi: Boolean(this.currentOrder?.mx_cfdi),
        });
        await super.toggleIsToInvoice(...arguments);
        if (this.currentOrder.isToInvoice() && this.currentOrder.isMxInvoiceOnline()) {
            this.currentOrder.setMxInvoiceOnline(false);
        }
        if (!this.currentOrder.isToInvoice()) {
            this.currentOrder.mx_cfdi = null;
        }
        logCfdi("toggleIsToInvoice after", {
            uuid: this.currentOrder?.uuid,
            isToInvoice: this.currentOrder?.isToInvoice?.(),
            isMxInvoiceOnline: this.currentOrder?.isMxInvoiceOnline?.(),
            hasMxCfdi: Boolean(this.currentOrder?.mx_cfdi),
        });
    },

    async _finalizeValidation() {
        logCfdi("_finalizeValidation enter");
        await super._finalizeValidation(...arguments);
        try {
            const order = this.currentOrder;
            logCfdi("_finalizeValidation after super", {
                uuid: order?.uuid,
                id: order?.id,
                name: order?.name,
                isToInvoice: order?.isToInvoice?.(),
                isMxInvoiceOnline: order?.isMxInvoiceOnline?.(),
                accountMove: order?.raw?.account_move,
            });
            if (!order?.isToInvoice?.() || order.isMxInvoiceOnline?.()) {
                order.mx_cfdi = null;
                logCfdi("_finalizeValidation skip cfdi load", {
                    uuid: order?.uuid,
                    isToInvoice: order?.isToInvoice?.(),
                    isMxInvoiceOnline: order?.isMxInvoiceOnline?.(),
                });
                return;
            }
            const data = await this.env.services.orm.call(
                "pos.order",
                "get_mx_cfdi_ticket_data_by_uuid",
                [order.uuid]
            );
            order.mx_cfdi = data || null;
            logCfdi("_finalizeValidation cfdi loaded", {
                uuid: order.uuid,
                hasData: Boolean(data && Object.keys(data).length),
                invoiceName: data?.invoice_name,
                cfdiUuid: data?.uuid,
                hasBarcode: Boolean(data?.extra_values?.barcode_src || data?.barcode_src),
            });
        } catch (e) {
            logCfdi("_finalizeValidation cfdi load error", e);
        }
    },
});

patch(OrderPaymentValidation.prototype, {
    async afterOrderValidation() {
        logCfdi("afterOrderValidation before print", {
            uuid: this.order?.uuid,
            id: this.order?.id,
            name: this.order?.name,
            isToInvoice: this.order?.isToInvoice?.(),
            isMxInvoiceOnline: this.order?.isMxInvoiceOnline?.(),
            accountMove: this.order?.raw?.account_move,
            hasMxCfdi: Boolean(this.order?.mx_cfdi),
            hasBarcode: Boolean(
                this.order?.mx_cfdi?.extra_values?.barcode_src || this.order?.mx_cfdi?.barcode_src
            ),
        });
        return await super.afterOrderValidation(...arguments);
    },
});

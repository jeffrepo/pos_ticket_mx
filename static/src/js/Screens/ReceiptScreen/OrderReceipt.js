odoo.define('pos_ticket_mx.OrderReceipt', function(require) {
  'use strict';


  const OrderReceipt = require('point_of_sale.OrderReceipt');
  const Registries = require('point_of_sale.Registries');
  const { useState, useContext } = owl.hooks;
  const models = require('point_of_sale.models');
  const pos_db = require('point_of_sale.DB');
  const rpc = require('web.rpc');


  const PosTicketMxOrderReceipt = OrderReceipt =>
      class extends OrderReceipt {

        constructor(){
          super(...arguments);
          console.log('constructos')
          console.log(this)
          this._invoice_cfdinfo = {
                'sucursal': this.env.pos.config.invoice_journal_id[1],
                'cajero': this.env.pos.employee.name,
                'qr_string': false,
                'total_letras':false,
                'sello_sat':false,
                'datos_certificacion':false,
                'certificado_sat':false,
                'fecha_certificacion':false,
                'sello_digital_cfdi':false,
                'folio_fiscal':false,
                'producto_descuento_id':false,
                'vat':false,
                'descuento':false,
                'serie': false,
                'folio': false,
                'uso_cfdi': false,

          }
        }

      get invoice_cfdinfo() {
          console.log('llamando get')
          console.log(this._invoice_cfdinfo)
          return this._invoice_cfdinfo;
      }
        async willStart(){
          // var self = this;
          var order = this.env.pos.get_order();
          var descuento = 0;
          console.log('will start')
          console.log(this)
          const invoice_cfdinfo = this._invoice_cfdinfo;
          // console.log('receiptenv.order.orderlines')
          // console.log(receiptenv.order.orderlines)
          order.orderlines.forEach(function(l) {
          if (l.price < 0){
              descuento+=l.get_base_price();
            }
          });
          invoice_cfdinfo.descuento = descuento
          console.log('receiptenv.order.name')
          console.log(order.name)
          var order_name = this._receiptEnv.order.name;
          const order_param = {
            model: 'pos.order',
            method: 'search_read',
            args: [[['pos_reference', '=', order_name]], []],
          }

          const orden = await this.rpc(order_param);
          // console.log('ORDEN')
          // console.log(orden)

          if (orden.length > 0 && 'account_move' in orden[0] && orden[0]['account_move'].length > 0){
              // invoice_cfdinfo.folio = orden.name
              const invoice_param = {
                model: 'account.move',
                method: 'search_read',
                args: [[ ['id', '=',  orden[0]['account_move'][0]] ], []],

              }
              const invoice = await this.rpc(invoice_param);
              // console.log('INVOICE')
              // console.log(invoice)
              if (invoice.length > 0){
                  const param_cfdi = {
                        model: 'account.move',
                        method: 'obtener_valores_factura_mx',
                        args: [invoice[0]['id']],
                      }
                  const factura_unica = await this.rpc(param_cfdi);
                  // console.log('factura_unica')
                  // console.log(factura_unica)
                  if (factura_unica){
                        invoice_cfdinfo.qr_string=false;
                        invoice_cfdinfo.total_letras= factura_unica['total_string'];
                        invoice_cfdinfo.datos_certificacion= factura_unica;
                        invoice_cfdinfo.certificado_sat= factura_unica['certificado_sat'];
                        invoice_cfdinfo.fecha_certificacion= factura_unica['fecha_certificacion'];
                        invoice_cfdinfo.folio_fiscal= factura_unica['folio_fiscal'];
                        invoice_cfdinfo.sello_digital_cfdi = factura_unica['sello_digital_cfdi'];
                        invoice_cfdinfo.sello_sat = factura_unica['sello_sat'];
                        invoice_cfdinfo.folio = factura_unica['folio_number'];
                        invoice_cfdinfo.cadena_original= factura_unica['cadena_original'];
                        invoice_cfdinfo.regimen_fiscal = factura_unica['regimen_fiscal'];
                        invoice_cfdinfo.vat = factura_unica['vat_usuario'];
                        invoice_cfdinfo.serie = factura_unica['serie'];
                        // invoice_cfdinfo.folio = "1234";
                        invoice_cfdinfo.uso_cfdi = factura_unica['uso_cfdi'];
                        var extraida = '';
                        var total_factura = Number(factura_unica['monto_total'])
                        if (factura_unica) {
                          let cadena = factura_unica['sello_digital_cfdi']
                          if (cadena != null) {
                              extraida = cadena.substring(336, 346)
                          }

                        }
                        var link="";
                        var string_parte_1 = "&rr="+invoice_cfdinfo['vat'];
                        var link = ["https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?re=",factura_unica['vat_empresa'],string_parte_1,"&","tt=",(total_factura).toFixed(2),"&","id=",invoice_cfdinfo.folio_fiscal,"&","fe=",extraida].join('');
                          console.log('link')
                          console.log(link)
                        invoice_cfdinfo.qr_string = link;
                  }

              }

          }else{
              // console.log('re impresion total')
              // console.log(order.get_total_with_tax())
              // console.log(orden)
              const orden_datos = {
                    model: 'pos.order',
                    method: 'texto_total',
                    args: [[],orden[0].amount_total],
                  }
              const total_texto = await this.rpc(orden_datos);
              invoice_cfdinfo.total_letras = total_texto
          }

        }

      };

  Registries.Component.extend(OrderReceipt, PosTicketMxOrderReceipt);

  return PosTicketMxOrderReceipt;


});

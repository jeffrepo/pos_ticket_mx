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

            var self = this;
            var order = self.env.pos.get_order();
            console.log('Hi my friend');

            this.state = useState({
              'qr_string': false,
              'total_letras':false,
              'datos_certificacion':false,
              'certificado_sat':false,
              'fecha_certificacion':false,
              'folio_fiscal':false,
              'producto_descuento_id':false,
              'vat':false,
              'total_letras':false,
              'descuento':false,
            });
            var state = this.state;

            console.log('Linea 35');
            console.log(state);

            var dicc_varios_datos={
              // 'producto_descuento_id':order.pos.config.producto_descuento_id[0],
              'cliente': order.attributes.client.name,
              'vat': order.attributes.client.vat,
            };

            var descuento = 0;
            order.get_orderlines().forEach(function(l) {
              console.log('linea 48');
              console.log(l);
              if (l.price < 0){
                descuento+=l.get_base_price();
              }
            });
            state['descuento']=descuento;
            rpc.query({
              model: 'pos.order',
              method: 'search_read',
              args: [[['pos_reference', '=', order.name.toString()]], []],
            },{
              timeout:1000,
            }).then(function (orders){
              console.log('Linea 51');
              console.log(orders);
              if (orders.length > 0 && 'account_move' in orders[0] && orders[0]['account_move'].length > 0) {

                rpc.query({
                  model: 'account.move',
                  method: 'search_read',
                  args: [[ ['id', '=', 0] ], []],

                }, {
                  timeout:5000,
                }).then(function (facturas){
                  if (facturas.length > 0) {
                    rpc.query({
                      model: 'account.move',
                      method: 'obtener_valores_factura_mx',
                      args: [facturas[0]['id']],
                    }).then(function (factura_unica) {
                      console.log('Linea 69');
                      console.log(factura_unica);
                      var extraida = '';
                      // var receipt_env = self.getOrderReceiptEnv();
                      // state.qr_string=false;
                      // state.total_letras = factura_unica['total_string'];
                      // order.set_totalString(factura_unica['total_string']);
                      // state.datos_certificacion = factura_unica;
                      // state.certificado_sat = factura_unica['certificado_sat'];
                      // state.fecha_certificacion = factura_unica['fecha_certificacion'];
                      // state.folio_fiscal = factura_unica['folio_fiscal'];
                      // state.producto_descuento_id = false;
                      // state.vat = order.attributes.client.vat;

                      state.qr_string=false;
                      state.total_letras = false;
                      order.set_totalString(factura_unica['total_string']);
                      state.datos_certificacion = false;
                      state.certificado_sat = false;
                      state.fecha_certificacion = false;
                      state.folio_fiscal = false;
                      state.producto_descuento_id = false;
                      state.vat = false;

                      if (factura_unica) {
                        let cadena = factura_unica['sello_digital_emisor']
                        if (cadena != null) {
                            let extraida = cadena.substring(336, 346)
                        }

                      }
                      var link="";
                      // "https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?re=",factura_unica['folio_fiscal'],+"&rr="+receipt_env['receipt']['company']['vat'], +"&tt="+receipt_env['vat'], receipt_env['receipt']['total_with_tax'], extraida
                      var string_parte_1 = "&rr="+state.vat;
                      // var link = ["https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?re=",receipt_env['receipt']['company']['vat'],string_parte_1,"&","tt=",(receipt_env['receipt']['total_with_tax']).toFixed(2),"&","id=",factura_unica['folio_fiscal'],"&","fe=",extraida].join('');
                      // var link = 'https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?re=%s&%s rr=%s tt=%s id=%s fe=%s'%(receipt_env['receipt']['company']['vat'],receipt_env['vat'],(receipt_env['receipt']['total_with_tax']).toFixed(2),factura_unica['folio_fiscal'],extraida);

                      console.log("LINK");
                      console.log(link);
                      state.qr_string = false;

                      // self.$('.pos-receipt-container').html(QWeb.render('OrderReceipt', receipt_env));
                      console.log('state linea 101');
                      console.log(state);
                    });


                  }

                  //else rpc a pos.order buscando la funcion a letras
                  //Codigo python abajo
                  //self.env['account.move'].nombre_funcion(tu parametro en este caso tu pedido)
                });

              }
              else{

                rpc.query({
                  model: 'pos.order',
                  method: 'texto_total',
                  args: [[],order.get_total_with_tax()],
                },{
                  timeout: 5000,
                }).then(function(total){
                  // var state = self.getOrderReceiptEnv();
                  // var state = this.state;
                  state['total_letras']=false;
                  console.log('Linea 137');
                  console.log(state);
                  console.log(total);
                  state['total_letras']=total;
                  console.log(state);
                  order.set_totalString(total);


                });

              }


            });


            console.log('Linea 147 ');
            console.log(self);
            console.log(state)

          }


        };

    Registries.Component.extend(OrderReceipt, PosTicketMxOrderReceipt);

    return PosTicketMxOrderReceipt;


});

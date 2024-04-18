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

            this.state = useState({
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
              'total_letras':false,
              'descuento':false,
            });
            var state = this.state;
            var dicc_varios_datos={
              // 'producto_descuento_id':order.pos.config.producto_descuento_id[0],
              'cliente': order.attributes.client.name,
              'vat': order.attributes.client.vat,
            };

            var descuento = 0;
            order.get_orderlines().forEach(function(l) {
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
              if (orders.length > 0 && 'account_move' in orders[0] && orders[0]['account_move'].length > 0) {
                rpc.query({
                  model: 'account.move',
                  method: 'search_read',
                  args: [[ ['id', '=',  orders[0]['account_move'][0]] ], []],

                }, {
                  timeout:5000,
                }).then(function (facturas){
                  if (facturas.length > 0) {

                    rpc.query({
                      model: 'account.move',
                      method: 'obtener_valores_factura_mx',
                      args: [facturas[0]['id']],
                    },{
                      timeout:3000,
                    }).then(function (factura_unica) {
                      var extraida = '';
                      console.log('factura_unica')
                      console.log(factura_unica)
                      state.qr_string=false;
                      // order.set_totalString(factura_unica['total_string']);
                      state.total_letras = factura_unica['total_string'];
                      state.datos_certificacion = factura_unica;
                      state.certificado_sat = factura_unica['certificado_sat'];
                      state.fecha_certificacion = factura_unica['fecha_certificacion'];
                      state.folio_fiscal = factura_unica['folio_fiscal'];
                      state.sello_digital_cfdi = factura_unica['sello_digital_cfdi'];
                      state.sello_sat = factura_unica['sello_sat'];
                      state.cadena_original = factura_unica['cadena_original'];
                      state.regimen_fiscal = factura_unica['regimen_fiscal'];
                      state.vat = factura_unica['vat_usuario'];
                      var total_factura = Number(factura_unica['monto_total'])
                      if (factura_unica) {
                        let cadena = factura_unica['sello_digital_cfdi']
                        if (cadena != null) {
                            extraida = cadena.substring(336, 346)
                        }

                      }
                      var link="";
                      // "https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?re=",factura_unica['folio_fiscal'],+"&rr="+receipt_env['receipt']['company']['vat'], +"&tt="+receipt_env['vat'], receipt_env['receipt']['total_with_tax'], extraida
                      var string_parte_1 = "&rr="+state.vat;
                      var link = ["https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?re=",factura_unica['vat_empresa'],string_parte_1,"&","tt=",(total_factura).toFixed(2),"&","id=",state.folio_fiscal,"&","fe=",extraida].join('');
                        console.log('link')
                        console.log(link)
                      // var link = 'https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?re=%s&%s rr=%s tt=%s id=%s fe=%s'%(receipt_env['receipt']['company']['vat'],receipt_env['vat'],(receipt_env['receipt']['total_with_tax']).toFixed(2),factura_unica['folio_fiscal'],extraida);

                      state.qr_string = link;

                      // self.$('.pos-receipt-container').html(QWeb.render('OrderReceipt', receipt_env));

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
                  state['total_letras']=total;
                  // order.set_totalString(total);


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

odoo.define('pos_ticket_mx.screens', function (require) {
"use strict";

var models = require('point_of_sale.models');
var screens = require('point_of_sale.screens');

var core = require('web.core');
var rpc = require('web.rpc');

var QWeb = core.qweb;
models.load_fields('res.partner','street2');
models.load_fields('res.partner','city');
models.load_fields('res.partner','country_id');

screens.ReceiptScreenWidget.include({
    render_receipt: function(){
        var order = this.pos.get_order();
        var self = this;
        var dicc_varios_datos={
          'producto_descuento_id':order.pos.config.producto_descuento_id[0],
          'cliente': order.attributes.client.name,
          'vat': order.attributes.client.vat,
        };

        rpc.query({
          model: 'pos.order',
          method: 'search_read',
          args: [[['pos_reference', '=', order.name]], []],
        }, {
          timeout: 5000,
        }).then(function (orders){

          if (orders.length > 0 && 'account_move' in orders[0] && orders[0]['account_move'].length > 0) {

            rpc.query({
              model: 'account.move',
              method: 'search_read',
              args: [[ ['id', '=', orders[0]['account_move'][0]] ], []],

            }, {
              timeout:5000,
            }).then(function (facturas){

              if (facturas.length > 0) {
                rpc.query({
                  model: 'account.move',
                  method: 'obtener_valores_factura_mx',
                  args: [facturas[0]['id']],
                }).then(function (factura_unica) {
                  var receipt_env = self.get_receipt_render_env();
                  receipt_env['qr_string'] = false;
                  receipt_env['receipt']['datos_certificacion'] = factura_unica;
                  receipt_env['certificado_sat'] = factura_unica['certificado_sat'];
                  receipt_env['fecha_certificacion'] = factura_unica['fecha_certificacion'];
                  receipt_env['folio_fiscal'] = factura_unica['folio_fiscal'];
                  console.log("receipt_env");
                  console.log(receipt_env);
                  receipt_env['producto_descuento_id']= order.pos.config.producto_descuento_id[0];
                  receipt_env['vat']= order.attributes.client.vat;
                  let cadena = factura_unica['sello_digital_emisor']
                  let extraida = cadena.substring(336, 346)
                  // "https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?re=",factura_unica['folio_fiscal'],+"&rr="+receipt_env['receipt']['company']['vat'], +"&tt="+receipt_env['vat'], receipt_env['receipt']['total_with_tax'], extraida
                  var string_parte_1 = "&rr="+receipt_env['vat'];
                  var link = ["https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?re=",receipt_env['receipt']['company']['vat'],string_parte_1,"&","tt=",(receipt_env['receipt']['total_with_tax']).toFixed(2),"&","id=",factura_unica['folio_fiscal'],"&","fe=",extraida].join('');
                  // var link = 'https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?re=%s&%s rr=%s tt=%s id=%s fe=%s'%(receipt_env['receipt']['company']['vat'],receipt_env['vat'],(receipt_env['receipt']['total_with_tax']).toFixed(2),factura_unica['folio_fiscal'],extraida);

                  console.log("LINK");
                  console.log(link);
                  receipt_env['qr_string'] = link;

                  self.$('.pos-receipt-container').html(QWeb.render('OrderReceipt', receipt_env));
                  console.log(receipt_env);
                });


              }

            });

          }

        });

        console.log(dicc_varios_datos);

    }
})



});

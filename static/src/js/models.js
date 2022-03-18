odoo.define('pos_ticket_mx.models', function (require) {
"use strict";

const { Context } = owl;
var models = require('point_of_sale.models');
// var { Gui } = require('point_of_sale.Gui');
var core = require('web.core');
var rpc = require('web.rpc');
var _t = core._t;

var _super_order = models.Order.prototype;
models.Order = models.Order.extend({

  set_totalString: function(totalString){
    this.set({
      totalString: totalString
    });
  },

  get_totalString: function(){
    return this.get('totalString');
  },

  initialize: function() {
    _super_order.initialize.apply(this,arguments);
    this.set_totalString();

  },


});







});

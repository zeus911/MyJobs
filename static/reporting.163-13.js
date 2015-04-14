window.onpopstate = function() {

};


// Determines if IE10+ is being used.
var modernBrowser = !(isIE() && isIE() < 10);


// Handles storing data, rendering fields, and submitting report. See prototype functions
var Report = function(types) {
  this.data = {};
  this.fields = [];
  this.types = types;
};


var Field = function(report, label, id, required, defaultVal, helpText) {
  this.report = report;
  this.label = label;
  this.id = id;
  this.required = !!required || false;
  this.defaultVal = defaultVal || '';
  this.helpText = helpText;
};


Field.prototype.renderLabel = function() {
  return '<label for="' + this.id + '">' + this.label + (this.required ? '*' : '') + '</label>';
};


Field.prototype.dom = function() {
  return document.getElementById(this.id);
};


Field.prototype.currentVal = function() {
  return this.dom().value;
};


// TODO: Document namespacing for binding events.
Field.prototype.bind = function(event, callback) {
  if (typeof callback !== "function") {
    throw "Callback parameter expecting function.";
  }

  $(this.dom()).on(event, function(e) {
    callback(e);
  });

  return this;
};


// Unbinds all events of event type on this field.
Field.prototype.unbind = function(event) {
  $(this.dom()).off(event);

  return this;
};


var TextField = function(report, label, id, required, defaultVal, helpText) {
  Field.call(this, report, label, id, required, defaultVal, helpText);
};

TextField.prototype = Object.create(Field.prototype);


// Checks to see if browser is IE. If it is then get version.
function isIE() {
    var myNav = navigator.userAgent.toLowerCase();
    return (myNav.indexOf('msie') !== -1) ? parseInt(myNav.split('msie')[1]) : false;
}

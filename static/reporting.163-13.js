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


Report.prototype.createFields = function(types) {
  var fields = {"prm": [new TextField(this, "Required1", "required1", true),
                        new TextField(this, "Not Required", "notrequired1", false),
                        new TextField(this, "Default Value 5", "defaultvalue", false, "5")]};


  return fields[types[0]];
};


Report.prototype.renderFields = function(renderAt, fields) {
  var $renderAt = $(renderAt),
      field,
      i;

  // Clear what is currently in the container.
  $renderAt.html("");

  // for field in fields render.
  for (i = 0; i < fields.length; i++) {
    field = fields[i];
    $renderAt.append(field.render());
    if (typeof field.bindEvents !== "undefined") {
      field.bindEvents();
    }
  }
};


Report.prototype.findField = function(fieldID) {
  return this.fields.filter(function(field) {
    return (field.id === fieldID ? field : undefined);
  })[0];
};


Report.prototype.save = function() {
  var field,
      i;
  for(i = 0; i < this.fields.length; i++) {
    field = this.fields[i];
    $.extend(this.data, field.onSave());
  }
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


TextField.prototype.render = function() {
  var label = this.renderLabel(),
      field = '<input id="' + this.id + '" value="' + this.defaultVal +
              '" type="text" placeholder="' + this.label + '" />';
  return label + field;
};


TextField.prototype.validate = function() {
  if (this.required && this.currentVal().trim() === "") {
    return {error: "This field is required"};
  } else {
    return {success: true};
  }
};


TextField.prototype.bindEvents = function() {
  var textField = this,
      validate = function(e) {
        var validation = textField.validate(),
            $field = $(textField.dom());
        if ("error" in validation && !$field.parent().hasClass("required")) {
          $field.wrap('<div class="required"></div>');
          $field.after('<div style="color: #990000;">' + validation.error + '</div>');
        }
      };
  this.bind("change", validate);
};

TextField.prototype.onSave = function() {
  var data = {};
  data[this.id] = this.currentVal();
  return data;
};


var DateField = function(report, label, id, required, defaultVal, helpText) {
  Field.call(this, report, label, id, required, defaultVal, helpText);
};

DateField.prototype = Object.create(Field.prototype);


DateField.prototype.render = function() {
  var label = this.renderLabel(),
      dateWidget = $("<div id='" + this.id + "' class='filter-option'><div class='date-picker'></div></div>"),
      datePicker = $(dateWidget).find(".date-picker"),
      to = "<span id='activity-to-' class='datepicker'>to</span>",
      start = "<input id='start-date' class='datepicker picker-left' type='text' value='" + (this.defaultVal ? this.defaultVal.start_date : "") + "' placeholder='Start Date' />",
      end = "<input id='end-date' class='datepicker picker-right' type='text' value='" + (this.defaultVal ? this.defaultVal.end_date : "")  + "' placeholder='End Date' />";

  datePicker.append(start).append(to).append(end);
  dateWidget.append(datePicker);
  return label + dateWidget.prop("outerHTML");
};


DateField.prototype.bindEvents = function() {
  var $element = $(this.dom());
  $element.on("focus.datepicker", ".datepicker", function() {
    $(this).pickadate({
      format: "mm/dd/yyyy",
      selectYears: true,
      selectMonths: true,
      today: false,
      clear: false,
      close: false,
      onOpen: function () {
        if (this.get("id") === "start-date") {
          var end_date = $("#end-date").val();
          this.set("max", new Date(end_date || new Date()));
        } else if (this.get("id") === "end-date") {
          var start_date = $("#start-date").val();
          this.set("min", new Date(start_date || new Date(0)));
        }
      }
    });
  });
};


DateField.prototype.onSave = function() {
  var data = {};
  data.start_date = '';
  return data;
};


var StateField = function(report, label, id, required, defaultVal, helpText) {
  Field.call(this, report, label, id, required, defaultVal, helpText);
};

StateField.prototype = Object.create(Field.prototype);


StateField.prototype.render = function() {
  var label = this.renderLabel(),
      field = this;
  (function() {
    $.ajax({
      type: "POST",
      url: location.protocol + "//" + location.host + "/reports/ajax/get-states",
      data: {"csrfmiddlewaretoken": read_cookie("csrftoken")},
      success: function(data) {
        var $state = $(".state");
        $state.html(data);
        if (field.defaultVal) {
          $state.find("select").val(field.defaultVal);
        }
      }
    });
  })();
  return label + '<div class="state"></div>';
};


// Checks to see if browser is IE. If it is then get version.
function isIE() {
    var myNav = navigator.userAgent.toLowerCase();
    return (myNav.indexOf('msie') !== -1) ? parseInt(myNav.split('msie')[1]) : false;
}

window.onpopstate = function() {

};


// Determines if IE10+ is being used.
var modernBrowser = !(isIE() && isIE() < 10);


// Handles storing data, rendering fields, and submitting report. See prototype functions
var Report = function(types) {
  this.data = {};
  this.fields = this.createFields(types);
  this.types = types;

  this.events();
};


Report.prototype.createFields = function(types) {
  var fields = {"prm": [new TextField(this, "Report Name", "report_name", true),
                        new DateField(this, "Select Date", "date", true, {start_date: "01/01/2014", end_date: "04/14/2015"}),
                        new StateField(this, "State", 'state', false, 'IN'),
                        new TextField(this, "City", "city", false)]};

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

  $renderAt.append('<div class="show-modal-holder">' +
                   '<a id="show-modal" class="btn primary">Generate Report</a>' +
                   '</div>');

  return this;
};


Report.prototype.findField = function(fieldID) {
  return this.fields.filter(function(field) {
    return (field.id === fieldID ? field : undefined);
  })[0];
};


Report.prototype.hasErrors = function() {
  return this.fields.some(function(field) {
    return field.errors.length;
  });
};


Report.prototype.save = function() {
  var errors;

  this.fields.every(function(field) {
    field.validate();
  });

  errors = this.fields.filter(function(field) {
    return field.errors.length > 0;
  });

  if (errors.length) {
    errors.every(function(field) {
      field.showErrors();
    });
    return false;
  } else {
    this.fields.every(function(field) {
      field.onSave();
    });
  }
  return true;
};


Report.prototype.events = function() {
  var report = this,
      container = $("#main-container");

  container.on("click", "#show-modal:not('.disabled')", function() {
    var modal = $("#report-modal"),
        body = modal.children(".modal-body"),
        footer = modal.children(".modal-footer"),
        saved;

    saved = report.save();

    if (saved) {
      body.html();
      modal.modal("show");
    }
  });
};


var Field = function(report, label, id, required, defaultVal, helpText) {
  this.report = report;
  this.label = label;
  this.id = id;
  this.required = !!required || false;
  this.defaultVal = defaultVal || '';
  this.helpText = helpText || '';
  this.errors = [];
};


Field.prototype.renderLabel = function() {
  return '<label for="' + this.id + '">' + this.label + (this.required ? '<span style="color: red;">*</span>' : '') + '</label>';
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


Field.prototype.showErrors = function() {
  var $field = $(this.dom()),
      $showModal = $("#show-modal");

  if (this.errors.length) {
    if (!$field.parent('div.required').length) {
      $field.wrap('<div class="required"></div>');
    }

    if (!$field.prev('.show-errors').length) {
      $field.before('<div class="show-errors">' + this.errors.join(',') + '</div>');
    } else {
      $field.prev().html(this.errors.join(','));
    }
    $showModal.addClass("disabled");
  }
};


Field.prototype.removeErrors = function() {
  var $field = $(this.dom()),
      $showModal = $("#show-modal");

  if ($field.parent('div.required').length) {
    $field.prev('.show-errors').remove();
    $field.unwrap();
  }

  if (!this.report.hasErrors()) {
    $showModal.removeClass("disabled");
  }

  return this;
};


Field.prototype.validate = function() {
  var err = this.label + " is required",
      index = this.errors.indexOf(err);

  if (this.required && this.currentVal().trim() === "") {
    if (index === -1) {
      this.errors.push(err);
    }
  } else {
    if (index !== -1) {
      this.errors.splice(index, 1);
    }
  }

  return this;
};


Field.prototype.onSave = function() {
  var data = {};
  data[this.id] = this.currentVal();
  return data;
};

var TextField = function(report, label, id, required, defaultVal, helpText) {
  Field.call(this, report, label, id, required, defaultVal, helpText);
};

TextField.prototype = Object.create(Field.prototype);


TextField.prototype.render = function() {
  var label = this.renderLabel(),
      field = '<input id="' + this.id + '" value="' + this.defaultVal +
              '" type="text" placeholder="' + this.label + '" />',
      helpText = '<div class="help-text">' + this.helpText + '</div>';
  return label + field + (this.helpText ? helpText : '');
};


TextField.prototype.bindEvents = function() {
  var textField = this,
      $field = $(textField.dom()),
      validate = function() {
        textField.validate();
        if (textField.errors.length) {
          textField.showErrors();
        } else {
          textField.removeErrors();
        }
      },
      trim = function() {
        var value = $field.val().trim();
        $field.val(value);
      };

  this.bind("change.validate", validate);
  this.bind("change.trim", trim);
};


var DateField = function(report, label, id, required, defaultVal, helpText) {
  Field.call(this, report, label, id, required, defaultVal, helpText);
};

DateField.prototype = Object.create(Field.prototype);


DateField.prototype.currentVal = function(id) {
  return $(this.dom()).find("#" + id).val();
};


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

DateField.prototype.bind = function(event, selector, callback) {
  if (typeof callback !== "function") {
    throw "Callback parameter expecting function.";
  }

  $(this.dom()).on(event, selector, function(e) {
    callback(e);
  });

  return this;
};


DateField.prototype.bindEvents = function() {
  var datePicker = function(e) {
        var $targeted = $(e.currentTarget);
        $targeted.pickadate({
          format: "mm/dd/yyyy",
          selectYears: true,
          selectMonths: true,
          min: [2014, 0, 1], // PRM started in 2014/1/1
          max: true,
          today: false,
          clear: false,
          close: false,
          onOpen: function() {
            if(this.get("id") === "start-date") {
              var end_date = $("#end-date").val();
              this.set("max", end_date ? new Date(end_date) : true);
            } else if (this.get("id") === "end-date") {
              var start_date = $("#start-date").val();
              this.set("min", start_date ? new Date(start_date) : [2014, 0, 1]);
            }
          }
        });
      };

  this.bind("focus.datepicker", ".datepicker", datePicker);
};


DateField.prototype.onSave = function() {
  var data = {};
  data.start_date = this.currentVal("start-date");
  data.end_date = this.currentVal("end-date");
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


$(document).ready(function() {
  $("body").append('<a id="test" class="btn">Click me!</a>').append('<div class="meh"></div>');
  $("#test").on("click", function() {
    $("#container").html("").addClass("rpt-container");
    report = new Report(['prm']);
    report.renderFields(".rpt-container", report.fields);
  });
});


// Checks to see if browser is IE. If it is then get version.
function isIE() {
    var myNav = navigator.userAgent.toLowerCase();
    return (myNav.indexOf('msie') !== -1) ? parseInt(myNav.split('msie')[1]) : false;
}

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
  var yesterday = (function(d){d.setDate(d.getDate() - 1); return d; })(new Date),
      contactTypeChoices = [new CheckBoxField(this, "Email", "contact_type", "email"),
                            new CheckBoxField(this,"Phone Call", "contact_type", "phone"),
                            new CheckBoxField(this,"Meeting or Event", "contact_type", "meetingorevent"),
                            new CheckBoxField(this,"Job Followup", "contact_type", "job"),
                            new CheckBoxField(this,"Saved Search Email", "contact_type", "pssemail")
                            ],
      fields = {"prm": [new TextField(this, "Report Name", "report_name", true, reportNameDateFormat(new Date())),
                        new DateField(this, "Select Date", "date", true, {start_date: "01/01/2014", end_date: dateFieldFormat(yesterday)}),
                        new StateField(this, "State", 'state', false),
                        new TextField(this, "City", "city", false),
                        new TagField(this, "Tags", "tag", false, undefined, "Use commas for multiple tags."),
                        new CheckListField(this, "Contact Types", "contact_type", contactTypeChoices, true, 'all'),
                        new FilteredList(this, "Partners", "partner", true),
                        new FilteredList(this, "Contacts", "contact", true)
  ]};

  return fields[types[0]];
};


Report.prototype.renderFields = function(renderAt, fields, clear) {
  var $renderAt = $(renderAt),
      field,
      i;

  // Clear what is currently in the container.
  if (clear) {
    $renderAt.html("");
  }

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
  var report = this,
      errors;

  this.fields.forEach(function(field) {
    field.validate();
  });

  errors = this.fields.filter(function(field) {
    return field.errors.length > 0;
  });

  if (errors.length) {
    errors.forEach(function(field) {
      field.showErrors();
    });
    return false;
  } else {
    this.fields.forEach(function(field) {
      $.extend(report.data, field.onSave());
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
  return '<label class="big-blu" for="' + this.id + '">' + this.label + (this.required ? '<span style="color: #990000;">*</span>' : '') + '</label>';
};


Field.prototype.dom = function() {
  return document.getElementById(this.id);
};


Field.prototype.currentVal = function() {
  return this.dom().value;
};


// TODO: Document namespacing for binding events.
Field.prototype.bind = function(event, selector, callback) {
  if (arguments.length === 2) {
    callback = selector;
    selector = undefined;
  }

  $(this.dom()).on(event, selector, function(e) {
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
    if (!$field.parent("div.required").length) {
      $field.wrap('<div class="required"></div>');
    }

    if (!$field.prev(".show-errors").length) {
      $field.before('<div class="show-errors">' + this.errors.join(', ') + '</div>');
    } else {
      $field.prev().html(this.errors.join(','));
    }
    $showModal.addClass("disabled");
  }
};


Field.prototype.removeErrors = function() {
  var $field = $(this.dom()),
      $showModal = $("#show-modal");

  if ($field.parent("div.required").length) {
    $field.prev(".show-errors").remove();
    $field.unwrap();
  }

  if (!this.report.hasErrors()) {
    $showModal.removeClass("disabled");
  }

  return this;
};


Field.prototype.validate = function() {
  console.log(this);
  var $field = $(this.dom()),
      err = this.label + " is required",
      index = this.errors.indexOf(err);

  if (this.required && this.currentVal().trim() === "") {
    if (index === -1) {
      this.errors.push(err);
      this.showErrors();
    }
  } else {
    if (index !== -1) {
      this.errors.splice(index, 1);
      this.removeErrors();
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
      trim = function() {
        var value = $field.val().trim();
        $field.val(value);
      };

  this.bind("change.validate", function(e) {
    textField.validate();
  });

  this.bind("change.trim", trim);
};

var CheckBoxField = function(report, label, name, defaultVal, checked, helpText) {
  this.checked = typeof checked === 'undefined' ? true : checked;
  this.name = name;
  this.id = name + '_' + defaultVal;

  Field.call(this, report, label, this.id, false, defaultVal, helpText);
};

CheckBoxField.prototype = Object.create(Field.prototype);



CheckBoxField.prototype.render = function(createLabel) {
  createLabel = typeof createLabel === 'undefined' ? true : createLabel;

  var label = this.renderLabel(),
      field = '<label class="field"><input id="' + this.id + '" name="' + this.name +
              '" type="checkbox" value="' + this.defaultVal + 
              (this.checked ? '" checked />' : '" />') + this.label + '</label>',
      helpText = '<div class="help-text">' + this.helpText + '</div>';

  return (createLabel ? label : '') + field + (this.helpText ? helpText : '');
};

var CheckListField = function(report, label, id, choices, required, defaultVal, helpText) {
  this.choices = choices;

  Field.call(this, report, label, id, required, defaultVal, helpText);
};

CheckListField.prototype = Object.create(Field.prototype);


CheckListField.prototype.currentVal = function() {
  return $.map(this.choices, function(c) {
    if (c.checked) {
      return c.currentVal();
    }
  });
};


CheckListField.prototype.render = function() {
  var label = this.renderLabel(),
      html = $.map(this.choices, function(choice) {
        return choice.render(false);
      }).join("  ");

  return label + '<div class="checklist" id="' + this.id + '">' +
                 '<label style="display: inline;"><input value="all" type="checkbox" checked/ >All</label>  ' + html +
                 '</div>';
};


CheckListField.prototype.findChoice = function(choiceID) {
  return this.choices.filter(function(choice) {
    return (choice.id == choiceID ? choice : undefined);
  })[0];
};


CheckListField.prototype.bindEvents = function() {
  var checklist = this;

  this.bind("change", "[value='all']", function(e) {
    var $all = $(e.currentTarget),
        $choices = $(checklist.dom()).find(".field input");

    $choices.prop("checked", $all.is(":checked")).change();
  });

  this.bind("change", ".field input", function(e) {
    var $choice = $(e.currentTarget),
        choices = $(checklist.dom()).find(".field input").toArray(),
        $all = $(checklist.dom()).find("[value='all']"),
        checked;

    checked = choices.every(function(c) { return $(c).is(":checked"); });
    $all.prop("checked", checked);

    checklist.findChoice($choice.attr("id")).checked = $choice.is(":checked");
  });

  this.bind("change.validate", "[value='all']", function(e) {
    checklist.validate();
  });

  this.bind("change.validate", ".field input", function(e) {
    checklist.validate();
  });

};


CheckListField.prototype.validate = function() {
  var err = this.label + " is required",
      index = this.errors.indexOf(err);

  if (this.required && !this.currentVal().length) {
    if (index === -1) {
      this.errors.push(err);
      this.showErrors();
    }
  } else {
    if (index !== -1) {
      this.errors.splice(index, 1);
      this.removeErrors();
    }
  }

  return this;
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
      dateWidget = $('<div id="' + this.id + '" class="filter-option"><div class="date-picker"></div></div>'),
      datePicker = $(dateWidget).find(".date-picker"),
      to = '<span id="activity-to-" class="datepicker">to</span>',
      start = '<input id="start-date" class="datepicker picker-left" type="text" value="' + (this.defaultVal ? this.defaultVal.start_date : "") + '" placeholder="Start Date" />',
      end = '<input id="end-date" class="datepicker picker-right" type="text" value="' + (this.defaultVal ? this.defaultVal.end_date : "")  + '" placeholder="End Date" />';

  datePicker.append(start).append(to).append(end);
  dateWidget.append(datePicker);
  return label + dateWidget.prop("outerHTML");
};


DateField.prototype.validate = function() {
  var dateField = this,
      $dom = $(this.dom()),
      $fields = $dom.find("input.datepicker"), // Both start and end inputs.
      label,
      err;

  $.each($fields, function(index, field) {
    label = $(field).attr('placeholder');
    err = label + " is required";
    index = dateField.errors.indexOf(err);
    if ($(field).val() === "") {
      if (index === -1) {
        dateField.errors.push(label + " is required");
        dateField.showErrors();
      }
    } else {
      if (index !== -1) {
        dateField.errors.splice(index, 1);
        dateField.removeErrors();
      }
    }
  });

  return this;
};


DateField.prototype.bindEvents = function() {
  var dateField = this,
      datePicker = function(e) {
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
  this.bind("change.validate", ".datepicker", function(e) {
    dateField.validate();
  });
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


var TagField = function(report, label, id, required, defaultVal, helpText) {
  TextField.call(this, report, label, id, required, defaultVal, helpText);
};

TagField.prototype = Object.create(TextField.prototype);


TagField.prototype.bindEvents = function() {
  var $dom = $(this.dom());
  $dom.autocomplete({
    focus: function() {
      // Prevent value inserted on focus.
      return false;
    },
    select: function(event, ui) {
      // Split string by "," then trim whitespace on either side of all inputs.
      var inputs = this.value.split(",").map(function(i) {return i.trim();});

      // Remove last element of inputs. Typically is an unfinished string.
      inputs.pop();
      // Add selected item from autocomplete
      inputs.push(ui.item.value);
      // Add placeholder for join to create an extra ", " for UX goodness.
      inputs.push("");
      // Combine everything in inputs with ", ".
      this.value = inputs.join(", ");

      // If there are any inputs already in the field make sure default functionality doesn't run.
      if (inputs.length) {
        return false;
      }
    },
    source: function(request, response) {
      var inputs = request.term.split(",").map(function(i) {return i.trim();}),
          // Last element is always going to be what is being searched for.
          keyword = inputs.pop(),
          // Initialize list of suggested tag names.
          suggestions;

      $.ajaxSettings.traditional = true;
      $.ajax({
        type: "GET",
        url: "/reports/ajax/mypartners/tag",
        data: {name: keyword, values: ["pk", "name"], order_by: ["name"]},
        success: function(data) {
          suggestions = data.filter(function(d) {
            // Don't suggest things that are already selected.
            if (inputs.indexOf(d.name) === -1) {
              return d;
            }
          }).map(function(d) {
            // Only care about name string.
            return d.name;
          });

          response(suggestions);
        }
      });
    }
  });
};


TagField.prototype.onSave = function() {
  var data = {};
  // Split on commas. Trim each element in array. Remove any elements that were blank strings.
  // #2proud2linebreak
  data.tags = this.currentVal().split(",").map(function(t) {return t.trim();}).filter(function(t) { if (!!t) {return t;} });
  return data;
};


var FilteredList = function(report, label, id, required, defaultVal, helpText) {
  Field.call(this, report, label, id, required, defaultVal, helpText);
};

FilteredList.prototype = Object.create(Field.prototype);


FilteredList.prototype.renderLabel = function() {
  return '<div id="'+ this.id +'-header" class="list-header">' +
         '<input id="' + this.id + '-all-checkbox" type="checkbox" ' + (this.value ? "" : "checked") + ' />' +
         ' All ' + this.label + ' ' +
         '<span>(<span class="record-count">0</span> ' + this.label + ' Selected)</span>' +
         '</div>';
};


FilteredList.prototype.render = function() {
  var label = this.renderLabel(),
      body = '<div id="' + this.id + '" class="list-body no-show"></div>';
  this.filter();
  return label + body;
};


FilteredList.prototype.filter = function() {
  var data = {},
      filteredList = this;

  if (this.id === "partner") {
    // annotate how many records a partner has.
    $.extend(data, {count: "contactrecord",
                    values: ["pk", "name", "count"],
                    order_by: ["name"]}
    );
  } else if (this.id === "contact") {
    $.extend(data, {values: ["pk", "name", "email"], order_by: "name"});
  }

  $.ajaxSettings.traditional = true;
  $.ajax({
    type: "GET",
    url: "/reports/ajax/mypartners/" + this.id,
    data: data,
    success: function(data) {
      $recordCount = $('#' + filteredList.id + '-header').find(".record-count");
      $(".list-body#" + filteredList.id).append('<ul><li>' + data.map(function(element) {
        return '<label><input type="checkbox" data-pk="' + element.pk + '" checked /> ' + element.name + 
               '<span class="pull-right">' + (filteredList.id === 'partner' ? element.count : "") + '</label>';
      }).join("</li><li>") + '</li></ul>').removeClass("no-show");
  
      $recordCount.text(filteredList.currentVal().length);
    }
  });
};


FilteredList.prototype.currentVal = function() {
  return $.map($(this.dom()).find("input").toArray(), function(c) {
    if (c.checked) {
      return $(c).data("pk");
    }
  });
};


FilteredList.prototype.bindEvents = function() {
  var filteredList = this,
      $header = $('#' + filteredList.id + '-header'),
      $recordCount = $header.find(".record-count"),
      $all = $header.find("input");

  $header.find("input").on("change", function() {
    var $choices = $(filteredList.dom()).find("input");

    $choices.prop("checked", $(this).is(":checked"));
    $($choices[$choices.length - 1]).change();
  });

  $(this.dom()).bind("change", "input", function() {
    var choices = $(filteredList.dom()).find("input").toArray(),
        checked;

    checked = choices.every(function(c) { return $(c).is(":checked"); });
    $all.prop("checked", checked);
    $recordCount.text(filteredList.currentVal().length);
  });

  $all.on("change", function(e) {
    filteredList.validate();
  });

  $(this.dom()).bind("change", "input", function(e) {
    filteredList.validate();
  });
};

FilteredList.prototype.validate = function() {
  var err = this.label + " is required",
      index = this.errors.indexOf(err);

  if (this.required && !this.currentVal().length) {
    if (index === -1) {
      this.errors.push(err);
      this.showErrors();
    }
  } else {
    if (index !== -1) {
      this.errors.splice(index, 1);
      this.removeErrors();
    }
  }

  return this;
};

// Capitalize first letter of a string.
String.prototype.capitalize = function() {
  return this.charAt(0).toUpperCase() + this.slice(1);
};


$(document).ready(function() {
  $("body").append('<a id="test" class="btn">Click me!</a>').append('<div class="meh"></div>');
  $("#test").on("click", function() {
    $("#container").html("").addClass("rpt-container");
    report = new Report(['prm']);
    report.renderFields(".rpt-container", report.fields, true);
  });
});


// Checks to see if browser is IE. If it is then get version.
function isIE() {
    var myNav = navigator.userAgent.toLowerCase();
    return (myNav.indexOf('msie') !== -1) ? parseInt(myNav.split('msie')[1]) : false;
}


function reportNameDateFormat(date) {
  var year = date.getFullYear(),
      month = date.getMonth(),
      day = date.getDate(),
      hours = date.getHours(),
      minutes = date.getMinutes(),
      seconds = date.getSeconds(),
      milliseconds = date.getMilliseconds();

  month = turnTwoDigit(parseInt(month) + 1);
  day = turnTwoDigit(day);
  hours = turnTwoDigit(hours);
  minutes = turnTwoDigit(minutes);
  seconds = turnTwoDigit(seconds);

  return year + "-" + month + "-" + day + "_" + hours + ":" + minutes + ":" + seconds + "." + milliseconds;
}


function dateFieldFormat(date) {
  var day = date.getDate(),
      month = date.getMonth(),
      year = date.getFullYear();

  day = turnTwoDigit(day);
  month = turnTwoDigit(parseInt(month) + 1);

  return month + "/" + day + "/" + year;
}


function turnTwoDigit(value) {
  return value < 10 ? "0" + value : value;
}

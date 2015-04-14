function checkDuplicates(elementID, values, url) {
  var $element = $(elementID),
      names = $.map(values, function(item, index) { return item.name.toLowerCase(); }),
      index = names.indexOf($element.val().trim().toLowerCase()),
      $editModal = $("#edit-item-modal");

  if (index > -1) {
    $("ul.record-info").html(
      "<li>Name: " + values[index].name + "</li>" +
      (values[index].uri ? "<li>URL: " + values[index].uri + "</li>" : "") +
      (values[index].email ? "<li>Email: " + values[index].email + "</li>" : "") +
      (values[index].phone ? "<li>Phone: " + values[index].phone + "</li>" : "")
    );

    $("#edit-record-button").attr("href", url + values[index].pk);

    $editModal.modal("show").on("hidden", function() {
      $element.select();
    });

    return false;
  }
  return true;
}

$(document).ready(function() {
  var $otherInputs = $("input:gt(0)"),
      $saveButton = $("#item-save"),
      validForm = false;
  
  $otherInputs.on("focus", function() {
    if ($("#id_partner-partnername").length) {
      checkDuplicates("#id_partner-partnername", partners, "/prm/view/details?partner=");
    } else if ($("#id_contact-name").length) {
      checkDuplicates("#id_contact-name", contacts, "/prm/view/details/edit?partner=" + partner + "&id=");
    }
  });

  if ($saveButton.length) {
    oldCallback = $._data($saveButton[0], "events").click[0];
    $saveButton.unbind("click");
    $saveButton.on("click", function(e) {
      e.preventDefault();

      if ($("#id_partner-partnername").length) {
        validForm = checkDuplicates("#id_partner-partnername", partners, "/prm/view/details?partner=");
      } else if ($("#id_contact-name").length) {
        validForm = checkDuplicates("#id_contact-name", contacts, "/prm/view/details/edit?partner=" + partner + "&id=");
      }

      if (validForm) {
        $saveButton.unbind("click").bind("click", oldCallback).click();
      }
    });
  }

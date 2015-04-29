/*
 * Checks if the vaue of an input is already in an array of objects
 *
 * Inputs:
 * :elementId: The element to grab by ID
 * :values: The list of objects to check against for duplicates. Also has a
 *          number of attributes used for display, such as email, uri, etc. 
 *  :url: The url to attach the element's primary key to. This url is used to
 *        take the user to the already existing item.
 *
 *  Outputs:
 *  This function returns a boolean denoting whether or not a duplicate was
 *  found.
 */
function checkDuplicates(elementID, values, url) {
  var $element = $(elementID),
      names = $.map(values, function(item, index) { return item.name.toLowerCase(); }),
      index = names.indexOf($.trim($element.val()).toLowerCase()),
      $editModal = $("#edit-item-modal");

  if (index > -1) {
    // Create an unordered list of the pre-existing item's attributes.
    $("ul.record-info").html(
      "<li>Name: " + values[index].name + "</li>" +
      (values[index].uri ? "<li>URL: " + values[index].uri + "</li>" : "") +
      (values[index].email ? "<li>Email: " + values[index].email + "</li>" : "") +
      (values[index].phone ? "<li>Phone: " + values[index].phone + "</li>" : "")
    );

    // Update the href for hte edit button.
    $("#edit-record-button").attr("href", url + values[index].pk);

    // Return focus to the element that contains duplicate data.
    $editModal.modal("show").on("hidden", function() {
      $element.select();
    });

    return false;
  }
  return true;
}

$(document).ready(function() {
  var $otherInputs = $("input:gt(0), textarea"),
      $saveButton = $("#item-save, #init-partner-save"),
      validForm = false;
  
  $otherInputs.on("focus", function() {
    // Which input is present determines which form we are viewing, and thus
    // which parameters we need to send to checkDuplicates.
    if ($("#id_partner-partnername").length) {
      checkDuplicates("#id_partner-partnername", partners, "/prm/view/details?partner=");
    } else if ($("#id_contact-name").length) {
      checkDuplicates("#id_contact-name", contacts, "/prm/view/details/edit?partner=" + partner + "&id=");
    }
  });

  // If the save button doesn't exist, we are editing a partner or contact,
  // which doens't require this special behavior.
  if ($saveButton.length) {
    // prm.x-x.js has different handlers depending on which form we are on.
    // Here, we are preserving that callback, detatching it, then re-attaching
    // it later if the form turns out to be valid
    oldCallback = $._data($saveButton[0], "events").click[0];
    $saveButton.unbind("click");
    $saveButton.on("click", function(e) {
      e.preventDefault();

      if ($("#id_partner-partnername").length) {
        validForm = checkDuplicates("#id_partner-partnername", partners, "/prm/view/details?partner=");
      } else if ($("#id_contact-name").length) {
        validForm = checkDuplicates("#id_contact-name", contacts, "/prm/view/details/edit?partner=" + partner + "&id=");
      }

      // Restore the original callback behavior for the save button
      if (validForm) {
        $saveButton.unbind("click").bind("click", oldCallback).click();
      }
    });
  }
});

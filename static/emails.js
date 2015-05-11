(function($) {
    $(document).ready(function () {
        var $model = $('#id_model'),
            // Fields don't change between requests; cache them so that they
            // can be quickly retrieved when the model input is toggled.
            model_fields = {};
        $model.change(
            function () {
                var fields,
                    field,
                    $input = $('#id_field'),
                    selected = $input.val(),
                    $select = $('<select id="id_field" name="field"></select>'),
                    options = ['<option value="">---------</option>'],
                    value = $model.val();
                if (value.length > 0) {
                    // A value other than the default (---------) has been
                    // selected for the model input; get the fields associated
                    // with that model.
                    if (model_fields.hasOwnProperty(value)) {
                        // We've already retrieved the fields for this model;
                        // pull it from our cache.
                        $select = model_fields[value];
                    } else {
                        // We have not retrieved this model's field list yet.
                        $.getJSON('/emails/get-fields/', 'model=' + value,
                            function (data) {
                                fields = window.location.href.indexOf('valueevent') > -1 ? data['value'] : data['time'];

                                for (field in fields) {
                                    if (fields.hasOwnProperty(field)) {
                                        // Construct the <option> for this field;
                                        // selects options based on whether anything
                                        // was already selected or not.
                                        options.push('<option value="' + fields[field] + '" ' + (options.length === 0 && selected === "" ? "selected" : (selected !== "" && fields[field] === selected ? "selected" : "")) + '>' + fields[field] + '</option>');
                                    }
                                }
                                $select.append(options.join(''));
                                model_fields[value] = $select;
                            })
                    }
                    $select.val(selected);
                    $input.replaceWith($select);
                }
            })
        $model.change()
    });
    // This will be used on admin and non-admin pages; ensure that jQuery is
    // usable regardless of location.
})($ || django.jQuery);

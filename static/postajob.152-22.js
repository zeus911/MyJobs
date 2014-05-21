$(document).ready(function(){
    update_apply_fields();

    $(document).on("change", '#id_apply_type', function(){
        update_apply_fields();
    });
});

function hide_apply_field(field_name) {
    $('.' + field_name + '-label').hide();
    $('.' + field_name + '-field').hide();
}

function show_apply_field(field_name) {
    $('.' + field_name + '-label').show();
    $('.' + field_name + '-field').show();
}

function clear_input(field_name) {
    $('#id_' + field_name).val('');
}

function update_apply_fields() {
    apply_type = $('#id_apply_type').val();

    if(apply_type == 'link') {
        show_apply_field('apply-link');
        clear_input('apply_email');
        clear_input('apply_info');
        hide_apply_field('apply-email');
        hide_apply_field('apply-instructions')
    }
    else if(apply_type == 'email') {
        show_apply_field('apply-email');
        clear_input('apply_email');
        clear_input('apply_link');
        hide_apply_field('apply-link');
        hide_apply_field('apply-instructions')
    }
    else {
        show_apply_field('apply-instructions');
        clear_input('apply_email');
        clear_input('apply_link');
        hide_apply_field('apply-link');
        hide_apply_field('apply-email');
    }
}
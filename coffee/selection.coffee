jQuery ->
    jQuery('#select-all').click ->
        jQuery('input[type="checkbox"]').prop 'checked', true

    jQuery('#select-none').click ->
        jQuery('input[type="checkbox"]').prop 'checked', false

jQuery ->
    $('#select-all').click ->
        $('input[type="checkbox"]').prop 'checked', true

    $('#select-none').click ->
        $('input[type="checkbox"]').prop 'checked', false

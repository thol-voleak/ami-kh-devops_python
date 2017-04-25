function onInlineSetupDataTable(tableId, m_action_types, m_actor_types, m_sof_types, m_amount_type, fee_tier_id, csrf_token) {

    var nEditing = null;
    var oTable;

    function restoreRow(oTable, nRow) {
        var aData = oTable.fnGetData(nRow);
        var jqTds = $('>td', nRow);

        for (var i = 0, iLen = jqTds.length; i < iLen; i++) {
            oTable.fnUpdate(aData[i], nRow, i, false);
        }

        oTable.fnDraw();
    }

    function editRow(oTable, nRow) {
        var aData = oTable.fnGetData(nRow);
        var jqTds = $('>td', nRow);
        var htmlSelected = '';

        // Master: ActionTypes Dropdown
        var htmlDDActionTypes = '';
        jQuery.each(m_action_types, function() {
            if (aData[0].toLowerCase() == this.action_type.toLowerCase()) {
                htmlSelected = ' selected=\"selected\" ';
            } else {
                htmlSelected = ' ';
            }

            htmlDDActionTypes += '<option value="' + this.action_type_id + '"' + htmlSelected + '>' + this.action_type + '</option>';
        });

        // Master: Actors Dropdown
        var htmlDDActors = '';
        jQuery.each(m_actor_types, function() {
            if (aData[1].toLowerCase() == this.actor_type.toLowerCase()) {
                htmlSelected = ' selected=\"selected\" ';
            } else {
                htmlSelected = ' ';
            }

            htmlDDActors += '<option value="' + this.actor_type_id + '"' + htmlSelected + '>' + this.actor_type + '</option>';
        });

        // Master: SOFTypes Dropdown
        var htmlDDSOFTypes = '';
        jQuery.each(m_sof_types, function() {
            if (aData[3].toLowerCase() == this.sof_type.toLowerCase()) {
                htmlSelected = ' selected=\"selected\" ';
            } else {
                htmlSelected = ' ';
            }

            htmlDDSOFTypes += '<option value="' + this.sof_type_id + '"' + htmlSelected + '>' + this.sof_type + '</option>';
        });

        // Master: AmountTypes Dropdown
        var htmlDDAmountTypes = '';
        jQuery.each(m_amount_type, function() {
            console.log('aData: ' + JSON.stringify(aData, null, 4));

            if (aData[5].toLowerCase() == this.amount_type.toLowerCase()) {
                htmlSelected = ' selected=\"selected\" ';
            } else {
                htmlSelected = ' ';
            }

            htmlDDAmountTypes += '<option value="' + this.amount_type_id + '"' + htmlSelected + '>' + this.amount_type + '</option>';
        });

        jqTds[0].innerHTML = '<select type=\'text\' class=\'form-control\' name=\'action_type\'>' + htmlDDActionTypes + '</select>';
        jqTds[1].innerHTML = '<select type=\'text\' class=\'form-control\' name=\'actor_type\'>' + htmlDDActors + '</select>';
        jqTds[2].innerHTML = '';
        jqTds[3].innerHTML = '<select type=\'text\' class=\'form-control\' name=\'sof_type_id\'>' + htmlDDSOFTypes + '</select>';
        jqTds[4].innerHTML = '<input type=\'text\' class=\'form-control\' name=\'specific_sof\' value=\'' + aData[4] + '\'>';
        jqTds[5].innerHTML = '<select type=\'text\' class=\'form-control\' name=\'amount_type\'>' + htmlDDAmountTypes + '</select>';
        jqTds[6].innerHTML = '<input type=\'text\' class=\'form-control\' name=\'rate\' required value=\'' + aData[6] + '\'>';

        // Action Buttons
        var htmlButtonSave = '<a class=\'edit btn btn-outline btn-xs btn-primary text-info small\' role=\'button\' id=\'payment_and_fee_stucture_btn_save\'>Save</a>';
        var htmlButtonCancel = '<a class=\'cancel btn btn-outline btn-xs btn-primary text-info small\' role=\'button\'>Cancel</a>';

        jqTds[7].innerHTML = htmlButtonSave + htmlButtonCancel;

        onBindingButtonsCancelEvent();
    }

    function saveRow(oTable, nRow) {
        var jqInputs = $('input', nRow);
        var jqSelects = $('select', nRow);

        var distribution_id = $(nRow).data('id');

        oTable.fnUpdate($(jqSelects[0]).find(":selected").html(), nRow, 0, false);      // Action_Type
        oTable.fnUpdate($(jqSelects[1]).find(":selected").html(), nRow, 1, false);      // Actor_Type
                                                                                        // Specific ID
        oTable.fnUpdate($(jqSelects[2]).find(":selected").val(), nRow, 3, false);       // Sof Type ID
        oTable.fnUpdate(jqInputs[0].value, nRow, 4, false);                             // Specific SOF
        oTable.fnUpdate($(jqSelects[3]).find(":selected").html(), nRow, 5, false);      // Amount Type
        oTable.fnUpdate(jqInputs[1].value, nRow, 6, false);                             // Rate

        var htmlButtonEdit = '<a class=\'edit btn btn-outline btn-xs btn-primary edit text-info small\' role=\'button\'>Edit</a>';
        var htmlButtonDelete = '';

        if (tableId == "tbl_setting_payment_fee_structure") {
            htmlButtonDelete = '' +
                '<span type=\'button\' class=\'btn btn-outline btn-xs delete btn-primary text-info\' role=\'button\' id=\'btn_setting_payment_fee_structure_delete\' onclick=\'deleteDistribution(' + distribution_id + ')\'>' +
                    '<span class=\'small\'>' +
                        'Delete' +
                    '</span>' +
                '</span>';
        } else if (tableId == "tbl_setting_bonus") {
            htmlButtonDelete = '' +
                '<span type=\'button\' class=\'btn btn-outline btn-xs delete btn-primary text-info\' role=\'button\' id=\'btn_setting_bonus_delete\' onclick=\'deleteSettingBonus(' + distribution_id + ')\'>' +
                '<span class=\'small\'>' +
                'Delete' +
                '</span>' +
                '</span>';
        }

        oTable.fnUpdate(htmlButtonEdit + htmlButtonDelete, nRow, 7, false);
        oTable.fnDraw();

        onBindingButtonsDeleteEvent();
    }

    // For Balance
    function saveRowToServer(oTable, nRow) {
        var jqInputs = $('input', nRow);
        var jqSelects = $('select', nRow);
        var url = $(nRow).data('url');

        // Request to server
        $.ajax({
            url: url,
            type: "POST",
            data: {
                "fee_tier_id": fee_tier_id,
                "action_type": $(jqSelects[0]).find(":selected").html(),
                "actor_type": $(jqSelects[1]).find(":selected").html(),
                // 2 = empty data
                "sof_type_id": $(jqSelects[2]).find(":selected").val(),
                "specific_sof": jqInputs[0].value,
                "amount_type": $(jqSelects[3]).find(":selected").html(),
                "rate": jqInputs[1].value
            },
            dataType: "json",
                beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            },
            success: function (response) {

                var data = JSON.stringify(response);
                var json = $.parseJSON(data);
                console.log('JSON: ');
                console.log(json);

                if (json.status.code == 'success') {
                    console.log('Saved row data');
                    saveRow(oTable, nRow);
                    addMessage("Edit successfully!");
                } else {
                    console.log('Error adding row data');
                    addMessage("Edit error!");
                }

            },
            error: function (err) {
                var json = JSON.stringify(err);
                console.log('JSON: ');
                console.log(json);

                addMessage("Edit error!");
            }
        });
    }

    function saveRowBonusToServer(oTable, nRow) {
        var jqInputs = $('input', nRow);
        var jqSelects = $('select', nRow);
        var url = $(nRow).data('url');

        // Request to server
        $.ajax({
            url: url,
            type: "POST",
            data: {
                "action_type": $(jqSelects[0]).find(":selected").html(),
                "actor_type": $(jqSelects[1]).find(":selected").html(),
                // 2 = empty data
                "sof_type_id": $(jqSelects[2]).find(":selected").val(),
                "specific_sof": jqInputs[0].value,
                "amount_type": $(jqSelects[3]).find(":selected").html(),
                "rate": jqInputs[1].value,
                "specific_actor_id": ''
            },
            dataType: "json",
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            },
            success: function (response) {

                var data = JSON.stringify(response);
                var json = $.parseJSON(data);
                console.log('JSON: ');
                console.log(json);

                if (json.status.code == 'success') {
                    console.log('Saved row data');
                    saveRow(oTable, nRow);
                    addMessage("Edit successfully!");
                } else {
                    console.log('Error adding row data');
                    addMessage("Edit error!");
                }

            },
            error: function (err) {
                var json = JSON.stringify(err);
                console.log('JSON: ');
                console.log(json);

                addMessage("Edit error!");
            }
        });
    }

    oTable = $('#' + tableId).dataTable({
        "searching":  false,
        "paging":   false,
        "ordering": false,
        "info":     false
    });

    function onBindingButtonsCancelEvent() {
        $('#' + tableId).on('click', 'a.cancel', function (e) {
            e.preventDefault();

            /* Get the row as a parent of the link that was clicked on */
            var nRow = $(this).parents('tr')[0];

            restoreRow(oTable, nEditing);
            nEditing = nRow;
        });
    }

    function onBindingButtonsDeleteEvent() {

        $('.datatable').on('click', 'span.delete', function (e) {
            e.preventDefault();

            var nRow = $(this).parents('tr')[0];
            oTable.fnDeleteRow(nRow);
        });
    }

    function onBindingButtonsEditEvent() {

        $('#' + tableId).on('click', 'a.edit', function (e) {
            e.preventDefault();

            /* Get the row as a parent of the link that was clicked on */
            var nRow = $(this).parents('tr')[0];

            if (nEditing !== null && nEditing !== nRow) {
                /* Currently editing - but not this row - restore the old before continuing to edit mode */
                restoreRow(oTable, nEditing);
                editRow(oTable, nRow);
                nEditing = nRow;
            } else if (nEditing === nRow && this.innerHTML === 'Save') {
                /* Editing this row and want to save it */

                if (tableId == "tbl_setting_payment_fee_structure")
                    saveRowToServer(oTable, nEditing);
                else
                    saveRowBonusToServer(oTable, nEditing);

                nEditing = null;
            } else {
                /* No edit in progress - let's start one */
                editRow(oTable, nRow);
                nEditing = nRow;
            }

            return false;
        });
    }

    onBindingButtonsEditEvent();
    onBindingButtonsDeleteEvent();
}


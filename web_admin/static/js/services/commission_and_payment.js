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
            if (aData[5].toLowerCase() == this.amount_type.toLowerCase()) {
                htmlSelected = ' selected=\"selected\" ';
            } else {
                htmlSelected = ' ';
            }

            htmlDDAmountTypes += '<option value="' + this.amount_type_id + '"' + htmlSelected + '>' + this.amount_type + '</option>';
        });

        // Build up HTML ID Element
        // Row data
        var htmlIDActionTypes = 'id=\'';
        var htmlIDActorTypes = 'id=\'';
        var htmlIDSpecificID = 'id=\'';
        var htmlIDSOFTypes = 'id=\'';
        var htmlIDSpecificSOF = 'id=\'';
        var htmlIDRate = 'id=\'';
        var htmlIDAmount = 'id=\'';

        // For SpecificID changing according to Actor Types.
        var htmlIDSpecificIDDisabled = '';
        var htmlActorEventJS = "";

        // Buttons
        var htmlIDBtnSave = 'id=\'';
        var htmlIDBtnCancel = 'id=\'';

        if (tableId == 'tbl_setting_payment_fee_structure') {
            htmlIDActionTypes += 'ddl_setting_payment_fee_structure_dc_edit';
            htmlIDActorTypes += 'ddl_setting_payment_fee_structure_actor_edit';
            htmlIDSpecificID += 'txt_setting_payment_fee_structure_specific_id_edit';
            htmlIDSOFTypes += 'ddl_setting_payment_fee_structure_source_of_fund_edit';
            htmlIDSpecificSOF += 'txt_setting_payment_fee_structure_specific_source_of_fund_edit';
            htmlIDAmount += 'ddl_setting_payment_fee_structure_from_amount_edit';
            htmlIDRate += 'txt_setting_payment_fee_structure_rate_edit';
            htmlIDBtnSave += 'btn_setting_payment_fee_structure_save';
            htmlIDBtnCancel += 'btn_setting_payment_fee_structure_cancel';

            htmlActorEventJS = "onchange=\"changeSpecificActorType('#ddl_setting_payment_fee_structure_actor_edit', '#txt_setting_payment_fee_structure_specific_id_edit')\"";

        } else if (tableId == 'tbl_setting_bonus') {
            htmlIDActionTypes += 'ddl_setting_bonus_dc_edit';
            htmlIDActorTypes += 'ddl_setting_bonus_actor_edit';
            htmlIDSpecificID += 'txt_setting_bonus_specific_id_edit';
            htmlIDSOFTypes += 'ddl_setting_bonus_src_fund_edit';
            htmlIDSpecificSOF += 'txt_setting_bonus_spec_src_fund_edit';
            htmlIDAmount += 'ddl_setting_bonus_amount_edit';
            htmlIDRate += 'txt_setting_bonus_rate_edit';
            htmlIDBtnSave += 'btn_setting_bonus_save';
            htmlIDBtnCancel += 'btn_setting_bonus_cancel';

            htmlActorEventJS = "onchange=\"changeSpecificActorType('#ddl_setting_bonus_actor_edit', '#txt_setting_bonus_specific_id_edit')\"";

        } else if (tableId == 'tbl_bonus') {
            htmlIDActionTypes += 'ddl_bonus_dc_edit';
            htmlIDActorTypes += 'ddl_bonus_actor_edit';
            htmlIDSpecificID += 'txt_bonus_specific_id_edit';
            htmlIDSOFTypes += 'ddl_bonus_source_of_fund_edit';
            htmlIDSpecificSOF += 'txt_bonus_specific_source_of_fund_edit';
            htmlIDAmount += 'ddl_bonus_amount_edit';
            htmlIDRate += 'txt_bonus_rate_edit';
            htmlIDBtnSave += 'btn_bonus_save';
            htmlIDBtnCancel += 'btn_bonus_cancel';

            htmlActorEventJS = "onchange=\"changeSpecificActorType('#ddl_bonus_actor_edit', '#txt_bonus_specific_id_edit')\"";
        }
        htmlIDActionTypes += '\'';
        htmlIDActorTypes += '\'';
        htmlIDSpecificID += '\'';
        htmlIDSOFTypes += '\'';
        htmlIDSpecificSOF += '\'';
        htmlIDAmount += '\'';
        htmlIDRate += '\'';
        htmlIDBtnSave += '\'';
        htmlIDBtnCancel += '\'';

        if (aData[1] === 'Specific ID')
            htmlIDSpecificIDDisabled = '';
        else
            htmlIDSpecificIDDisabled = 'disabled';

        jqTds[0].innerHTML = '<select ' + htmlIDActionTypes + ' type=\'text\' class=\'form-control\' name=\'action_type\' >' + htmlDDActionTypes + '</select>';
        jqTds[1].innerHTML = '<select ' + htmlActorEventJS + ' ' + htmlIDActorTypes + ' type=\'text\' class=\'form-control\' name=\'actor_type\'>' + htmlDDActors + '</select>';
        jqTds[2].innerHTML = '<input ' + htmlIDSpecificIDDisabled + ' ' + htmlIDSpecificID + ' type=\'text\' class=\'form-control\' name=\'specific_id\' value=\'' + aData[2] + '\'>';
        jqTds[3].innerHTML = '<select ' + htmlIDSOFTypes + ' type=\'text\' class=\'form-control\' name=\'sof_type_id\'>' + htmlDDSOFTypes + '</select>';
        jqTds[4].innerHTML = '<input ' + htmlIDSpecificSOF + ' type=\'text\' class=\'form-control\' name=\'specific_sof\' value=\'' + aData[4] + '\'>';
        jqTds[5].innerHTML = '<select ' + htmlIDAmount + ' type=\'text\' class=\'form-control\' name=\'amount_type\'>' + htmlDDAmountTypes + '</select>';
        jqTds[6].innerHTML = '<input ' + htmlIDRate + ' type=\'text\' class=\'form-control\' name=\'rate\' required value=\'' + aData[6] + '\'>';

        // Action Buttons
        var htmlButtonSave = '<button type=\'button\' ' + htmlIDBtnSave + ' class=\'btn btn-outline btn-xs edit btn-primary text-info small\'>Save</button>';
        var htmlButtonCancel = '<button type=\'button\' ' + htmlIDBtnCancel + ' class=\'btn btn-outline btn-xs cancel btn-primary text-info small\'>Cancel</button>';

        jqTds[7].innerHTML = htmlButtonSave + '&nbsp;' + htmlButtonCancel;

        onBindingButtonsCancelEvent();
    }

    function saveRow(oTable, nRow) {
        var jqInputs = $('input', nRow);
        var jqSelects = $('select', nRow);

        var distribution_id = $(nRow).data('id');

        // DD Type
        oTable.fnUpdate($(jqSelects[0]).find(":selected").html(), nRow, 0, false);      // Action_Type
        oTable.fnUpdate($(jqSelects[1]).find(":selected").html(), nRow, 1, false);      // Actor_Type
        oTable.fnUpdate($(jqSelects[2]).find(":selected").html(), nRow, 3, false);      // Sof Type ID
        oTable.fnUpdate($(jqSelects[3]).find(":selected").html(), nRow, 5, false);      // Amount Type

        // Input Text Type
        if (jqInputs.length > 2) { // In case we got "Specific ID"
            oTable.fnUpdate(jqInputs[0].value, nRow, 2, false);                             // Specific ID
            oTable.fnUpdate(jqInputs[1].value, nRow, 4, false);                             // Specific SOF
            oTable.fnUpdate(jqInputs[2].value, nRow, 6, false);                             // Rate
        } else {
            oTable.fnUpdate(jqInputs[0].value, nRow, 4, false);                             // Specific SOF
            oTable.fnUpdate(jqInputs[1].value, nRow, 6, false);                             // Rate
        }

        // Build up HTML ID Element
        var htmlIDBtnEdit = 'id=\'';
        var htmlIDBtnDelete = 'id=\'';
        var htmlEventBtnDelete = 'onclick=\'';
        if (tableId == 'tbl_setting_payment_fee_structure') {
            htmlIDBtnEdit += 'btn_setting_payment_fee_structure_edit';
            htmlIDBtnDelete += 'btn_setting_payment_fee_structure_delete';
            htmlEventBtnDelete += 'deleteDistribution(' + distribution_id + ')';
        } else if (tableId == 'tbl_setting_bonus') {
            htmlIDBtnEdit += 'btn_setting_bonus_edit';
            htmlIDBtnDelete += 'btn_setting_bonus_delete';
            htmlEventBtnDelete += 'deleteSettingBonus(' + distribution_id + ')';
        } else if (tableId == 'tbl_agent_hier_fee') {
            htmlIDBtnEdit += 'btn_agent_hier_fee_edit';
            htmlIDBtnDelete += 'btn_agent_hier_fee_delete';
            htmlEventBtnDelete += 'deleteAgentFee(' + distribution_id + ')';
        } else if (tableId == 'tbl_bonus') {
            htmlIDBtnEdit += 'btn_bonus_edit';
            htmlIDBtnDelete += 'btn_bonus_delete';
            htmlEventBtnDelete += '';
        }
        htmlIDBtnEdit += '\'';
        htmlIDBtnDelete += '\'';
        htmlEventBtnDelete += '\'';

        var htmlButtonEdit = '<button ' + htmlIDBtnEdit + 'type=\'button\' class=\'edit btn btn-outline btn-xs btn-primary edit text-info small\'>Edit</button>';
        var htmlButtonDelete = '&nbsp;<button ' + htmlIDBtnDelete + htmlEventBtnDelete + 'type=\'button\' class=\'btn btn-outline btn-xs delete btn-danger text-info small\'>Delete</button>';

        oTable.fnUpdate(htmlButtonEdit + htmlButtonDelete, nRow, 7, false);
        oTable.fnDraw();

        onBindingButtonsDeleteEvent();
    }

    // Commission and Payment Table
    function saveRowToServer(oTable, nRow) {
        var jqInputs = $('input', nRow);
        var jqSelects = $('select', nRow);
        var url = $(nRow).data('url');

        // console.log(jqInputs[0].value);
        // console.log(jqInputs[1].value);
        // console.log(jqInputs[2].value);

        // Request to server
        $.ajax({
            url: url,
            type: "POST",
            data: {
                "fee_tier_id": fee_tier_id,
                "action_type": $(jqSelects[0]).find(":selected").html(),
                "actor_type": $(jqSelects[1]).find(":selected").html(),
                "sof_type_id": $(jqSelects[2]).find(":selected").val(),
                "amount_type": $(jqSelects[3]).find(":selected").html(),
                "specific_actor_id": jqInputs[0].value,
                "specific_sof": jqInputs[1].value,
                "rate": jqInputs[2].value
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
                    addMessage("Updated Setting Payment & Fee Structure Successfully");
                } else {
                    console.log('Error adding row data');
                    addMessage("Updated Setting Payment & Fee Structure got error!");
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

    // Setting Bonus Table
    function saveSettingBonusToServer(oTable, nRow) {
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
                "sof_type_id": $(jqSelects[2]).find(":selected").val(),
                "amount_type": $(jqSelects[3]).find(":selected").html(),
                "specific_actor_id": jqInputs[0].value,
                "specific_sof": jqInputs[1].value,
                "rate": jqInputs[2].value
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
                    addMessage("Updated Setting Bonus Successfully");
                } else {
                    console.log('Error adding row data');
                    addMessage("Updated Setting Bonus got error!");
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

    // Agent Bonus Table
    function saveAgentBonusToServer(oTable, nRow) {
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
                "sof_type_id": $(jqSelects[2]).find(":selected").val(),
                "amount_type": $(jqSelects[3]).find(":selected").html(),
                "specific_actor_id": jqInputs[0].value,
                "specific_sof": jqInputs[1].value,
                "rate": jqInputs[2].value
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
                    addMessage("Updated Agent Hierrachy Distribution - Bonus Successfully");
                } else {
                    console.log('Error adding row data');
                    addMessage("Updated Agent Hierrachy Distribution - Bonus got error!");
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

    // for Agent Hierrachy Distribution - Fee
    function saveRowFeeToServer(oTable, nRow) {
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
                "sof_type_id": $(jqSelects[2]).find(":selected").val(),
                "amount_type": $(jqSelects[3]).find(":selected").html(),
                "specific_actor_id": jqInputs[0].value,
                "specific_sof": jqInputs[1].value,
                "rate": jqInputs[2].value
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
                    addMessage("Updated Agent Hirarchy Distribution - Fee successfully");
                } else {
                    console.log('Error adding row data');
                    addMessage("Updated Agent Hirarchy Distribution - Fee got error!");
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

    function onBindingButtonsCancelEvent() {
        $('#' + tableId).on('click', 'button.cancel', function (e) {
            e.preventDefault();

            /* Get the row as a parent of the link that was clicked on */
            var nRow = $(this).parents('tr')[0];

            restoreRow(oTable, nEditing);
            nEditing = nRow;
        });
    }

    function onBindingButtonsDeleteEvent() {

        $('#' + tableId).on('click', 'button.delete', function (e) {
            e.preventDefault();

            var nRow = $(this).parents('tr')[0];
            oTable.fnDeleteRow(nRow);
        });
    }

    function onBindingButtonsEditEvent() {

        $('#' + tableId).on('click', 'button.edit', function (e) {
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
                else if (tableId == "tbl_agent_hier_fee")
                    saveRowFeeToServer(oTable, nEditing);
                else if (tableId == "tbl_setting_bonus")
                    saveSettingBonusToServer(oTable, nEditing);
                else if (tableId == "tbl_bonus")
                    saveAgentBonusToServer(oTable, nEditing);

                nEditing = null;
            } else {
                /* No edit in progress - let's start one */
                editRow(oTable, nRow);
                nEditing = nRow;
            }

            return false;
        });
    }

    oTable = $('#' + tableId).dataTable({
        "searching":  false,
        "paging":   false,
        "ordering": false,
        "info":     false
    });

    onBindingButtonsEditEvent();
    onBindingButtonsDeleteEvent();
}


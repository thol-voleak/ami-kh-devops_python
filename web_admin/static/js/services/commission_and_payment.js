function onInlineSetupDataTable(tableId, m_action_types, m_actor_types, m_specific_ids, m_sof_types, m_amount_type, fee_tier_id, csrf_token) {

    var nEditing = null;
    var oTable;

    function restoreRow(oTable, nRow) {
        var aData = oTable.fnGetData(nRow);
        var jqTds = $('>td', nRow);

        for (var i = 0, iLen = jqTds.length; i < iLen; i++) {
            oTable.fnUpdate(aData[i], nRow, i, false);
        }

        oTable.fnDraw();
        $("body").find("th").each(function () {
               $(this).removeAttr( "style" );
            });
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

            htmlDDActors += '<option value="' + this.actor_type + '"' + htmlSelected + '>' + this.actor_type + '</option>';
        });

        // Master: Specific ID Dropdown
        var htmlDDSpecificIDs = '<option value=""></option>';
        jQuery.each(m_specific_ids, function() {
            if (aData[2] == this) {
                htmlSelected = ' selected=\"selected\" ';
            } else {
                htmlSelected = ' ';
            }

            htmlDDSpecificIDs += '<option value="' + this + '"' + htmlSelected + '>' + this + '</option>';
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
        var setDisabled = '';
        var htmlActorEventJS = "";
        var setRequired = '';

        // For Specific SOF changing according to SpecificID & SOF Type.
        var htmlgetSOFEventJS = "";

        // For Amount Types.
        var htmlAmountTypeEventJS = "";
        var setRateDisabled = '';

        // Buttons
        var htmlIDBtnSave = 'id=\'';
        var htmlIDBtnCancel = 'id=\'';

        if (tableId == 'tbl_setting_payment_fee_structure') {
            htmlIDActionTypes += 'ddl_setting_payment_fee_structure_dc_edit';
            htmlIDActorTypes += 'ddl_setting_payment_fee_structure_actor_edit';
            htmlIDSpecificID += 'ddl_setting_payment_fee_structure_specific_id_edit';
            htmlIDSOFTypes += 'ddl_setting_payment_fee_structure_source_of_fund_edit';
            htmlIDSpecificSOF += 'ddl_setting_payment_fee_structure_specific_source_of_fund_edit';
            htmlIDAmount += 'ddl_setting_payment_fee_structure_from_amount_edit';
            htmlIDRate += 'txt_setting_payment_fee_structure_rate_edit';
            htmlIDBtnSave += 'btn_setting_payment_fee_structure_save';
            htmlIDBtnCancel += 'btn_setting_payment_fee_structure_cancel';

            htmlgetSOFEventJS = "onchange=\"getSOF('ddl_setting_payment_fee_structure_actor_edit', 'ddl_setting_payment_fee_structure_specific_id_edit','ddl_setting_payment_fee_structure_source_of_fund_edit','ddl_setting_payment_fee_structure_specific_source_of_fund_edit')\"";
            htmlActorEventJS = "onchange=\"changeSpecificActorType('#ddl_setting_payment_fee_structure_actor_edit', '#ddl_setting_payment_fee_structure_specific_id_edit', '#ddl_setting_payment_fee_structure_specific_source_of_fund_edit')\"";
            htmlAmountTypeEventJS = "onchange=\"changeAmountType('#ddl_setting_payment_fee_structure_from_amount_edit', '#txt_setting_payment_fee_structure_rate_edit')\"";

        } else if (tableId == 'tbl_setting_bonus') {
            htmlIDActionTypes += 'ddl_setting_bonus_dc_edit';
            htmlIDActorTypes += 'ddl_setting_bonus_actor_edit';
            htmlIDSpecificID += 'ddl_setting_bonus_specific_id_edit';
            htmlIDSOFTypes += 'ddl_setting_bonus_src_fund_edit';
            htmlIDSpecificSOF += 'ddl_setting_bonus_spec_src_fund_edit';
            htmlIDAmount += 'ddl_setting_bonus_amount_edit';
            htmlIDRate += 'txt_setting_bonus_rate_edit';
            htmlIDBtnSave += 'btn_setting_bonus_save';
            htmlIDBtnCancel += 'btn_setting_bonus_cancel';

            htmlgetSOFEventJS = "onchange=\"getSOF('ddl_setting_bonus_actor_edit', 'ddl_setting_bonus_specific_id_edit','ddl_setting_bonus_src_fund_edit','ddl_setting_bonus_spec_src_fund_edit')\"";
            htmlActorEventJS = "onchange=\"changeSpecificActorType('#ddl_setting_bonus_actor_edit', '#ddl_setting_bonus_specific_id_edit', '#ddl_setting_bonus_spec_src_fund_edit')\"";
            htmlAmountTypeEventJS = "onchange=\"changeAmountType('#ddl_setting_bonus_amount_edit', '#txt_setting_bonus_rate_edit')\"";

        } else if (tableId == 'tbl_bonus') {
            htmlIDActionTypes += 'ddl_bonus_dc_edit';
            htmlIDActorTypes += 'ddl_bonus_actor_edit';
            htmlIDSpecificID += 'ddl_bonus_specific_id_edit';
            htmlIDSOFTypes += 'ddl_bonus_source_of_fund_edit';
            htmlIDSpecificSOF += 'ddl_bonus_specific_source_of_fund_edit';
            htmlIDAmount += 'ddl_bonus_amount_edit';
            htmlIDRate += 'txt_bonus_rate_edit';
            htmlIDBtnSave += 'btn_bonus_save';
            htmlIDBtnCancel += 'btn_bonus_cancel';

            htmlgetSOFEventJS = "onchange=\"getSOF('ddl_bonus_actor_edit', 'ddl_bonus_specific_id_edit','ddl_bonus_source_of_fund_edit','ddl_bonus_specific_source_of_fund_edit')\"";
            htmlActorEventJS = "onchange=\"changeSpecificActorType('#ddl_bonus_actor_edit', '#ddl_bonus_specific_id_edit', '#ddl_bonus_specific_source_of_fund_edit')\"";
            htmlAmountTypeEventJS = "onchange=\"changeAmountType('#ddl_bonus_amount_edit', '#txt_bonus_rate_edit')\"";
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

        // set disabled, required for specific ID & specific SOF according to Actor Types
        if (aData[1] === 'Specific ID') {
            setDisabled = '';
            setRequired = 'required';
        } else {
            setDisabled = 'disabled';
        }

        // set disabled, required for Rate according to AmountType
        if (aData[5].indexOf("Rate") >= 0) {
            setRateDisabled = '';
        } else {
            setRateDisabled = 'disabled';
        }

        jqTds[0].innerHTML = '<select ' + htmlIDActionTypes + ' type=\'text\' class=\'form-control\' name=\'action_type\' >' + htmlDDActionTypes + '</select>';
        jqTds[1].innerHTML = '<select ' + htmlActorEventJS + ' ' + htmlIDActorTypes + ' class=\'form-control\' name=\'actor_type\'>' + htmlDDActors + '</select>';
        jqTds[2].innerHTML = '<select ' + htmlgetSOFEventJS + ' ' + ' ' + setRequired + ' ' + setDisabled + ' ' + htmlIDSpecificID + ' type=\'number\' class=\'form-control\' name=\'specific_id\'>' + htmlDDSpecificIDs + '</select>';
        jqTds[3].innerHTML = '<select ' + htmlgetSOFEventJS + ' ' + htmlIDSOFTypes + ' type=\'text\' class=\'form-control\' name=\'sof_type_id\'>' + htmlDDSOFTypes + '</select>';
        jqTds[4].innerHTML = '<select ' + ' ' + setRequired + ' ' + setDisabled + ' ' + htmlIDSpecificSOF + ' type=\'text\' class=\'form-control\' name=\'specific_sof\'></select>';
        jqTds[5].innerHTML = '<select ' + htmlAmountTypeEventJS + ' ' + htmlIDAmount + ' type=\'text\' class=\'form-control\' name=\'amount_type\'>' + htmlDDAmountTypes + '</select>';
        jqTds[6].innerHTML = '<input ' + ' ' + setRateDisabled + ' ' + htmlIDRate + ' type=\'text\' class=\'form-control\' name=\'rate\' required value=\'' + aData[6] + '\'>';

        // Master: Specific SOF Dropdown
        var htmlDDSpecificSOFs = '';
        if (tableId == "tbl_setting_payment_fee_structure")
            {getSOF('ddl_setting_payment_fee_structure_actor_edit', 'ddl_setting_payment_fee_structure_specific_id_edit','ddl_setting_payment_fee_structure_source_of_fund_edit','ddl_setting_payment_fee_structure_specific_source_of_fund_edit',aData[4]);}
        else if (tableId == "tbl_bonus")
            {getSOF('ddl_bonus_actor_edit', 'ddl_bonus_specific_id_edit','ddl_bonus_source_of_fund_edit','ddl_bonus_specific_source_of_fund_edit',aData[4]);}
        else if (tableId == 'tbl_setting_bonus')
            {getSOF('ddl_setting_bonus_actor_edit', 'ddl_setting_bonus_specific_id_edit','ddl_setting_bonus_src_fund_edit','ddl_setting_bonus_spec_src_fund_edit',aData[4]);}

        // Action Buttons
        var htmlButtonSave = '<button type=\'button\' ' + htmlIDBtnSave + ' class=\'btn btn-outline btn-xs edit btn-primary text-info small\'>Save</button>';
        var htmlButtonCancel = '<button type=\'button\' ' + htmlIDBtnCancel + ' class=\'btn btn-default btn-outline btn-xs cancel small\'>Cancel</button>';

        jqTds[7].innerHTML = htmlButtonSave + '&nbsp;' + htmlButtonCancel;

        onBindingButtonsCancelEvent();

        $("body").find("th").each(function () {
               $(this).removeAttr( "style" );
            });
    }

    function saveRow(oTable, nRow) {
        var jqInputs = $('input', nRow);
        var jqSelects = $('select', nRow);

        var distribution_id = $(nRow).data('id');

        // DD Type
        oTable.fnUpdate($(jqSelects[0]).find(":selected").html(), nRow, 0, false);      // Action_Type
        oTable.fnUpdate($(jqSelects[1]).find(":selected").html(), nRow, 1, false);      // Actor_Type
        oTable.fnUpdate($(jqSelects[2]).find(":selected").html(), nRow, 2, false);      // Specific ID
        oTable.fnUpdate($(jqSelects[3]).find(":selected").html(), nRow, 3, false);      // Sof Type ID
        var spec_SOF = $(jqSelects[4]).find(":selected").html();
        if (spec_SOF === undefined)
            spec_SOF = "";
        oTable.fnUpdate(spec_SOF, nRow, 4, false);      // Specific SOF
        oTable.fnUpdate($(jqSelects[5]).find(":selected").html(), nRow, 5, false);      // Amount Type
        oTable.fnUpdate(jqInputs[0].value, nRow, 6, false);                             // Rate

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

        $("body").find("th").each(function () {
               $(this).removeAttr( "style" );
            });
    }

    // Commission and Payment Table
    function saveRowToServer(oTable, nRow) {
        var jqInputs = $('input', nRow);
        var jqSelects = $('select', nRow);
        var url = $(nRow).data('url');
        var ActorType = $(jqSelects[1]).find(":selected").html();
        var AmountType = $(jqSelects[5]).find(":selected").html();

        if ((ActorType === 'Specific ID' && jqSelects[2].value === "") || (ActorType === 'Specific ID' && jqSelects[4].value === "") || (AmountType.indexOf("Rate") !== -1 && jqInputs[0].value === "")) {
            document.getElementById("btn_setting_payment_fee_structure_add").click();
            nEditing = nRow;
        }
        else {
            // Request to server
            $.ajax({
                url: url,
                type: "POST",
                data: {
                    "fee_tier_id": fee_tier_id,
                    "action_type": $(jqSelects[0]).find(":selected").html(),
                    "actor_type": $(jqSelects[1]).find(":selected").html(),
                    "specific_actor_id": $(jqSelects[2]).find(":selected").html(),
                    "sof_type_id": $(jqSelects[3]).find(":selected").val(),
                    "specific_sof": $(jqSelects[4]).find(":selected").html(),
                    "amount_type": $(jqSelects[5]).find(":selected").html(),
                    "rate": jqInputs[0].value
                },
                dataType: "json",
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", csrf_token);
                },
                success: function (response) {

                    if (response.status == 1) {
                        // Logout
                        var url = window.location.origin + "/admin-portal/authentications/login/?next=" + window.location.pathname ;
                        window.location.replace(url);
                    } else if (response.status == 2) {
                        // success
                        console.log('Updated Setting Payment & Fee Structure Successfully');
                        saveRow(oTable, nRow);
                        addMessage("Updated Setting Payment & Fee Structure Successfully");
                    } else {
                        // Failed
                        console.log('Updated Setting Payment & Fee Structure got error!');
                        addErrorMessage(response.msg);
                    }

                    $("body").find("th").each(function () {
                    $(this).removeAttr( "style" );
            });
                },
                error: function (err) {
                    var json = JSON.stringify(err);

                    addErrorMessage("Edit error!");
                }
            });
        }
    }

    // Setting Bonus Table
    function saveSettingBonusToServer(oTable, nRow) {
        var jqInputs = $('input', nRow);
        var jqSelects = $('select', nRow);
        var url = $(nRow).data('url');
        var ActorType = $(jqSelects[1]).find(":selected").html();
        var AmountType = $(jqSelects[5]).find(":selected").html();

        if ((ActorType === 'Specific ID' && jqSelects[2].value === "") || (ActorType === 'Specific ID' && jqSelects[4].value === "") || (AmountType.indexOf("Rate") !== -1 && jqInputs[0].value === "")) {
            document.getElementById("btn_setting_bonus_add").click();
            nEditing = nRow;
        }
        else {

            // Request to server
            $.ajax({
                url: url,
                type: "POST",
                data: {
                    "fee_tier_id": fee_tier_id,
                    "action_type": $(jqSelects[0]).find(":selected").html(),
                    "actor_type": $(jqSelects[1]).find(":selected").html(),
                    "specific_actor_id": $(jqSelects[2]).find(":selected").html(),
                    "sof_type_id": $(jqSelects[3]).find(":selected").val(),
                    "specific_sof": $(jqSelects[4]).find(":selected").html(),
                    "amount_type": $(jqSelects[5]).find(":selected").html(),
                    "rate": jqInputs[0].value
                },
                dataType: "json",
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", csrf_token);
                },
                success: function (response) {

                    if (response.status == 1) {
                        // Logout
                        var url = window.location.origin + "/admin-portal/authentications/login/?next=" + window.location.pathname ;
                        window.location.replace(url);
                    } else if (response.status == 2) {
                        console.log('Saved row data');
                        saveRow(oTable, nRow);
                        addMessage("Updated Setting Bonus Successfully");
                    } else {
                        console.log('Error adding row data');
                        addErrorMessage(response.msg);
                    }

                    $("body").find("th").each(function () {
                        $(this).removeAttr( "style" );
                    });

                },
                error: function (err) {
                    var json = JSON.stringify(err);

                    addErrorMessage("Edit error!");
                }
            });
        }
    }

    // Agent Bonus Table
    function saveAgentBonusToServer(oTable, nRow) {
        var jqInputs = $('input', nRow);
        var jqSelects = $('select', nRow);
        var url = $(nRow).data('url');
        var ActorType = $(jqSelects[1]).find(":selected").html();
        var AmountType = $(jqSelects[5]).find(":selected").html();

        if ((ActorType === 'Specific ID' && jqSelects[2].value === "") || (ActorType === 'Specific ID' && jqSelects[4].value === "") || (AmountType.indexOf("Rate") !== -1 && jqInputs[0].value === "")) {
            document.getElementById("btn_agent_hierarchy_distribution_bonus_add").click();
            nEditing = nRow;
        }
        else {
            // Request to server
            $.ajax({
                url: url,
                type: "POST",
                data: {
                    "fee_tier_id": fee_tier_id,
                    "action_type": $(jqSelects[0]).find(":selected").html(),
                    "actor_type": $(jqSelects[1]).find(":selected").html(),
                    "specific_actor_id": $(jqSelects[2]).find(":selected").html(),
                    "sof_type_id": $(jqSelects[3]).find(":selected").val(),
                    "specific_sof": $(jqSelects[4]).find(":selected").html(),
                    "amount_type": $(jqSelects[5]).find(":selected").html(),
                    "rate": jqInputs[0].value
                },
                dataType: "json",
                beforeSend: function (xhr) {
                    xhr.setRequestHeader("X-CSRFToken", csrf_token);
                },
                success: function (response) {

                    if (response.status == 1) {
                        // Logout
                        var url = window.location.origin + "/admin-portal/authentications/login/?next=" + window.location.pathname ;
                        window.location.replace(url);
                    } else if (response.status == 2) {
                        console.log('Saved row data');
                        saveRow(oTable, nRow);
                        addMessage("Updated Agent Hierrachy Distribution - Bonus Successfully");
                    } else {
                        console.log('Error adding row data');
                        addErrorMessage(response.msg);
                    }

                    $("body").find("th").each(function () {
                        $(this).removeAttr( "style" );
                    });
                },
                error: function (err) {
                    var json = JSON.stringify(err);
                    addErrorMessage("Edit error!");
                }
            });
        }
    }

    // for Agent Hierrachy Distribution - Fee
    function saveRowFeeToServer(oTable, nRow) {
        var jqInputs = $('input', nRow);
        var jqSelects = $('select', nRow);
        var url = $(nRow).data('url');
        var ActorType = $(jqSelects[1]).find(":selected").html();

        //Validate Input Value specific_actor_id
        if(ActorType == 'Specific ID' && jqInputs[0].value == "") {
            editRow(oTable, nRow);
            document.getElementById("txt_agent_hier_fee_specific_id_edit").style.borderColor = "red";
            // $(jqInputs[0]).prop("style", "border-color: red;");
            addErrorMessage("Please input Specific ID");

        }
        //Validate Input Value specific_sof
        else if(ActorType == 'Specific ID' && jqInputs[1].value == "") {
            editRow(oTable, nRow);
            document.getElementById("txt_agent_hier_fee_specific_source_of_fund_edit").style.borderColor = "red";
            // $(jqInputs[1]).prop("style", "border-color: red;");
            addErrorMessage("Please input Specific Source of Fund");
        }
        else {

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

                    if (response.status == 1) {
                        // Logout
                        var url = window.location.origin + "/admin-portal/authentications/login/?next=" + window.location.pathname ;
                        window.location.replace(url);
                    } else if (response.status == 2) {
                        console.log('Saved row data');
                        saveRow(oTable, nRow);
                        addMessage("Updated Agent Hirarchy Distribution - Fee successfully");
                    } else {
                        console.log('Error adding row data');
                        addErrorMessage(response.msg);
                    }

                    $("body").find("th").each(function () {
                         $(this).removeAttr( "style" );
                    });
                },
                error: function (err) {
                    var json = JSON.stringify(err);
                    addErrorMessage("Edit error!");
                }
            });
        }
    }

    function onBindingButtonsCancelEvent() {
        $('#' + tableId).on('click', 'button.cancel', function (e) {
            e.preventDefault();

            /* Get the row as a parent of the link that was clicked on */
            var nRow = $(this).parents('tr')[0];

            restoreRow(oTable, nEditing);
            nEditing = nRow;

            $("body").find("th").each(function () {
               $(this).removeAttr( "style" );
            });
            // location.reload();
        });
    }

    function onBindingButtonsDeleteEvent() {

        $('#' + tableId).on('click', 'button.delete', function (e) {
            e.preventDefault();

            var nRow = $(this).parents('tr')[0];
            oTable.fnDeleteRow(nRow,null, true);
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

            } else {
                /* No edit in progress - let's start one */
                editRow(oTable, nRow);
                nEditing = nRow;
            }

            $("body").find("th").each(function () {
               $(this).removeAttr( "style" );
            });

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


function startEdittingTableRow(tr) {
    resetDataTableRow(tr);

    $(tr).find("span").each(function () {
        $(this).hide();
    });

    $(tr).find("select").each(function () {
        $(this).show();
    });

    $(tr).find("input").each(function () {
        $(this).show();
    });

    $(tr).find("div.Normal").each(function () {
        $(this).hide();
    });

    $(tr).find("div.Editting").each(function () {
        $(this).show();
    });
}

function endEdittingTableRow(tr) {
    $(tr).find("span").each(function () {
        $(this).show();
    });

    $(tr).find("select").each(function () {
        $(this).hide();
    });

    $(tr).find("input").each(function () {
        $(this).hide();
    });

    $(tr).find("div.Normal").each(function () {
        $(this).show();
    });

    $(tr).find("div.Editting").each(function () {
        $(this).hide();
    });
}

function updateSpanTableRow(tr) {
    $(tr).find("td").each(function () {
        var td = $(this);
        var span = td.find("span");
        if (span.length) {
            var select = td.find("select");
            if (select.length) {
                span.html(select.val());
            } else {
                var input = td.find("input");
                span.html(input.val());
            }

        }
    });
}

function resetDataTableRow(tr) {
    $(tr).find("td").each(function () {
        var td = $(this);
        var span = td.find("span");
        if (span.length) {
            var currentValue = span.html().trim();
            var select = td.find("select");
            if (select.length) {
                $(select).val(currentValue).change();
            } else {
                var input = td.find("input");
                $(input).val(currentValue);
            }
        }
    });
}

function removeCurrentEdittingsDataTable(tb) {
    var rows = $(tb).children();
    for (var i = rows.length - 2; i >= 0; i--) {
        endEdittingTableRow(rows[i]);
    }
}

function tapOnEdit(e) {
    tr = $(e).parent().parent().parent();
    removeCurrentEdittingsDataTable(tr.parent());
    startEdittingTableRow(tr);
}

function tapOnCancel(e) {
    tr = $(e).parent().parent().parent();
    endEdittingTableRow(tr);
}

function tapOnSave(e) {
    tr = $(e).parent().parent().parent();

    if(validateForm(tr)) {
        // Post data to server:
        saveAgentHierarchyDistribution(tr);
    }
}

function validateForm(nRow) {
    var text_input = document.getElementById('txt_agent_hier_fee_rate_edit');
    var jqInputs = $('input', nRow);
    var rate_value = jqInputs[0].value;//2
    var text_element = jqInputs[0];//2

    var jqSelects = $('select', nRow);
    var select_value = $(jqSelects[5]).find(":selected").html();

    if((select_value.indexOf("Rate") !== -1) || (select_value.indexOf("rate") !== -1)) {
        // exist
        text_element.required = true;

        if(!rate_value) {
            text_element.style.borderColor = '#0ac2ff';//"#e4e4e4";
            text_input.setCustomValidity('Pleased fill in this field');
            var btn = document.getElementById("btn_agent_hier_fee_add");
            btn.click();
            return false;
        }
    }
    text_element.style.borderColor = "transparent";

    var actor = $(jqSelects[1]).find(":selected").html();
    if(actor == 'Specific ID') {
        var specific_id = $(jqSelects[2]);
        var sof = $(jqSelects[4]);
        if(!specific_id.val() || !sof.val()) {
            var btn = document.getElementById("btn_agent_hier_fee_add");
            btn.click();
            return false;
        }

    }


    return true;


}

function saveAgentHierarchyDistribution(nRow) {
    var jqInputs = $('input', nRow);
    var jqSelects = $('select', nRow);
    var url = $(nRow).data('url');
    var fee_tier_id = $(nRow).data('fee_tier_id');
    var params = {
        "fee_tier_id": fee_tier_id,
        "action_type": $(jqSelects[0]).find(":selected").html(),
        "actor_type": $(jqSelects[1]).find(":selected").html(),
        "sof_type_id": $(jqSelects[3]).find(":selected").data('sof_type_id'), //.val(),
        "amount_type": $(jqSelects[5]).find(":selected").html(),//3
        "specific_actor_id": jqSelects[2].value,
        "specific_sof": jqSelects[4].value,//1
        "rate": jqInputs[0].value // 2
    };

    var token = csrf_token;

    var ActorType = $(jqSelects[1]).find(":selected").html();
    var specificId = document.getElementById("txt_agent_hier_fee_specific_id_edit");

    //Validate Input Value specific_actor_id
    if(ActorType == 'Specific ID' && jqSelects[2].value == "") {
        startEdittingTableRow(nRow);
        // $(tr).find("input").each(function () {
        //     $(this).prop("style", "border-color: red;");
        // });
        $(jqSelects[2]).prop("style", "border-color: red;");
        addErrorMessage("Please input Specific ID");

    }
    //Validate Input Value specific_sof
    else if(ActorType == 'Specific ID' && jqSelects[4].value == "") {
        startEdittingTableRow(nRow);
        // $(tr).find("input").each(function () {
        //     $(this).prop("style", "border-color: red;");
        // });
        $(jqSelects[4]).prop("style", "border-color: red;");
        addErrorMessage("Please input Specific Source of Fund");
    }
    else {
        // Request to server
        $.ajax({
            url: url,
            type: "POST",
            data: params,
            dataType: "json",
            beforeSend: function (xhr) {
                xhr.setRequestHeader("X-CSRFToken", token);
            },
            success: function (response) {

                if (response.status == 1) {
                    // Logout
                    var url = window.location.origin + "/admin-portal/logout/";
                    window.location.replace(url);
                } else if (response.status == 2) {
                    console.log('Saved row data');
                    updateSpanTableRow(nRow);
                    endEdittingTableRow(nRow);
                    addMessage("Updated Agent Hierarchy Distribution - Fee successfully");
                } else {
                    console.log('Error adding row data');
                    addErrorMessage(response.msg);
                }
            },
            error: function (err) {
                var json = JSON.stringify(err);
                addMessage("Edit error!");
            }
        });
    }
}
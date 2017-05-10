function startEdittingTableRow(tr) {
    resetDataTableRow(tr);

    $(tr).find("span").each(function () {
        $(this).prop("style", "display: none;");
    });

    $(tr).find("select").each(function () {
        $(this).prop("style", "display: block;");
    });

    $(tr).find("input").each(function () {
        $(this).prop("style", "display: block;");
    });

    $(tr).find("div.Normal").each(function () {
        $(this).prop("style", "display: none;");
    });

    $(tr).find("div.Editting").each(function () {
        $(this).prop("style", "display: block;");
    });
}

function endEdittingTableRow(tr) {
    $(tr).find("span").each(function () {
        $(this).prop("style", "display: block;");
    });

    $(tr).find("select").each(function () {
        $(this).prop("style", "display: none;");
    });

    $(tr).find("input").each(function () {
        $(this).prop("style", "display: none;");
    });

    $(tr).find("div.Normal").each(function () {
        $(this).prop("style", "display: block;");
    });

    $(tr).find("div.Editting").each(function () {
        $(this).prop("style", "display: none;");
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
    // Post data to server:
    saveAgentHierarchyDistribution(tr)
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
        "sof_type_id": $(jqSelects[2]).find(":selected").data('sof_type_id'), //.val(),
        "amount_type": $(jqSelects[3]).find(":selected").html(),
        "specific_actor_id": jqInputs[0].value,
        "specific_sof": jqInputs[1].value,
        "rate": jqInputs[2].value
    };

    var token = csrf_token;

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

            var data = JSON.stringify(response);
            var json = $.parseJSON(data);
            console.log('JSON: ');
            console.log(json);

            if (json.status.code == 'success') {
                console.log('Saved row data');
                updateSpanTableRow(nRow);
                endEdittingTableRow(nRow);
                addMessage("Updated Agent Hierarchy Distribution - Fee successfully");
            } else {
                console.log('Error adding row data');
                addMessage("Updated Agent Hierarchy Distribution - Fee got error!");
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
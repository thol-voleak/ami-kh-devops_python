function searchUser(url) {
    var mobile_number = $('#txt_mobile_number').val();
    if(mobile_number.length < 4) {
        return;
    }

    $.ajax({
        url: url,
        data: {
            'mobile_number' : mobile_number,
            'current_page_index' : $('#current_page_index').val()
        },
        type: "GET",
        success: function (response) {
            if(response.no_record === 'true') {
                $('#divUserSearchMessage').css({'display':'block'});
                $('#lb_user_search_message').text('Cannot find user you are trying to search');
            } else if(response.user_id !== undefined) {
                $('#txt_user_id').val(response.user_id);
                $('#ddl_user_type').val(response.user_type_id);
            } else {
                $('.modal-content').html(response);
                $('#modalUser').modal({
                    show: 'true'
                });
            }
        },
        error: function (request) {
            if(request.status === 504) {
              $('#divUserSearchMessage').css({'display': 'block'});
              $('#lb_user_search_message').text('Search timed out, please try again or contact support');
            }
            else {
                $('#divUserSearchMessage').css({'display': 'block'});
                $('#lb_user_search_message').text('Search failed, please try again or contact support');
            }
        }
    });
}

function initSearchIconVisible() {
    var searchBtn = document.getElementById("btn_search_icon");
    var input_phone_no = document.getElementById("txt_mobile_number");

    input_phone_no.addEventListener("keyup", function (event) {
        if (input_phone_no.value.trim().length >= 4) {
            searchBtn.removeAttribute("disabled");
        } else {
            searchBtn.setAttribute("disabled", true);
        }
    })
}
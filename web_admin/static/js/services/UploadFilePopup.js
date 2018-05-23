function initUploadFilePopup(popupContainer, openCallBackFunction, uploadDelegateFunction) {
    bindBrowseFileButtonEvent(popupContainer);
    bindFileInputFakeEvent(popupContainer);
    bindFileInputEvent(popupContainer);
    bindUploadButtonEvent(popupContainer, uploadDelegateFunction)
    $(popupContainer).on("shown.bs.modal", function (event) {
        if (openCallBackFunction != undefined && openCallBackFunction != null) {
            openCallBackFunction(popupContainer);
        } else {
            //    call default open popup
            defaultOpenUploadFilePopup(popupContainer);
        }
    })
}

bindBrowseFileButtonEvent = function (popupContainer) {
    var uploadFileInput = $(popupContainer).find("input[name='file_data']");
    $(popupContainer).find("#browse_file").click(function (event) {
        $(uploadFileInput).trigger('click');
    })
}

bindFileInputFakeEvent = function (popupContainer) {
    var uploadFileInput = $(popupContainer).find("input[name='file_data']");
    $(popupContainer).find("input[name='file_data_mask']").click(function (event) {
        $(uploadFileInput).trigger('click');
    })
}

bindFileInputEvent = function (popupContainer) {
    var uploadFileInput = $(popupContainer).find("input[name='file_data']");
    var uploadFileInputFake = $(popupContainer).find("input[name='file_data_mask']");
    $(uploadFileInput).change(function (event) {
        var file = event.target.files[0];
        if (file != null) {
            //add file name to fake input
            $(uploadFileInputFake).val(file.name);
        } else {
            //clear the input fake value
            $(uploadFileInputFake).val('');
        }
    })
}


bindUploadButtonEvent = function (popupContainer, uploadDelegateFunction) {
    $(popupContainer).find("#btn_upload").click(function () {
        if (uploadDelegateFunction != undefined && uploadDelegateFunction != null) {
            uploadDelegateFunction(popupContainer);
        }
    })
}

defaultOpenUploadFilePopup = function (popupContainer) {
    var uploadFileInput = $(popupContainer).find("input[name='file_data']");
    var uploadFileInputFake = $(popupContainer).find("input[name='file_data_mask']");
    //reset input file
    $(uploadFileInput).val('');
    $(uploadFileInputFake).val("");
}

commonUploadValidation = function (popupContainer) {
    return validateFileEmpty(popupContainer);
}

function validateFileEmpty(popupContainer) {
    if ($(popupContainer).find('input[name=file_data]')[0].files[0].size == 0) {
        swal({
            title: 'File cannot be empty',
            type: "error",
            confirmButtonColor: "#2ECC71",
            confirmButtonText: "Close",
            closeOnConfirm: true
        });
        return false;
    }
}
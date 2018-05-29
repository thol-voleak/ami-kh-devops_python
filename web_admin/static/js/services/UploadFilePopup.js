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
    $(popupContainer).find("#btn_upload").click(function (event) {
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
    $("#uploadFileModal").find($('#progress_info')).hide();
    $("#uploadFileModal").find($('#download_link')).hide();
    $("#uploadFileModal").find($('#btn_dialog_done')).hide();
    $("#uploadFileModal").find($('#btn_dialog_cancel')).show();
    $("#uploadFileModal").find($('#download_link')).text("")
    $("#uploadFileModal").find($('#download_link')).attr("href", "#")
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
    return true;
}

function validateFileType(popupContainer, fileTypes) {
    //don't care the file type
    if (fileTypes == undefined || fileTypes == null || fileTypes.length === 0) {
        return true;
    }
    var uploadFileInput = $(popupContainer).find("input[name='file_data']");
    var fileName = $(uploadFileInput)[0].files[0].name;
    var fileExtension = fileName.substr((fileName.lastIndexOf('.') + 1));
    return jQuery.inArray(fileExtension, fileTypes) > -1;
}

function validateRequireInputFile(popupContainer) {
    var uploadFileInput = $(popupContainer).find("input[name='file_data']");
    return $(uploadFileInput)[0].files.length > 0;
}

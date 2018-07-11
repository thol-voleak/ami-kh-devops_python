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

resetUploadProgress = function (popupContainer) {
    $(popupContainer).find($('#progress_info')).hide();
    $(popupContainer).find($('#progress')).width(0);
    $(popupContainer).find($('#download_link')).hide();
    $(popupContainer).find($('#btn_dialog_done')).hide();
    $(popupContainer).find($('#btn_dialog_cancel')).show();
    $(popupContainer).find($('#download_link')).text("")
    $(popupContainer).find($('#download_link')).attr("href", "#")
    $(popupContainer).find('#dlg_icon_ok').hide()
    $(popupContainer).find('#progress_container').hide()
}

bindFileInputEvent = function (popupContainer) {
    var uploadFileInput = $(popupContainer).find("input[name='file_data']");
    var uploadFileInputFake = $(popupContainer).find("input[name='file_data_mask']");
    $(uploadFileInput).change(function (event) {
        var file = event.target.files[0];
        if (file != null) {
            //add file name to fake input
            $(uploadFileInputFake).val(file.name);
            resetUploadProgress(popupContainer)
        } else {
            //clear the input fake value
            $(uploadFileInputFake).val('');
        }
    })
}

processUpload = function (popupContainer, uploadDelegateFunction) {
    resetUploadProgress(popupContainer)
    if (uploadDelegateFunction != undefined && uploadDelegateFunction != null) {
        uploadDelegateFunction(popupContainer);
    }
}
bindUploadButtonEvent = function (popupContainer, uploadDelegateFunction) {
    $(popupContainer).find("#btn_upload").click(function (event) {
        processUpload(popupContainer, uploadDelegateFunction)
    })
}

defaultOpenUploadFilePopup = function (popupContainer) {
    var uploadFileInput = $(popupContainer).find("input[name='file_data']");
    var uploadFileInputFake = $(popupContainer).find("input[name='file_data_mask']");
    //reset input file
    $(uploadFileInput).val('');
    $(uploadFileInputFake).val("");
    resetUploadProgress(popupContainer)
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

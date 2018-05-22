function initUploadFilePopup(popupContainer, openCallBackFunction) {
    bindBrowseFileButtonEvent(popupContainer);
    bindFileInputFakeEvent(popupContainer);
    bindFileInputEvent(popupContainer);

    $(popupContainer).on("shown.bs.modal", function (event) {
        if (openCallBackFunction != undefined) {
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

defaultOpenUploadFilePopup = function (popupContainer) {
    var uploadFileInput = $(popupContainer).find("input[name='file_data']");
    var uploadFileInputFake = $(popupContainer).find("input[name='file_data_mask']");
    //reset input file
    $(uploadFileInput).val('');
    $(uploadFileInputFake).val("");
}
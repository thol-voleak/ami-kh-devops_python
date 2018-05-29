from braces.views import GroupRequiredMixin

from authentications.utils import get_correlation_id_from_username, check_permissions_by_user
from django.views.generic import TemplateView
from web_admin.utils import make_download_file


from web_admin import setup_logger
from web_admin.restful_client import RestFulClient
from web_admin.get_header_mixins import GetHeaderMixin
import logging
from web_admin.api_settings import DOWNLOAD_URL

logger = logging.getLogger(__name__)


class Download(GroupRequiredMixin, TemplateView, GetHeaderMixin):
    login_url = 'web:permission_denied'
    logger = logger
    template_name = "files/list.html"
    group_required = "CAN_GET_UPLOAD_RESULT"

    def check_membership(self, permission):
        self.logger.info(
            "Checking permission for [{}] username with [{}] permission".format(self.request.user, permission))
        return check_permissions_by_user(self.request.user, permission[0])

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(Download, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        headers = self._get_headers()
        file_id = kwargs['file_id']
        status_id = kwargs['status_id']
        params = {'file_id': int(file_id), 'status_id': int(status_id)}
        self.logger.info('========== Start download file ==========')
        status_code, is_success, data = RestFulClient.download(url=DOWNLOAD_URL, headers=headers, loggers=self.logger,
                                                               params=params)
        self.logger.info('========== Finished download file ==========')
        if is_success:
            response = make_download_file(data, 'csv')
            return response

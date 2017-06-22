from web_admin.api_settings import SPI_DETAIL_PATH, SPI_DELETE_PATH
from web_admin.utils import setup_logger
from web_admin.restful_methods import RESTfulMethods

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic.base import TemplateView

import logging

logger = logging.getLogger(__name__)


class SPIDeleteView(TemplateView, RESTfulMethods):
    template_name = 'services/spi/delete.html'
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(SPIDeleteView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self.logger.info('========== Start Show Delete SPI page ==========')
        try:
            context = super(SPIDeleteView, self).get_context_data(**kwargs)
            spi_url_id = context['spi_url_id']
            self.logger.info('========== Finished show Delete SPI page ==========')
            context['spi_detail'] = self.get_spi_detail(spi_url_id)
            return context
        except Exception as e:
            self.logger.error(e)
            return {}

    def post(self, request, *args, **kwargs):
        self.logger.info("========== Start delete SPI URL by service command ==========")
        service_command_id = kwargs.get('service_command_id')
        service_id = kwargs.get('service_id')
        command_id = kwargs.get('command_id')
        spi_url_id = kwargs.get('spi_url_id')

        if not service_command_id:
            raise Http404

        data, success = self._delete_method(api_path=SPI_DELETE_PATH.format(spi_url_id=spi_url_id),
                                            func_description="",
                                            logger=logger)
        self.logger.info("========== Finish delete SPI URL by service command ==========")

        if success:
            request.session['spi_delete_msg'] = 'Deleted data successfully'
            messages.add_message(
                self.request,
                messages.SUCCESS,
                'Deleted data successfully'
            )
            return redirect('services:spi_list', service_id=service_id, command_id=command_id,
                            service_command_id=service_command_id)
        else:
            messages.add_message(
                self.request,
                messages.ERROR,
                data
            )
            return redirect('services:spi_list', service_id=service_id, command_id=command_id,
                            service_command_id=service_command_id)

    def get_spi_detail(self, spi_url_id):
        path = SPI_DETAIL_PATH.format(spiUrlId=spi_url_id)
        data, success = self._get_method(path, '', logger)
        return data

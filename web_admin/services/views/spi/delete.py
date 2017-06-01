from web_admin.restful_methods import RESTfulMethods
from django.http import Http404
from django.views.generic.base import TemplateView
from django.shortcuts import redirect
from web_admin.api_settings import SPI_DETAIL_PATH, SPI_DELETE_PATH
import logging

logger = logging.getLogger(__name__)


class SPIDeleteView(TemplateView, RESTfulMethods):
    template_name = 'services/spi/delete.html'

    def get_context_data(self, **kwargs):
        logger.info('========== Start Show Delete SPI page ==========')
        try:
            context = super(SPIDeleteView, self).get_context_data(**kwargs)
            spi_url_id = context['spi_url_id']
            logger.info('========== Finished show Delete SPI page ==========')
            context['spi_detail'] = self.get_spi_detail(spi_url_id)
            return context
        except Exception as e:
            return {}

    def post(self, request, *args, **kwargs):
        logger.info("========== Start delete SPI URL by service command ==========")
        service_command_id = kwargs.get('service_command_id')
        service_id = kwargs.get('service_id')
        command_id = kwargs.get('command_id')
        spi_url_id = kwargs.get('spi_url_id')

        if not service_command_id:
            raise Http404

        data, success = self._delete_method(api_path=SPI_DELETE_PATH.format(spi_url_id=spi_url_id),
                                            func_description="",
                                            logger=logger)
        logger.info("========== Finish delete SPI URL by service command ==========")

        if success:
            request.session['spi_delete_msg'] = 'Deleted data successfully'
            return redirect('services:spi_list', service_id=(service_id), command_id=(command_id), service_command_id=(service_command_id) )
        else:
            raise Exception("Something wrong")
        
    def get_spi_detail(self, spi_url_id):
        path = SPI_DETAIL_PATH.format(spiUrlId=spi_url_id)
        data, success = self._get_method(path, '', logger)
        return data



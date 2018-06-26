from web_admin import api_settings, setup_logger, RestFulClient
from authentications.utils import get_correlation_id_from_username
from web_admin.get_header_mixins import GetHeaderMixin
from authentications.apps import InvalidAccessToken
from web_admin.api_logger import API_Logger

from django.contrib import messages
from django.http import Http404
from django.views.generic.base import TemplateView
from django.shortcuts import redirect, render

import logging

logger = logging.getLogger(__name__)


class SPIUpdate(TemplateView, GetHeaderMixin):
    template_name = 'services/spi/update.html'

    logger = logger
    internal_urls = [
        "/voucher/v${api.version}/internal/vouchers",
        "/voucher/v${api.version}/internal/vouchers/pre-payment",
        "/voucher/v${api.version}/internal/vouchers/post-payment",
        "/voucher/v${api.version}/internal/vouchers/cancellation",
        "/voucher/v${api.version}/internal/vouchers/rollback"
    ]

    def dispatch(self, request, *args, **kwargs):
        correlation_id = get_correlation_id_from_username(self.request.user)
        self.logger = setup_logger(self.request, logger, correlation_id)
        return super(SPIUpdate, self).dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.logger.info('========== Start updated SPI url ==========')
        service_command_id = kwargs.get('service_command_id')
        service_id = kwargs.get('service_id')
        command_id = kwargs.get('command_id')
        spi_url_id = kwargs.get('spiUrlId')

        if not service_command_id:
            raise Http404

        spi_type = request.POST.get('spi_url_type')
        spi_url_option = request.POST.get('spi_url_option')
        spi_url_value_internal = request.POST.get('spi_url_value_internal')
        spi_url_value_external = request.POST.get('spi_url_value_external')
        spi_url_call_method = request.POST.get('spi_url_call_method')
        connection_timeout = request.POST.get('connection_timeout', 0)
        read_timeout = request.POST.get('read_timeout', 0)
        max_retry = request.POST.get('max_retry', 0)
        retry_delay = request.POST.get('retry_delay', 0)
        expire_in_minute = request.POST.get('expire_in_minute', 0)
        created_timestamp = request.POST.get('created_timestamp')
        last_updated_timestamp = request.POST.get('last_updated_timestamp')


        if spi_url_option == 'internal':
            spi_url = spi_url_value_internal
        elif spi_url_option == 'external':
            spi_url = spi_url_value_external


        if spi_url != "" and spi_url is not None:
            params = {
                "service_command_id": service_command_id,
                "spi_url_type": spi_type,
                "url": spi_url,
                "spi_url_call_method": spi_url_call_method,
                "expire_in_minute": 0 if expire_in_minute == "" else int(expire_in_minute),
                "max_retry": 0 if max_retry == "" else int(max_retry),
                "retry_delay_millisecond": 0 if retry_delay == "" else int(retry_delay),
                "read_timeout": 0 if read_timeout == "" else int(read_timeout),
                "connection_timeout": 0 if connection_timeout == "" else int(connection_timeout)
            }
            success, status_code, message, data = self.update_spi(spi_url_id, params)


            if success:
                message_level = messages.SUCCESS
                message_text = 'Updated data successfully'
                self.logger.info('========== Finish updated SPI url ==========')
            elif status_code in ["access_token_expire", 'authentication_fail', 'invalid_access_token']:
                self.logger.info('========== Finish updated SPI url ==========')
                raise InvalidAccessToken(message)
            else:
                self.logger.info('========== Finish updated SPI url ==========')
                context = super(SPIUpdate, self).get_context_data(**kwargs)
                context.update({'data':{
                    'spi_url_id': spi_url_id,
                    'spi_url_type': spi_type,
                    'spi_url_call_method': spi_url_call_method,
                    'read_timeout': read_timeout,
                    'max_retry': max_retry,
                    'retry_delay_millisecond': retry_delay,
                    'expire_in_minute': expire_in_minute,
                    'created_timestamp': created_timestamp,
                    'last_updated_timestamp': last_updated_timestamp,
                    'internal_url': spi_url_value_internal,
                    'external_url': spi_url_value_external,
                }})
                spi_types = self.get_spi_types()
                data_spi_call_method = self.get_call_method()
                context['internal'] = True if spi_url_option == 'internal' else False
                context['external'] = True if spi_url_option == 'external' else False
                context['spi_types'] = spi_types
                context['data_spi_call_method'] = data_spi_call_method
                context['service'] = service_id
                context['command'] = command_id
                context['service_command'] = service_command_id

                messages.add_message(
                    request,
                    messages.ERROR,
                    message
                )
                return render(request, self.template_name, context=context)
        else:
            message_level = messages.ERROR
            message_text = "SPI url cannot be empty."
            self.logger.info('========== Finish updated SPI url ==========')
            return redirect('services:spi_update',
                                service_command_id=service_command_id,
                                command_id=command_id,
                                service_id=service_id,
                                spiUrlId=spi_url_id)

        messages.add_message(
            request,
            message_level,
            message_text
        )
        return redirect('services:spi_list',
                        service_command_id=service_command_id,
                        command_id=command_id,
                        service_id=service_id)

    def get_context_data(self, **kwargs):
        context = super(SPIUpdate, self).get_context_data(**kwargs)
        service_id = kwargs.get('service_id')
        command_id = kwargs.get('command_id')
        service_command_id = kwargs.get('service_command_id')
        spi_url_id = kwargs.get('spiUrlId')

        if not service_command_id:
            raise Http404

        spi_types = self.get_spi_types()
        data_spi_call_method = self.get_call_method()
        self.logger.info('========== Start getting SPI url detail ==========')
        success, status_code, data  = RestFulClient.get(
                                        url=api_settings.SPI_DETAIL_PATH.format(spiUrlId=spi_url_id),
                                        loggers=self.logger,
                                        headers=self._get_headers())
        self.logger.info('Response_content: {}'.format(data))
        if success:
            if data['url'] in self.internal_urls:
                context['internal'] = True
                data['internal_url'] = data['url']
            else:
                context['external'] = True
                data['external_url'] = data['url']
            context['data'] = data
            context['spi_types'] = spi_types
            context['data_spi_call_method'] = data_spi_call_method
            context['add_spi_url_msg'] = self.request.session.pop('add_spi_url_msg', None)
            context['service'] = service_id
            context['command'] = command_id
            context['service_command'] = service_command_id
        elif (status_code == "access_token_expire") or (status_code == 'authentication_fail') or (
                    status_code == 'invalid_access_token'):
            self.logger.info("{}".format(data))
            raise InvalidAccessToken(data)
        self.logger.info('========== Finish getting SPI url detail ==========')
        return context

    def get_spi_types(self):
        self.logger.info('========== Start getting spi url types ==========')
        success, status_code, data  = RestFulClient.get(url=api_settings.SPI_TYPES_PATH, loggers=self.logger, headers=self._get_headers())
        self.logger.info('========== finish get spi url types ==========')
        return data

    def get_call_method(self):
        self.logger.info('========== Start getting spi call method ==========')
        success, status_code, data  = RestFulClient.get(url=api_settings.SPI_CALL_METHOD_PATH, loggers=self.logger, headers=self._get_headers())
        self.logger.info('========== finish get spi call method ==========')
        return data

    def update_spi(self, spi_url_id, params):
        path = api_settings.SPI_UPDATE_PATH.format(spiUrlId=spi_url_id)
        success, status_code, message, data = RestFulClient.put(
                url = path,
                headers=self._get_headers(),
                loggers=self.logger,
                params=params)
        API_Logger.put_logging(loggers=self.logger, params=params, response=data, status_code=status_code)
        return success, status_code, message, data

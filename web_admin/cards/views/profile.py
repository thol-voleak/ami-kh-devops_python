import logging
from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods
from web_admin.api_settings import CARD_LIST_PATH
from web_admin.utils import setup_logger


logger = logging.getLogger(__name__)

IS_STOP = {
    True: 'YES',
    False: 'NO',
}


class ProfileView(TemplateView, RESTfulMethods):
    template_name = "profile.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(ProfileView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start search card ==========')

        card_identifier = request.GET.get('card_identifier')
        card_token = request.GET.get('card_token')
        user_id = request.GET.get('user_id')
        user_type = request.GET.get('user_type')

        self.logger.info('card_identifier: {}'.format(card_identifier))
        self.logger.info('card_token: {}'.format(card_token))
        self.logger.info('user_id: {}'.format(user_id))
        self.logger.info('user_type: {}'.format(user_type))

        body = {}
        
        if card_identifier is not '' and card_identifier is not None:
            body['card_identifier'] = card_identifier
        if card_token is not '' and card_token is not None:
            body['token'] = card_token
        if user_id is not '' and user_id is not None:
            body['user_id'] = int(0 if user_id is None else user_id)
        if user_type is not '' and user_type is not '0':
            body['user_type_id'] = int(0 if user_type is None else user_type)

        data = self.get_card_list(body)
        if data is not None:
            result_data = self.format_data(data)
        else:
            result_data = data

        context = {'data': result_data,
                   'card_identifier': card_identifier,
                   'card_token': card_token,
                   'user_id': user_id,
                   'user_type': user_type
                   }

        self.logger.info('========== End search card ==========')
        return render(request, 'profile.html', context)

    def get_card_list(self, body):
        url = CARD_LIST_PATH
        data, success = self._post_method(url, "card list", logger, body)
        if isinstance(data, list):
            return data
        else:
            return []

    def format_data(self, data):
        for i in data:
            i['is_stopped'] = IS_STOP.get(i.get('is_stopped'))
        return data

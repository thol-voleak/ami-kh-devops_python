import logging
from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods
from web_admin.api_settings import CARD_LIST_PATH
logger = logging.getLogger(__name__)

IS_STOP = {
    True: 'YES',
    False: 'NO',
}


class ProfileView(TemplateView, RESTfulMethods):
    template_name = "profile.html"

    def post(self, request, *args, **kwargs):
        logger.info('========== Start search card ==========')

        card_identifier = request.POST.get('card_identifier')
        user_id = request.POST.get('user_id')
        user_type = request.POST.get('user_type')

        logger.info('card_identifier: {}'.format(card_identifier))
        logger.info('user_id: {}'.format(user_id))
        logger.info('user_type: {}'.format(user_type))

        body = {}

        if card_identifier is not '':
            body['card_identifier'] = card_identifier
        if user_id is not '':
            body['user_id'] = int(user_id)
        if user_type is not '' and user_type is not '0':
            body['user_type_id'] = int(user_type)

        data = self.get_card_list(body)
        if data is not None:
            result_data = self.format_data(data)
        else:
            result_data = data

        context = {'data': result_data,
                   'card_identifier': card_identifier,
                   'user_id': user_id,
                   'user_type': user_type
                   }

        logger.info('========== End search card ==========')
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

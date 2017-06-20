import logging
from django.shortcuts import render
from django.views.generic.base import TemplateView
from web_admin.restful_methods import RESTfulMethods
from web_admin.api_settings import CARD_HISTORY_PATH
from web_admin.utils import setup_logger


logger = logging.getLogger(__name__)

IS_SUCCESS = {
    True: 'Success',
    False: 'Failed',
}


class HistoryView(TemplateView, RESTfulMethods):
    template_name = "history.html"
    logger = logger

    def dispatch(self, request, *args, **kwargs):
        self.logger = setup_logger(self.request, logger)
        return super(HistoryView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.logger.info('========== Start search history card ==========')

        trans_id = request.GET.get('trans_id')
        card_id = request.GET.get('card_id')
        user_id = request.GET.get('user_id')
        user_type_id = request.GET.get('user_type_id')

        self.logger.info('trans_id: {}'.format(trans_id))
        self.logger.info('card_id: {}'.format(card_id))
        self.logger.info('user_id: {}'.format(user_id))
        self.logger.info('user_type_id: {}'.format(user_type_id))

        body = {}
        if trans_id is None and card_id is None and user_id is None and user_type_id is None:
            result_data = {}
        else:
            if trans_id is not '':
                body['trans_id'] = trans_id
            if card_id is not '':
                body['card_id'] = int(0 if card_id is None else card_id)
            if user_id is not '':
                body['user_id'] = int(0 if user_id is None else user_id)
            if user_type_id is not '' and user_type_id is not '0':
                body['user_type_id'] = int(0 if user_type_id is None else user_type_id)

            data = self.get_card_history_list(body)
            if data is not None:
                result_data = self.format_data(data)
            else:
                result_data = data

        context = {'data': result_data,
                   'trans_id': trans_id,
                   'card_id': card_id,
                   'user_id': user_id,
                   'user_type_id': user_type_id
                   }

        self.logger.info('========== End search card history ==========')
        return render(request, 'history.html', context)

    def get_card_history_list(self, body):
        url = CARD_HISTORY_PATH
        data, success = self._post_method(url, "card history list", logger, body)
        if isinstance(data, list):
            return data
        else:
            return []

    def format_data(self, data):
        for i in data:
            i['is_success'] = IS_SUCCESS.get(i.get('is_success'))
        return data

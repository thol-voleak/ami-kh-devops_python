from authentications.utils import get_auth_header


class GetHeaderMixin(object):
    def _get_headers(self):
        if getattr(self, '_headers', None) is None:
            self._headers = get_auth_header(self.request.user)
        return self._headers

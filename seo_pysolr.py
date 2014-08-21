import pysolr
import requests
import time


class Solr(pysolr.Solr):
    def __init__(self, url, decoder=None, timeout=60, auth=None):
        super(Solr, self).__init__(url, decoder, timeout)
        self.auth = auth

    def _send_request(self, method, path='', body=None, headers=None,
                      files=None):
        """
        Copy and paste of the base (pysolr version 3.2.0) _send_request()
        method except for the resp = requests_method() line, which
        passes along the auth information.

        """
        url = self._create_full_url(path)
        method = method.lower()
        log_body = body

        if headers is None:
            headers = {}

        if log_body is None:
            log_body = ''
        elif not isinstance(log_body, str):
            log_body = repr(body)

        self.log.debug("Starting request to '%s' (%s) with body '%s'...", url,
                       method, log_body[:10])
        start_time = time.time()

        try:
            requests_method = getattr(self.session, method, 'get')
        except AttributeError:
            err = "Unable to send HTTP method '{0}.".format(method)
            raise pysolr.SolrError(err)

        try:
            bytes_body = body

            if bytes_body is not None:
                bytes_body = pysolr.force_bytes(body)

            resp = requests_method(url, data=bytes_body, headers=headers,
                                   files=files, timeout=self.timeout,
                                   auth=self.auth)
        except requests.exceptions.Timeout as err:
            error_message = "Connection to server '%s' timed out: %s"
            self.log.error(error_message, url, err, exc_info=True)
            raise pysolr.SolrError(error_message % (url, err))
        except requests.exceptions.ConnectionError as err:
            error_message = "Failed to connect to server at '%s', are you " \
                            "sure that URL is correct? Checking it in a " \
                            "browser might help: %s"
            params = (url, err)
            self.log.error(error_message, *params, exc_info=True)
            raise pysolr.SolrError(error_message % params)

        end_time = time.time()
        self.log.info("Finished '%s' (%s) with body '%s' in %0.3f seconds.",
                      url, method, log_body[:10], end_time - start_time)

        if int(resp.status_code) != 200:
            error_message = self._extract_error(resp)
            data = {'data': {'headers': resp.headers, 'response': resp.content}}
            self.log.error(error_message, extra=data)
            raise pysolr.SolrError(error_message)

        return pysolr.force_unicode(resp.content)
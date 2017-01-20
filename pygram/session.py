import time
import requests
from . import config

HTTP_OK = 200


class Session(object):
    """
    Session class describes current session of any instagram user.
    """
    def __init__(self, verbose=True):
        self.logged = False
        self.username = None
        self.session = requests.Session()
        self.cookie = None
        self.verbose = verbose

    def log(self, *args, **kwargs):
        """
        Works like ``print`` if ``self.verbose`` is ``True``.

        :param args: ``print`` args
        :param kwargs: ``print`` kwargs
        :return: ``None``
        """
        if self.verbose:
            print(*args, **kwargs)
        else:
            pass

    def reset_session(self):
        """
         - Resets session header and cookie to its default values.
         - Loads remote X-CSRFToken and stores it in the header
        :return:
        """
        self.session.cookies.update(config.BASE_COOKIE)
        self.session.headers.update(config.BASE_HEADER)
        answer = self.session.get(config.URL)
        self.session.headers.update({'X-CSRFToken': answer.cookies['csrftoken']})
        time.sleep(1)

    def _check_login(self, answer):
        """
        Checks, whether user is logged in correctly.

        - HTTP status must be 200
        - Next answer from POST to https://www.instagram.com must contain USERNAME
        :param answer: response from logging in POST request
        :return: :bool: login status
        """
        if answer.status_code == HTTP_OK:
            answer = self.session.get(config.URL)
            if answer.text.find(self.user_login) != -1:
                return True
            else:
                self.log("Can't login: Invalid login or password.")
                return False
        else:
            self.log("Can't login. Status code: {}".format(answer.status_code))
            return False

    def login(self, username=None, password=None, path=None):
        """
        Performing login for the session.

        **TODO**: Maybe it's possible to store cookie in the file somehow.

        :param username: Instagram username
        :param password: Instagram password
        :param path: Path to cookie file (**TODO**)
        :return: True/False of logging correctly
        """
        if self.logged:
            self.logout()
        self.reset_session()
        user = {'username': username,
                'password': password}
        answer = self.session.post(config.URL_LOGIN,
                                   data=user,
                                   allow_redirects=True)
        self.session.headers.update(
            {'X-CSRFToken': answer.cookies['csrftoken']})
        self.cookie = answer.cookies['csrftoken']
        time.sleep(1)
        self.logged = self._check_login(answer)
        self.username = username
        return self.logged

    def logout(self):
        """
        Logging out from instagram in the current session
        :return: requests.get response
        """
        answer = requests.post(config.URL_LOGOUT,
                        {'csrfmiddlewaretoken': self.cookie})
        if answer:
            self.logged = False
        return answer

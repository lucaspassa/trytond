# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import logging
import urlparse

import ldap3
from ldap3.core.exceptions import LDAPException

from trytond.transaction import Transaction
from trytond.pool import PoolMeta
from trytond.config import config, parse_uri
from trytond.exceptions import LoginException

__all__ = ['User']

logger = logging.getLogger(__name__)
section = 'ldap_authentication'

# Old version of urlparse doesn't parse query for ldap
# see http://bugs.python.org/issue9374
if 'ldap' not in urlparse.uses_query:
    urlparse.uses_query.append('ldap')


def parse_ldap_url(uri):
    unquote = urlparse.unquote
    uri = parse_uri(uri)
    dn = unquote(uri.path)[1:]
    attributes, scope, filter_, extensions = (
        uri.query.split('?') + [''] * 4)[:4]
    if not scope:
        scope = 'base'
    extensions = urlparse.parse_qs(extensions)
    return (uri, dn, unquote(attributes), unquote(scope), unquote(filter_),
        extensions)


def ldap_server():
    uri = config.get(section, 'uri')
    if not uri:
        return
    uri, _, _, _, _, extensions = parse_ldap_url(uri)
    if uri.scheme.startswith('ldaps'):
        scheme, port = 'ldaps', 636
    else:
        scheme, port = 'ldap', 389
    return ldap3.Server('%s://%s:%s' % (
            scheme, uri.hostname, uri.port or port))


class User:
    __metaclass__ = PoolMeta
    __name__ = 'res.user'

    @classmethod
    def __setup__(cls):
        super(User, cls).__setup__()
        cls._error_messages.update({
                'set_passwd_ldap_user': (
                    'You can not set the password of ldap user "%s".'),
                })

    @staticmethod
    def ldap_search_user(login, server, attrs=None):
        '''
        Return the result of a ldap search for the login using the ldap
        server.
        The attributes values defined in attrs will be return.
        '''
        _, dn, _, scope, filter_, extensions = parse_ldap_url(
            config.get(section, 'uri'))
        scope = {
            'base': ldap3.BASE,
            'onelevel': ldap3.LEVEL,
            'subtree': ldap3.SUBTREE,
            }[scope]
        uid = config.get(section, 'uid', default='uid')
        if filter_:
            filter_ = '(&(%s=%s)%s)' % (uid, login, filter_)
        else:
            filter_ = '(%s=%s)' % (uid, login)

        bindpass = None
        bindname, = extensions.get('bindname', [None])
        if not bindname:
            bindname, = extensions.get('!bindname', [None])
        if bindname:
            # XXX find better way to get the password
            bindpass = config.get(section, 'bind_pass')

        with ldap3.Connection(server, bindname, bindpass) as con:
            con.search(dn, filter_, search_scope=scope, attributes=attrs)
            result = con.entries
            if result and len(result) > 1:
                logger.info('ldap_search_user found more than 1 user')
            return [(e.entry_dn, e.entry_attributes_as_dict)
                for e in result]

    @classmethod
    def _check_passwd_ldap_user(cls, logins):
        find = False
        try:
            server = ldap_server()
            if not server:
                return
            for login in logins:
                if cls.ldap_search_user(login, server, attrs=[]):
                    find = True
                    break
        except LDAPException:
            logger.error('LDAPError when checking password', exc_info=True)
        if find:
            cls.raise_user_error('set_passwd_ldap_user', (login,))

    @classmethod
    def create(cls, vlist):
        tocheck = []
        for values in vlist:
            if values.get('password') and 'login' in values:
                tocheck.append(values['login'])
        if tocheck:
            with Transaction().set_context(_check_access=False):
                cls._check_passwd_ldap_user(tocheck)
        return super(User, cls).create(vlist)

    @classmethod
    def write(cls, *args):
        actions = iter(args)
        for users, values in zip(actions, actions):
            if values.get('password'):
                logins = [x.login for x in users]
                cls._check_passwd_ldap_user(logins)
        super(User, cls).write(*args)

    @classmethod
    def set_preferences(cls, values, parameters):
        if 'password' in values:
            if 'password' not in parameters:
                msg = cls.fields_get(['password'])['password']['string']
                raise LoginException('password', msg, type='password')
            old_password = parameters['password']
            try:
                server = ldap_server()
                if server:
                    user = cls(Transaction().user)
                    uid = config.get(section, 'uid', default='uid')
                    users = cls.ldap_search_user(
                        user.login, server, attrs=[uid])
                    if users and len(users) == 1:
                        [(dn, attrs)] = users
                        con = ldap3.Connection(server, dn, old_password)
                        if con.bind():
                            con.extend.standard.modify_password(
                                dn, old_password, values['password'])
                            values = values.copy()
                            del values['password']
                        else:
                            cls.raise_user_error('wrong_password')
            except LDAPException:
                logger.error('LDAPError when setting preferences',
                    exc_info=True)
        super(User, cls).set_preferences(values, parameters)

    @classmethod
    def _login_ldap(cls, login, parameters):
        if 'password' not in parameters:
            msg = cls.fields_get(['password'])['password']['string']
            raise LoginException('password', msg, type='password')
        password = parameters['password']
        try:
            server = ldap_server()
            if server:
                uid = config.get(section, 'uid', default='uid')
                users = cls.ldap_search_user(login, server, attrs=[uid])
                if users and len(users) == 1:
                    [(dn, attrs)] = users
                    con = ldap3.Connection(server, dn, password)
                    if (password and con.bind()):
                        # Use ldap uid so we always get the right case
                        login = attrs.get(uid, [login])[0]
                        user_id, _ = cls._get_login(login)
                        if user_id:
                            return user_id
                        elif config.getboolean(section, 'create_user'):
                            user, = cls.create([{
                                        'name': login,
                                        'login': login,
                                        }])
                            return user.id
        except LDAPException:
            logger.error('LDAPError when login', exc_info=True)

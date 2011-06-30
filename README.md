Cheeta : A dummy wrapper for MailChimp API (1.3)
========================================================

Cheeta is a simple wrapper for MailChimp API (http://apidocs.mailchimp.com/1.3/). It uses mailsnake for the work behind the scenes. It doesn't cover all the API.

Usage:
------


    from cheeta import Cheeta
    c = Cheeta(api_key='yourapikey')

    c.get_list_members('d1677ca3f3')
    >> {u'tarzan@jungle.br': {u'timestamp': datetime.datetime(2011, 6, 29, 7, 12, 45)},
    >>  u'jane@jungle.br': {u'timestamp': datetime.datetime(2011, 6, 29, 7, 14, 49)},
    >> }

    for email,data in c.get_list_members_detailed('d1677ca3f3',['tarzan@jungle.br','jane@jungle.br']):
        print email, data
    >> tarzan@jungle.br {u'status': u'subscribed', u'info_changed': u'2011-06-29 12:56:28', u'web_id': 123123,
    >> u'email_type': u'html', u'language': None, u'static_segments': [{u'added': u'2011-06-28 14:21:38', u'id': 169,
    >> u'name': u'The_Tarzan1309270897.11'}], u'merges': {u'REGION': u'Deep Jungle', u'BRANCH': u'The top one!',
    >> u'EMAIL': u'tarzan@jungle.br', u'MEMBERID': u'123123123123213', u'NAME': u'The Tarzan'}, u'clients': [],
    >> u'lists': [], u'member_rating': 2, u'timestamp': datetime.datetime(2011, 6, 28, 9, 59, 47), u'id': u'xxxxxxxx',
    >> u'ip_opt': u'212.212.111.111', u'geo': [], u'ip_signup': None}
    

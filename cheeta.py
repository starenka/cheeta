#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime, re, copy, time
from mailsnake import MailSnake

class MailChimpAPIException(Exception):
   def __init__(self, value,method=None,*args,**kwargs):
       super(MailChimpAPIException,self).__init__(*args,**kwargs)
       self.val = value
   def __str__(self):
       return repr(self.val)

class Cheeta(object):
    """ Simple wrapper for MailChimp API (http://apidocs.mailchimp.com/1.3/)
        It uses mailsnake for the work behind the scenes. It doesn't cover all
        the API.
    """
    DATE_REGEXP = re.compile(r'.*(time)|(date).*')
    PREVIEW_ID_REGEXP = re.compile(r'http://gallery.mailchimp.com/(.*?)/.*')
    CAMPAIGN_TYPE = ('regular','plaintext','absplit','rss','trans','auto')
    DEFAULT_CAMPAIGN = 'regular'
    DEFAULT_CONTENT_TYPE = 'html'

    def __init__(self,api_key=None,debug=False):
        self.mailsnake = MailSnake(api_key)
        self.debug = debug

    def _api_call(self,method,*args,**kwargs):
        if self.debug:
            print method,args,kwargs
        try:
            return getattr(self.mailsnake,method)(*args,**kwargs)
        except Exception,e:
            raise MailChimpAPIException(e)

    def _parse_data_dict(self,data):
        for k,v in data.items():
            if re.match(self.DATE_REGEXP,k):
                data[k] = self._str_to_datetime(v)
        return data

    def _parse_create_call(self,data):
        if not isinstance(data,dict):
            return data
        else:
            raise MailChimpAPIException(data['error'] if 'error' in data else data['errors'])

    def _parse_list_call(self,response,key='name',data_key='data'):
        parsed = {}
        if 'error' in response:
            raise MailChimpAPIException(response['error'])
        if data_key in response:
            for one in response[data_key]:
                parsed[one[key]] = self._parse_data_dict(one)
                del(parsed[one[key]][key])
        else:
            parsed = response
        return parsed

    def _parse_error_success(self,response):
        if isinstance(response,dict):
            if 'error' in response: #normalize
                response['errors'] = copy.copy(response['error'])
                del(response['error'])
            if response['errors']:
                raise MailChimpAPIException(response['errors'])
        else:
            return response

    def _str_to_datetime(self,dt_string,format='%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.datetime.strptime(dt_string,format)
        except:
            return dt_string

    def get_lists(self):
        return self._parse_list_call(self._api_call('lists'))

    def get_list_members(self,id,limit=15000):
        return self._parse_list_call(self._api_call('listMembers',id=id,limit=limit),'email')

    def get_static_segments(self,list_id):
        return self._parse_list_call(self._api_call('listStaticSegments',id=list_id))

    def get_list_members_detailed(self,list_id,members):
        for one in members:
            member = self._parse_list_call(self._api_call('listMemberInfo',
                                                          id=list_id,
                                                          email_address=one),
                                  data_key='data',
                                  key='email'
            )
            yield one,member[one]

    def get_user_templates(self,types=None,inactives=None,category=None):
        return self._parse_list_call(
                self._api_call('templates',types=types,inactives=inactives,category=category),
                data_key='user'
        )

    def get_user_template(self,template_id):
        return self._parse_list_call(self._api_call('templateInfo',tid=template_id))

    def get_user_template_preview_url(self,template_id,campaign_id):
        templates = self._parse_list_call(
                self._api_call('templates'),key='id',data_key='user'
        )
        preview_image = templates[int(template_id)].get('preview_image','') or ''
        id = re.match(self.PREVIEW_ID_REGEXP,preview_image)
        if id:
            return 'http://us2.campaign-archive2.com/?u=%s&id=%s&e='%(id.group(1),campaign_id)
        else:
            return False

    def get_campaigns(self,filters=None,start=None,limit=None):
        return self._parse_list_call(
                self._api_call('campaigns',filters=filters,start=start,limit=limit),
                'title'
        )

    def create_static_segment(self,list_id,name):
        return self._parse_create_call(
            self._api_call('listStaticSegmentAdd',id=list_id,name=name)
        )

    def purge_static_segment(self,list_id,segment_id):
        return self._parse_error_success(
            self._api_call('listStaticSegmentReset',id=list_id,seg_id=segment_id)
        )

    def update_static_segment(self,list_id,segment_id,members):
        call = self.purge_static_segment(list_id,segment_id)
        if call:
            return self._parse_error_success(
                self._api_call('listStaticSegmentMembersAdd',id=list_id,seg_id=segment_id,batch=members)
            )
        return call

    def create_static_segment_w_members(self,list_id,name,members):
        id = self.create_static_segment(list_id=list_id,name=name)
        call = self._parse_error_success(
            self._api_call('listStaticSegmentMembersAdd',id=list_id,seg_id=id,batch=members)
        )
        return id

    def test_campaign_segment(self,list_id,options):
        return self._api_call('campaignSegmentTest',list_id=list_id,options=options)        

    def create_campaign_from_static_segment(self,list_id,content,subject,from_email,from_name,members):
        now = datetime.datetime.now()
        now_str = datetime.datetime.strftime(now,'Y-m-d H:M:S')
        seg_id = self.create_static_segment_w_members(  list_id=list_id,
                                                        name='%s_%s_%s'%(now_str,from_name,time.time()),
                                                        members=members
        )
        if seg_id:
            return self.create_campaign(content=content,
                                        list_id=list_id,
                                        subject=subject,
                                        from_email=from_email,
                                        from_name=from_name,
                                        segment_opts={
                                            'conditions':[{
                                                'field':'static_segment',
                                                'op':'eq',
                                                'value':seg_id
                                            }],
                                            'match':'all'
                                        }
            ),seg_id


    def create_campaign(self,content,type=None,**kwargs):
        """ 'list_id','subject','from_email','from_name' """
        opts = ('list_id','subject','from_email','from_name')
        options = {}
        segment_opts = kwargs.get('segment_opts',{})
        type_opts = kwargs.get('type_opts',{})

        for n,v in kwargs.items():
            if n in opts:
                options[n] = v
        type = type if type else self.DEFAULT_CAMPAIGN

        return self._parse_create_call(
            self._api_call('campaignCreate',
                type=type,
                options=options,
                content={self.DEFAULT_CONTENT_TYPE:content},
                segment_opts=segment_opts,
                type_opts=type_opts
            )
        )

    def update_campaign(self,campaign_id,data):
        errors = []
        for k,v in data.items():
            call = self._api_call('campaignUpdate',cid=campaign_id,name=k,value=v)
            if isinstance(call,dict):
                errors.append(call['error'])

        return errors if errors else True

    def test_campaign(self,campaign_id,test_emails):
        return self._parse_create_call(self._api_call('campaignSendTest',
                                                      cid=campaign_id,test_emails=test_emails)
        )

    def send_campaign(self,campaign_id):
        return self._parse_create_call(self._api_call('campaignSendNow',
                                                      cid=campaign_id)
        )

    def has_template_placeholder(self,template_id,needle='{{ placeholder }}'):
        template = self.get_user_template(template_id)
        return needle in template['source']
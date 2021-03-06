"""
The basic apaf panel, accessible as it is from
"""
import os
import os.path
import sys

from cyclone import web
import txtorcon

import apaf
from apaf.core import Service, add_service
from apaf import config
from apaf.panel import handlers, controllers
from apaf.utils import hashing



class PanelService(Service):
    name = 'panel'
    desc = 'Administration panel and apaf manager.'
    port = 80
    icon = None
    conf = config.Config('panel.cfg',
                             defaults=dict(
                                 remote_login=True,
                                 passwd=hashing.hash('None'),
    ))



    static_dir = os.path.join(config.services_dir, 'panel', 'static')
    templates_dir = os.path.join(config.services_dir, 'panel', 'templates')

    _paneldir = os.path.join(config.services_dir, 'panel')
    urls = [
        ## REST API ##
        # services informations
        (r'/services/(.*)/start', handlers.rest.ServiceHandler, {'action':'start'}),
        (r'/services/(.*)/stop', handlers.rest.ServiceHandler, {'action':'stop'}),
        (r'/services/(.*)', handlers.rest.ServiceHandler, {'action':'state'}),
        (r'/services', handlers.rest.ServiceHandler),
        # authentication
        (r'/auth/login', handlers.rest.AuthHandler, {'action':'login'}),
        (r'/auth/logout', handlers.rest.AuthHandler, {'action':'logout'}),
        # configuration
        (r'/config', handlers.rest.ConfigHandler),
        # tor controlport
        (r'/tor', handlers.rest.TorHandler),
        (r'/tor/(.*)', handlers.rest.TorHandler),

        (r'/', handlers.IndexHandler),

        # Legacy html
        (r'/index.html', handlers.html.render('index.html')),
        (r'/services.html', handlers.html.ServiceHandler),
        (r'/tor.html', handlers.html.TorHandler),
        (r'/config.html', handlers.html.ConfigHandler),
        (r'/about.html', handlers.html.render('about.html')),
        (r'/login.html', handlers.html.LoginHandler),

        # JS Application
        (r'/app.html', handlers.html.render('index.html')),

        ## STATIC FILES ##
        (r'/(.*)', web.StaticFileHandler, {'path':static_dir}),
    ]

    def get_factory(self):
        # create the hidden service directory of the panel
        if not os.path.exists(self._paneldir):
            os.mkdir(self._paneldir)

        app = web.Application(self.urls,
                               debug=True,
                               cookie_secret=config.custom['cookie_secret'],
                               login_url='/login.html',
                               xsrf_cookies=True,
                               template_path=self.templates_dir,
        )
        app.conf = self.conf
        return app

def start_panel(torconfig):
    """
    Set up the panel service, which lets the user customize apaf and choose
    which services are going to run.

    :param torconfig: an instance of txtorcon.TorConfig representing the
                      configuration file.
    """
    panel = PanelService()
    add_service(torconfig, panel)

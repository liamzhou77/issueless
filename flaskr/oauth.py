from authlib.integrations.flask_client import OAuth


oauth = OAuth()
client_id = '3silBpYY8BSfVWca3Q0suIwB8h24vMzz'
domain = 'issue-tracker-7.auth0.com'


def configure_oauth(client_secret):
    auth0 = oauth.register(
        'auth0',
        client_id=client_id,
        client_secret=client_secret,
        api_base_url=f'https://{domain}',
        access_token_url=f'https://{domain}/oauth/token',
        authorize_url=f'https://{domain}/authorize',
        client_kwargs={'scope': 'openid profile email'},
    )
    return auth0

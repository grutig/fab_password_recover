# fab_password_recover
User password recovery for flask_appbuilder

Flask appbuilder lacks of a user password recovery function. Since I needed it for an application, I wrote this add-on module that requires no modification on the code, just a few file in config.py and in __init__.py

How to setup:

1) place `passrec.py` in app root folder
2) add
    `from app import passrec`
   at the end of __init__.py
3) append
   `MAIL_SERVER = <server>
   
   MAIL_PORT = <port>
   
   MAIL_USE_TLS = True
   
   MAIL_USE_SSL = False
   
   MAIL_DEBUG = False
   
   MAIL_USERNAME = <mail username>
   
   MAIL_PASSWORD = <mail pass>
   
   MAIL_DEFAULT_SENDER = ("<sender name>", "<sender address>")
   
   MAIL_MAX_EMAILS = 10
   
   MAIL_SUPPRESS_SEND = False
   
   PUBLIC_URL = <web site public url>
   
   TOKEN_VALIDITY = <token validity>  # minutes
   
   SUPPORT_EMAIL = <support email>`
   
   to config.py
5) place all the template files in `templaes/appbuilder/general/security` directory.

done

It overrides the default login_db template, showing a link to request user password change. If selected it prompts for the user's own email.
If email if valid and registered in database, it sends it a message with a link, valid for TOKEN VALIDITY minutes, as specified in config.py
During that time interval, it will not accept further requests for the same email.
If the user follows that link, it is prompted for a new password, that - if validated - will replace that one stored in db.
The validation is done, as is, just on lenght, but it easy to enforce more strict rules.


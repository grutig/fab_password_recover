# fab_password_recover
User password recovery for flask_appbuilder

Flask appbuilder lacks of a user password recovery function. Since I needed it for an application, I wrote this add-on module that requires no modification on the code, just a few file in config.py and in __init__.py

How to setup:

1) place `passrec.py` in app root folder
2) add 
    `from app import passrec`
   at the end of __init__.py
3) append `config.append.py` to `config.py` and set correct values
5) copy all the template files in `templates` directory.

done

It overrides the default login_db template, showing a link to request user password change.

If selected it prompts for the user's own email.

If email if valid and registered in database, it sends it a message with a link, valid for TOKEN VALIDITY minutes, as specified in config.py

During that time interval, it will not accept further requests for the same email.

If the user follows that link, it is prompted for a new password, that - if validated - will replace that one stored in db.

The validation is done, as is, just on lenght, but it easy to enforce more strict rules.

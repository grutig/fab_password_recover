from flask_appbuilder import expose, BaseView, Model
from flask_appbuilder.security.sqla.models import User
from flask import abort, redirect, url_for, current_app, flash
from flask_babel import gettext
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, email, EqualTo
from sqlalchemy import Column, String, TIMESTAMP
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from flask_mail import Message
from app import mail, appbuilder, db
import binascii
import os
import re

""" 
Copyright (c) 2023 Giorgio L. Rutigliano
(www.iltecnico.info, www.i8zse.eu, www.giorgiorutigliano.it)

This is free software released under MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

#  Data Model #####################################

class Pwdreset(Model):
    email = Column(String(64), primary_key=True)
    token = Column(String(40), unique=True, nullable=False)
    created = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

#  Forms ##########################################

class PwrrForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), email()])

    def validate(self, extra_validators=None):
        rv = FlaskForm.validate(self, extra_validators)
        if not rv:
            return False
        # check if there is no other request queued
        row = db.session.query(Pwdreset).filter_by(email=self.email.data).first()
        if row is not None:
            self.email.errors.append(gettext("There is another request pending, try later"))
            return False
        return True

class NewPwForm(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=32)])
    confirm = PasswordField('Confirm Password', [InputRequired(), Length(min=8, max=32), EqualTo('password')])

#  Views ##########################################

class PRView(BaseView):

    route_base = "/pwd/"

    @expose('/resetpass', methods=['GET', 'POST'])
    #
    # send password recovery email
    #
    def passreset(self):
        self.update_redirect()
        form = PwrrForm()
        if form.validate_on_submit():
            row = db.session.query(User).filter_by(email=form.email.data).first()
            if row is not None:
                # create token
                pwrr = Pwdreset(
                    email=form.email.data,
                    token=binascii.hexlify(os.urandom(20)).decode()
                )
                # create mail message
                regurl = url_for('PRView.newpass', token=pwrr.token)
                msg = Message(gettext("Password reset"), recipients=[form.email.data, ])
                tplfile = os.path.join(current_app.jinja_loader.searchpath[0],
                            "email/resetpass." + appbuilder.bm.get_locale() + ".ema")
                buf = open(tplfile).read()
                fullink = current_app.config['PUBLIC_URL'] + regurl
                # fill both versions of body
                msg.html = buf.replace("%token%", fullink).replace("%tkv%", str(current_app.config['TOKEN_VALIDITY']))
                msg.body = re.sub(re.compile('<.*?>'), '', msg.html)
                # send message
                msg.sender = current_app.config['MAIL_DEFAULT_SENDER']
                try:
                    mail.send(msg)
                except:
                    flash(gettext("Send mail error, please try again later"), 'danger')
                    return redirect("/")
                # email sent, save request into db
                db.session.add(pwrr)
                db.session.commit()
            tmpl = 'appbuilder/general/security/ema1_sent.' + appbuilder.bm.get_locale() + '.html'
            return self.render_template(tmpl, title=gettext("Check email"), tkv=current_app.config['TOKEN_VALIDITY'])
        return self.render_template('appbuilder/general/security/password_reset.html', title=gettext("Password recover"), form=form)

    @expose('/newpass/<token>', methods=['GET', 'POST'])
    #
    # semd password recovery email
    #
    def newpass(self, token=None):
        self.update_redirect()
        form = NewPwForm()
        tkv = current_app.config['TOKEN_VALIDITY']
        # delete expired tokens
        xp = (datetime.utcnow() - timedelta(minutes=tkv))
        db.session.execute("delete from pwdreset where created < :sd ", {'sd': xp})
        db.session.commit()
        # check token
        pwdr = db.session.query(Pwdreset).filter_by(token=token).first()
        if pwdr is None:
            return abort(404)
        # handle form validation
        if form.validate_on_submit():
            user = db.session.query(User).filter_by(email=pwdr.email).first()
            user.password = generate_password_hash(form.password.data)
            db.session.commit()
            # remove token
            db.session.query(Pwdreset).filter_by(token=token).delete()
            db.session.commit()
            flash(gettext("New password has been recorded"), 'info')
            return redirect("/")

        return self.render_template('appbuilder/general/security/newpassword.html',
                                    title=gettext("Enter new password"), form=form, email=pwdr.email)


appbuilder.add_view_no_menu(PRView())

from flask import Flask, render_template, request, redirect, url_for, session, make_response, flash
from flask_ckeditor import CKEditor, CKEditorField
from wtforms import StringField, SubmitField, SelectField, FileField, BooleanField, ColorField, DateTimeField
from wtforms.widgets import TextArea
from flask_wtf import FlaskForm
from suds.client import Client
from werkzeug.utils import secure_filename
from flask_wtf.file import FileField, FileRequired, FileAllowed
import datetime, os
from wtforms.validators import DataRequired

from modules.sql import SQL
from modules.log import LOG
from modules.ConfigReader import Config
from modules.Captcha import Captcha
from modules.sms import SMS
from modules.password import Password, recovery_codes
from modules.strings import MSGList, Forms, Console, SOAPCS
from modules.soap import SOAPC
from modules.character import CharacterFinder
from modules.Realmlist import RealmCheck, realmlists
from modules.RecruitFreind import RF
from modules.skill import SkillStructure
from modules.tools import key, GetDate, Check, IpFormatCheck, restart, email_check
from modules.translate import gtranslate
from modules.theme import ChangeCSS, GetColors

app = Flask(__name__, static_folder='../static', template_folder='../templates')
ckeditor = CKEditor()
ckeditor.init_app(app)

if bool(Config.read()['core']['debug']) == True:
    app.secret_key = "123456"
else:
    app.secret_key = key()

if Config.read()['core']['setup'] == "disable":
    accounts = SQL.ReadAccounts()
    storeitems = SQL.StoreItems()
    redeemcodes = SQL.ReadRedeemCode()
    navlinks, navigation = SQL.ReadLinks()
    statics, blogs, homewidth, cover = SQL.ReadArtciles()
    versions = SQL.ReadVersions()
    language = SQL.ReadLanguage()
    bugs = SQL.ReadBugs()
else:
    versions = []
    LOG.debug(Console.Setup.value)

users = {}
items = ["Item", "Reputation", "Mount", "Gold", "Service", "Proffesions"]
BugKind = ['Choose...', 'Spell', 'Boss', 'Quest', 'Item']
BlogKindList = ['Home', 'Static', 'Blog']
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'static\\img\\content')

class AdminForm(FlaskForm):
    # article blog
    title = StringField('Title')
    body = CKEditorField('Body')
    submit = SubmitField('Submit')
    # send sms to everyone
    sendtext = SubmitField(label=Forms.Send.value, render_kw={"class": "btn"})
    text_message = StringField(render_kw={"class": "admintextbox"}, widget=TextArea())
    # admin post article
    title = StringField(render_kw={"class": "admintextbox", "placeholder": Forms.TitlePost.value})
    detail = StringField(widget=TextArea(), render_kw={"class": "admintextbox", "placeholder": Forms.DetailPost.value})
    position = SelectField(choices=["HomeWidth", "article"])
    post = SubmitField(label=Forms.Post.value, render_kw={"class": "btn"})
    ArticleImage = FileField(render_kw={"class": "file"}, validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    # admin add item in Store
    ItemTitle = StringField(render_kw={"class": "admintextbox", "placeholder": Forms.ItemStore.value})
    ItemDetail = StringField(widget=TextArea(), render_kw={"class": "admindetail", "placeholder": Forms.DetailPost.value})
    ItemPrice = StringField(render_kw={"class": "admintextbox", "placeholder": Forms.PriceItem.value})
    ItemSubmit = SubmitField(label=Forms.ItemSubmit.value, render_kw={"class": "adminbtn"})
    ItemKind = SelectField(render_kw={"class": "adminselect"}, choices=["Item", "Reputation", "Mount", "Gold", "Service", "Proffesions"])
    ItemImage = FileField(render_kw={"class": "file"}, validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    ItemID = StringField(render_kw={"class": "admintextbox", "placeholder": Forms.ItemID.value})
    Faction = SelectField(render_kw={"class": "adminselect"}, choices=["Horde", "Alliance", "All"])
    MaxSkill = StringField(render_kw={"class": "admintextbox", "placeholder": Forms.Skill.value})
    ItemVersion = SelectField(render_kw={"class": "adminselect"}, choices=versions)
    #core
    test = BooleanField(render_kw={"placeholder": "test"}, label="test", default=Check("debug"))
    save = SubmitField(label="save", render_kw={"class": "btn"})
    # theme
    MainColor = ColorField(Forms.Color.value, validators=[DataRequired()])
    MainColorHover = ColorField(Forms.Color.value, validators=[DataRequired()])
    Background = ColorField(Forms.Color.value, validators=[DataRequired()])
    SaveColor = SubmitField(Forms.SaveColor.value)
    # Report
    start =     event_datetime = DateTimeField('Event Date & Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()])

class LoginForm(FlaskForm):
    email = StringField(render_kw={"placeholder": Forms.email.value, "class": "textbox", "type": "text"})
    password = StringField(render_kw={"placeholder": Forms.password.value, "class": "textbox", "type": "password"})
    code = StringField(render_kw={"placeholder": Forms.captcha.value, "class": "captchatextbox", "autocomplete": "off", "inputmode": "numeric", "maxlength": "4"})
    reloadcode = SubmitField(render_kw={"class": "reloadcap"})
    login = SubmitField(label=Forms.login.value, render_kw={"class": "btn"})

class RegisterForm(FlaskForm):
    reloadcode = SubmitField(render_kw={"class": "reloadcap"})
    code = StringField(render_kw={"placeholder": Forms.captcha.value, "class": "captchatextbox", "autocomplete": "off", "inputmode": "numeric", "maxlength": "4"})
    firstname = StringField(render_kw={"placeholder": f"{Forms.firstname.value}", "class": "textbox", "type": "text"})
    lastname = StringField(render_kw={"placeholder": f"{Forms.lastname.value}", "class": "textbox", "type": "text"})
    email = StringField(render_kw={"placeholder": f"{Forms.email.value}", "class": "textbox", "type": "text"})
    phonenumber = StringField(render_kw={"placeholder": f"{Forms.phonenumber.value}", "class": "textbox", "type": "text"})
    username = StringField(render_kw={"placeholder": f"{Forms.username.value}", "class": "textbox", "type": "text"})
    password = StringField(render_kw={"placeholder": f"{Forms.password.value}", "class": "textbox", "type": "password"})
    repassword = StringField(render_kw={"placeholder": f"{Forms.repassword.value}", "class": "textbox", "type": "password"})
    register = SubmitField(label=Forms.register.value, render_kw={"class": "btn"})

class ChangePasswordForm(FlaskForm):
    oldpassword = StringField(render_kw={"placeholder": f"{Forms.oldpassword.value}", "class": "textbox", "type": 'password'})
    newpassword = StringField(render_kw={"placeholder": f"{Forms.newpassword.value}", "class": "textbox", "type": 'password'})
    renewpassword = StringField(render_kw={"placeholder": f"{Forms.renewpassword.value}", "class": "textbox", "type": 'password'})
    changepassword = SubmitField(label=Forms.changepassword.value, render_kw={"class": "btn"})

class RecoveryForm(FlaskForm):
    code = StringField(render_kw={"placeholder": Forms.EnterCode.value, "class": "textbox", "type": "text", "autocomplete": "off", "inputmode": "numeric", "maxlength": "5"})
    submit = SubmitField(label=Forms.Submit.value, render_kw={"class": "btn"})

class SendCodeForm(FlaskForm):
    email = StringField(render_kw={"placeholder": Forms.email.value, "class": "textbox", "type": "text"})
    phonenumber = StringField(render_kw={"placeholder": Forms.EnterPhoneNumber.value, "class": "textbox", "type": "text"})
    submit = SubmitField(label=Forms.SendCode.value, render_kw={"class": "btn"})

class UserPanelForms(FlaskForm):
    # Change password section
    oldpassword = StringField(render_kw={"placeholder": f"{Forms.oldpassword.value}", "class": "textbox", "type": 'password'})
    newpassword = StringField(render_kw={"placeholder": f"{Forms.newpassword.value}", "class": "textbox", "type": 'password'})
    renewpassword = StringField(render_kw={"placeholder": f"{Forms.renewpassword.value}", "class": "textbox", "type": 'password'})
    changepassword = SubmitField(label=Forms.changepassword.value, render_kw={"class": "btn"})
    # Redeem code section
    redeemcode = SubmitField(label=Forms.redeemcode.value, render_kw={"class": "btn"})
    code = StringField(render_kw={"placeholder": f"{Forms.redeemcodecode.value}", "class": "textbox", "type": "text"})
    # Freind code
    createcode = SubmitField(label=Forms.createcode.value, render_kw={"class": "btn"})
    friendcode = StringField(render_kw={"placeholder": f"{Forms.frindcode.value}", "class": "textbox", "type": "text"})
    # Token
    buytoken = SubmitField(label=Forms.buytoken.value, render_kw={"class": "btn"})
    token = StringField(render_kw={"dir": "ltr", "class": "range-input", "type": "range", "value": "25", "min": "5", "max": "200", "Step": "5", "oninput": "rangeValue.innerText = this.value"})
    # invite Friend
    invitefriendcode = StringField(render_kw={"placeholder": f"{Forms.InvitedFriendCode.value}", "class": "textbox", "readonly": "readonly"})
    invitefriendgen = SubmitField(render_kw={"class": "btn"})
    # admin add item in Store
    ItemTitle = StringField(render_kw={"class": "admintextbox", "placeholder": Forms.ItemStore.value})
    ItemDetail = StringField(widget=TextArea(), render_kw={"class": "admindetail", "placeholder": Forms.DetailPost.value})
    ItemPrice = StringField(render_kw={"class": "admintextbox", "placeholder": Forms.PriceItem.value})
    ItemKind = SelectField(render_kw={"class": "adminselect"}, choices=items)
    file = FileField(render_kw={"class": "file"}, validators=[FileRequired(), FileAllowed(ALLOWED_EXTENSIONS, 'Images only!')])
    ItemID = StringField(render_kw={"class": "admintextbox", "placeholder": Forms.ItemID.value})
    ItemVersion = SelectField(render_kw={"class": "adminselect"}, choices=versions)
    
    ItemSubmit = SubmitField(label=Forms.ItemSubmit.value, render_kw={"class": "adminbtn"})
    # admin post article
    title = StringField(render_kw={"class": "admintextbox", "placeholder": Forms.TitlePost.value})
    detail = StringField(widget=TextArea(), render_kw={"class": "admintextbox", "placeholder": Forms.DetailPost.value})
    position = SelectField(choices=["HomeWidth", "article"])
    post = SubmitField(label=Forms.Post.value, render_kw={"class": "btn"})
    articlefile = FileField(render_kw={"class": "file"}, validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])

class SelectRealmForm(FlaskForm):
    select = SelectField(render_kw={"style": "margin-top: 30px"})
    submit = SubmitField(label=Forms.Choose.value, render_kw={"class": "btn"})

class StoreForm(FlaskForm):
    select = SelectField()
    submit = SubmitField(label=Forms.Buy.value, render_kw={"class": "btn"})

class ReportBug(FlaskForm):
    kindselect = SelectField(choices=BugKind)
    detail = (StringField(render_kw={"class": "textbox", "placeholder": Forms.DetailBug.value}))
    submit = SubmitField(render_kw={"class": "btnbug"}, label=Forms.PostBug.value)

class forum(FlaskForm):
    newtopic = ""

class SetupForm(FlaskForm):
    # CMS CORE SERVER
    CMSServerName = StringField(render_kw={"placeholder": Forms.ServerName.value})
    CMSServerIP = StringField(render_kw={"placeholder": Forms.ServerIP.value})
    CMSPort = StringField(render_kw={"placeholder": Forms.CMSPort.value})
    #CMS SQL
    SQLServerIP = StringField(render_kw={"placeholder": Forms.ServerIP.value})
    SQLServerPORT = StringField(render_kw={"placeholder": Forms.SQLServerPORT.value})
    SQLUsername = StringField(render_kw={"placeholder": Forms.SQLUsername.value})
    SQLPaswword = StringField(render_kw={"placeholder": Forms.SQLPassword.value})
    # CORE SQL
    CoreSQLServerIP = StringField(render_kw={"placeholder": Forms.CoreSQLServerIP.value})
    CoreSQLServerPORT = StringField(render_kw={"placeholder": Forms.CoreSQLServerPORT.value})
    CoreSQLUsername = StringField(render_kw={"placeholder": Forms.CoreSQLUsername.value})
    CoreSQLPaswword = StringField(render_kw={"placeholder": Forms.CoreSQLPaswword.value})
    # SOAP
    soapusername = StringField(render_kw={"placeholder": Forms.CoreSQLPaswword.value})
    soappassword = StringField(render_kw={"placeholder": Forms.CoreSQLPaswword.value})
    # Admin
    adminusername = StringField(render_kw={"placeholder": Forms.CoreSQLPaswword.value})
    adminpassword = StringField(render_kw={"placeholder": Forms.CoreSQLPaswword.value})
    adminrepassword = StringField(render_kw={"placeholder": Forms.CoreSQLPaswword.value})
    Submit = SubmitField(label=Forms.Submit.value)

class Comment(FlaskForm):
    text = StringField(render_kw={"placeholder": Forms.Comments.value, "class": "textbox"})
    submit = SubmitField(label=Forms.Submit.value, render_kw={"class": "btn"})

def FlaskpApp():
    # admin page
    @app.route("/admin",methods=['POST', 'GET'])
    def admin():
        form = AdminForm()
        if "email" in session:
            if session['rank'] == 3:
                if form.sendtext.data == True:
                    msg = form.text_message.data
                    SMS.STA(msg)
                if form.post.data  == True:
                    file_data = form.file.data
                    file_name = secure_filename(file_data.filename)
                    file_data.save(f'{app.static_folder}\\img\\content\\' + file_name)
                # Submit Item Store
                if form.ItemSubmit.data == True:
                    if form.ItemTitle.data == "" or form.ItemPrice.data == "" or form.ItemDetail.data == "" or form.ItemID.data == "":
                        flash(MSGList.EmptyFields.value)
                    else:
                        file_data = form.ItemImage.data
                        file_name = secure_filename(file_data.filename)
                        file_data.save(f'{app.static_folder}\\img\\store\\' + file_name)
                        SQL.InsertItem(file_name, form.ItemPrice.data, form.ItemDetail.data, form.ItemTitle.data, form.ItemKind.data.lower(), form.Faction.data, form.ItemVersion.data, form.ItemID.data, form.MaxSkill.data)
                        flash(MSGList.ItemSuccess.value)
                if form.save.data == True:
                    tt = form.test.data
                    Config.write("economy", 'status', tt)
                if form.SaveColor.data == True:
                    MainColor = form.MainColor.data
                    MainColorHover = form.MainColorHover.data
                    Background = form.Background.data
                    ChangeCSS(6, MainColor)
                    ChangeCSS(7, MainColorHover)
                    ChangeCSS(9, Background)
                    LOG.debug(Console.Theme.value.format(username=session['username']))
                else:
                    form.MainColor.data = GetColors(6)
                    form.MainColorHover.data = GetColors(7)
                    form.Background.data = GetColors(9)
                return render_template('admin.html', form=form, history=SQL.GetBuyHistory(session['email'], session['rank']))
            else:
                return redirect(url_for('home'))
        else:
            return redirect(url_for('home'))
        
    @app.context_processor
    def inject_user():
        return dict(navlinks=navlinks, navigation=navigation, language=language)
    
    #home page and defualt page
    @app.route("/", methods=['GET', 'POST'])
    @app.route('/home', methods=['GET', 'POST'])
    def home():
        if Config.read()['core']['maintence'] == "on":
            if session['rank'] < 3:
                return render_template('maintence.html')
            else:
                return render_template('home.html',  articles=blogs, homewidth=homewidth, cover=cover)
        else:
            return render_template('home.html',  articles=blogs, homewidth=homewidth, cover=cover)

    # static pages
    @app.route("/static/<staticname>", methods=['GET'])
    def staticpage(staticname):
        if staticname not in statics:
            return render_template('message.html', titlemsg=MSGList.PageNotFoundTitle.value, detailmsg=MSGList.PageNotFoundDetail.value, image="blueprint/404")
        else:
            return render_template('static.html', article=statics[staticname])

    # blog page
    @app.route("/blog",methods=['POST', 'GET'])
    def blog():
        return render_template('blog.html', blogs=blogs)

    # blogpost
    @app.route("/blogpost/<blogpostname>", methods=['POST', 'GET'])
    def blogpost(blogpostname):
        form = Comment()
        if form.submit.data == True:
            print(form.text.data)
        if blogpostname not in blogs:
            return render_template('message.html', titlemsg=MSGList.PageNotFoundTitle.value, detailmsg=MSGList.PageNotFoundDetail.value, image="blueprint/404")
        else:
            return render_template('blogpost.html', article=blogs[blogpostname], form=form)
    # login page
    @app.route("/login", methods=['POST', 'GET'])
    def login():
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            session["registerip"] = request.environ['REMOTE_ADDR']
            Captcha.GenCaptcha(session["registerip"])
        else:
            session["registerip"] = request.environ['HTTP_X_FORWARDED_FOR']
            Captcha.GenCaptcha(session["registerip"])
        form = LoginForm()
        if form.validate_on_submit():
            if form.reloadcode.data == True:
                Captcha.RegenCaptcha(session["registerip"])
            if form.login.data == True:
                email = form.email.data
                password = form.password.data
                CaptchaCode = form.code.data
                if email == "" or password == "" or CaptchaCode == "":
                    flash(MSGList.EmptyFields.value, "alert-error")
                else:
                    if Captcha.CompareCaptcha(CaptchaCode, session["registerip"]) == True:
                        if email_check(email) == True:
                            password = Password.Generate(email, password)
                            if email not in accounts:
                                flash(MSGList.WrongPasswordOrEmail.value, "alert-error")
                                Captcha.GenImage(session["registerip"])
                            else:
                                account = accounts[email]
                                if not password == account["password"]:
                                    flash(MSGList.WrongPasswordOrEmail.value, "alert-error")
                                    Captcha.GenCaptcha(session["registerip"])
                                else:
                                    session["email"] = account['email']
                                    session['firstname'] = account['firstname']
                                    session['lastname'] = account['lastname']
                                    session['ip'] = session["registerip"]
                                    session['status'] = account['status']
                                    session['regdate'] = account['regdate']
                                    session['phonenumber'] = account['phonenumber']
                                    session['token'] = account['token']
                                    session['username'] = account['username']
                                    session['code'] = account['code']
                                    session['count'] = account['count']
                                    session['rank'] = account['rank']
                                    session['language'] = "English"
                                    LOG.debug(Console.LoginSuccess.value.format(email=session["email"], ip=session["registerip"]))
                                    return redirect(url_for('upanel'))
                        else:
                            flash(MSGList.WrongEmailFormat.value, "alert-error")
                            Captcha.RegenCaptcha(session["registerip"])
                    else:
                        flash(MSGList.WrongCode.value, "alert-error")
                        Captcha.RegenCaptcha(session["registerip"])
        else:
            if "email" in session:
                 return redirect(url_for('upanel'))
            else:
                return render_template('login.html', form=form)
        return render_template('login.html', form=form)

    #store page
    @app.route("/store", methods=['POST', 'GET'])
    def store():
        return render_template('store.html', storeitems=storeitems)
    
    # Select Realm page
    @app.route("/select-realm/<route>", methods=['POST', 'GET'])
    def select_realm(route):
        form = SelectRealmForm()
        if "email" in session:
            form.select.choices = [realm for realm in realmlists]
            session["getitemid"] = int(''.join(filter(str.isdigit, route)))
            if form.validate_on_submit():
                if form.submit.data == True:
                    session['version'] = form.select.data
                    session['realmip'] = realmlists[session['version']]['localip']
                    return redirect(url_for("store_item", id=route))
            return render_template('select-realm.html', form=form)
        else:
            return redirect(url_for('login'))

    # store item detail
    @app.route("/store_item/<id>", methods=['POST', 'GET'])
    def store_item(id):
        form = StoreForm()
        if "email" in session:
            session["getitemid"] = int(''.join(filter(str.isdigit, id)))
            try: # if item not in databse
                session["itemid"] = storeitems[session["getitemid"]]['itemid']
                session['itemname'] = storeitems[session["getitemid"]]['title']
                session['itemdetail'] = storeitems[session["getitemid"]]['detail']
                session['itemimage'] = storeitems[session["getitemid"]]['image']
                session['itemtoken'] = storeitems[session["getitemid"]]['token']
                session['itemmode'] = storeitems[session["getitemid"]]['mode']
                session['service'] = storeitems[session["getitemid"]]['service']
                session['maxskill'] = storeitems[session["getitemid"]]['maxskill']
                if "all" not in storeitems[session["getitemid"]]['version']:
                    session['version'] = storeitems[session["getitemid"]]['version']
                if form.submit.data == True:
                    charactername = form.select.data
                    if charactername == "":
                        flash(MSGList.CharacterNotSelected.value, "alert-error")
                    else:
                        if int(accounts[session["email"]]['token']) >= int(session['itemtoken']):
                            if session['service'] == "mount":
                                session['msg'] = SOAPC.Command(realmlists[session['version'].replace(".", "")]['localip'], SOAPCS.Item.value.format(character=charactername, itemid=session['itemid']))
                            elif session['service'] == "gold":
                                session['msg'] = SOAPC.Command(realmlists[session['version'].replace(".", "")]['localip'], SOAPCS.Gold.value.format(character=charactername, gold=session['itemid']))
                            elif session['service'] == "faction":
                                session['msg'] = SOAPC.Command(session['realmip'], SOAPCS.ServiceFaction.value.format(character=charactername))
                            elif session['service'] == "race":
                                session['msg'] = SOAPC.Command(session['realmip'], SOAPCS.ServiceRace.value.format(character=charactername))
                            elif session['service'] == "level":
                                session['msg'] = SOAPC.Command(session['realmip'], SOAPCS.CharacterLevel.value.format(character=charactername))
                            elif session['service'] == "work":
                                session['msg'] = SkillStructure.SetProfessionSkill(charactername, session['itemid'], realmlists[session['version']]['maxskill'], session['realmip'], realmlists[session['version']]['maxlevel'])
                            elif session['service'] == "rep":
                                session['msg'] = SkillStructure.SetReputationSkill(realmlists[session['version'].replace(".", "")]['localip'], charactername, realmlists[session['version'].replace(".","")]['maxlevel'], session['itemid'], session['maxskill'])
                            if session['msg'] == True:
                                session['token'] = int(accounts[session["email"]]['token']) - int(session['itemtoken'])
                                SQL.token(session['email'], session['token'])
                                SQL.InsertHistory(session['email'], session['itemname'], GetDate(), session['username'], charactername)
                                flash(MSGList.ItemSuccess.value, "alert-success")
                            else:
                                flash(SOAPCS.SOAPCE.value, "alert-error")
                        else:
                            flash(MSGList.NotEnoughToken.value, "alert-error")
            except IndexError:
                return render_template('message.html', titlemsg=MSGList.PageNotFoundTitle.value, detailmsg=MSGList.PageNotFoundDetail.value, image="blueprint/404"), 404
            if session['service'] == "mount" or "gold":
                session['realmip'] = realmlists[session['version'].replace(".", "")]['localip']
                form.select.choices = CharacterFinder.FindCharactersNames(session["email"], session['username'], session['realmip'], session['version'])
                if not form.select.choices:
                    try:
                        form.select.choices += [MSGList.Empty.value]
                    except:
                        flash(MSGList.WarningDetail.value, "alert-success")
                return render_template('store_item.html', storeitems=storeitems, form=form)
            else:
                form.select.choices = CharacterFinder.FindCharactersNames(session["email"], session['username'], session['realmip'], session['version'])
                return render_template('store_item.html', storeitems=storeitems, form=form)
        else:
            return redirect(url_for('login'))

    # user panel
    @app.route("/upanel", methods=['POST', 'GET'])
    def upanel():
        form = UserPanelForms()
        if form.validate_on_submit():
            # redeem code section
            if form.redeemcode.data == True:
                redeemcode = form.code.data
                if redeemcode == "":
                    flash(MSGList.EmptyRedeemCode.value, "alert-error")
                else:
                    if redeemcode not in redeemcodes:
                        flash(MSGList.WrongCode.value, "alert-error")
                    else:
                        if redeemcodes[redeemcode]["usedto"] == "":
                            redeemcodes[redeemcode].update({'usedto': session['email']})
                            SQL.RedeemCode(session['email'], redeemcode)
                            SQL.token(session['email'], str(int(session['token']) + 100))
                            session['token'] = accounts[session['email']]['token']
                            flash(MSGList.RedeemcodeUse.value, "alert-success")
                        else:
                            flash(MSGList.ThisCodeIsUsed.value,"alert-error")
            # change password section
            if form.changepassword.data == True:
                oldpassword = form.oldpassword.data
                newpassword = form.newpassword.data
                renewpassowrd = form.renewpassword.data
                if oldpassword == "" or newpassword == "" or renewpassowrd == "":
                    flash(MSGList.EmptyFields.value, "alert-error")
                else:
                    if Password.Generate(session['email'], oldpassword) == accounts[session['email']]['password']:
                        if newpassword == renewpassowrd:
                            SQL.ChangePassword(session['email'], Password.Generate(session['email'], newpassword))
                            for realm in realmlists:
                                if int(realm) > 335:
                                    SOAPC.Command(realmlists[realm]['localip'], SOAPCS.BTChangePAssword.value.format(email=session['email'], newpassword=newpassword))
                                else:
                                    SOAPC.Command(realmlists[realm]['localip'], SOAPCS.UsernameChangePassword.value.format(username=session['username'], newpassword=newpassword))
                            return redirect(url_for('logout'))
                        else:
                            flash(MSGList.WrongPassword.value, "alert-error")
                    else:
                        flash(MSGList.ComparePassword.value, "alert-error")
            # Friend code
            if form.createcode.data == True:
                res = RF.GenerateCode(session['email'], accounts)
                if type(res) == int:
                    session['code'] = res
                else:
                    pass
            # token section
            if form.buytoken.data == True:
                session['amount'] = int(form.token.data) * 1000
                session['tokenbuy'] = form.token.data
                return redirect(url_for('send_request'))
        # check email for session
        if "email" in session:
            return render_template('upanel.html', history=SQL.GetBuyHistory(session['email'], rank=str(session['rank'])), form=form)
        else:
            return redirect(url_for('login'))

    # recovery my password
    @app.route("/recovery", methods=['POST', 'GET'])
    def recovery():
        form = SendCodeForm()
        if form.validate_on_submit():
            if form.submit.data == True:
                email = form.email.data
                phonenumber = form.phonenumber.data
                if email == "" or phonenumber == "":
                    flash(MSGList.EmptyFields.value, "alert-error")
                else:
                    if email_check(email) == True:
                        if email not in accounts:
                            flash(MSGList.EmailNotExist.value, "alert-error")
                        else:
                            if f"0{accounts[email]['phonenumber']}" == str(phonenumber):
                                if SMS.PhoneNumberCheck(phonenumber) == True:
                                    if Password.RecPass(phonenumber) == True:
                                        session["phonenumberrecovery"] = phonenumber
                                        session["emailrecovery"] = email
                                        accounts[email]['recover'] = "1"
                                        return redirect(url_for('recovery_code'))
                                    else:
                                        flash(MSGList.TrySendSMS.value, "alert-error")
                                else:
                                    flash(MSGList.WrongPhoneNumberFromat.value, "alert-error")
                            else:
                                flash(MSGList.WrongPhoneNumberOrEmail.value, "alert-error")
                    else:
                        flash(Forms.WrongEmailFormat.value,  "alert-error")
        if "email" in session:
            return render_template('upanel.html')
        else:
            return render_template('recovery.html', form=form)

    # paswword recovery code confrim
    @app.route("/recovery-code", methods=['POST', 'GET'])
    def recovery_code():
        #print(recovery_codes[session["phonenumberrecovery"]]['code'])
        form = RecoveryForm()
        if form.submit.data == True:
            code = form.code.data
            if code == recovery_codes[session["phonenumberrecovery"]]['code']:
                session.pop("phonenumberrecovery", None)
                return redirect(url_for('change_password'))
            else:
                flash(MSGList.WrongCode.value, "alert-error")
        if accounts[session["emailrecovery"]]['recover'] == "1":
            return render_template('recovery-code.html', form=form)
        else:
            return redirect(url_for('home'))

    # Chnage password
    @app.route("/change-password", methods=['POST', 'GET'])
    def change_password():
        form = ChangePasswordForm()
        if form.changepassword.data == True:
            new_password = form.newpassword.data
            new_cpassword = form.renewpassword.data
            if new_password == "" or new_cpassword == "":
                flash(MSGList.EmptyFields.value)
            else:
                if not new_password == new_cpassword:
                    flash(MSGList.ComparePassword.value)
                else:
                    newpassword = Password.Generate(session["emailrecovery"], new_password)
                    SQL.ChangePassword(session["emailrecovery"], newpassword)
                    for realm in realmlists:
                        if int(realm) > 335:
                            SOAPC.Command(realmlists[realm]['localip'], SOAPCS.BTChangePAssword.value.format(email=session['emailrecovery'], newpassword=newpassword))
                        else:
                            SOAPC.Command(realmlists[realm]['localip'], SOAPCS.UsernameChangePassword.value.format(username=accounts[session['emailrecovery']]['username'], newpassword=newpassword))
                    accounts[session["emailrecovery"]]['recover'] = "0"
                    session.pop("emailrecovery", None)
                    session.pop("phonenumberrecovery", None)
                    return render_template('message.html', titlemsg=str(MSGList.ChangePasswordTitle.value), detailmsg=MSGList.ChangePasswordChangedDetail.value, image="ChangePass")
        try:
            if accounts[session["emailrecovery"]]['recover'] == "1":
                return render_template('ChangePassword.html', form=form)
        except:
            return redirect(url_for('home'))

    # user realmlist
    @app.route("/realm",methods=['POST', 'GET'])
    def realm():
        realmlist = RealmCheck()
        return render_template('realm.html', realmlist=realmlist)

    # register page
    @app.route("/register",methods=['POST', 'GET'])
    def register(): 
        if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
            session["registerip"] = request.environ['REMOTE_ADDR']
            Captcha.GenCaptcha(session["registerip"])
        else:
            session["registerip"] = request.environ['HTTP_X_FORWARDED_FOR']
            Captcha.GenCaptcha(session["registerip"])
        form = RegisterForm()
        if form.validate_on_submit():
            if form.reloadcode.data == True:
                Captcha.RegenCaptcha(session["registerip"])
            elif form.register.data == True:
                firstname = form.firstname.data
                lastname = form.lastname.data
                email = form.email.data
                phonenumber = form.phonenumber.data
                username = form.username.data
                password = form.password.data
                repassword = form.repassword.data
                CaptchaCode = form.code.data
                if firstname == "" or lastname == "" or email == "" or username == "" or password == "" or phonenumber == "" or repassword == "":
                    flash(MSGList.EmptyFields.value, "alert-error")
                else:
                    if Password.PasswordEqual(password, repassword) == True:
                        if email_check(email) == True:
                            if email not in accounts:
                                if SQL.CheckUsername(username) == False:
                                    if Captcha.CompareCaptcha(CaptchaCode, session["registerip"]) == True:
                                        PasswordGened = Password.Generate(email, password)
                                        try:
                                            SQL.Register(firstname, lastname, email, PasswordGened, GetDate(), phonenumber, username)
                                            for realm in realmlists:
                                                if int(realm) > 335:
                                                    SOAPC.Command(realmlists[realm]['localip'], SOAPCS.BTAccountCreate.value.format(email=email, password=password))
                                                else:
                                                    SOAPC.Command(realmlists[realm]['localip'], SOAPCS.AccountCreate.value.format(username=username, password=password))
                                            return render_template('message.html', titlemsg=str(MSGList.RegisterSuccessTitle.value), detailmsg=MSGList.RegisterSuccessDetail.value, image="reg-success")
                                        except:
                                            LOG.error(Console.RegisterFailed.value, "alert-error")
                                    else:
                                        Captcha.RegenCaptcha(session["registerip"])
                                        flash(MSGList.WrongCode.value, "alert-error")
                                else:
                                    flash(MSGList.UsernameExist.value, "alert-error")
                            else:
                                flash(MSGList.EmailInUsed.value.format(email=email), "alert-error")
                        else:
                            flash(MSGList.WrongEmailFormat.value, "alert-error")
                    else:
                        flash(MSGList.ComparePassword.value, "alert-error")
            else:
                if "email" in session:
                    return redirect(url_for('upanel'))
        return render_template('register.html',form=form)

    # forum page
    @app.route("/forum", methods=['POST', 'GET'])
    def forum():
        return render_template('forum.html')

    @app.route('/request/')
    def send_request():
        client = Client(Config.read()['pay']['ZarinpalGateway'])
        result = client.service.PaymentRequest(Config.read()['pay']['MerchantID'], session['amount'], u'', session['email'], session['phonenumber'], str(url_for('verify', _external=True)))
        if result.Status == 100:
            return redirect('https://www.zarinpal.com/pg/StartPay/' + result.Authority)
        else:
            return 'Error'

    @app.route('/verify/', methods=['GET', 'POST'])
    def verify():
        if "email" in session:
            client = Client(Config.read()['pay']['ZarinpalGateway'])
            if request.args.get('Status') == 'OK':
                result = client.service.PaymentVerification(Config.read()['pay']['MerchantID'], request.args['Authority'], session['amount'])
                if result.Status == 100:
                    SQL.token(session['email'], str(int(session['token']) + int(session['tokenbuy'])))
                    session['token'] = accounts[session['email']]['token']
                    SQL.InsertHistory(session['email'], session['tokenbuy'], GetDate(), session['username'], Forms.Token.value)
                    return render_template('message.html', titlemsg=str(result.RefID), detailmsg=MSGList.SuccessMSG.value, image="transaction/success")
                elif result.Status == 101:
                    return 'Transaction submitted : ' + str(result.Status)
                else:
                    # Failed
                    return render_template('message.html', titlemsg=MSGList.Warning.value, detailmsg=MSGList.FailMSG.value, image="transaction/failed")
            else:
                # Canceled by user
                return render_template('message.html', titlemsg=MSGList.Warning.value, detailmsg=MSGList.CancelMSG.value, image="transaction/canceled")
        else:
            return redirect(url_for('home'))

   # Bugreport page
    @app.route("/bugreport",methods=['POST', 'GET'])
    def bugreport():
        form = ReportBug()
        if form.validate_on_submit():
            if "email" in session:
                kindselect = form.kindselect.data
                detail = form.detail.data
                if kindselect == "Choose...":
                    flash(MSGList.BugNotSelected.value)
                else:
                    SQL.InsertBug(kindselect, detail, "Checkin", session['username'], GetDate(), 0)
            else:
                return redirect(url_for('login'))
        return render_template('bugreport.html', form=form, bugs=bugs)

    # Site maps
    @app.route('/sitemap.xml', methods=['GET'])
    def sitemap():
        sitemap_xml = render_template(url_for('sitemap'))
        response = make_response(sitemap_xml)
        response.headers["Content-Type"] = "application/xml"
        return response

    #session time
    @app.before_request
    def make_session_permanent():
        session.permanent = True
        app.permanent_session_lifetime = datetime.timedelta(minutes=60)

    # Blueprints
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('message.html', titlemsg=MSGList.PageNotFoundTitle.value, detailmsg=MSGList.PageNotFoundDetail.value, image="blueprint/404"), 404
    app.register_error_handler(404, page_not_found)

    @app.errorhandler(403)
    def page_not_found(e):
        return render_template('message.html', titlemsg=MSGList.PageNotFoundTitle.value, detailmsg=MSGList.PageNotFoundDetail.value, image="blueprint/403"), 403
    app.register_error_handler(403, page_not_found)

    @app.errorhandler(500)
    def page_not_found(e):
        return render_template('message.html', titlemsg=MSGList.Warningtitle.value, detailmsg=MSGList.WarningDetail.value, image="blueprint/500"), 500
    app.register_error_handler(500, page_not_found)

    @app.before_request
    def keep_session_alive():
        session.modified = True

    # user logout
    @app.route("/logout")
    def logout():
        try:
            LOG.debug(Console.Logout.value.format(email=session["email"], ip=session['registerip']))
            session.clear()
            return redirect(url_for('login'))
        except:
             LOG.error(Console.ErrorSocket.value)
    
def FlaskSetup():
    @app.route("/", methods=['GET', 'POST'])
    @app.route('/setup', methods=['GET', 'POST'])
    def setup():
        form = SetupForm()
        if form.validate_on_submit():
            cmsservername = form.CMSServerName.data
            cmsserverip = form.CMSServerIP.data
            cmsport = form.CMSPort.data

            sqlip = form.SQLServerIP.data
            sqlport = form.SQLServerPORT.data
            sqlusername = form.SQLUsername.data
            sqlpassword = form.SQLPaswword.data

            coresqlip = form.CoreSQLServerIP.data
            coresqlport = form.CoreSQLServerPORT.data
            coresqlusername = form.CoreSQLUsername.data
            coresqlpassword = form.CoreSQLPaswword.data
            if cmsservername or cmsserverip or cmsport or sqlip or sqlport or sqlusername or sqlpassword or coresqlip or coresqlport or coresqlusername or coresqlpassword == "":
                flash(MSGList.EmptyFields.value, "alert-warning")
            else:
                ips = [cmsserverip, sqlip, coresqlip]
                for ip in ips:
                    if IpFormatCheck(ip) == True:
                        Config.write('core', 'servername', cmsservername)
                        Config.write('core', 'ip', cmsserverip)
                        Config.write('core', 'port', cmsport)
                        Config.write('core', 'setup', 'disable')
                        restart()
                    else:
                        flash(MSGList.WrongIPAddressFormat.value, "alert-error")
        return render_template('setup.html', form=form)
    
    @app.errorhandler(404)
    def page_not_found(e):
        return redirect(url_for('setup'))
    app.register_error_handler(404, page_not_found)

    @app.errorhandler(403)
    def page_not_found(e):
        return redirect(url_for('setup'))
    app.register_error_handler(403, page_not_found)

    @app.errorhandler(500)
    def page_not_found(e):
        return redirect(url_for('setup'))
    app.register_error_handler(500, page_not_found)
import os
import sys
import subprocess
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from data_base import get_tiggers, get_all_chat, add_tiggers, get_tigger, update_tigger, delete_tigger
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


script_dir = os.path.dirname(os.path.realpath(__file__))
chat_control_script = os.path.join(script_dir, "chat_control.py")

SECRET_KEY = '3f59-UE49N45UF4530VKNSALeuof480894JLroopir'
LOGIN = os.getenv('LOGIN')
PASSWORD =  os.getenv('PASSWORD')
PREFIX = os.getenv('PREFIX')
if PREFIX is None:
    PREFIX = ''

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
login_manager = LoginManager(app)
login_manager.login_view = 'login'

csrf = CSRFProtect(app)

class User(UserMixin):
    def __init__(self, user_id, username, password):
        self.id = user_id
        self.username = username
        self.password = password

# Replace this with your actual user authentication logic
def authenticate_user(username, password):
    # Example: Check if the username and password are valid
    # Replace this with your actual authentication logic
    if username == LOGIN  and password == PASSWORD:
        return User(1, username, password)
    return None

@login_manager.user_loader
def load_user(user_id):
    # Replace this with your actual user loading logic
    # Example: Load user from your database
    return User(user_id, 'admin@mail.ru', 'password')

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route(f'{PREFIX}/static/<path:filename>')
def serve_static(filename):
    root_dir = os.path.dirname(os.getcwd())
    return send_from_directory(os.path.join(root_dir, 'static'), filename)



@app.route(f'{PREFIX}/')
@login_required
def start():
    chats = get_tiggers()

    return render_template('main.html', chats=chats, bot_user="Менеджер", PREFIX=PREFIX)


@app.route(f'{PREFIX}/editchat/<int:addchat_id>', methods=['GET', 'POST'])
@login_required
def editchat(addchat_id):
    print(addchat_id)
    cahats = get_all_chat()
   
    chat = get_tigger(cahats, id=addchat_id)
    if request.method == 'POST':
        print(request.form)
        sender_id = request.form['sender_id']
        trigger_words = request.form['trigger_words']
        recipient_id = request.form['recipient_id']
        exclude_words = request.form['exclude_words']
        prefix = request.form['prefix']
        if request.form.get('is_anonym') == 'yes':
            is_anonym = True
        else:
            is_anonym = False
        if request.form.get('not_duplicate') == 'yes':
            not_duplicate = True
        else:
            not_duplicate = False
        print(sender_id,  trigger_words, recipient_id)
        update_tigger(
            sender_id=sender_id,
            trigger_words=trigger_words,
            recipient_id=recipient_id,
            addchat_id=addchat_id,
            exclude_words=exclude_words,
            is_anonym=is_anonym,
            not_duplicate=not_duplicate,
            prefix=prefix
        )
        #chat.chat_name = request.form['name']
        #chat.keywords = request.form['keywords']
        
        return redirect(f'{PREFIX}/')
    
    return render_template(
        'editchat.html',
        chat=chat,
        bot_user="Менеджер",
        addchat_id =addchat_id,
        all_chat = cahats.all_chat,
        all_recipient = cahats.recipient,
        PREFIX=PREFIX
    )

@app.route(f'{PREFIX}/delete/<int:addchat_id>', methods=['GET','DELETE'])
@login_required
def deletetigger(addchat_id):
    delete_tigger(addchat_id=addchat_id)
        
    return redirect(f'{PREFIX}/')



@app.route(f'{PREFIX}/controlchat', methods=['GET'])
@login_required
def controlchat():
    subprocess.run([sys.executable, chat_control_script], check=True)
        
    return redirect(f'{PREFIX}/')
    


@app.route(f'{PREFIX}/addchat', methods=['GET', 'POST'])
@login_required
def addchat():
    cahats = get_all_chat()
    if request.method == 'POST':
        print(request.form)
        sender_id = request.form['sender_id']
        trigger_words = request.form['trigger_words']
        recipient_id = request.form['recipient_id']
        exclude_words = request.form['exclude_words']
        prefix = request.form['prefix']
        if request.form.get('is_anonym') == 'yes':
            is_anonym = True
        else:
            is_anonym = False
        if request.form.get('not_duplicate') == 'yes':
            not_duplicate = True
        else:
            not_duplicate = False
        print('is_anonym', is_anonym)
        add_tiggers(
            sender_id=sender_id,
            trigger_words=trigger_words,
            recipient_id=recipient_id,
            exclude_words=exclude_words,
            is_anonym=is_anonym,
            not_duplicate =not_duplicate,
            prefix =prefix
        )
        print(sender_id,  trigger_words, recipient_id)
        
        return redirect(f'{PREFIX}/')
    
    return render_template(
        'addchat.html',
        bot_user="Менеджер",
        all_chat = cahats.all_chat,
        all_recipient = cahats.recipient,
        PREFIX=PREFIX
    )


@app.route(f'{PREFIX}/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = authenticate_user(username, password)

        if user:
            login_user(user, remember=form.remember.data)
            return redirect(url_for('start'))
        else:
            return 'Неверное имя пользователя или пароль'

    return render_template('login.html', form=form, PREFIX=PREFIX)


@app.route(f'{PREFIX}/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
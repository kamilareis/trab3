# Aqui vai as rotas e links
import os

from flask import render_template, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename

from instagram.models import load_user, User, Posts
from instagram import app, database
from instagram.forms import FormLogin, FormCreateNewAccount, FormCreateNewPost
from instagram import bcrypt
from instagram import login_manager


@app.route('/', methods=['POST', 'GET'])
@app.route('/home', methods=['POST', 'GET'])
def homepage():
    formLogin = FormLogin()

    if formLogin.validate_on_submit():
        userToLogin = User.query.filter_by(email=formLogin.email.data).first()
        if userToLogin and bcrypt.check_password_hash(userToLogin.password, formLogin.password.data):
            login_user(userToLogin)
            return redirect(url_for('profile', user_id=userToLogin.id))

    return render_template("home.html", teto='HOME', form=formLogin)


@app.route('/profile/<user_id>', methods=['POST', 'GET'])
@login_required
def profile(user_id):
    if int(user_id) == int(current_user.id):
        # estou vendo meu perfil
        _formNewPost = FormCreateNewPost()

        if _formNewPost.validate_on_submit():
            # pegar o texto
            _post_text = _formNewPost.text.data

            # pegar a img
            _post_img = _formNewPost.photo.data
            _img_name = secure_filename(_post_img.filename)
            path = os.path.abspath(os.path.dirname(__file__))
            path2 = app.config['UPLOAD_FOLDER']
            _final_path = f'{path}/{path2}/{_img_name}'

            _post_img.save(_final_path)

            # criar um obj Post
            newPost = Posts(post_text=_post_text,
                            post_img=_img_name,
                            user_id=int(current_user.id)
                            )

            # salvar no banco
            database.session.add(newPost)
            database.session.commit()

        return render_template("profile.html", user=current_user, form=_formNewPost)
    else:
        # outro perfil"""
        _user = User.query.get(int(user_id))
        return render_template("profile.html", user=_user, form=False)


@app.route('/capaivara')
def capaivara():
    return render_template("capaivara.html")


@app.route('/teste')
def teste():
    return render_template("teste.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))


@app.route('/new', methods=['POST', 'GET'])
def create_account():
    formCreateAccount = FormCreateNewAccount()

    if formCreateAccount.validate_on_submit():
        password = formCreateAccount.password.data
        password_cr = bcrypt.generate_password_hash(password)
        # print(password)
        # print(password1)

        newUser = User(username=formCreateAccount.username.data,
                       email=formCreateAccount.email.data,
                       password=password_cr)

        database.session.add(newUser)
        database.session.commit()
        login_user(newUser, remember=True)
        return redirect(url_for('profile', user_id=newUser.id))

    return render_template("new.html", form=formCreateAccount)

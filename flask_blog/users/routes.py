from flask_login import login_user, current_user, logout_user, login_required
from flask import Blueprint, render_template, url_for, flash, redirect, request, current_app
from flask_blog import  db, bcrypt
from flask_blog.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from flask_blog.models import User, Post
from flask_blog.users.utils import save_picture, send_reset_email

users=Blueprint('users', __name__)


@users.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.hello_world'))
    form= RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! Please log in to continue', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.hello_world'))
    form= LoginForm()
    if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                flash('You have been logged in !', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.hello_world'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route("/logout")
def logout():
    logout_user()
    flash('You are Now Logged out!', 'danger')                     
    return redirect(url_for('main.hello_world'))

@users.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
       if form.picture.data:
            old_pic = current_user.image_file
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
            if old_pic != 'default.jpg':
                os.remove(os.path.join(current_app.root_path, 'static/profile_pics', old_pic))
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file = image_file, form=form)



@users.route("/reset_password", methods=['GET', 'POST'])
def password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.hello_world'))
    form = RequestResetForm()
    if form.validate_on_submit():
         user = User.query.filter_by(email=form.email.data).first()
         send_reset_email(user)
         flash('An email has been sent with instructions to reset your password.', 'info')
         return redirect(url_for('users.login'))
    return render_template('password_request.html', form=form, title='Reset Password')


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.hello_world'))
    
    user_check = User.verify_reset_token(token)
    if user_check is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.password_request'))
    form = ResetPasswordForm()    
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user_check.password =  hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('password_post.html', form=form, title='Reset Password')

@users.route("/user/<string:username>")
def user_post(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page = page, per_page=5, error_out=False)
    
    return render_template('user_post.html', user=user, posts=posts)

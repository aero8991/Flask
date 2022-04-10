from flask import request, render_template, Blueprint
from flask_blog.models import Post

main = Blueprint('main', __name__)


@main.route("/home")
@main.route("/")
def hello_world():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page = page, per_page=5, error_out=False)
    #posts = posts.order_by(ascending=False )
    return render_template('home.html', posts=posts)

@main.route("/about")
def about():
    return render_template('about.html', title='About')
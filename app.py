from auth import *
from helper import add_no_cache

# Register the API Blueprint
from api import api_bp
app.register_blueprint(api_bp, url_prefix='/api')



@app.route('/')
def home():
    keyword = request.args.get("search", "")
    page = request.args.get("page", 1, type=int)
    per_page = 4
    msg = None

    if keyword:
        blogs_query = Blog.query.join(Category).filter(
            or_(
                Blog.title.ilike(f"%{keyword}%"),
                Blog.body.ilike(f"%{keyword}%"),
                Category.titles.ilike(f"%{keyword}%")
            )
        )

        if blogs_query.count() == 0:
            msg = "There is no article with the keyword."
            blogs = Blog.query.filter_by(id=None).paginate(page=1)
        else:
            blogs = blogs_query.paginate(page=1, per_page=per_page)

    else:
        blogs = Blog.query.paginate(page=page, per_page=per_page, error_out=False)

    categories = Category.query.all()

    return render_template(
        "index.html",
        blogs=blogs,
        msg=msg,
        categories=categories
    )


@app.route('/detail/<slug>', methods=['GET', 'POST'])
def detail(slug):
    blog = Blog.query.filter_by(slug=slug).first_or_404()

    related_blogs = Blog.query.filter(
        Blog.category_id == blog.category_id,
        Blog.id != blog.id
    ).limit(4).all()

    comments = Comment.query.filter_by(blog_id=blog.id).all()

    form = CommentForm()

    if form.validate_on_submit():
        new_comment = Comment(
            body=form.body.data,
            user_id=current_user.id,
            blog_id=blog.id
        )
        db.session.add(new_comment)
        db.session.commit()
        flash("Comment added successfully!", "success")
        return redirect(url_for("detail", slug=blog.slug))

    return render_template(
        "detail.html",
        blog=blog,
        comments=comments,
        form=form,
        r_blogs=related_blogs
    )


@app.route('/create/article', methods=['GET', 'POST'])
@login_required
def create_article():
    categories = Category.query.all()
    
    form = CreateArticleForm()
    form.category_id.choices = [(c.id, c.titles) for c in categories]

    if form.validate_on_submit():
        slug = slugify(form.title.data)
        thumbnail_filename = "assets/blog.png"

        existing_article = Blog.query.filter_by(slug=slug).first()
        if existing_article:
            flash('An article with this title already exists. Please choose a different title.', 'danger')
            return render_template('create.html', form=form, categories=categories)

        if form.thumbnail.data:
            thumbnail = form.thumbnail.data
            filename = secure_filename(f"{slug}-{thumbnail.filename}")
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                thumbnail.save(upload_path)
                thumbnail_filename = f"uploads/{filename}"
            except Exception as e:
                print(f"File Upload Error: {str(e)}")
                flash('Error saving the thumbnail image.', 'danger')
        try:
            new_post = Blog(
                title=form.title.data,
                slug=slug,
                body=form.body.data,
                thumbnail=thumbnail_filename,
                user_id=current_user.id,
                category_id=form.category_id.data if form.category_id.data else None
            )

            db.session.add(new_post)
            db.session.commit()
            flash('Your article has been published successfully!', 'success')
            return redirect(url_for('home'))

        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred while publishing your article: {str(e)}', 'danger')

    return render_template('create.html', form=form, categories=categories)


@app.route('/article/delete/<slug>', methods=['POST'])
@login_required
def delete_article(slug):
    blog = Blog.query.filter_by(slug=slug, user_id=current_user.id).first_or_404()
    
    db.session.delete(blog)
    db.session.commit()
    flash("Article deleted successfully!", "danger")

    return redirect(url_for('profile'))


@app.route('/update/article/<string:slug>', methods=['GET', 'POST'])
@login_required
def update_article(slug):
    blog = Blog.query.filter_by(slug=slug).first_or_404()
    form = CreateArticleForm(obj=blog)
    form.category_id.choices = [(category.id, category.titles) for category in Category.query.all()]

    if request.method == 'POST' and form.validate_on_submit():
        try:
            form.populate_obj(blog)
            blog.slug = slugify(form.title.data)
            if form.thumbnail.data and hasattr(form.thumbnail.data, 'filename'):  
                file = form.thumbnail.data
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.static_folder, 'uploads', filename)
                file.save(file_path)
                blog.thumbnail = 'uploads/' + filename

            db.session.commit()
            flash('Article updated successfully!', 'success')
            return redirect(url_for('detail', slug=blog.slug))

        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating the article.', 'error')

    return render_template('create.html', form=form, blog=blog, update=True)



@app.route('/user/profile')
@login_required
def profile():
    user_blogs = Blog.query.filter_by(user_id=current_user.id).all()
    return render_template('profile.html', user=current_user, blogs=user_blogs)


@app.route('/update-profile', methods=['GET', 'POST'])
@login_required
def update_profile():
    user = current_user
    form = UpdateProfileForm(obj=user)

    if form.validate_on_submit():

        user.email = form.email.data
        user.username = form.username.data

        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile"))

    return render_template("update_profile.html", form=form)


@app.route('/add_comment/<int:blog_id>', methods=['POST'])
@login_required
def add_comment(blog_id):
    blog = Blog.query.get_or_404(blog_id)
    form = CommentForm()

    if form.validate_on_submit():
        new_comment = Comment(
            body=form.body.data,
            user_id=current_user.id,
            blog_id=blog.id,
        )
        db.session.add(new_comment)
        db.session.commit()
        flash("Comment added successfully!", "success")
    
    return redirect(url_for("detail", slug=blog.slug))


def create_default_categories():
    default_categories = ["Python", "JavaScript", "Frontend", "Backend", "Database"]
    for cat in default_categories:
        if not Category.query.filter_by(titles=cat).first():
            db.session.add(Category(titles=cat))
    db.session.commit()



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=8000,debug=True)
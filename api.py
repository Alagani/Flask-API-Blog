from flask import Blueprint
from flask import jsonify
from flask_restful import Api, Resource, reqparse
from datetime import datetime
from slugify import slugify
from models import *

# Create a Flask Blueprint for the API
api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Request parser for Blog API
blog_parser = reqparse.RequestParser()
blog_parser.add_argument('title', type=str, required=True, help='Title is required')
blog_parser.add_argument('body', type=str, required=True, help='Body is required')
blog_parser.add_argument('category_id', type=int, required=False, help='Category ID is optional')
blog_parser.add_argument('thumbnail', type=str, required=False, help='Thumbnail is optional')

# Request parser for User API
user_parser = reqparse.RequestParser()
user_parser.add_argument('email', type=str, required=True, help='Email is required')
user_parser.add_argument('username', type=str, required=True, help='Username is required')
user_parser.add_argument('password', type=str, required=True, help='Password is required')
user_parser.add_argument('is_admin', type=bool, required=False, help='Admin status is optional')

# Request parser for Comment API
comment_parser = reqparse.RequestParser()
comment_parser.add_argument('body', type=str, required=True, help='Comment body is required')
comment_parser.add_argument('blog_id', type=int, required=True, help='Blog ID is required')

# Blog Resource
class BlogResource(Resource):
    # GET /api/blogs/<int:blog_id>
    def get(self, blog_id):
        blog = Blog.query.get_or_404(blog_id)
        return jsonify({
            'id': blog.id,
            'title': blog.title,
            'slug': blog.slug,
            'body': blog.body,
            'thumbnail': blog.thumbnail,
            'user_id': blog.user_id,
            'category_id': blog.category_id,
            'created_at': blog.created_at.isoformat(),
            'updated_at': blog.updated_at.isoformat() if blog.updated_at else None
        })

    # PUT /api/blogs/<int:blog_id>
    def put(self, blog_id):
        blog = Blog.query.get_or_404(blog_id)
        args = blog_parser.parse_args()

        blog.title = args['title']
        blog.slug = slugify(args['title'])
        blog.body = args['body']
        blog.category_id = args['category_id']
        blog.thumbnail = args['thumbnail']
        blog.updated_at = datetime.utcnow()

        db.session.commit()
        return jsonify({'message': 'Blog updated successfully', 'id': blog.id})

    # DELETE /api/blogs/<int:blog_id>
    def delete(self, blog_id):
        blog = Blog.query.get_or_404(blog_id)
        db.session.delete(blog)
        db.session.commit()
        return jsonify({'message': 'Blog deleted successfully'})

# Blog List Resource
class BlogListResource(Resource):
    # GET /api/blogs
    def get(self):
        blogs = Blog.query.all()
        return jsonify([{
            'id': blog.id,
            'title': blog.title,
            'slug': blog.slug,
            'body': blog.body,
            'thumbnail': blog.thumbnail,
            'user_id': blog.user_id,
            'category_id': blog.category_id,
            'created_at': blog.created_at.isoformat(),
            'updated_at': blog.updated_at.isoformat() if blog.updated_at else None
        } for blog in blogs])

    # POST /api/blogs
    def post(self):
        args = blog_parser.parse_args()

        # Create a new blog
        new_blog = Blog(
            title=args['title'],
            slug=slugify(args['title']),
            body=args['body'],
            thumbnail=args['thumbnail'],
            user_id=1,
            category_id=args['category_id'],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.session.add(new_blog)
        db.session.commit()
        return jsonify({'message': 'Blog created successfully', 'id': new_blog.id})



# User Resource
class UserResource(Resource):
    # GET /api/users/<int:user_id>
    def get(self, user_id):
        user = User.query.get_or_404(user_id)
        return jsonify({
            'id': user.id,
            'email': user.email,
            'username': user.username
        })

    # PUT /api/users/<int:user_id>
    def put(self, user_id):
        user = User.query.get_or_404(user_id)
        args = user_parser.parse_args()

        # Update user fields
        user.email = args['email']
        user.username = args['username']
        if args['password']:
            user.set_password(args['password'])

        db.session.commit()
        return jsonify({'message': 'User updated successfully', 'id': user.id})

    # DELETE /api/users/<int:user_id>
    def delete(self, user_id):
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User deleted successfully'})

# User List Resource
class UserListResource(Resource):
    # GET /api/users
    def get(self):
        users = User.query.all()
        return jsonify([{
            'id': user.id,
            'email': user.email,
            'username': user.username
        } for user in users])

    # POST /api/users
    def post(self):
        args = user_parser.parse_args()

        if User.query.filter_by(email=args['email']).first():
            return jsonify({'message': 'Email already exists'}), 400

        new_user = User(
            email=args['email'],
            username=args['username'],
            is_active=args.get('is_admin', False)
        )
        new_user.set_password(args['password'])

        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'User created successfully', 'id': new_user.id})

# Comment Resource
class CommentResource(Resource):
    # GET /api/comments/<int:comment_id>
    def get(self, comment_id):
        comment = Comment.query.get_or_404(comment_id)
        return jsonify({
            'id': comment.id,
            'body': comment.body,
            'user_id': comment.user_id,
            'blog_id': comment.blog_id,
        })

    # PUT /api/comments/<int:comment_id>
    def put(self, comment_id):
        comment = Comment.query.get_or_404(comment_id)
        args = comment_parser.parse_args()
        comment.body = args['body']
        db.session.commit()
        return jsonify({'message': 'Comment updated successfully', 'id': comment.id})

    # DELETE /api/comments/<int:comment_id>
    def delete(self, comment_id):
        comment = Comment.query.get_or_404(comment_id)
        db.session.delete(comment)
        db.session.commit()
        return jsonify({'message': 'Comment deleted successfully'})

# Comment List Resource
class CommentListResource(Resource):
    # GET /api/comments
    def get(self):
        comments = Comment.query.all()
        return jsonify([{
            'id': comment.id,
            'body': comment.body,
            'user_id': comment.user_id,
            'blog_id': comment.blog_id
        } for comment in comments])

    # POST /api/comments
    def post(self):
        args = comment_parser.parse_args()

        # Create a new comment
        new_comment = Comment(
            body=args['body'],
            user_id=1,
            blog_id=args['blog_id']
        )

        db.session.add(new_comment)
        db.session.commit()
        return jsonify({'message': 'Comment created successfully', 'id': new_comment.id})

# Add resources to the API
api.add_resource(BlogResource, '/blogs/<int:blog_id>')
api.add_resource(BlogListResource, '/blogs')
api.add_resource(UserResource, '/users/<int:user_id>')
api.add_resource(UserListResource, '/users')
api.add_resource(CommentResource, '/comments/<int:comment_id>')
api.add_resource(CommentListResource, '/comments')
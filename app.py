from flask import Flask, render_template, redirect, url_for, flash ,request, jsonify, session
import sqlite3
import bcrypt
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'secret_key'
DATABASE = 'CNAP-FinalProject.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/get_session_data')
def get_session_data():
    if 'user_id' in session:
        return jsonify({
            'username': session.get('username'),
            'user_id': session.get('user_id')
        })
    else:
        return jsonify({'error': 'User not logged in'}), 401

# Auth Routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            session['next'] = request.url
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def hash_password(password):
    password = password.encode('utf-8')
    hashed_password = bcrypt.hashpw(password)
    return hashed_password

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password_confirmation = request.form['password_confirmation']
        
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        try:
            # Check if username already exists
            cur.execute('SELECT * FROM user WHERE username = ?', (username,))
            if not username or not email    or not password or not password_confirmation:
                flash('All fields are required', 'error')
                return render_template('/auth/register.html')
            
            if cur.fetchone():
                flash('Username already exists.', 'error')
                return render_template('/auth/register.html')

            # Check if email already exists
            cur.execute('SELECT * FROM user WHERE email = ?', (email,))
            if cur.fetchone():
                flash('Email already exists.', 'error')
                return render_template('/auth/register.html')
            
            if '@' not in email or '.' not in email:
                flash('Invalid email format', 'error')
                return render_template('/auth/register.html')

            if len(password) < 6 or len(password_confirmation) < 6:
                flash('Password must be at least 6 characters long', 'error')
                return render_template('/auth/register.html')

            if password != password_confirmation:
                flash('Passwords do not match', 'error')
                return render_template('/auth/register.html')

            # Insert new user
            cur.execute('INSERT INTO user (username, email) VALUES (?, ?)', (username, email))
            user_id = cur.lastrowid
            password_hash = hash_password(password) 
            cur.execute('INSERT INTO password (fk_user_id, hashed_password) VALUES (?, ?, ?)',(user_id, password_hash))

            cur.execute('INSERT INTO profile (fk_user_id, username) VALUES (?, ?)', (user_id, username))    

            conn.commit()
            return redirect(url_for('login'))
            
        except sqlite3.IntegrityError as e:
            if 'UNIQUE constraint failed' in str(e):
                return jsonify({'error': 'Email already exists.'}), 400
            return jsonify({'error': 'Database error occurred.'}), 500
        except Exception as e:
            return jsonify({'error': f'Unexpected error: {e}'}), 500
        finally:
            conn.close()

    #Get register page
    return render_template('/auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    #Send login form
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db()
        cur = conn.cursor()

        cur.execute('SELECT * FROM user WHERE email = ?', (email,))
        user = cur.fetchone()

        if user is None:
            flash('Email does not exist', 'danger')
            return render_template('/auth/login.html')

        cur.execute('SELECT hashed_password FROM password WHERE fk_user_id = ?', (user[0],))
        hashed_password = cur.fetchone()
        conn.close()

        if bcrypt.checkpw(password.encode('utf-8'), hashed_password['hashed_password']):
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash('You have successfully logged in.', 'success')
            next_page = session.get('next')
            if next_page:
                session.pop('next')
                return redirect(next_page)
            return redirect(url_for('home'))
        else:
            flash('Incorrect password', 'danger')
            return render_template('/auth/login.html')


    #Get login page
    return render_template('/auth/login.html', username=session.get('username'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Template Routes
@app.route('/')
def home():
    conn = get_db()
    cur = conn.cursor()

    # Fetch posts along with their tag names
    cur.execute('''
        SELECT post.*, tag.* 
        FROM post 
        JOIN tag ON post.fk_tag_id = tag.pk_tag_id
        ORDER BY post.created_at DESC
    ''')
    posts = cur.fetchall()

    # Calculate time elapsed since post creation
    time_elapsed_list = []
    for post in posts:
        created_at = datetime.strptime(post['created_at'], '%Y-%m-%d %H:%M:%S')
        now = datetime.now()
        time_diff = now - created_at
        days = time_diff.days
        seconds = time_diff.seconds
        hours = seconds // 3600

        if days < 1:
            time_elapsed = f'{hours} hours ago'
        elif days < 30:
            time_elapsed = f'{days} days ago'
        elif days < 365:
            time_elapsed = created_at.strftime('%m-%d')
        else:
            time_elapsed = created_at.strftime('%Y-%m-%d')
        
        time_elapsed_list.append(time_elapsed)

    conn.close()
    if 'user_id' in session:
        return render_template('/home/home.html', posts=posts, username=session.get('username'), time_elapsed_list=time_elapsed_list, zip=zip)
    else:
        return render_template('/home/home.html', posts=posts, guest=True, time_elapsed_list=time_elapsed_list, zip=zip)

@app.route('/tags')
def tags():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tag')
    tags = cur.fetchall()
    conn.close()
    return render_template('/tags/tags.html', tags=tags)

@app.route('/search')
@login_required
def search():
    return render_template('/search/search.html')

@app.route('/createPost/<int:tag_id>', methods=['GET', 'POST'])
@login_required
def createPost(tag_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tag WHERE pk_tag_id = ?', (tag_id,))
    tag = cur.fetchone()

    if request.method == 'POST':
        user_id = session['user_id']
        tag_id = tag[0]
        title = request.form['title']
        content = request.form['content']
        cur.execute('INSERT INTO post (fk_user_id, fk_tag_id, title, content) VALUES (?, ?, ?, ?)', (user_id, tag_id, title, content))
        cur.execute('UPDATE profile SET post_count = post_count + 1 WHERE fk_user_id = ?', (user_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('showTagPosts', tag_id=tag_id))

    conn.close()
    return render_template('/posts/createPost.html', tag=tag, username=session['username'])

@app.route('/showPost/<int:post_id>')
def showPost(post_id):
    conn = get_db()
    cur = conn.cursor()

    # Fetch post data
    cur.execute('SELECT * FROM post WHERE pk_post_id = ?', (post_id,))
    post = cur.fetchone()
    
    if post is None:
        conn.close()
        return "Post not found", 404
    
    # Fetch tag name
    cur.execute('SELECT tag.* FROM tag JOIN post ON tag.pk_tag_id = post.fk_tag_id WHERE post.pk_post_id = ?', (post_id,))
    tag = cur.fetchone()
    
    # Fetch author's username
    cur.execute('SELECT user.username FROM post JOIN user ON post.fk_user_id = user.pk_user_id WHERE post.pk_post_id = ?', (post_id,))
    author = cur.fetchone()

    # Fetch comments
    cur.execute('SELECT comment.*, user.username FROM comment JOIN user ON comment.fk_user_id = user.pk_user_id WHERE comment.fk_post_id = ? ORDER BY comment.created_at DESC', (post_id,))
    comments = cur.fetchall()
    
    conn.close()
    
    # Format the created_at timestamp
    created_at = datetime.strptime(post['created_at'], '%Y-%m-%d %H:%M:%S')
    created_at = created_at.strftime('%Y年%m月%d日 %H:%M')
    
    return render_template('/posts/showPost.html', post=post, tag=tag, author=author['username'], created_at=created_at, comments=comments)

@app.route('/showTagPosts/<int:tag_id>')
def showTagPosts(tag_id):
    conn = get_db()
    cur = conn.cursor()

    cur.execute('SELECT * FROM tag WHERE pk_tag_id = ?', (tag_id,))
    tag = cur.fetchone()
    cur.execute('SELECT * FROM post WHERE fk_tag_id = ?', (tag_id,))
    posts = cur.fetchall()

    conn.close()
    return render_template('/posts/showTagPosts.html', tag=tag, posts=posts)

@app.route('/add_comment/<int:post_id>', methods=['POST'])
@login_required
def add_comment(post_id):
    user_id = session['user_id']
    content = request.form['content']
    
    conn = get_db()
    cur = conn.cursor()
    
    # Insert the comment into the comments table
    cur.execute('INSERT INTO comment (fk_post_id, fk_user_id, content) VALUES (?, ?, ?)', (post_id, user_id, content))
    # Update the comments_count in the post table
    cur.execute('UPDATE post SET comments_count = comments_count + 1 WHERE pk_post_id = ?', (post_id,))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('showPost', post_id=post_id))

@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    current_user_id = session['user_id']
    is_own_profile = (current_user_id == user_id)
    print(current_user_id, user_id, is_own_profile)
    
    conn = get_db()
    cur = conn.cursor()
    
    # Fetch user profile
    cur.execute('SELECT * FROM profile WHERE fk_user_id = ?', (user_id,))
    profile = cur.fetchone()
    
    # Fetch user posts
    cur.execute('SELECT title, content FROM post WHERE fk_user_id = ?', (user_id,))
    posts = cur.fetchall()
    
    # Fetch followers count
    cur.execute('SELECT COUNT(*) FROM follower WHERE followed_user_id = ?', (user_id,))
    followers_count = cur.fetchone()[0]
    
    # Fetch following count
    cur.execute('SELECT COUNT(*) FROM follower WHERE follower_user_id = ?', (user_id,))
    following_count = cur.fetchone()[0]
    
    # Check if the current user is following this profile
    cur.execute('SELECT * FROM follower WHERE follower_user_id = ? AND followed_user_id = ?', (current_user_id, user_id))
    is_following = cur.fetchone() is not None
    
    conn.close()
    return render_template('/profile/profile.html', profile=profile, posts=posts, followers_count=followers_count, following_count=following_count, is_own_profile=is_own_profile, is_following=is_following)

@app.route('/editProfile')
def editProfile():
    return render_template('/profile/editProfile.html')

@app.route('/follow/<int:user_id>', methods=['POST'])
def follow(user_id):
    follower_id = session['user_id']
    conn = get_db()
    cur = conn.cursor()
    
    # Check if already following
    cur.execute('SELECT * FROM follower WHERE follower_user_id = ? AND followed_user_id = ?', (follower_id, user_id))
    if cur.fetchone():
        conn.close()
        return jsonify({'error': 'Already following'}), 400
    
    # Insert follow relationship
    cur.execute('INSERT INTO follower (follower_user_id, followed_user_id) VALUES (?, ?)', (follower_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({'success': 'Followed successfully'}), 200

@app.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow(user_id):
    follower_id = session['user_id']
    conn = get_db()
    cur = conn.cursor()
    
    # Check if following
    cur.execute('SELECT * FROM follower WHERE follower_user_id = ? AND followed_user_id = ?', (follower_id, user_id))
    if not cur.fetchone():
        conn.close()
        return jsonify({'error': 'Not following'}), 400
    
    # Delete follow relationship
    cur.execute('DELETE FROM follower WHERE follower_user_id = ? AND followed_user_id = ?', (follower_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({'success': 'Unfollowed successfully'}), 200

@app.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    user_id = session['user_id']
    
    conn = get_db()
    cur = conn.cursor()
    
    # Check if the user has already liked the post
    cur.execute('SELECT * FROM like WHERE fk_post_id = ? AND fk_user_id = ?', (post_id, user_id))
    like = cur.fetchone()
    
    if like:
        # Unlike the post
        cur.execute('UPDATE post SET likes_count = likes_count - 1 WHERE pk_post_id = ?', (post_id,))
        cur.execute('DELETE FROM like WHERE fk_post_id = ? AND fk_user_id = ?', (post_id, user_id))
        conn.commit()
        conn.close()
        return jsonify({'success': 'Unliked successfully', 'liked': False}), 200
    else:
        # Like the post
        cur.execute('UPDATE post SET likes_count = likes_count + 1 WHERE pk_post_id = ?', (post_id,))
        cur.execute('INSERT INTO like (fk_post_id, fk_user_id) VALUES (?, ?)', (post_id, user_id))
        conn.commit()
        conn.close()
        return jsonify({'success': 'Liked successfully', 'liked': True}), 200

if __name__ == '__main__':
    app.run(debug=True)
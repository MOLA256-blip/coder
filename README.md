# VideoStream - Modern Video Streaming App

A beautiful, modern video streaming web application built with Django. Upload, stream, and share videos with a clean, responsive interface.

## 🚀 Features

### Core Functionality
- **Video Upload & Streaming**: Upload videos up to 100MB with efficient streaming
- **User Authentication**: Complete user registration and login system
- **Video Management**: Upload, view, delete, and organize your videos
- **Comments System**: Interactive commenting on videos
- **Search & Discovery**: Find videos by title, description, or creator

### Modern UI/UX
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Modern Interface**: Clean, intuitive design with smooth animations
- **Drag & Drop Upload**: Easy file upload with progress tracking
- **Video Grid Layout**: Pinterest-style video browsing
- **Real-time Stats**: View counts and engagement metrics

### Technical Features
- **Efficient Streaming**: HTTP range request support for smooth playback
- **File Upload Handling**: Optimized for large video files
- **Database Integration**: SQLite database with Django ORM
- **Security**: CSRF protection, user authentication, file validation

## 📋 Requirements

- Python 3.8+
- Django 4.2+
- Modern web browser with HTML5 video support

## 🛠 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser
```bash
python manage.py createsuperuser
```

### 4. Create Media Directories
```bash
mkdir -p media/videos
mkdir -p media/thumbnails
```

### 5. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to access the application.

## 🎯 Usage

### For Users
1. **Register/Login**: Create an account or sign in
2. **Upload Videos**: Use the upload page to add videos
3. **Browse Content**: Explore videos on the home page
4. **Watch Videos**: Click on any video to watch and comment
5. **Manage Videos**: View and manage your uploaded videos

### For Administrators
1. **Admin Panel**: Access `/admin/` for content management
2. **User Management**: Manage users and permissions
3. **Content Moderation**: Review videos and comments

## 📁 Project Structure

```
videostream/
├── videostream/           # Project settings
│   ├── settings.py       # Django configuration
│   ├── urls.py          # Main URL routing
│   └── wsgi.py          # WSGI configuration
├── videos/               # Main app
│   ├── models.py        # Video and Comment models
│   ├── views.py         # Video streaming and CRUD views
│   ├── forms.py         # Upload and user forms
│   ├── urls.py          # App URL routing
│   └── admin.py         # Admin interface
├── templates/            # HTML templates
│   ├── base.html        # Base template
│   ├── videos/          # Video-specific templates
│   └── registration/    # Auth templates
├── static/              # Static files
│   └── css/            # Custom styles
├── media/              # User uploads
│   ├── videos/         # Video files
│   └── thumbnails/     # Generated thumbnails
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## ⚙️ Configuration

### Video Settings
The app supports videos up to 100MB. To change this limit, edit `videostream/settings.py`:

```python
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
```

### Supported Video Formats
- MP4 (recommended)
- AVI
- MOV
- WMV
- MKV
- WebM

## 🎨 Customization

### Styling
The app uses Bootstrap 5 with custom CSS. To customize the appearance:

1. Edit `static/css/custom.css` for custom styles
2. Modify `templates/base.html` for layout changes
3. Update color variables in CSS for theme changes

### Features
- Add new video fields in `videos/models.py`
- Create new views in `videos/views.py`
- Add new templates in `templates/videos/`

## 🚀 Production Deployment

### 1. Security Settings
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = 'your-secure-secret-key'
```

### 2. Static Files
```bash
python manage.py collectstatic
```

### 3. Database
Consider using PostgreSQL for production:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'videostream',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🐛 Troubleshooting

### Common Issues

**Video not playing:**
- Check if video file exists in media/videos/
- Verify video format is supported
- Check browser compatibility

**Upload errors:**
- Verify file size is under 100MB
- Check file format is supported
- Ensure media directory has write permissions

**Database errors:**
- Run `python manage.py migrate`
- Check database file permissions
- Verify Django installation

## 📝 API Endpoints

- `GET /` - Home page with video list
- `GET /video/<id>/` - Video detail page
- `GET /stream/<id>/` - Video streaming endpoint
- `POST /upload/` - Upload new video
- `GET /my-videos/` - User's video dashboard
- `POST /register/` - User registration
- `POST /login/` - User login

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- Django framework and community
- Bootstrap for UI components
- Font Awesome for icons
- Modern web technologies

---

Built with ❤️ using Django and modern web technologies.

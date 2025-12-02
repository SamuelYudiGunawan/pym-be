from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
import json
from .models import Note, Reply
from .forms import NoteForm, ReplyForm
from .applications.model_methods import NoteMethods, ReplyMethods


@require_http_methods(["GET"])
def get_notes(request):
    """API endpoint to get all notes with pagination"""
    page = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 8)

    notes = Note.objects.all()
    paginator = Paginator(notes, per_page)
    page_obj = paginator.get_page(page)

    notes_data = []
    for note in page_obj:
        notes_data.append({
            'id': note.id,
            'content': note.content,
            'author': NoteMethods.get_display_author(note),
            'is_anonymous': note.is_anonymous,
            'created_at': note.created_at.strftime('%B %d, %Y'),
            'reply_count': NoteMethods.get_reply_count(note)
        })

    return JsonResponse({
        'notes': notes_data,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages
    })


@require_http_methods(["GET"])
def get_note_detail(request, note_id):
    """API endpoint to get a single note with its replies"""
    note = get_object_or_404(Note, id=note_id)

    replies_data = []
    for reply in note.replies.all():
        replies_data.append({
            'id': reply.id,
            'content': reply.content,
            'author': ReplyMethods.get_display_author(reply),
            'is_anonymous': reply.is_anonymous,
            'created_at': reply.created_at.strftime('%B %d, %Y at %I:%M %p')
        })

    note_data = {
        'id': note.id,
        'content': note.content,
        'author': NoteMethods.get_display_author(note),
        'is_anonymous': note.is_anonymous,
        'created_at': note.created_at.strftime('%B %d, %Y'),
        'replies': replies_data,
        'reply_count': NoteMethods.get_reply_count(note)
    }

    return JsonResponse({'note': note_data})


@csrf_exempt
@require_http_methods(["POST"])
def submit_note(request):
    """API endpoint to submit a new note"""
    try:
        data = json.loads(request.body)

        # Extract only the fields the form expects
        form_data = {
            'content': data.get('content', ''),
            'author_name': data.get('author_name', '')
        }

        form = NoteForm(form_data)

        if form.is_valid():
            note = form.save(commit=False)

            # Handle anonymous posting from frontend
            is_anonymous = data.get('is_anonymous', True)
            if is_anonymous or not form.cleaned_data.get('author_name'):
                note.is_anonymous = True
                note.author_name = ''
            else:
                note.is_anonymous = False

            note.save()

            return JsonResponse({
                'success': True,
                'note': {
                    'id': note.id,
                    'content': note.content,
                    'author': NoteMethods.get_display_author(note),
                    'is_anonymous': note.is_anonymous,
                    'created_at': note.created_at.strftime('%B %d, %Y')
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def submit_reply(request, note_id):
    """API endpoint to submit a reply to a note"""
    try:
        note = get_object_or_404(Note, id=note_id)
        data = json.loads(request.body)

        # Extract only the fields the form expects
        form_data = {
            'content': data.get('content', ''),
            'author_name': data.get('author_name', '')
        }

        form = ReplyForm(form_data)

        if form.is_valid():
            reply = form.save(commit=False)
            reply.note = note

            # Handle anonymous posting from frontend
            is_anonymous = data.get('is_anonymous', True)
            if is_anonymous or not form.cleaned_data.get('author_name'):
                reply.is_anonymous = True
                reply.author_name = ''
            else:
                reply.is_anonymous = False

            reply.save()

            return JsonResponse({
                'success': True,
                'reply': {
                    'id': reply.id,
                    'content': reply.content,
                    'author': ReplyMethods.get_display_author(reply),
                    'is_anonymous': reply.is_anonymous,
                    'created_at': reply.created_at.strftime('%B %d, %Y at %I:%M %p')
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def about_api(request):
    """API endpoint for about information"""
    return JsonResponse({
        'about': {
            'name': 'Pour Your Mind',
            'description': 'A platform to share your thoughts with the world, either anonymously or with your name.',
            'features': [
                'Share thoughts publicly',
                'Post anonymously or with your name',
                'Reply to others\' thoughts',
                'View all thoughts in a feed'
            ],
            'version': '1.0.0'
        }
    })


# Authentication Views

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """API endpoint for user login"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return JsonResponse({
                'success': False,
                'error': 'Username and password are required'
            }, status=400)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Invalid username or password'
            }, status=401)
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def logout_view(request):
    """API endpoint for user logout"""
    logout(request)
    return JsonResponse({
        'success': True,
        'message': 'Logged out successfully'
    })


@require_http_methods(["GET"])
def current_user(request):
    """API endpoint to get current logged-in user"""
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': {
                'id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
            }
        })
    else:
        return JsonResponse({
            'authenticated': False,
            'user': None
        })


@csrf_exempt
@require_http_methods(["POST"])
def register_view(request):
    """API endpoint for user registration"""
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        email = data.get('email', '')

        if not username or not password:
            return JsonResponse({
                'success': False,
                'error': 'Username and password are required'
            }, status=400)

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'error': 'Username already exists'
            }, status=400)

        # Create new user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        # Log the user in
        login(request, user)

        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
            }
        })
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

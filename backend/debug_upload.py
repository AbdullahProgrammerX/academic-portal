"""Debug upload endpoint"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from submissions.views import SubmissionViewSet
import traceback

User = get_user_model()

# Get user
user = User.objects.get(email='user123@test.com')
print(f"User: {user.email}")

# Create test file
with open('test_manuscript.docx', 'rb') as f:
    file_content = f.read()

uploaded_file = SimpleUploadedFile(
    "test_manuscript.docx",
    file_content,
    content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
)

# Create request
factory = RequestFactory()
request = factory.post('/api/submissions/submissions/start/', {
    'file': uploaded_file
})
request.user = user

# Call view
view = SubmissionViewSet()
view.action = 'start'
view.request = request
view.format_kwarg = None

try:
    response = view.start(request)
    print(f"\n✓ Success! Status: {response.status_code}")
    print(f"Response: {response.data}")
except Exception as e:
    print(f"\n✗ Error: {e}")
    traceback.print_exc()

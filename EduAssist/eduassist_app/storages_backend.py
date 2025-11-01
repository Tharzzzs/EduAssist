from django.core.files.storage import Storage
from django.conf import settings
from supabase import create_client
import os
from io import BytesIO

class SupabaseStorage(Storage):
    def __init__(self):
        self.url = os.environ.get("SUPABASE_URL")
        self.key = os.environ.get("SUPABASE_KEY")
        self.bucket = os.environ.get("SUPABASE_BUCKET", "eduassist-uploads")
        self.client = create_client(self.url, self.key)

    def _save(self, name, content):
        """Save file to Supabase Storage"""
        path = f"uploads/{name}"
        file_bytes = BytesIO(content.read())
        res = self.client.storage.from_(self.bucket).upload(path, file_bytes, {"upsert": True})
        if res.status_code not in (200, 201):
            raise Exception(f"Supabase upload failed: {res.text}")
        return path

    def url(self, name):
        """Return public URL to access the file"""
        res = self.client.storage.from_(self.bucket).get_public_url(name)
        return res['publicUrl'] 


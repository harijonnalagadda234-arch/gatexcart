from django.db import models
class ChatMessage(models.Model):
 session_key=models.CharField(max_length=80,db_index=True); role=models.CharField(max_length=20,choices=[("user","User"),("assistant","Assistant")]); message=models.TextField(); created_at=models.DateTimeField(auto_now_add=True)
 class Meta:ordering=["created_at"]

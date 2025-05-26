from django.db import models

# Create your models here.


from django.db import models
import uuid

class ChatRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=255)  # 目前使用 demo-user 或硬編碼字串即可
    question = models.TextField()
    answer = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id}：{self.question[:20]}..."

        

from django.db import models


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            try:
                from accounts.push import send_web_push
                send_web_push(
                    title=f"📩 New Inquiry: {self.subject}",
                    body=f"From {self.name} ({self.email}): {self.message[:90]}",
                    url=f"/admin/pages/contactmessage/{self.pk}/change/"
                )
            except Exception as e:
                import logging
                logging.getLogger(__name__).error(f"Failed to trigger web push for contact message #{self.pk}: {e}")


class NewsletterSubscriber(models.Model):
    name = models.CharField(max_length=120, blank=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return self.email

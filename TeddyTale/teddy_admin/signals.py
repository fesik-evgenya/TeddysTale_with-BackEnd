import os
from django.conf import settings
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import UploadedImage, SectionContent


@receiver(post_delete, sender=UploadedImage)
def delete_uploaded_image_file(sender, instance, **kwargs):
    """
    Удаляет файл изображения при удалении записи UploadedImage
    """
    if instance.file_path:
        file_path = os.path.join(settings.MEDIA_ROOT, instance.file_path)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                # Логируем ошибку, но не прерываем выполнение
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Ошибка при удалении файла {file_path}: {e}")


@receiver(pre_save, sender=UploadedImage)
def delete_old_image_on_update(sender, instance, **kwargs):
    """
    Удаляет старый файл при обновлении записи UploadedImage
    """
    if not instance.pk:
        return False  # Новая запись

    try:
        old_instance = UploadedImage.objects.get(pk=instance.pk)
        if old_instance.file_path != instance.file_path:
            old_file_path = os.path.join(settings.MEDIA_ROOT,
                                         old_instance.file_path)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
    except UploadedImage.DoesNotExist:
        pass


@receiver(pre_save, sender=SectionContent)
def delete_image_on_section_content_update(sender, instance, **kwargs):
    """
    Удаляет старый файл при обновлении SectionContent с изображением
    """
    if not instance.pk:
        return False  # Новая запись

    try:
        old_instance = SectionContent.objects.get(pk=instance.pk)
        # Если тип контента - изображение и путь изменился
        if (old_instance.content_type == 'image' and
                instance.content_type == 'image' and
                old_instance.value != instance.value and
                old_instance.value):

            # Находим связанную запись UploadedImage
            uploaded_image = UploadedImage.objects.filter(
                file_path=old_instance.value
            ).first()

            if uploaded_image:
                uploaded_image.delete()  # Это удалит и файл через сигнал
    except SectionContent.DoesNotExist:
        pass
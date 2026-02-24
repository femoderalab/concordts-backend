# results/signals.py
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from .models import StudentResult, SubjectScore, PsychomotorSkills, AffectiveDomains


@receiver(pre_save, sender=SubjectScore)
def validate_subject_score(sender, instance, **kwargs):
    """Validate subject score before saving"""
    # Ensure scores don't exceed obtainable marks
    if instance.ca_score > instance.ca_obtainable:
        instance.ca_score = instance.ca_obtainable
    
    if instance.exam_score > instance.exam_obtainable:
        instance.exam_score = instance.exam_obtainable


@receiver(post_save, sender=SubjectScore)
def update_result_on_subject_score_change(sender, instance, created, **kwargs):
    """Update parent result when subject score changes"""
    # Use transaction.on_commit to ensure it runs after the main transaction
    transaction.on_commit(
        lambda: update_result_totals(instance.result)
    )


@receiver(post_delete, sender=SubjectScore)
def update_result_on_subject_score_delete(sender, instance, **kwargs):
    """Update parent result when subject score is deleted"""
    transaction.on_commit(
        lambda: update_result_totals(instance.result)
    )


def update_result_totals(result):
    """Helper function to update result totals"""
    # Recalculate totals
    result.calculate_totals()
    
    # Recalculate position
    result.calculate_position()
    
    # Save the result
    result.save(update_fields=[
        'total_ca_score', 'total_exam_score', 'overall_total_score',
        'total_obtainable', 'percentage', 'average_score',
        'overall_grade', 'overall_remark', 'position_in_class',
        'number_of_pupils_in_class'
    ])


@receiver(post_save, sender=PsychomotorSkills)
def calculate_psychomotor_rating(sender, instance, created, **kwargs):
    """Calculate overall psychomotor rating"""
    instance.calculate_overall_rating()
    # Don't save here to avoid infinite loop - rating is calculated in save()


@receiver(post_save, sender=AffectiveDomains)
def calculate_affective_rating(sender, instance, created, **kwargs):
    """Calculate overall affective rating"""
    instance.calculate_overall_rating()
    # Don't save here to avoid infinite loop - rating is calculated in save()


@receiver(post_save, sender=StudentResult)
def create_assessment_records(sender, instance, created, **kwargs):
    """Create psychomotor and affective records when result is created"""
    if created:
        # Create psychomotor skills record if it doesn't exist
        if not hasattr(instance, 'psychomotor_skills'):
            PsychomotorSkills.objects.create(result=instance)
        
        # Create affective domains record if it doesn't exist
        if not hasattr(instance, 'affective_domains'):
            AffectiveDomains.objects.create(result=instance)


@receiver(pre_save, sender=StudentResult)
def update_student_class(sender, instance, **kwargs):
    """Update student's class level if promoted"""
    if instance.is_promoted and instance.student.class_level:
        # Get next class level
        from academic.models import ClassLevel
        current_level = instance.student.class_level
        
        # Find next level based on order
        next_level = ClassLevel.objects.filter(
            program=current_level.program,
            order__gt=current_level.order
        ).order_by('order').first()
        
        if next_level:
            instance.student.class_level = next_level
            instance.student.save(update_fields=['class_level'])
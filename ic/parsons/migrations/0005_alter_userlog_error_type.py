from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parsons', '0004_userlogview_onlineclass_alter_chapterlink_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlog',
            name='error_type',
            field=models.CharField(blank=True, choices=[('C', 'Conceptual'), ('S', 'Syntax'), ('D', 'Distraction'), ('I', 'Interpretation'), ('O', 'Ordenation')], max_length=2, null=True),
        ),
    ]

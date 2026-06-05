from django.db import models

# Create your models here.




class ProblemManager(models.Manager):
    def random(self):
        count = self.aggregate(count=Count('id'))['count']
        random_index = randint(0, count - 1)
        return self.all()[random_index]


class Problem(models.Model):
    QUESTION_TYPES = (("C", "Code"),
                      ("M", "Multiple Choice"),
                      ("T", "Text"),
                      ("P", "Parsons Problem"))

    question_type = models.CharField(max_length=2, choices=QUESTION_TYPES,
                                     default="C")
    title = models.CharField(max_length=200, blank=False)
    content = models.TextField(blank=False)
    options = models.TextField(blank=True)
    difficulty = models.CharField(max_length=200, blank=True)
    link = models.URLField(blank=True)
    retrieved_date = models.DateTimeField(blank=True, auto_now_add=True)
    crawler = models.CharField(max_length=200, blank=True)
    hint = models.TextField(blank=True)
    objects = ProblemManager()
    chapter = models.ManyToManyField(Chapter, through='ExerciseSet')
    test_case_generator = models.TextField(blank=True, null=True)
    history = HistoricalRecords()

    def unicode(self):
        return self.title

    def str(self):
        return "%d - %s" % (self.id, self.title)
    class Meta:
        verbosename = ('Problem')
        verbose_nameplural = ('Problems')
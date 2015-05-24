from celery.task import task


@task
def test():
    return True
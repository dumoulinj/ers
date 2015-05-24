from swampdragon import route_handler
from swampdragon.route_handler import BaseRouter
import time
from dataset_manager.enums import ComputingStateType
from testing import tasks


class TestServerRouter(BaseRouter):
    route_name = 'test_server'

    valid_verbs = BaseRouter.valid_verbs + ['test', 'test_celery']

    def test(self):
        try:
            time.sleep(2)
            self.send({"state": ComputingStateType.SUCCESS})
        except:
            self.send({"state": ComputingStateType.FAILED})

    def test_celery(self):
        try:
            task = tasks.test.delay()
            time.sleep(2)
            state = task.state

            if state == "SUCCESS":
                self.send({"state": ComputingStateType.SUCCESS})
            else:
                self.send({"state": ComputingStateType.FAILED})
        except:
            self.send({"state": ComputingStateType.FAILED})

route_handler.register(TestServerRouter)
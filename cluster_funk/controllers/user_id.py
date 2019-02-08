import uuid
from cement import Controller, ex

class UserId(Controller):

    class Meta:
        label = 'user_id'
        stacked_type = 'nested'
        stacked_on = 'base'
        help = "Set a user_id to associated AWS resources with you"

    @ex(help='Set user id')
    def set(self):
        user_info = {
            'id': str(uuid.uuid4())
        }
        table = self.app.db.table('users')
        allusers = table.all()
        if not len(allusers):
           table.insert(user_info)
        else:
           user_info = allusers[0]
        self.app.log.info("Your userid has been set too %s" % (user_info['id']))
        self.app.log.info("Every resource you use will be tagged with this user_id")

    @ex(help='get user id')
    def get(self):
        table = self.app.db.table('users')
        try:
            self.app.log.info("Your user_id is: %s" % (table.all()[0]['id']))
        except IndexError:
            self.app.log.info("No user_id set so can't get it. Please run user-id set first")

    @ex(help='clear user id')
    def clear(self):
        table = self.app.db.table('users')
        table.purge()

# coding: utf-8

from starmachine.model.user import User
from starmachine.model.notify import Notify
from starmachine.model.consts import NOTIFY_UNREAD, NOTIFY_READ, NOTIFY_ACTION_CONTENT_COMMENT, \
    NOTIFY_ACTION_CONTENT_REWARD, NOTIFY_ACTION_CONTENT_LIKED, NOTIFY_ACTION_COMMENT_REPLY, NOTIFY_TYPE_COMMENT, \
    NOTIFY_TYPE_REWARD, NOTIFY_TYPE_SYSTEM, NOTIFY_TYPE_LIKED

notifies = Notify.gets_all()
for notify in notifies:
    notify_action = int(notify.action)
    if notify_action == NOTIFY_ACTION_CONTENT_LIKED:
        user = User.get(notify.sender_id)
        user_name = user.name
        if not isinstance(user_name, unicode):
            user_name = user_name.decode('utf-8')

        text = u'%s对你的内容进行了点赞' % user_name
        notify.update(extra_info=text, notify_type=NOTIFY_TYPE_LIKED)
    elif notify_action == NOTIFY_ACTION_CONTENT_REWARD:
        user = User.get(notify.sender_id)
        amount = float(notify.extra_info)
        user_name = user.name
        if not isinstance(user_name, unicode):
            user_name = user_name.decode('utf-8')

        text = u'哇，%s给你打赏了：￥%s' % (user_name, amount)
        notify.update(extra_info=text, notify_type=NOTIFY_TYPE_REWARD)
    elif notify_action == NOTIFY_ACTION_CONTENT_COMMENT:
        user = User.get(notify.sender_id)
        user_name = user.name
        if not isinstance(user_name, unicode):
            user_name = user_name.decode('utf-8')

        text = u'%s评论了你：%s' % (user_name, notify.extra_info)
        notify.update(extra_info=text, notify_type=NOTIFY_TYPE_COMMENT)
        # notify.update(notify_type=NOTIFY_TYPE_COMMENT)
    elif notify_action == NOTIFY_ACTION_COMMENT_REPLY:
        user = User.get(notify.sender_id)
        user_name = user.name
        if not isinstance(user_name, unicode):
            user_name = user_name.decode('utf-8')
        text = u'%s回复了你：%s' % (user_name, notify.extra_info)
        notify.update(extra_info=text, notify_type=NOTIFY_TYPE_COMMENT)
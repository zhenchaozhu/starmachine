# coding: utf-8

from rq.decorators import job
from starmachine.model.notify import Notify
from starmachine.model.PushNotification import push_client
from starmachine.worker import conn
from starmachine.model.consts import NOTIFY_ACTION_CONTENT_LIKED, NOTIFY_ACTION_CONTENT_COMMENT, \
    NOTIFY_ACTION_CONTENT_REWARD, NOTIFY_ACTION_COMMENT_REPLY, NOTIFY_TYPE_COMMENT, NOTIFY_TYPE_LIKED, NOTIFY_TYPE_REWARD

@job('default', connection=conn)
def notify_content_like(user, content):
    user_name = user.name
    if not isinstance(user_name, unicode):
        user_name = user_name.decode('utf-8')

    text = u'%s对你的内容进行了点赞' % user_name
    Notify.add(user.id, content.creator_id, NOTIFY_ACTION_CONTENT_LIKED, content.id, NOTIFY_TYPE_LIKED, extra_info=text)
    push_client.notify_content_like(content)

@job('default', connection=conn)
def notify_content_comment(user, content, comment):
    user_name = user.name
    comment_text = comment.text
    if not isinstance(user_name, unicode):
        user_name = user_name.decode('utf-8')

    if not isinstance(comment_text, unicode):
        comment_text = comment_text.decode('utf-8')

    text = u'%s评论了你：%s' % (user_name, comment_text)
    Notify.add(user.id, content.creator_id, NOTIFY_ACTION_CONTENT_COMMENT, content.id, NOTIFY_TYPE_COMMENT, comment.id, text)
    push_client.notify_comment(content.creator, content)

@job('default', connection=conn)
def notify_content_reward(user, content, reward_order):
    user_name = user.name
    if not isinstance(user_name, unicode):
        user_name = user_name.decode('utf-8')

    text = u'哇，%s给你打赏了：￥%s' % (user_name, float(reward_order.amount))
    Notify.add(user.id, content.creator_id, NOTIFY_ACTION_CONTENT_REWARD, content.id, NOTIFY_TYPE_REWARD, reward_order.id, text)
    push_client.notify_reward(content)

@job('default', connection=conn)
def notify_comment_reply(user, receiver, content, comment):
    user_name = user.name
    if not isinstance(user_name, unicode):
        user_name = user_name.decode('utf-8')

    comment_text = comment.text
    if not isinstance(comment_text, unicode):
        comment_text = comment_text.decode('utf-8')

    text = u'%s回复了你：%s' % (user_name, comment_text)
    Notify.add(user.id, receiver.id, NOTIFY_ACTION_COMMENT_REPLY, content.id, NOTIFY_TYPE_COMMENT, comment.id, text)
    push_client.notify_comment(receiver, content)

@job('default', connection=conn)
def push_validate_status(user_validate):
    push_client.push_validate_status(user_validate)

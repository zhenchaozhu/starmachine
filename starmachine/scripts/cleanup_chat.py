# coding: utf-8

from optparse import OptionParser
from datetime import datetime, timedelta
from starmachine.lib.query import DbManager
from starmachine.lib.redis_cache import CacheManager
from starmachine.model.group_message_liked import GroupMessage, GroupMessageLiked
from starmachine import settings

GROUP_MESSAGE_LIKED_KEY = 'group:%s:message:%s:liked'
GROUP_MESSAGE_LIKED_LIST = 'group:%s:message:liked'

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-p', '--profile', dest='profile', default='develop')
    options, args = parser.parse_args()
    if not options.profile:
        profile = 'product'
    else:
        profile = options.profile

    settings.init(profile)
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    db = DbManager().db
    cache = CacheManager().cache
    messages = GroupMessage.get_messages_by_time(yesterday)

    for message in messages:
        message_id = message.id
        group_id = message.group_id
        # 删除群组聊天点赞记录的缓存
        group_message_liked_key = GROUP_MESSAGE_LIKED_KEY % (group_id, message_id)
        cache.delete(group_message_liked_key)
        # 删除群组消息列表的缓存
        group_message_liked_list = GROUP_MESSAGE_LIKED_LIST % group_id
        cache.zrem(group_message_liked_list, message_id)
        sql = 'delete from {table} where message_id=%s and group_id=%s'.format(table=GroupMessageLiked.table)
        db.execute(sql, message_id, group_id)
        sql = 'delete from {table} where id=%s'.format(table=GroupMessage.table)
        db.execute(sql, message_id)







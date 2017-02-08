# coding: utf-8

import logging
from tornado.web import MissingArgumentError
from starmachine.lib.utils import check_access_token, check_api_key
from starmachine.handlers.base import APIBaseHandler
from starmachine.handlers.error import MISSING_PARAMS, TAG_NOT_FOUND, SENSITIVE_WORD_EXISTS, TAG_PROVERBS_NOT_FOUND, \
    SYSTEM_ERROR, TAG_PROVERBS_LIMIT_NOT_RELEASE
from starmachine.model.user import User
from starmachine.model.tag import Tag
from starmachine.model.consts import USER_CREATED, USER_DAILY_RECEIVE_LIKE_COUNT
from starmachine.sensitive_word.filter import filter, filter_name
from starmachine.model.tag_proverbs import TagProverbs, TagProverbsLiked

logger = logging.getLogger(__name__)

class TagHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        tag_id = self.get_argument('tag_id', '')
        if not tag_id:
            return self.error(MISSING_PARAMS)

        tag = Tag.get(tag_id)
        if not tag:
            return self.error(TAG_NOT_FOUND)

        data = {
            'status': 0,
            'data': tag.jsonify()
        }

        return self.render(data)


    @check_access_token
    def post(self, *args, **kwargs):
        try:
            tag_name = self.get_argument('tag_name')
            # source = self.get_argument('source', USER_CREATED)
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        if filter.check_sensitive(tag_name) or filter_name.check_sensitive(tag_name):
            return self.error(SENSITIVE_WORD_EXISTS)

        tag = Tag.get_by_name(tag_name)
        if not tag:
            tag_id = Tag.add(tag_name, USER_CREATED)
            tag = Tag.get(tag_id)

        data = {
            'status': 0,
            'data': tag.jsonify()
        }

        return self.render(data)


class TagListHandler(APIBaseHandler):

    @check_api_key
    def get(self):
        count = int(self.get_argument('count', 6))
        tags = Tag.get_random_list(count)
        data = {
            'status': 0,
            'data': [tag.jsonify() for tag in tags]
        }

        return self.render(data)


class TagProverbsHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            proverbs = self.get_argument('proverbs')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        if TagProverbs.has_time_limit(user_id):
            return self.error(TAG_PROVERBS_LIMIT_NOT_RELEASE)

        try:
            proverbs = TagProverbs.add(user_id, proverbs)
        except Exception as e:
            logger.error(u'投稿标签箴言失败呢。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
        })


class TagProverbsListHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        count = int(self.get_argument('count', 1))
        user = User.get(user_id)
        proverbs = TagProverbs.get_pass_proverb()
        return self.render({
            'status': 0,
            'data': [proverb.jsonify(user) for proverb in proverbs]
        })


class TagProverbsLikedHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            proverbs_id = self.get_argument('proverbs_id')
        except AttributeError:
            return self.error(MISSING_PARAMS)

        proverbs = TagProverbs.get(proverbs_id)
        if not proverbs:
            return self.error(TAG_PROVERBS_NOT_FOUND)

        try:
            liked_count = TagProverbsLiked.add(user_id, proverbs_id, proverbs.creator_id)
            has_liked = TagProverbsLiked.has_liked(user_id, proverbs_id)
        except Exception as e:
            logger.error(u'添加点赞失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
            'data': {
                'has_liked': bool(has_liked),
                'liked_count': liked_count,
            }
        })





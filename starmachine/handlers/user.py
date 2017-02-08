# coding: utf-8

from __future__ import division
import json
import calendar
import logging
from datetime import datetime, timedelta
from tornado.web import MissingArgumentError
from starmachine.lib.redis_cache import CacheManager
from starmachine.handlers.base import APIBaseHandler
from starmachine.model.user import User, UserAddress, UserPaymentCode, UserBind
from starmachine.model.user_auth import UserAuth
from starmachine.model.verify import Verify
from starmachine.model.room_user import RoomUser, RoomBlackUser
from starmachine.model.room import Room, RoomQuestion, RoomQuestionOption
from starmachine.model.tag import Tag
from starmachine.model.user_tag import UserTag
from starmachine.model.city import City
from starmachine.model.consts import REGISTER_VERIFY_CODE_TYPE, RESET_PASSWORD_VERIFY_CODE_TYPE, VALIDATE_VERIFY_CODE_TYPE, \
    VALIDATED_STATUS, WITHDRAW_ALIPAY, RESET_PAYMENT_CODE_TYPE, NEICE_TELEPHONES, PRESENT_NEICE, PRESENT_BEFORE_500, \
    VALIDATE_FAILED_STATUS, VALIDATING_STATUS, ROOM_USER_NORMAL, USER_INTEGRAL_FIRST_JOIN_ROOM, INTEGRAL_MAP, IOS_DEVICE, \
    ANDROID_DEVICE
from starmachine.model.user_validate import UserValidate
from starmachine.model.account import Account
from starmachine.model.order.reward_order import RewardOrder
from starmachine.model.withdraw import Withdraw, WithdrawAccount
from starmachine.model.room_tag import RoomTag
from starmachine.model.content import Content
from starmachine.model.wallet_record import WalletRecord
from starmachine.model.user_intergal import UserIntegral, UserIntegralRecord
from starmachine.lib.utils import gen_access_token, encrypt_password, check_access_token, check_api_key, \
    verify_telephone, init_pic_url
from starmachine.sensitive_word.filter import filter, filter_name
from starmachine.handlers.error import SYSTEM_ERROR, MISSING_PARAMS, EXIST_USER_TELEPHONE, MISMATCHED_PASSWORD, \
    USER_NOT_FOUND, MISMATCHED_VERIFY_CODE, ROOM_NOT_FOUND, ROOM_EXISTS_USER, CREATOR_NOT_NEED_JOIN_ROOM, \
    ROOM_USER_FULL, TAG_NOT_FOUND, USER_TAG_EXISTS, USER_NAME_EXISTS, CITY_NOT_FOUND, PHONE_NOT_RIGHT, ENTERED_PASSWORD_DIFFER, \
    RENT_NOT_ENOUGH, PAYMENT_CODE_NOT_EXISTS, PAYMENT_CODE_ERROR, USER_NOT_VALIDATED, USER_ALREADY_VALIDATED, ROOM_NOT_JOIN, \
    ACCOUNT_NOT_FOUND, ACCOUNT_BALANCE_NOT_ENOUGH, CREATOR_COULD_NOT_EXIT_ROOM, TELEPHONE_NOT_REGISTER, ENTERED_PAYMENT_CODE_DIFFER, \
    SENSITIVE_WORD_EXISTS, OPERATE_NOT_EFFECT, USER_IN_ROOM_BLACK_LIST, ALREADY_GET_DAILY_LOGIN_INTEGRAL, ADDRESS_NOT_FOUND, \
    ACCESS_NOT_ALLOWED, ROOM_QUESTION_ANSWER_LIMIT, ROOM_QUESTION_ANSWER_WRONG, ROOM_QUESTION_NOT_FOUND
from starmachine import settings
from starmachine.tools.sms import send_register_verify_code_sms
from starmachine.jobs.integral import handle_join_room_integral, handle_set_payment_code_integral, handle_room_user_over_500_integral, handle_daily_login
from starmachine.jobs.user import notify_change_password, notify_change_payment_code
from starmachine.model.rong import UserChatStatus
from starmachine.rong.rong_client import rong_client


logger = logging.getLogger(__name__)

class RegisterHandler(APIBaseHandler):

    @check_api_key
    def post(self, *args, **kwargs):
        try:
            telephone = self.get_argument('telephone')
            password = self.get_argument('password')
            verify_code = self.get_argument('verify_code')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        if not verify_telephone(telephone):
            return self.error(PHONE_NOT_RIGHT)

        # 检测是否有相同手机号的用户
        exist_user_telephone = User.exists_user_by_telephone(telephone)
        if exist_user_telephone:
            return self.error(EXIST_USER_TELEPHONE)

        # 检测验证码是否正确
        if str(verify_code) != str(Verify.get_verify_code(REGISTER_VERIFY_CODE_TYPE, telephone)):
            return self.error(MISMATCHED_VERIFY_CODE)

        password = encrypt_password(password)
        try:
            user_id = User.add(telephone, password)
            user_amount = User.get_user_count()
            account = Account.add(user_id, 0.00)
            # UserIntegral.add(user_id, 0)
            # if user_amount <= 500:
            #     account.add_balance(10.00)
            #     PresentedBalance.add(user_id, 10.00, PRESENT_BEFORE_500)
            #
            # if int(telephone) in NEICE_TELEPHONES:
            #     account.add_balance(10.00)
            #     PresentedBalance.add(user_id, 10.00, PRESENT_NEICE)

            access_token = gen_access_token(user_id)
            UserAuth.add(user_id, access_token)
            user = User.get(user_id)
            rst = {
                'status': 0,
                'data': {
                    'user': user.jsonify(),
                    'access_token': access_token,
                },
            }

            return self.render(rst)
        except Exception as e:
            logger.error(u'添加用户失败。Error:%s', e)
            return self.error(SYSTEM_ERROR)


class LoginHandler(APIBaseHandler):

    @check_api_key
    def post(self, *args, **kwargs):
        try:
            telephone = self.get_argument('telephone')
            password = self.get_argument('password')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        if not verify_telephone(telephone):
            return self.error(PHONE_NOT_RIGHT)

        password = encrypt_password(password)
        user = User.get_user_by_telephone(telephone)
        if not user:
            return self.error(TELEPHONE_NOT_REGISTER)

        if password != user.password:
            return self.error(MISMATCHED_PASSWORD)

        try:
            access_token = gen_access_token(user.id)
            UserAuth.update_access_token(user.id, access_token)
            rst = {
                'status': 0,
                'data': {
                    'user': user.jsonify(),
                    'access_token': access_token,
                },
            }
            return self.render(rst)
        except Exception as e:
            logger.error(u'用户登录失败。telephone:[%s], Error:[%s]' % (telephone, e))
            return self.error(SYSTEM_ERROR)


class LogoutHandler(APIBaseHandler):

    @check_access_token
    def post(self, *args, **kwargs):
        user_id = self.get_argument('user_id', '')
        if not user_id:
            return self.error(MISSING_PARAMS)

        try:
            user_auth = UserAuth.get_by_user_id(user_id)
            user_auth.clear_access_token()
            return self.render({
                'status': 0,
            })
        except Exception as e:
            logger.error(u'用户注销失败。User:[%s], Error:[%s]' % (user_id, e))
            return self.error(SYSTEM_ERROR)


class UserInfoHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        try:
            uid = self.get_argument('uid')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(uid)
        if not user:
            return self.error(USER_NOT_FOUND)

        data = {
            'status': 0,
            'data': user.jsonify(),
        }

        return self.render(data)

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            name = self.get_argument('name')
            tag_ids = self.get_argument('tag_ids', '[]')
            avatar_url = self.get_argument('avatar', '')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        if filter.check_sensitive(name) or filter_name.check_sensitive(name):
            return self.error(SENSITIVE_WORD_EXISTS)

        try:
            tag_ids = json.loads(tag_ids)
        except ValueError:
            tag_ids = []

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        if user.exists_user_name(name):
            return self.error(USER_NAME_EXISTS)

        try:
            avatar = json.loads(avatar_url)[0]
        except:
            avatar = avatar_url
        try:
            user.add_user_info(avatar, name, tag_ids)
            user = User.get(user_id)
            return self.render({
                'status': 0,
                'data': user.jsonify(),
            })
        except Exception as e:
            logger.error(u'添加完善用户信息失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)


class UserAvatarHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id', '')
            avatar_url = self.get_argument('avatar')
        except (MissingArgumentError):
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        try:
            avatar = json.loads(avatar_url)[0]
        except:
            avatar = avatar_url

        user.update(avatar=avatar)
        if UserChatStatus.is_flower_identity(user_id):
            rong_client.user_refresh(user_id, portrait_uri=init_pic_url(avatar))

        return self.render({
            'status': 0,
            'data': {
                'avatar': init_pic_url(avatar)
            }
        })


class ResetPasswordHandler(APIBaseHandler):

    def post(self):
        try:
            password = self.get_argument('password')
            confirm_password = self.get_argument('confirm_password')
            verify_code = self.get_argument('verify_code')
            telephone = self.get_argument('telephone')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        change_time = datetime.now()
        if password != confirm_password:
            return self.error(ENTERED_PASSWORD_DIFFER)

        if str(verify_code) != Verify.get_verify_code(RESET_PASSWORD_VERIFY_CODE_TYPE, telephone):
            return self.error(MISMATCHED_VERIFY_CODE)

        user = User.get_user_by_telephone(telephone)
        if not user:
            return self.error(TELEPHONE_NOT_REGISTER)

        password = encrypt_password(password)
        user.update(password=password, update_time=change_time)
        user_auth = UserAuth.get_by_user_id(user.id)
        user_auth.clear_access_token()
        notify_change_password.delay(user.id, change_time)
        return self.render({
            'status': 0,
        })


class UserNameUpdateHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            name = self.get_argument('name')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        if filter.check_sensitive(name) or filter_name.check_sensitive(name):
            return self.error(SENSITIVE_WORD_EXISTS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        try:
            if name != user.name:
                if user.exists_user_name(name):
                    return self.error(USER_NAME_EXISTS)
                else:
                    user.update(name=name)
                    if UserChatStatus.is_flower_identity(user_id):
                        rong_client.user_refresh(user_id, name=name)

            return self.render({
                'status': 0,
                'data': {
                    'name': name,
                }
            })
        except Exception as e:
            logger.error(u'修改用户名失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)


class UserRoleUpdateHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            role = self.get_argument('role')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        try:
            if role != user.role:
                user.update(role=role)

            return self.render({
                'status': 0,
                'data': {
                    'role': role
                }
            })
        except Exception as e:
            logger.error(u'修改用户性别失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)


class UserCityUpdateHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            city_id = int(self.get_argument('city_id'))
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        city = City.get(city_id)
        if not city:
            return self.error(CITY_NOT_FOUND)

        try:
            if city_id != user.city_id:
                user.update(city_id=city_id)

            return self.render({
                'status': 0,
                'data': {
                    'city': city.jsonify(),
                }
            })
        except Exception as e:
            logger.error(u'修改用户所在地失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)


class UserTagUpdateHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            tag_ids = self.get_argument('tag_ids')
            tag_ids = json.loads(tag_ids)
        except (MissingArgumentError, TypeError):
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        try:
            UserTag.update_tags(user_id, tag_ids)
            tags = UserTag.get_tags_by_user(user_id)
            return self.render({
                'status': 0,
                'data': {
                    'tags': [tag.jsonify() for tag in tags]
                }
            })
        except Exception as e:
            logger.error(u'修改用户标签信息失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)


class VerifyCodeHandler(APIBaseHandler):

    @check_api_key
    def post(self):
        try:
            telephone = self.get_argument('telephone')
            verify_type = int(self.get_argument('verify_type'))
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        if not verify_telephone(telephone):
            return self.error(PHONE_NOT_RIGHT)

        if verify_type == REGISTER_VERIFY_CODE_TYPE and User.exists_user_by_telephone(telephone):
            return self.error(EXIST_USER_TELEPHONE)

        verify_code = Verify.gen_verify_code()
        try:
            Verify.add_verify_code(verify_type, telephone, verify_code)
            if not settings.DEBUG:
                send_register_verify_code_sms.delay(telephone, verify_code)
            return self.render({
                'status': 0,
                'data': {
                    'telephone': telephone,
                    'verify_code': str(verify_code),
                }
            })
        except Exception as e:
            logger.warning(u'获取注册验证码失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)


class UserRoomHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        if int(room.creator_id) == int(user_id):
            return self.error(CREATOR_NOT_NEED_JOIN_ROOM)

        if RoomUser.room_exists_user(room_id, user_id):
            return self.error(ROOM_EXISTS_USER)

        if RoomBlackUser.is_room_black_user(room_id, user_id):
            return self.error(USER_IN_ROOM_BLACK_LIST)

        # 房主自身也属于房间成员之一
        if room.limit_user_number:
            room_user_amount = RoomUser.get_user_amount_by_room(room_id)
            if room_user_amount == room.limit_user_number:
                return self.error(ROOM_USER_FULL)

        if room.private_not_join:
            return self.error(ROOM_NOT_JOIN)

        if room.private_need_verify:
            room_question = RoomQuestion.get_question_by_room(room_id)
            return self.render({
                'status': 0,
                'data': room_question.jsonify() if room_question else None
            })
        else:
            try:
                RoomUser.add(room_id, user_id, ROOM_USER_NORMAL)
                # handle_join_room_integral.delay(user_id, room_id)
                # user_amount = room.user_amount
                # if user_amount == 500:
                #     handle_room_user_over_500_integral.delay(room.creator_id, room.id)

                return self.render({
                    "status": 0,
                    "data": room.jsonify(user),
                })
            except Exception as e:
                logger.error(u'用户加入房间失败。User:[%s] Room:[%s] Error:[%s]' % (user_id, room_id, e))
                return self.error(SYSTEM_ERROR)

    def delete(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        if int(room.creator_id) == int(user_id):
            return self.error(CREATOR_COULD_NOT_EXIT_ROOM)

        try:
            RoomUser.delete_room_user(room_id, user_id)
        except Exception as e:
            logger.error(u'用户退出房间失败。User:[%s], Room:[%s], Error:[%s]' % (user_id, room_id, e))

        return self.render({
            'status': 0,
        })


class UserRoomQuestionAnswerHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            room_id = self.get_argument('room_id')
            question_id = self.get_argument('question_id')
            option_id = self.get_argument('option_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        room = Room.get(room_id)
        question = RoomQuestion.get(question_id)
        option = RoomQuestionOption.get(option_id)
        if not question:
            return self.error(ROOM_QUESTION_NOT_FOUND)

        if int(question.room_id) != int(room_id) or option.question_id != int(question_id):
            return self.error(ACCESS_NOT_ALLOWED)

        user_room_question_24_hours_limit = 'user:%s:room:%s:question:24:limit'
        LIMIT_SECONDS = 24 * 60 * 60
        redis_key = user_room_question_24_hours_limit % (user_id, room_id)
        cache = CacheManager().cache
        if cache.exists(redis_key):
            return self.error(ROOM_QUESTION_ANSWER_LIMIT)

        cache.set(redis_key, 'true')
        cache.expire(redis_key, LIMIT_SECONDS)
        if option.is_right_answer:
            try:
                RoomUser.add(room_id, user_id, ROOM_USER_NORMAL)
                return self.render({
                    "status": 0,
                    "data": room.jsonify(user),
                })
            except Exception as e:
                logger.error(u'用户加入房间失败。User:[%s] Room:[%s] Error:[%s]' % (user_id, room_id, e))
                return self.error(SYSTEM_ERROR)
        else:
            return self.error(ROOM_QUESTION_ANSWER_WRONG)


class UserRoomPassVerifyHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            room_id = self.get_argument('room_id')
            user_id = self.get_argument('user_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        room = Room.get(room_id)
        if not room:
            return self.error(ROOM_NOT_FOUND)

        if int(room.creator_id) == int(user_id):
            return self.error(CREATOR_NOT_NEED_JOIN_ROOM)

        if RoomUser.room_exists_user(room_id, user_id):
            return self.error(ROOM_EXISTS_USER)

        if RoomBlackUser.is_room_black_user(room_id, user_id):
            return self.error(USER_IN_ROOM_BLACK_LIST)

        if room.private_not_join:
            return self.error(ROOM_NOT_JOIN)

        try:
            RoomUser.add(room_id, user_id, ROOM_USER_NORMAL)
            return self.render({
                "status": 0,
                "data": room.jsonify(),
            })
        except Exception as e:
            logger.error(u'用户加入房间失败。User:[%s] Room:[%s] Error:[%s]' % (user_id, room_id, e))
            return self.error(SYSTEM_ERROR)


class UserTagHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            tag_id = self.get_argument('tag_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        tag = Tag.get(tag_id)
        if not tag:
            return self.error(TAG_NOT_FOUND)

        if UserTag.exists_tag(user_id, tag_id):
            return self.error(USER_TAG_EXISTS)

        try:
            UserTag.add(user_id, tag_id)
            return self.render({
                'status': 0
            })
        except:
            return self.error(SYSTEM_ERROR)

    @check_access_token
    def get(self):
        try:
            user_id = self.get_argument('user_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        tags = UserTag.get_tags_by_user(user_id)
        return self.render({
            'status': 0,
            'data': [tag.jsonify() for tag in tags]
        })

    @check_access_token
    def delete(self):
        try:
            user_id = self.get_argument('user_id')
            tag_id = self.get_argument('tag_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        tag = Tag.get(tag_id)
        if not tag:
            return self.error(TAG_NOT_FOUND)

        try:
            UserTag.delete(user_id, tag_id)
            return self.render({
                'status': 0,
            })
        except:
            return self.error(SYSTEM_ERROR)


class UserRoomRecommendHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        try:
            user_id = self.get_argument('user_id', '')
            start = int(self.get_argument('start', 0))
            count = int(self.get_argument('count', 10))
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        has_joined_rooms = RoomUser.get_rooms_by_user(user_id, 0, 1)
        if has_joined_rooms:
            join_rooms = RoomUser.get_rooms_by_user_order_by_update_time(user_id, start, count)
            return self.render({
                'status': 0,
                'data': {
                    'recommend': 'joined',
                    'data': [room.jsonify(user) for room in join_rooms],
                }
            })

        user_tags = UserTag.get_tags_by_user(user_id)
        if user_tags:
            rooms = RoomTag.get_rooms_by_tags(user_tags)
            if rooms:
                rooms = sorted(rooms, key=lambda room: room.user_amount, reverse=True)
                end = start + count - 1
                rooms = rooms[start: end]
                return self.render({
                    'status': 0,
                    'data': {
                        'recommend': 'tags',
                        'data': [room.jsonify(user) for room in rooms],
                    }
                })

        rooms = Room.get_rooms_by_user_amount(start, count)
        return self.render({
            'status': 0,
            'data': {
                'recommend': 'hot',
                'data': [room.jsonify(user) for room in rooms if int(room.id) not in [100043, 100053]],
            }
        })


class UserRewardRankHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        start = int(self.get_argument('start', 0))
        count = int(self.get_argument('count', 10))
        rst = RewardOrder.get_user_reward_rank(start, count)
        data = []
        for d in rst:
            user = User.get(d.get('user_id'))
            data.append({
                'user': {
                    'id': user.id,
                    'name': user.user_name,
                    'avatar': user.avatar_url,
                },
                'reward_amount': d.get('amount') / 100,
            })

        return self.render({
            'status': 0,
            'data': data,
        })


class UserAddressHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        start = int(self.get_argument('start', 0))
        count = int(self.get_argument('count', 10))
        addresses = UserAddress.gets_by_user(user_id, start, count)
        return self.render({
            'status': 0,
            'data': [address.jsonify() for address in addresses],
        })

    @check_access_token
    def post(self):
        try:
            address_id = self.get_argument('address_id', '')
            user_id = self.get_argument('user_id')
            name = self.get_argument('name')
            district = self.get_argument('district')
            address = self.get_argument('address')
            telephone = self.get_argument('telephone')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        try:
            if not address_id:
                address_obj = UserAddress.add(user_id, district, name, telephone, address)
            else:
                address_obj = UserAddress.get(address_id)
                address_obj.update(name=name, district=district, address=address, telephone=telephone)
                address_obj = UserAddress.get(address_id)
            return self.render({
                'status': 0,
                'data': address_obj.jsonify(),
            })
        except Exception as e:
            logger.error(u'添加用户地址信息失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)

    @check_access_token
    def delete(self):
        try:
            user_id = int(self.get_argument('user_id'))
            address_id = self.get_argument('address_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        address = UserAddress.get(address_id)
        if not address:
            return self.error(ADDRESS_NOT_FOUND)

        if address.user_id != user_id:
            return self.error(ACCESS_NOT_ALLOWED)

        try:
            address.delete()
        except Exception as e:
            logger.error(u'删除地址信息失败。Address:[%s], Error:[%s]' % (address_id, e))
            return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
        })


class UserRewardHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        try:
            user_id = self.get_argument('user_id')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        result = []
        now = datetime.now()
        for delta in xrange(1, 5):
            year, month, max_day = self.add_months(now, delta)
            # start_day = datetime(year=year, month=month, day=1).strftime('%Y-%m-%d')
            end_day = (datetime(year=year, month=month, day=max_day) + timedelta(days=1)).strftime('%Y-%m-%d')
            amount = RewardOrder.get_reward_amount_by_user_and_date(user_id, end_day)
            result.append({
                'month': month,
                'amount': amount
            })

        return self.render({
            'status': 0,
            'data': result
        })

    def add_months(self, date, delta):
        month = date.month - 1 + delta
        year = date.year + month / 12
        month = month % 12 + 1
        cal = calendar.monthrange(year, month)
        return year, month, cal[1]


class UserGetRewardHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        try:
            user_id = self.get_argument('user_id')
            start = int(self.get_argument('start', 0))
            count = int(self.get_argument('count', 10))
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        reward_orders = RewardOrder.get_reward_orders_by_receiver(user_id, start, count)
        data = []
        for reward_order in reward_orders:
            creator = reward_order.creator
            d = {
                'creator': {
                    'id': creator.id,
                    'name': creator.user_name,
                    'avatar': creator.avatar_url,
                },
                'amount': float(reward_order.amount),
                'create_time': reward_order.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                'type': reward_order.type,
            }
            data.append(d)

        return self.render({
            'status': 0,
            'data': data,
        })


class PaymentCodeHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            payment_code = self.get_argument('payment_code')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        payment_code = encrypt_password(payment_code)
        payment_code_obj = UserPaymentCode.get_by_user(user_id)
        if payment_code_obj:
            return self.error(ACCESS_NOT_ALLOWED)
        else:
            try:
                UserPaymentCode.add(user_id, payment_code)
                handle_set_payment_code_integral.delay(user_id)
            except Exception as e:
                logger.error(u'添加用户支付密码失败。Error:[%s]' % e)
                return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
        })


class ResetPaymentCodeHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            payment_code = self.get_argument('payment_code')
            confirm_payment_code = self.get_argument('confirm_payment_code')
            verify_code = self.get_argument('verify_code')
            telephone = self.get_argument('telephone')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        if not verify_telephone(telephone):
            return self.error(PHONE_NOT_RIGHT)

        user = User.get(user_id)
        if not user:
            return self.error(USER_NOT_FOUND)

        if str(payment_code) != str(confirm_payment_code):
            return self.error(ENTERED_PAYMENT_CODE_DIFFER)

        if str(verify_code) != Verify.get_verify_code(RESET_PAYMENT_CODE_TYPE, telephone):
            return self.error(MISMATCHED_VERIFY_CODE)

        payment_code = encrypt_password(payment_code)
        payment_code_obj = UserPaymentCode.get_by_user(user_id)
        if not payment_code_obj:
            try:
                UserPaymentCode.add(user_id, payment_code)
                handle_set_payment_code_integral.delay(user_id)
            except Exception as e:
                logger.error(u'添加用户支付密码失败。Error:[%s]' % e)
                return self.error(SYSTEM_ERROR)
        else:
            try:
                change_time = datetime.now()
                payment_code_obj.update_payment_code(payment_code, change_time)
                notify_change_payment_code.delay(user_id, change_time)
            except Exception as e:
                logger.error(u'更新用户密码失败。Error:[%s]' % e)
                return self.error(SYSTEM_ERROR)

        return self.render({
            'status': 0,
            'data': {
                'has_payment_code': True,
            }
        })


class VerifyPaymentCodeHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            payment_code = str(self.get_argument('payment_code'))
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        user_payment_code = UserPaymentCode.get_by_user(user_id)
        if not user_payment_code:
            return self.error(PAYMENT_CODE_NOT_EXISTS)

        payment_code = encrypt_password(payment_code)
        if payment_code != str(user_payment_code.payment_code):
            return self.error(PAYMENT_CODE_ERROR)

        return self.render({
            'status': 0
        })


class WithdrawAccountHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        try:
            user_id = self.get_argument('user_id')
            name = self.get_argument('name')
            alipay_account = self.get_argument('alipay_account')
        except MissingArgumentError:
            return self.error(MISSING_PARAMS)

        try:
            WithdrawAccount.add(user_id, name, alipay_account)
            return self.render({
                'status': 0,
            })
        except Exception as e:
            logger.error(u'绑定提现账号失败。Error:[%s]' % e)
            return self.error(SYSTEM_ERROR)


class UserFootprintHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        start = int(self.get_argument('start', 0))
        count = int(self.get_argument('count', 10))
        contents = Content.get_contents_by_user(user_id, start, count)
        data = []
        for content in contents:
            if content:
                content_obj = content.jsonify()
                data.append({
                    'id': content_obj.get('id'),
                    'room_id': content.room_id,
                    'content_type': content.content_type,
                    'create_time': content.create_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'name': content_obj.get('text') or content_obj.get('name'),
                    'images': content_obj.get('images'),
                })

        return self.render({
            'status': 0,
            'data': data,
        })


class UserJoinedRoomsHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        target_user_id = self.get_argument('target_user_id')
        start = int(self.get_argument('start', 0))
        count = int(self.get_argument('count', 10))
        user = User.get(user_id)
        rooms = RoomUser.get_rooms_by_user(target_user_id, start, count)
        return self.render({
            'status': 0,
            'data': [room.jsonify(user) for room in rooms]
        })


class UserWalletRecordHandler(APIBaseHandler):

    @check_access_token
    def get(self):
        user_id = self.get_argument('user_id')
        start = int(self.get_argument('start', 0))
        count = int(self.get_argument('count', 10))
        records = WalletRecord.gets_by_user(user_id, start, count)
        return self.render({
            'status': 0,
            'data': [record.jsonify() for record in records],
        })


class UserDailyLoginIntegralHandler(APIBaseHandler):

    @check_access_token
    def post(self):
        user_id = self.get_argument('user_id')
        if UserIntegralRecord.daily_login_integral_enough(user_id):
            return self.error(ALREADY_GET_DAILY_LOGIN_INTEGRAL)

        handle_daily_login.delay(user_id)
        return self.render({
            'status': 0,
        })

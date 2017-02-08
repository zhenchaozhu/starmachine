# # coding: utf-8
#
# from starmachine.handlers.base import APIBaseHandler
# from starmachine.model.user_validate import UserValidate
# from starmachine.model.withdraw import WithDraw
# from starmachine.model.room import Room
# from starmachine.lib.utils import init_pic_url
#
# class UserValidateListHandler(APIBaseHandler):
#
#     def get(self):
#         page = self.get_argument('page', 0)
#         size = self.get_argument('size', 20)
#         user_validates = UserValidate.gets_all()
#         total_counts = UserValidate.amount()
#         rst = []
#         for user_validate in user_validates:
#             rst.append({
#                 'id': user_validate.id,
#                 'create_time': user_validate.create_time.strftime('%Y-%m-%d %H:%M:%S'),
#                 'telephone': user_validate.telephone,
#                 'name': user_validate.name,
#                 'id_card': user_validate.id_card,
#                 'id_card_front': init_pic_url(user_validate.id_card_front),
#                 'id_card_back': init_pic_url(user_validate.id_card_back),
#                 'status': user_validate.status,
#                 'reason': user_validate.reason,
#             })
#
#         return self.render({
#             'data': rst
#         })
#
# class WithdrawListHandler(APIBaseHandler):
#
#     def get(self):
#         page = self.get_argument('page', 0)
#         size = self.get_argument('size', 20)
#         withdraws = WithDraw.get_lists(page, size)
#         total_counts = WithDraw.get_amount()
#         return self.render({
#             'status': 0,
#             'data': {
#                 'withdraws': [withdraw.jsonify() for withdraw in withdraws],
#                 'recodeCount': total_counts,
#             }
#         })
#
#
# class RoomRecommendList(APIBaseHandler):
#
#     def get(self):
#         page = self.get_argument('page', 0)
#         size = self.get_argument('size', 20)
#         rooms = Room.gets_all()
#         rst = []
#         for room in rooms:
#             rst.append([
#                 room.name, room.creator.name, room.user_amount, room.star_fund, room.intro,
#                 room.create_time.strftime('%Y-%m-%d %H:%M:%S'), 1, 2, 'admin'
#             ])
#
#         return self.render({
#             'data': rst
#         })
#

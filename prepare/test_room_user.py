# coding: utf-8

from starmachine.model.room_user import RoomUser
from starmachine.model.user import User
from starmachine.model.room import Room

room_users = RoomUser.gets_all()
try:
    for room_user in room_users:
        room_id = room_user.room_id
        user_id = room_user.user_id
        room = Room.get(room_id)
        if room:
            if int(room.creator_id) == int(user_id):
                room_user.update(status=1)
except Exception as e:
    print e

# coding: utf-8

from starmachine.model.content import Content
from starmachine.model.room import Room
from starmachine.model.room_user import RoomUser

contents = Content.gets_all()
for content in contents:
    room = Room.get(content.room_id)
    room_id = content.room_id
    user_id = content.creator_id
    room_user = RoomUser.get_by_room_and_user(room_id, user_id)
    if not room_user:
        content.update(room_user_status=1)
    else:
        content.update(room_user_status=room_user.status)
    room.update(last_content_updated=content.create_time)
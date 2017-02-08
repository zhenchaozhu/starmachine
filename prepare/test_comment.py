# coding: utf-8

from starmachine.model.comment import Comment

comments = Comment.gets_all()
for comment in comments:
    parent_id = comment.parent_id
    if parent_id:
        parent_comment = Comment.get(parent_id)
        parent_user_id = parent_comment.user_id
        comment.update(parent_id=parent_user_id)
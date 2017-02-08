###数据样例
#### Room
{
    "id": id,
    "creator": 用户数据结构,
    "name": name,
    "intro": intro,
    "rent": rent, # 两位小数点
    "avatar_url": avatar_url,
    "limit_user_number': limit_user_number,
    "status": status,   # 0代表房间未公开，1代表房间公开
    "user_amount": user_amount,
    "balance": star_fund_balance, # 房间星基金，两位小数
    "create_time": create_time
}

###API
#### 创建房间
`POST /api/room/`

参数:
```
{
    "user_id": user_id,
    "name": name,
    "tag_ids": tag_ids,
    "intro": intro,
    "rent": rent,
    "avatar": avatar # 头像图片文件,
    "limit_user_number": limit_user_number # 默认人数限制为100人
}
```

返回:
```
{
    "status": 0,
    "data": 房间数据结构
}
```

`GET /api/room/`

参数:
```
{
    "user_id": user_id,
    "access_token": access_token,
    "room_id": room_id
}
```

返回:
```
{
    "status": 0,
    "data": 房间数据结构
}
```

#### 房间内容推送
`POST /api/room/push/`

参数:
```
{
    "user_id": user_id,
    "access_token": access_token,
    "room_id": room_id,
    "content_id": content_id
}
```

返回:
```
{
    "status": 0,
}
```
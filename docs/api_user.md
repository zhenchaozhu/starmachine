###数据样例
#### User
{
    "id": id,
    "telephone": telephone,
    "name": name,
    "role": role,
    "avatar": avatar,
    "intro": intro,
    "city": {
        "province_name": province_name,
        "name": name,
    },
    "join_rooms": [加入的房间数据结构],
    "created_rooms": [创建的房间的数据结构],
    "address_list": [地址信息],
    "tags": [标签信息]
}
APP_KEY = '0b07e8037029e05b2117b80a507da111'
APP_SECRET = '72ec644ae9c94cb2'

###API
#### 获取注册验证码接口
`POST /api/verify_code/`

参数:
```
{
    "app_key": APP_KEY,
    "app_secret": APP_SECRET,
    "telephone": telephone,
    "verify_type": verify_type # 1代表注册,2代表重置密码,3代表验证身份
}
```

返回:
```
{
    "status": 0,
    "data": {
        "telephone": telephone,
        "verify_code": verify_code
    }
}
```

#### 注册接口
`POST /api/register/`

参数:
```
{
    "telephone": telephone,
    "password": password,
    "verify_code": verify_code,
    "app_key": APP_KEY,
    "app_secret": APP_SECRET
}
```

返回:
```
{
    "status": 0,
    "data": {
        "user": 用户数据结构,
        "access_token": access_token
    }
}
```

#### 登录接口
`POST /api/user/login/`

参数:
```
{
    "telephone": telephone,
    "password": password,
    "app_key": APP_KEY,
    "app_secret": APP_SECRET
}
```

返回:
```
{
    "status": 0,
    "data": {
        "user": 用户数据结构,
        "access_token": access_token
    }
}
```

#### 登出接口
`POST /api/user/logout/`

参数:
```
{
    "user_id": user_id,
    "access_token": access_token
}
```

返回:
```
{
    "status": 0
}
```

#### 获取用户信息接口
`GET /api/user/`

参数:
```
{
    "user_id": user_id,
    "access_token": access_token
}
```

返回:
```
{
    "status": 0,
    "data": 用户数据结构
}
```

#### 添加用户信息接口
`POST /api/user/`

参数:
```
{
    "user_id": user_id,
    "access_token": access_token,
    "name": name,
    "tag_ids": tag_ids,
    "avatar": avatar # 头像文件
}
```

返回:
```
{
    "status": 0,
    "data": 用户数据结构
}
```

#### 更新头像
`POST /api/avatar/`

参数:
```
{
    "user_id": user_id,
    "access_token": access_token,
    "avatar": avatar
}
```

返回:
```
{
    "status": 0,
    "data": {
        "avatar": avatar
    }
}
```

#### 更新昵称
`POST /api/user/name/update/`

参数:
```
{
    "user_id": user_id,
    "access_token": access_token,
    "name": name
}
```

返回:
```
{
    "status": 0,
    "data": {
        "name": name
    }
}
```

#### 更新性别
`POST /api/user/role/update/`

参数:
```
{
    "user_id": user_id,
    "access_token": access_token,
    "role": role
}
```

返回:
```
{
    "status": 0,
    "data": {
        "role": role
    }
}
```

#### 更新所在城市
`POST /api/user/city/update/`

参数：
```
{
    "user_id": user_id,
    "access_token": access_token,
    "city_id": city_id
}
```

返回:
```
{
    "status": 0,
    "data": {
        "city_id": city_id
    }
}
```

#### 更新用户的标签
`POST /api/user/tags/update/`

参数:
```
{
    "user_id": user_id,
    "access_token": access_token,
    "tag_ids": tag_ids
}
```

返回:
```
{
    "status": 0,
    "data": {
        "tag_ids": tag_ids
    }
}
```

#### 更新用户密码
`POST /api/reset_password/`

参数:
```
{
    "user_id": user_id,
    "access_token": access_token,
    "password": password,
    "confirm_password": confirm_password,
    "verify_code": verify_code,
    "telephone": telephone
}
```

返回:
```
{
    "status": 0,
    "data": {
        "access_token": access_token,
    }
}
```

#### 游客房间推荐接口
`GET /api/visitor/room/recommend/`

参数:
```
{
    "page": page, # 默认是1
    "size": size  # 默认是20
}
```

返回:
```
{
    "status": 0,
    "data": 房间数据结构
}
```

#### 房间推荐接口
`GET /api/user/room/recommend/`

参数:
```
{
    "user_id": user_id, # 不是必须的
    "access_token": access_token, # 不是必须的
    "page": page, # 默认是1
    "size": size  # 默认是20
}
```

返回:
```
{
    "status": 0,
    "data": 房间数据结构
}
```

#### 加入房间
`POST /api/user/room/`

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
    "status": 0
}
```

#### 获取验证验证码
`POST /api/validate/verify_code/`

参数:
```
{
    "telephone": telephone,
    "user_id": user_id,
    "access_token": access_token
}
```

返回:
```
{
    "status": 0,
    "data": {
        "telephone": telephone,
        "verify_code": verify_code
    }
}
```

#### 提交用户资料进行验证
`POST /api/user/validate/`

参数:
```
{
    "user_id": user_id,
    "access_token": access_token,
    "telephone": telephone,
    "verify_code": verify_code,
    "id_card": id_card,
    "id_card_front": id_card_front,
    "id_card_back": id_card_back
}
```

返回:
```
{
    "status": 0,
    "data": 用户验证信息
}
```

#### 设备注册
`POST /api/device/`

参数:
```
{
    "user_id": user_id,
    "access_token": access_token,
    "device_token": device_token
}
```

返回:
```
{
    "status": 0,
    "data": device的数据结构
}
```

`GET /api/device/`

参数:
```
{
    "user_id": user_id,
    "access_token": access_token,
    "user_id": user_id
}
```

返回:
```
{
    "status": 0,
    "data": device的数据结构
}
```

#### 删除设备
`DELETE /api/device/`

参数:
```
{
    "user_id": user_id,
    "access_token": access_token,
    "user_id": user_id
}
```

返回:
```
{
    "status": 0,
}
```

#### 通知接口
`GET /api/user/notify/`

参数:
```
{
    "user_id": user_id,
    "access_token": access_token,
    "page": page,
    "size": size
}
```

返回:
```
{
    "status": 0,
    "data": 返回的通知
}
```


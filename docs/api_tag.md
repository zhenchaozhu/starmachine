###数据样例
#### Tag
{
    "id": id,
    "name": name,
    "source": source, # 1代表用户创建的，2代表往上抓取的
    "type": type,     # 1代表娱乐明星
    "create_time": create_time
}

###API
#### 创建标签
`POST /api/tag/`

参数:
```
{
    "tag_name": tag_name,
    "source": 1, # 可选
    "access_token": access_token,
    "user_id": user_id
}
```

返回:
```
{
    "status": 0,
    "data": 标签数据结构
}
```

#### 获取标签信息
`GET /api/tag/`

参数:
```
{
    "access_token": access_token,
    "user_id": user_id,
    "tag_id": tag_id
}
```

返回:
```
{
    "status": 0,
    "data": 标签数据结构
}
```

#### 获取标签列表信息
`GET /api/tag/list/`

参数:
```
{
    "access_token": access_token,
    "user_id": user_id,
    "count": count
}
```

返回:
```
{
    "status": 0,
    "data": [标签数据结构]
}
```
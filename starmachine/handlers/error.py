# coding: utf-8

# source 1代表系统错误，2代表用户错误
SYSTEM_ERROR = (1000, u'系统错误', 500, 1)
INVALID_API_KEY_OR_SECRET = (1001, u'错误的APIKEY和SECRET', 403, 1)
INVALID_ACCESS_TOKEN = (1002, u'身份验证标识已过期，请重新登录', 403, 2)

MISSING_PARAMS = (1100, u'缺少参数', 400, 1)
EXIST_USER_TELEPHONE = (1101, u'注册手机号码已经存在', 403, 2)
MISMATCHED_PASSWORD = (1102, u'用户密码错误', 403, 2)
MISMATCHED_VERIFY_CODE = (1103, u'验证码错误', 403, 2)
USER_NOT_FOUND = (1104, u'用户信息不存在', 404, 2)
ACCESS_NOT_ALLOWED = (1105, u'没有访问权限', 403, 2)
USER_TAG_EXISTS = (1106, u'用户已经拥有该标签', 403, 2)
USER_NAME_EXISTS = (1107, u'用户姓名已存在', 403, 2)
PHONE_NOT_RIGHT = (1108, u'手机号码不对', 403, 2)
ENTERED_PASSWORD_DIFFER = (1109, u'两次输入密码不一致', 403, 2)
ACCOUNT_NOT_FOUND = (1110, u'用户账户不存在', 404, 2)
ACCOUNT_BALANCE_NOT_ENOUGH = (1111, u'用户账户余额不足', 403, 2)
ACCOUNT_PAY_FAILED = (1112, u'余额支付失败', 403, 2)
PAYMENT_CODE_NOT_EXISTS = (1113, u'用户还未设置支付密码', 404, 2)
PAYMENT_CODE_ERROR = (1114, u'支付密码验证失败', 403, 2)
USER_NOT_VALIDATED = (1115, u'用户还未提交验证', 403, 2)
USER_ALREADY_VALIDATED = (1116, u'您已经通过身份验证，不必再进行提交', 403, 2)
TELEPHONE_NOT_REGISTER = (1117, u'该手机还未注册', 403, 2)
ENTERED_PAYMENT_CODE_DIFFER = (1118, u'两次输入的支付密码不一致', 403, 2)
PAYMENT_CODE_EXISTS = (1119, u'支付密码已经设置', 403, 2)
SENSITIVE_WORD_EXISTS = (1120, u'提交的信息存在敏感词', 403, 2)
OPERATE_NOT_EFFECT = (1121, u'提交的操作不是有效的', 403, 2)
ADDRESS_NOT_FOUND = (1122, u'地址不存在', 404, 2)
USER_BACKGROUND_NOT_FOUND = (1123, u'用户背景图不存在', 404, 2)
USER_ROOM_BACKGROUND_NOT_FOUND = (1124, u'用户房间背景图不存在', 404, 2)

TAG_NOT_FOUND = (1200, u'标签信息不存在', 404, 1)
TAG_PROVERBS_NOT_FOUND = (1201, u'标签箴言不存在', 404, 1)
TAG_PROVERBS_LIMIT_NOT_RELEASE = (1202, u'24小时之内已经投稿过标签箴言', 403, 2)

ROOM_NOT_FOUND = (1300, u'房间不存在', 404, 2)
ROOM_EXISTS_USER = (1301, u'用户已经加入房间', 403, 2)
CREATOR_NOT_NEED_JOIN_ROOM = (1302, u'房主不必加入房间', 403, 2)
ROOM_CREATE_ERROR = (1303, u'创建房间失败', 400, 1)
ROOM_NAME_COULD_NOT_NONE = (1304, u'房间名不能为空', 404, 2)
ROOM_NAME_EXISTS = (1305, u'房间已经存在', 400, 2)
ROOM_USER_FULL = (1306, u'房间已满员', 403, 2)
RENT_NOT_ENOUGH = (1307, u'所交房费不足', 403, 2)
ROOM_NOT_JOIN = (1308, u'房间不让用户加入', 403, 2)
CREATOR_COULD_NOT_EXIT_ROOM = (1309, u'房主不被允许离开房间', 403, 2)
ROOM_PUSH_OVER_LIMIT = (1310, u'房间推送次数超过限制', 403, 2)
ROOM_STAR_FUND_NOT_ENOUGH =(1311, u'房基金余额不足', 403, 2)
USER_IN_ROOM_BLACK_LIST = (1312, u'用户被房主加入房间黑名单', 403, 2)
USER_IN_ROOM_SILENT_LIST = (1313, u'用户被房主禁言', 403, 2)
ROOM_ADMIN_USER_OVER_LIMIT = (1314, u'房间管理员最多为2人', 403, 2)
ROOM_QUESTION_ANSWER_LIMIT = (1315, u'房间问题24小时内只能回答一次', 403, 2)
ROOM_QUESTION_ANSWER_WRONG = (1316, u'房间问题回答错误', 403, 2)
ROOM_QUESTION_NOT_FOUND = (1317, u'房间问题不存在', 404, 2)

CONTENT_NOT_FOUND = (1400, u'内容不存在', 404, 2)
CONTENT_NOT_NONE = (1401, u'发布内容不能为空', 400, 2)
COMMENT_NOT_FOUND = (1402, u'评论不存在', 404, 2)
REPLY_COMMENT_NOT_FOUND = (1403, u'回复的评论不存在', 404, 2)

INVALID_IMAGE_TYPE = (1500, u'上传图片格式不正确', 400, 2)

CITY_NOT_FOUND = (1600, u'城市信息不存在', 404, 2)

VOTE_NOT_FOUND = (1700, u'投票项目不存在', 404, 2)
VOTE_OPTION_NOT_FOUND = (1701, u'投票选项不存在', 404, 2)
OPTION_NOT_IN_VOTE = (1702, u'选项在投票中不存在', 404, 2)
USER_HAS_ALREADY_VOTED = (1703, u'用户已经投过票了', 403, 2)
OPTION_TEXT_TOO_LONG = (1704, u'选项长度超过限制', 403, 2)

DEVICE_NOT_FOUND = (1800, u'设备token不存在', 404, 1)

TRADE_NOT_FOUND = (1900, u'交易订单不存在', 404, 2)

WELFARE_NOT_FOUND = (2000, u'福利不存在', 404, 2)
WELFARE_HAS_ROBED = (2001, u'用户已经抢过该福利', 403, 2)
WELFARE_HAS_ROBED_OVER = (2002, u'福利已被抢完', 404, 2)
WELFARE_UNDER_WAY = (2003, u'抢福利活动还在进行中，无法下单', 403, 2)
WELFARE_HAS_ALREADY_DELIVERY = (2004, u'抢福利活动已经下单', 403, 2)
WELFARE_HAS_ALREADY_COMPLETE = (2005, u'抢福利订单已确认', 403, 2)

ALREADY_HAS_FOLLOWED = (2100, u'已经关注了该用户', 403, 2)
USER_NOT_FOLLOWED = (2101, u'还未关注该用户', 403, 2)

ALREADY_GET_DAILY_LOGIN_INTEGRAL = (2200, u'已经领取每日登录积分奖励', 403, 2)

GET_RONG_TOKEN_FAIL = (2300, u'获取融云token失败', 404, 2)
GROUP_NOT_FOUND = (2301, u'聊天群组不存在', 404, 2)
USER_IN_GROUP_BLACK_LIST = (2311, u'您已被拉入群组黑名单', 403, 2)
USER_ALREADY_IN_GROUP = (2312, u'您已经加入了该群组', 403, 2)
FLOWER_USER_NAME_EXISTS = (2313, u'用户设置的花名已经存在', 403, 2)
FLOWER_USER_NAME_UPDATE_OVER_LIMIT = (2314, u'一个月只能更新3次花名', 403, 2)
FLOWER_USER_INFO_NOT_SET = (2315, u'群组用户信息还未设置', 404, 1)
FLOWER_USER_INFO_EXISTS = (2316, u'群组用户信息已经存在', 403, 2)
USER_NOT_IN_GROUP = (2317, u'用户并未加入该群组', 404, 2)
GROUP_CREATED_COUNT_OVER_LIMIT = (2318, u'最多只能创建3个八卦群', 403, 2)
GROUP_IS_FULL = (2319, u'群组已满员', 403, 2)
GROUP_ENVELOPE_NOT_FOUND = (2320, u'群组红包不存在', 404, 2)
GROUP_ENVELOPE_HAS_OPENED = (2321, u'群组红包已经打开过', 403, 2)
GROUP_NAME_EXISTS = (2322, u'群组名称已经存在', 403, 2)
USER_JOIN_GROUP_OVER_LIMIT = (2323, u'最多只能加入10个群啦，您满啦！', 403, 2)
GROUP_NAME_LESS_MINIMUM_LIMIT = (2324, u'群名称字数小于2个汉字最小限制', 403, 2)
GROUP_NAME_OVER_MAXIMUM_LIMIT = (2325, u'群名称字数超过30个汉字最大限制', 403, 2)
GROUP_ANNOUNCEMENT_OVER_MAXIMUM_LIMIT = (2326, u'群公告字数超过50个汉字最大限制', 403, 2)
FLOWER_NAME_LESS_MINIMUM_LIMIT = (2327, u'花名小于最少1个汉字最小限制', 403, 2)
FLOWER_NAME_OVER_MAXIMUM_LIMIT = (2328, u'花名超过最多10个汉字最大限制', 403, 2)
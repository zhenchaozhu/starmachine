# coding: utf-8

# 用户默认级别
USER_NORMAL = 0 # 普通用户
USER_ADMIN = 1  # 管理员用户

# 用户默认信息
USER_DEFAULT_ROLE = 'm'
USER_DEFAULT_CITY = 100000

# 标签来源
USER_CREATED = 1
WEB_CRAWL = 2

TAG_TYPE_STAR = 1

# 订单状态
STATUS_PENDING = 'P'    # 交易初始状态
STATUS_SUSPEND = 'S'    # 因不确定因素，交易被停止
STATUS_REFUNDED = 'O'   # 已退款
STATUS_COMPLETE = 'C'   # 交易正常完成
STATUS_FAIL = 'F'       # 交易失败

VALID_STATUS = (STATUS_PENDING, STATUS_SUSPEND, STATUS_REFUNDED, STATUS_COMPLETE)

# 提现状态
WITHDRAW_WAITING = 'W' # 等待提现
WITHDRAW_PENDING = 'P' # 提现进行中
WITHDRAW_COMPLETE = 'C' # 完成提现
WITHDRAW_FAIL = 'F'    # 提现失败

# 支付方式
PAYMETHOD_UNSET = 0
PAYMETHOD_ALIPAY = 1
PAYMETHOD_WEIXIN = 2
PAYMETHOD_ACCOUNT = 3

# 订单类型
ORDER_CHARGE = 1
ORDER_ROOM = 2
ORDER_REWARD = 3
ORDER_ACTIVITY = 4
ORDER_GROUP_ENVELOPE = 5

# 房间用户默认人数限制
LIMIT_USER_NUMBER = -1 # 代表没有限制

# 房间公开,非公开交房费,非公开所有人不允许加入
ROOM_PUBLIC = 2
ROOM_PRIVATE_NEED_VERIFY = 1
ROOM_PRIVATE_NOT_JOIN = 0

# 房间成员状态
ROOM_USER_CREATOR = 1
ROOM_USER_ADMIN = 2
ROOM_USER_NORMAL = 3
ROOM_USER_SILENT = 4

# 房间最多允许管理员人数
ROOM_ADMIN_USER_MAX_AMOUNT = 2

# 内容开放or隐藏
CONTENT_PUBLIC = 1
CONTENT_HIDE = 0

# 房间内容内容类型
POSTS_TYPE = 1
VOTE_TYPE = 2
WELFARE_TYPE = 3

# 验证码类型
REGISTER_VERIFY_CODE_TYPE = 1
RESET_PASSWORD_VERIFY_CODE_TYPE = 2
VALIDATE_VERIFY_CODE_TYPE = 3
WITHDRAW_VERIFY_CODE_TYPE = 4
RESET_PAYMENT_CODE_TYPE = 5
WITHDRAW_ACCOUNT_CODE_TYPE = 6

# 通知状态
NOTIFY_UNREAD = 0
NOTIFY_READ = 1

# 通知类型
NOTIFY_TYPE_SYSTEM = 1    # 系统通知
NOTIFY_TYPE_LIKED = 2     # 点赞通知
NOTIFY_TYPE_COMMENT = 3   # 评论通知
NOTIFY_TYPE_REWARD = 4    # 打赏通知

# 通知动作
NOTIFY_ACTION_CONTENT_LIKED = 1
NOTIFY_ACTION_CONTENT_COMMENT = 2
NOTIFY_ACTION_CONTENT_REWARD = 3
NOTIFY_ACTION_COMMENT_REPLY = 4
# 福利模块通知
NOTIFY_ACTION_WELFARE_CREATED = 5
NOTIFY_ACTION_WELFARE_ROBED = 6
NOTIFY_ACTION_WELFARE_END = 7
NOTIFY_ACTION_WELFARE_ORDERED = 8
NOTIFY_ACTION_WELFARE_CONFIRMED = 9
# 房间模块
NOTIFY_ACTION_ROOM_REMOVED = 10
NOTIFY_ACTION_ROOM_SILENT= 11
# 个人模块
NOTIFY_ACTION_BE_FOLLOWED = 12
NOTIFY_ACTION_CHANGE_PASSWORD = 13
NOTIFY_ACTION_CHANGE_PAYMENT_CODE = 14
NOTIFY_ACTION_LEVEL_UP_THREE = 15
NOTIFY_ACTION_LEVEL_UP = 16
# 聊八卦
NOTIFY_ACTION_CHAT_REMOVED = 17
NOTIFY_ACTION_CHAT_ENVELOPE_REWARD = 18
NOTIFY_ACTION_CHAT_ENVELOPE_AST = 19
NOTIFY_ACTION_CHAT_SEEDS_REWARD = 20
NOTIFY_ACTION_CHAT_SEEDS_AST = 21

# 推送类型区分
PUSH_UNICAST_TYPE = 1
PUSH_LISTCAST_TYPE = 2

# 推送动作
PUSH_ACTION_GROUP_REWARD = 1

IOS_DEVICE = 1
ANDROID_DEVICE = 2
DEVICE_OS = {
    IOS_DEVICE: 'iOS',
    ANDROID_DEVICE: 'Android'
}
OTHER_DEVICE = 3

# 用户验证状态
VALIDATING_STATUS = 'P'
VALIDATE_FAILED_STATUS = 'F'
VALIDATED_STATUS = 'C'

# 提现账户类型
WITHDRAW_ALIPAY = 1
WITHDRAW_WXPAY = 2

# 房间推送
ROOM_PUSH_PENDING = 'P'
ROOM_PUSH_FAIL = 'F'
ROOM_PUSH_COMPLETE = 'C'

# 好友关注类型
FOLLOW_SINGLE_TYPE = 1
FOLLOW_BOTH_TYPE = 2

# 审核状态
CHECK_STATUS_PENDING = 'P'
CHECK_STATUS_PASS = 'C'
CHECK_STATUS_REJECT = 'R'

NEICE_TELEPHONES = [15810052914, 18638527170, 18600501940, 18502609955, 13469433278, 13131339314, 18501379157, 18774907009,
    15261595231, 18810860336, 18600668735, 18625293726, 18611519775, 18002187602, 18503089027, 15801631253, 18612035613,
    13829052013, 18600073782, 18620607636, 18101038396, 15897316999, 13926072808, 18098886901, 13911655759, 13488869977,
    13818198355, 18601361819, 18616008977, 18575585643, 18604248388, 15968759607, 13855253331, 18321376461, 18608991666,
    13825058185, 13942874668, 18701402213, 13876869799, 18576769602, 13570855241, 18675529955, 18566215285, 13405387432,
    18918681310, 13823513824, 15011705873, 18801617451, 18601287412, 18002570122, 18634872539, 15210554323, 13719278857,
    15821181236, 15225814261, 18675596968, 15360668993, 13717026637, 18537250856, 18818593365, 18601027202, 18566205791,
    15177413171, 18627440987, 13631531340, 13810350672, 18510088684, 13911551135, 13269677951, 18601357864, 13917780591,
    18515987857, 15711072388, 15510722268, 13331185289, 18217767515, 13881920397, 13810791013, 15920115526, 15820249101,
    13810350672, 15001100135, 18201638366, 13581930292, 13488793993, 18210488404, 15675375708, 1589510502, 13810946154]

PRESENT_NEICE = 1
PRESENT_BEFORE_500 = 2

# 钱包记录
WALLET_RECORD_REGISTER_SEND = 1
WALLET_RECORD_CHARGE = 2
WALLET_RECORD_ROOM_RENT = 3
WALLET_RECORD_REWARD_SEND = 4
WALLET_RECORD_REWARD_RECEIVE = 5
WALLET_RECORD_ROOM_REFUND = 6
WALLET_RECORD_GROUP_CHAT_REWARD = 7

# 房基金记录
STAR_FUND_RANK_SEND = 1
STAR_FUND_WELFARE_EXPAND = 2

# 福利类型
WELFARE_TYPE_SPECIAL = 1
WELFARE_TYPE_PHOTO = 2
WELFARE_TYPE_TICKETS = 3

# 福利邮费
WELFARE_POSTAGE = 10

# 福利状态
WELFARE_ROB_UNDER_WAY = 'P' # 抢福利活动进行中
WELFARE_ROB_END = 'O'       # 抢福利活动已结束,等待下单
WELFARE_ROB_END_AND_DELIVERY = 'D' # 抢福利活动结束并且已经下单

# 发福利订单状态
WELFARE_ORDER_PENDING = 'P' # 待下单
WELFARE_ORDER_ADDRESS_ERROR = 'E' # 地址有误请确认
WELFARE_ORDER_DELIVER = 'D' # 已下单
WELFARE_ORDER_COMFIRM = 'C' # 已完成

# 积分记录
# 首次
USER_INTEGRAL_FIRST_JOIN_ROOM = 1
USER_INTEGRAL_FIRST_SEND_LIKE = 2
USER_INTEGRAL_FIRST_SET_PAYMENT_CODE = 3
USER_INTEGRAL_FIRST_COMPLETE_VALIDATE = 4
USER_INTEGRAL_FIRST_ROOM_USER_OVER_500 = 5
# 长期
USER_INTEGRAL_DAILY_LOGIN = 6
USER_INTEGRAL_DAILY_CREATE_CONTENT = 7
USER_INTEGRAL_DAILY_DRAW_LOTS = 8
USER_INTEGRAL_DAILY_COMMENT = 9
USER_INTEGRAL_DAILY_VOTE = 10
USER_INTEGRAL_DAILY_GET_LIKED = 11
USER_INTEGRAL_DAILY_GET_REWARD = 12
USER_INTEGRAL_DAILY_SEND_REWARD = 13
USER_INTEGRAL_DAILY_CREATE_WELFARE = 14
USER_INTEGRAL_DAILY_ROB_WELFARE = 15
# 积分表
INTEGRAL_MAP = {
    'first_join_room': 1, # 首次加入房间可获得1积分
    'first_send_like': 1, # 首次发出赞可以获得1积分
    'first_set_payment_code': 5, # 首次成功设置支付密码可以获得5积分
    'first_complete_validate': 15, # 首次完成验证真实身份可以获得15积分
    'first_room_user_over_500': 100, # 创建的房间中任意一个房间总人数达到500人或以上，一次性奖励100积分，对第二个或之后达到500人的房间不再额外进行奖励
    'daily_login': 2, # 每个自然日当天首次登陆应用可以获得2积分
    'daily_create_content': 2, # 每成功发布1次内容（图、文、图文、投票、抽签结果）可获得2积分，每天通过发布内容最多可获得6积分
    'daily_draw_lots': 2, # 抽签一次可获得2积分，每天最多可通过抽签获得2积分，发布抽签结果参照发布内容积分规则
    'daily_comment': 1, # 成功评论1次可获得1积分，每天最多通过评论可以获得10积分
    'daily_vote': 1, # 每成功参与2次投票可获得1积分，不足2次不计分，每天最多可以通过参与投票获得3积分
    'daily_get_like': 1, # 每收到10个赞可获得1积分，每天通过赞最多可累计20积分
    'daily_get_reward': 1, # 在房间里每收到1次打赏可获得1积分，每天最多可以通过收到房间里的打赏获得15积分
    'daily_send_reward': 1, # 打赏一次可获得1积分，每天最多可通过打赏获得10积分
    'daily_create_welfare': 10, # 发福利可获得10积分，每天最多可以通过发放福利获得30积分
    'daily_rob_welfare': 10 # 抢福利可获得10积分，每天最多可通过参与活动获得30积分
}

# 举报类型
REPORT_ROOM_CONTENT = 1
REPORT_USER = 2
REPORT_GROUP = 3

# 房间成员状态
GROUP_USER_CREATOR = 1
GROUP_USER_NORMAL = 2

# 群聊奖励类型
CHAT_RED_ENVELOPE = 1
CHAT_MELON_SEEDS = 2

# 聊八卦聊天身份
CHAT_NORMAL_IDENTITY = 0
CHAT_FLOWER_IDENTITY = 1

GROUP_USER_LIMIT = 500

JOIN_GROUP_LIMIT = 10

# 花名随即头像
FLOWER_AVATAR_ARR = \
    ['cow', 'dog', 'dragon', 'horse', 'monkey', 'pig', 'rabbit', 'rat', 'sheep', 'snake', 'tiger', 'chicken']

# redis key
ROOM_TAG_CACHE_KEY = 'room:%s:tag'  # 房间的标签 redis sets
TAG_ROOM_CACHE_KEY = 'tag:%s:room'  # 相同标签的房间 redis sets

# 房主创建房间也会加入redis
ROOM_USER_CACHE_KEY = 'room:%s:user' # 房间用户集合 redis sorted sets 以加入房间的时间戳作为score
USER_ROOM_CACHE_KEY = 'user:%s:room' # 用户加入的房间集合 redis sorted sets 以加入房间的时间戳作为score
ROOM_USER_COUNT_KEY = 'room:user:count' # 房间用户排序 redis sorted sets 以加入房间的人数作为score

USER_TAG_CACHE_KEY = 'user:%s:tag'   # 用户拥有的标签 redis sets
TAG_USER_CACHE_KEY = 'tag:%s:user'   # 拥有相关标签的用户 redis sets

CONTENT_LIKED_CACHE_KEY = 'content:%s:liked'  # 给内容点赞的用户集合 redis sorted sets 以点赞的时间戳作为score
CONTENT_LIKED_RANK_KEY = 'content:liked:rank' # 内容点赞总数排名 redis sorted sets 以点赞总数作为score
POSTS_LIKED_RANK_KEY = 'posts:liked:rank'     # 帖子点赞总数排名 redis sorted sets 以点赞总数作为score 已不用
VOTE_LIKED_RANK_KEY = 'vote:liked:rank'       # 投票点赞总数排名 redis sorted sets 以点赞总数作为score 已不用
WELFARE_LIKED_RANK_KEY = 'welfare:liked:rank' # 福利点赞总数排名 redis sorted sets 以点赞总数作为score 已不用
VOTE_PEOPLE_CACHE_KEY = 'vote:%s:people'             # 投票用户集合
VOTE_OPTION_PEOPLE_CACHE_KEY = 'vote:option:%s:people'    # 投票选项用户集合

POSTS_CACHE_KEY = 'posts:%s'

CONTENT_COMMENT_CACHE_KEY = 'content:%s:comments' # 内容评论 redis lists 存储comment id

USER_CREATED_ROOM_KEY = 'user:%s:created_room' # 用户创建的房间 redis sets
USER_CREATED_CONTENT_KEY = 'user:%s:created:content' # 用户创建的内容 redis sets 以创建时间为score
# USER_CREATED_POSTS_KEY = 'user:%s:created:posts' # 用户创建的帖子 redis sets 以创建时间为score  先不用这个key了
# USER_CREATED_VOTE_KEY = 'user:%s:created:vote' # 用户创建的投票 redis sets 以创建时间为score    先不用这个key了
USER_LIKED_CONTENT_KEY = 'user:%s:liked:content' # 用户点赞的内容 redis sets 以点赞时间为score
USER_REWARD_CONTENT_KEY = 'user:%s:reward:content' # 用户打赏的内容 redis sets 以打赏时间为score

CONTENT_REWARD_AMOUNT_CACHE_KEY = 'content:reward:amount' # 内容打赏总额 redis sorted sets 以打赏总额作为score
CONTENT_REWARD_CACHE_KEY = 'content:%s:reward' # 给内容打赏的打赏订单列表 redis list
ROOM_USER_REWARD_CACHE_KEY = 'room:%s:user:reward'  # 房间用户打赏排行 redis sorted sets 以房间打赏总额作为score
USER_REWARD_RANK_CACHE_KEY = 'user:reward:rank' # 用户打赏总额排行 redis sorted sets 以打赏总额作为score

COMMENT_CACHE_KEY = 'comment:%s'

# 好友关系redis key
USER_FOLLOW_KEY = 'user:%s:follows'
USER_FANS_KEY = 'user:%s:fans'

ACTIVITY_USER_CACHE_KEY = 'activity:%s:user' # 活动用户集合 redis sorted sets 以加入活动的时间戳作为score
ACTIVITY_OPTION_USER_CACHE_KEY = 'activity_option:%s:user' # 活动选项用户集合 redis sorted sets 以加入活动的时间戳作为score
USER_ACTIVITY_OPTION_CACHE_KEY = 'user:%s:activity_option' # 用户活动集合 redis sorted sets 以加入活动的时间戳作为score

ROOM_INCREASE_RANK_CACHE_KEY = 'room:increase:rank:%s:%s' # 房间每月增量排行

USER_DAILY_RECEIVE_LIKE_COUNT = 'user:%s:date:%s:like' # 用户每日收到的点赞总数
USER_DAILY_VOTE_COUNT = 'user:%s:date:%s:vote' # 用户每日参加的投票总数

# 群组redis key
GROUP_USER_CACHE_KEY = 'group:%s:user' # 群组用户集合 redis sorted sets  以加入群组的时间戳作为score
USER_GROUP_CACHE_KEY = 'user:%s:group' # 用户加入的群组集合 redis sorted sets 以在群组的最后发言时间戳作为score，刚加入以加入时间作为最后发言时间
GROUP_USER_COUNT_KEY = 'group:user:count' # 群组用户排序 redis sorted sets 以加入群组的人数作为score

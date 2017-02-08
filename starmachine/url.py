# coding: utf-8

from starmachine.handlers.index import IndexHandler, AdvertiseHandler, RegistrationClauseHandler, XiaoShuoHandler, \
    GroupHotMessagePageHandler
from starmachine.handlers.user import RegisterHandler, LoginHandler, LogoutHandler, UserInfoHandler, VerifyCodeHandler,\
    UserAvatarHandler, UserRoomHandler, UserTagHandler, UserRoomRecommendHandler, UserNameUpdateHandler, \
    UserCityUpdateHandler, UserRoleUpdateHandler, UserTagUpdateHandler, ResetPasswordHandler, \
    UserAddressHandler, UserRewardHandler, VerifyPaymentCodeHandler, ResetPaymentCodeHandler, \
    UserRewardRankHandler, UserFootprintHandler, UserJoinedRoomsHandler, UserRoomPassVerifyHandler, \
    UserWalletRecordHandler, UserGetRewardHandler, UserDailyLoginIntegralHandler, UserRoomQuestionAnswerHandler, \
    PaymentCodeHandler
from starmachine.handlers.user_validate import UserValidateHandler, UserValidateNotifyHandler
from starmachine.handlers.tag import TagHandler, TagListHandler, TagProverbsHandler, TagProverbsLikedHandler, TagProverbsListHandler
from starmachine.handlers.room import RoomHandler, RoomContentHandler, RoomPushHandler, RoomSearch, RoomUserHandler, \
    RoomAvatarHandler, RoomNameUpdateHandler, RoomIntroUpdateHandler, RoomTagUpdateHandler, RoomStatusUpdateHandler, \
    RoomFundHandler, RoomPageShareHandler, RoomSerialUserHandler, RoomUserSilentHandler, RoomUserRemoveHandler, \
    RoomUserRewardRankHandler, RoomIncreaseRankHandler, RoomAdminHandler, RoomContentReportHandler, \
    RoomStarFundRecordHandler, RoomOrderUserHandler
from starmachine.handlers.content import PostsHandler, ContentLikedHandler, ContentHandler, ContentRewardHandler, ContentStatusHandler
from starmachine.handlers.comment import ContentCommentHandler
from starmachine.handlers.vote import VoteHandler, VoteJoinedHandler
from starmachine.handlers.device import DeviceHandler
from starmachine.handlers.notify import UserNotifyHandler, UserNotifyCountHandler
from starmachine.handlers.order import ChargeOrderHandler, AccountPayHandler, TradePayHandler
from starmachine.handlers.reward import RewardHandler
from starmachine.handlers.alipay import AlipayNotifyHandler, AlipayTransNotifyHandler
from starmachine.handlers.wxpay import WxPayNotifyAPI
from starmachine.handlers.qiniu import QiNiuTokenHandler, QiNiuNotifyHandler
# from starmachine.handlers.activity import ActivityHandler, ActivityJoinHandler, ActivityOptionHandler, \
#     ActivityReleaseHandler, ActivityQuitHandler
from starmachine.handlers.welfare import WelfareHandler, WelfareRobHandler, WelfareRobListHandler, WelfareRobConfirmHandler, \
    WelfareDeliveryHandler, WelfareOrderDeliveryHandler

# from starmachine.handlers.houtai import UserValidateListHandler, WithdrawListHandler, RoomRecommendList
# from starmachine.handlers.qrcode_login import QrCodePageHandler, QrCodeLoginHandler, QrCodeScanned, QrCodeConfirmed
from starmachine.handlers.leancloud import LeanCloudSignHandler
from starmachine.handlers.friendship import FriendShipHandler, UserFansHandler
from starmachine.handlers.lots import UserDrawLotsHandler
from starmachine.handlers.withdraw import WithdrawHandler, WithdrawHandleHandler, WithdrawAccountHandler
from starmachine.handlers.background import UserBackgroundHandler, UserRoomBackgroundHandler
from starmachine.handlers.rong import GetTokenHandler, GroupHandler, GroupUserHandler, GroupListHandler, \
    GroupSyncHandler, FlowerUserAvatarHandler, FlowerUserHandler, GroupSearchHandler, GroupMessageLikedHandler, \
    GroupUserListHandle, GroupUserRemoveHandler, GroupVoiceTimeHandler, UserJoinedGroupsHandler, GroupMessageNotify, \
    UserCreatedGroupsHandler, GroupHotMessageHandler, GroupSwitchIdentityHandler, GroupReportHandler, \
    GroupEnvelopeOpenHandler, GroupMessagePublishHandler, GroupAvatarUpdateHandler, GroupAnnouncementUpdateHandler, \
    GroupNameUpdateHandler
from starmachine.handlers.advice import AdviceHandler, UserAdviceListHandler

from starmachine.handlers.upload import Uploadhandler

from starmachine.handlers.wx_editor import  WxEditorHandler, WxEditorRegisterHandler

urls = [
    # 首页链接
    (r'/', IndexHandler),
    # 宣传页面
    (r'/advertise/', AdvertiseHandler),
    # 分享页面
    (r'/room/(\d+)/share/', RoomPageShareHandler),
    # 注册条款页面
    (r'/registration/clause/', RegistrationClauseHandler),
    # 小说
    (r'/xiaoshuo/', XiaoShuoHandler),
    # 微信编辑器
    (r'/editor/', WxEditorHandler),
    # 微信编辑器注册
    (r'/editor/register/', WxEditorRegisterHandler),
    # 微信图片上传
    (r'/upload/', Uploadhandler),
    # 群组神聊页面
    (r'/group/(\d+)/hot_message/', GroupHotMessagePageHandler),
    # 注册
    (r'/api/register/', RegisterHandler),
    # 获取验证码接口
    (r'/api/verify_code/', VerifyCodeHandler),
    # 登录
    (r'/api/login/', LoginHandler),
    # 注销
    (r'/api/logout/', LogoutHandler),
    # 每日登录奖励
    # (r'/api/daily/login_integral/', UserDailyLoginIntegralHandler),
    # 用户信息
    (r'/api/user/', UserInfoHandler),
    # 更改密码
    (r'/api/reset_password/', ResetPasswordHandler),
    # 设置,重置支付密码
    (r'/api/user/reset_payment_code/', ResetPaymentCodeHandler),
    # 添加支付密码
    (r'/api/user/payment_code/', PaymentCodeHandler),
    # 更新用户头像
    (r'/api/user/avatar/', UserAvatarHandler),
    # 更新用户昵称
    (r'/api/user/name/update/', UserNameUpdateHandler),
    # 更新用户标签
    (r'/api/user/tags/update/', UserTagUpdateHandler),
    # 更新用户性别
    (r'/api/user/role/update/', UserRoleUpdateHandler),
    # 更新用户所在地
    (r'/api/user/city/update/', UserCityUpdateHandler),
    # 添加, 更新, 删除用户的地址
    (r'/api/user/address/', UserAddressHandler),
    # 获取用户个人打赏详情
    (r'/api/user/reward/', UserRewardHandler),
    # 获取用户收到打赏详情
    (r'/api/user/get_reward/', UserGetRewardHandler),
    # 获取房间打赏详情
    (r'/api/room/fund/', RoomFundHandler),
    # 用户首页房间推荐
    (r'/api/user/room/recommend/', UserRoomRecommendHandler),
    # 房间排行
    (r'/api/room/increase/rank/', RoomIncreaseRankHandler),
    # 用户打赏总排行榜
    (r'/api/user/reward/rank/', UserRewardRankHandler),
    # 房间搜索
    (r'/api/room/search/', RoomSearch),
    # 房间创建
    (r'/api/room/', RoomHandler),
    # 更新房间头像
    (r'/api/room/avatar/', RoomAvatarHandler),
    # 更新房间名称
    (r'/api/room/name/update/', RoomNameUpdateHandler),
    # 更新房间标签
    (r'/api/room/tags/update/', RoomTagUpdateHandler),
    # 更新房间描述
    (r'/api/room/intro/update/', RoomIntroUpdateHandler),
    # 更新房间状态
    (r'/api/room/status/update/', RoomStatusUpdateHandler),
    # 加入,退出房间
    (r'/api/user/room/', UserRoomHandler),
    # 加入房间回答问题
    (r'/api/room_question/answer/', UserRoomQuestionAnswerHandler),
    # 通过验证加入房间
    ('/api/user/room/pass_verify/', UserRoomPassVerifyHandler),
    # 获取房间内容接口
    (r'/api/room/content/', RoomContentHandler),
    # 获取房间用户
    (r'/api/room/user/', RoomUserHandler),
    # 获取房间排序用户
    (r'/api/room/order_user/', RoomOrderUserHandler),
    # 房间打赏土豪榜
    (r'/api/room/user/reward/rank/', RoomUserRewardRankHandler),
    # 添加,删除房间管理员
    (r'/api/room/admin/', RoomAdminHandler),
    # 禁言房间用户
    (r'/api/room/user/silent/', RoomUserSilentHandler),
    # 删除拉黑房间用户
    (r'/api/room/user/remove/', RoomUserRemoveHandler),
    # 根据序号获取房间的用户
    (r'/api/room/serial/user/', RoomSerialUserHandler),
    # 添加标签,获取标签info
    (r'/api/tag/', TagHandler),
    # 随机获取标签列表数据
    (r'/api/tag/list/', TagListHandler),
    # 发布文字,图文,视频
    (r'/api/posts/', PostsHandler),
    # 发表评论,获取评论,删除评论
    (r'/api/comment/', ContentCommentHandler),
    # 对发表内容添加喜欢
    (r'/api/content/liked/', ContentLikedHandler),
    # 内容隐藏接口
    (r'/api/content/status/', ContentStatusHandler),
    # 用户标签
    (r'/api/user/tag/', UserTagHandler),
    # 用户提交身份验证
    (r'/api/user/validate/', UserValidateHandler),
    # 通过用户身份验证
    ('/api/user/validate/notify/', UserValidateNotifyHandler),
    # 创建投票，获取投票内容
    (r'/api/vote/', VoteHandler),
    # 提交投票
    (r'/api/vote/joined/', VoteJoinedHandler),
    # device注册
    (r'/api/device/', DeviceHandler),
    # 未读消息通知数量
    (r'/api/user/notify/count/', UserNotifyCountHandler),
    # notify接口
    (r'/api/user/notify/', UserNotifyHandler),
    # 房间内容推送
    (r'/api/room/content/push/', RoomPushHandler),
    # 余额充值
    (r'/api/charge/', ChargeOrderHandler),
    # 生成打赏订单
    (r'/api/reward/', RewardHandler),
    # 余额支付接口
    (r'/api/account/payment/', AccountPayHandler),
    # 支付宝回调
    (r'/api/alipay/notify/', AlipayNotifyHandler),
    # 微信回调
    (r'/api/wxpay/notify/', WxPayNotifyAPI),
    # 验证支付密码接口
    (r'/api/verify/payment_code/', VerifyPaymentCodeHandler),
    # 获取内容
    (r'/api/content/', ContentHandler),
    # 交易trade
    (r'/api/trade/payment/', TradePayHandler),
    # 获取内容打赏详情
    (r'/api/room/content/reward/', ContentRewardHandler),
    # 七牛申请token接口
    (r'/api/qiniu/token/', QiNiuTokenHandler),
    # 七牛回调接口
    (r'/api/qiniu/notify/', QiNiuNotifyHandler),
    # # 活动创建接口
    # (r'/api/activity/', ActivityHandler),
    # (r'/api/activity/option/', ActivityOptionHandler),
    # (r'/api/activity/release/', ActivityReleaseHandler),
    # # 参加活动
    # (r'/api/activity/join/', ActivityJoinHandler),
    # # 退出活动
    # (r'/api/activity/quit/', ActivityQuitHandler),
    # 关注，取消关注，我的关注
    (r'/api/user/follow/', FriendShipHandler),
    # 我的好友
    (r'/api/user/fans/', UserFansHandler),
    # 我的足迹
    (r'/api/user/footprint/', UserFootprintHandler),
    # 我加入的房间
    (r'/api/user/joined_rooms/', UserJoinedRoomsHandler),
    # 我的钱包明细
    (r'/api/user/wallet/record/', UserWalletRecordHandler),
    # 提现账号创建
    (r'/api/withdraw_account/', WithdrawAccountHandler),
    # 提现
    (r'/api/wallet/withdraw/', WithdrawHandler),
    # 提现确认
    (r'/api/wallet/withdraw/handle/', WithdrawHandleHandler),
    # 阿里提现回调通知
    (r'/api/wallet/withdraw/notify/', AlipayTransNotifyHandler),

    # 标签描述
    (r'/api/tag_proverbs/', TagProverbsHandler),
    # 获取随机箴言
    (r'/api/tag_proverbs/list/', TagProverbsListHandler),
    # 标签箴言点赞
    (r'/api/tag_proverbs/liked/', TagProverbsLikedHandler),

    # 房间内容举报
    (r'/api/room/content/report/', RoomContentReportHandler),
    # 房基金明细
    (r'/api/room/star_fund/record/', RoomStarFundRecordHandler),

    # 创建福利接口
    (r'/api/welfare/', WelfareHandler),
    # 抢福利接口
    (r'/api/welfare/rob/', WelfareRobHandler),
    # 抢福利明细
    (r'/api/welfare/rob/list/', WelfareRobListHandler),
    # 确认收到福利接口
    (r'/api/welfare/rob/confirm/', WelfareRobConfirmHandler),
    # 系统确认福利下单接口
    (r'/api/welfare/delivery/', WelfareDeliveryHandler),
    # 福利订单确认下单接口
    (r'/api/welfare_order/delivery/', WelfareOrderDeliveryHandler),

    # 参加抽签
    (r'/api/user/draw_lots/', UserDrawLotsHandler),

    # 用户背景设置
    ('/api/user/background/', UserBackgroundHandler),
    # 房间背景设置
    ('/api/user/room/background/', UserRoomBackgroundHandler),

    (r'/api/leancloud/sign/', LeanCloudSignHandler),

    # (r'/api/leancloud/peer/chat/', )

    # IM通知
    (r'/api/rong/get_token/', GetTokenHandler),
    # 设置，更新花名头像接口
    (r'/api/flower_user/avatar/', FlowerUserAvatarHandler),
    # 获取,设置花名信息接口
    (r'/api/flower_user/', FlowerUserHandler),
    # 创建, 获取群组信息
    (r'/api/rong/group/', GroupHandler),
    # 更新群组头像
    (r'/api/rong/group/avatar/', GroupAvatarUpdateHandler),
    # 更新群组公告
    (r'/api/rong/group/announcement/', GroupAnnouncementUpdateHandler),
    # 更新群组名称
    (r'/api/rong/group/name/', GroupNameUpdateHandler),
    # 获取群组用户接口
    (r'/api/rong/group/user_list/', GroupUserListHandle),
    # 同步融云群组信息
    (r'/api/rong/group/sync/', GroupSyncHandler),
    # 标记群聊用户最后发言时间
    (r'/api/rong/group/voice_time/', GroupVoiceTimeHandler),
    # (r'/api/rong/group/chat/', )
    # 获取群组列表
    (r'/api/rong/group/list/', GroupListHandler),
    # 加入, 退出群组
    (r'/api/rong/group/user/', GroupUserHandler),
    # 删除拉黑房间用户
    (r'/api/rong/group/user/remove/', GroupUserRemoveHandler),
    # 我加入的群组
    (r'/api/user/joined_groups/', UserJoinedGroupsHandler),
    # 我创建的群组
    (r'/api/user/created_groups/', UserCreatedGroupsHandler),
    # 群组搜索
    (r'/api/group/search/', GroupSearchHandler),
    # 群组聊天信息点赞
    (r'/api/group/message/liked/', GroupMessageLikedHandler),
    # 同步融云群组聊天信息
    (r'/api/group/message/notify/', GroupMessageNotify),
    # 热门群聊
    (r'/api/group/hot_message/', GroupHotMessageHandler),
    # 切换聊天身份
    (r'/api/group/switch/chat_identity/', GroupSwitchIdentityHandler),
    # 群组举报
    (r'/api/group/report/', GroupReportHandler),
    # 打开红包接口
    ('/api/group/envelope/open/', GroupEnvelopeOpenHandler),
    # 群组聊天
    ('/api/group/message/publish/', GroupMessagePublishHandler),

    # 投诉与建议
    (r'/api/advice/', AdviceHandler),
    (r'/api/user/advice/list/', UserAdviceListHandler),

    # 后台接口
    # 审核信息接口
    # (r'/api/user_validate/list/', UserValidateListHandler),
    # # 提现接口
    # (r'/api/withdraw/list/', WithdrawListHandler),
    # # 房间推荐接口
    # (r'/api/room/list/', RoomRecommendList)
]
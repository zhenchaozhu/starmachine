DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `telephone` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `name` varchar(255) DEFAULT NULL,
  `role` varchar(255) DEFAULT NULL,
  `avatar` varchar(255) DEFAULT NULL,
  `intro` varchar(10000) NOT NULL,
  `city_id` int(11) NOT NULL DEFAULT 100000,
  `status` tinyint(2) NOT NULL DEFAULT 0,
  `create_time` datetime NOT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT 10000 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `user_address`;
CREATE TABLE `user_address` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `district` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `telephone` varchar(255) NOT NULL,
  `address` varchar(255) NOT NULL,
  `create_time` datetime NOT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `user_auth`;
CREATE TABLE `user_auth` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `access_token` varchar(255) NOT NULL,
  `create_time` datetime NOT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `account`;
CREATE TABLE `account` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `balance` decimal(9, 2) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `tag`;
CREATE TABLE `tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `source` tinyint(1) NOT NULL,
  `type` int(11) NOT NULL DEFAULT 1,
  `create_time` datetime NOT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT 10000 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `user_tag`;
CREATE TABLE `user_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `room`;
CREATE TABLE `room` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `creator_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `intro` varchar(255) DEFAULT NULL,
  `rent` decimal(9, 2) NOT NULL DEFAULT 0,
  `avatar` varchar(255) DEFAULT NULL,
  `limit_user_number` int(11) NOT NULL DEFAULT 100,
  `status` tinyint(1) NOT NULL DEFAULT 1,
  `create_time` datetime NOT NULL,
  `update_time` datetime DEFAULT NULL,
  `last_content_updated` datetime,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT 100000 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `star_fund`;
CREATE TABLE `star_fund` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `room_id` int(11) NOT NULL,
  `balance` decimal(9, 2) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `room_tag`;
CREATE TABLE `room_tag` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `room_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `room_user`;
CREATE TABLE `room_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `room_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `join_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `content`;
CREATE TABLE `content` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `creator_id` int(11) NOT NULL,
  `room_id` int(11) NOT NULL,
  `content_type` int(11) NOT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 1,
  `create_time` datetime NOT NULL,
  `update_time` datetime,
  `last_comment_time` datetime,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT 10000 DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `posts`;
CREATE TABLE `posts` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `creator_id` int(11) NOT NULL,
  `room_id` int(11) NOT NULL,
  `text` char(255),
  `images` text,
  `video` char(255),
  `create_time` datetime NOT NULL,
  `update_time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT 10000 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `posts_liked`;
CREATE TABLE `posts_liked` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `posts_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `vote`;
CREATE TABLE `vote` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `creator_id` int(11) NOT NULL,
  `room_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `deadline` datetime NOT NULL,
  `create_time` datetime NOT NULL,
  `update_time` datetime,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `vote_option`;
CREATE TABLE `vote_option` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `vote_id` int(11) NOT NULL,
  `content` varchar(255) NOT NULL,
  `create_time` datetime NOT NULL,
  `update_time` datetime,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10000 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `vote_result`;
CREATE TABLE `vote_result` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `vote_id` int(11) NOT NULL,
  `option_id` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  `update_time` datetime,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `content_liked`;
CREATE TABLE `content_liked` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `content_id` int(11) NOT NULL,
  `content_type` tinyint(1) DEFAULT 1,
  `user_id` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `comment`;
CREATE TABLE `comment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `content_id` int(11) NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `text` text NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10000 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `user_validate`;
CREATE TABLE `user_validate` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `telephone` varchar(255) NOT NULL,
  `id_card` varchar(255) NOT NULL,
  `id_card_front` varchar(255),
  `id_card_back` varchar(255),
  `status` char(1) NOT NULL DEFAULT 'P',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `country`;
CREATE TABLE `country` (
  `id` int(11) NOT NULl AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `name_en` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=100000 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `province`;
CREATE TABLE `province` (
  `id` int(11) NOT NULl AUTO_INCREMENT,
  `country_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `name_en` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=100000 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `city`;
CREATE TABLE `city` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `province_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `name_en` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=100000 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `district`;
CREATE TABLE `district` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `city_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `name_en` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=100000 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `charge_order`;
CREATE TABLE `charge_order` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `creator_id` int(11) NOT NULL,
  `amount` decimal(9, 2) NOT NULL DEFAULT 0,
  `status` char(1) NOT NULL DEFAULT 'P',
  `create_time` datetime NOT NULL,
  `pay_time` datetime,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=100000 DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `reward_order`;
CREATE TABLE `reward_order` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `creator_id` int(11) NOT NULL,
  `receiver_id` int(11) NOT NULL,
  `type` tinyint(1) NOT NULL,
  `content_id` int(11) NOT NULL,
  `room_id` int(11) NOT NULL,
  `amount` decimal(9, 2) NOT NULL DEFAULT 0,
  `status` char(1) NOT NULL DEFAULT 'P',
  `create_time` datetime NOT NULL,
  `pay_time` datetime,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=100000 DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `room_order`;
CREATE TABLE `room_order` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `creator_id` int(11) NOT NULl,
  `room_id` int(11) NOT NULL,
  `amount` decimal(9, 2) NOT NULL DEFAULT 0,
  `status` char(1) NOT NULL DEFAULT 'P',
  `create_time` datetime NOT NULL,
  `pay_time` datetime,
  `refund_time` datetime,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=100000 DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `trade`;
CREATE TABLE `trade` (
  `id` varchar(32) NOT NULL,
  `order_id` int(11) NOT NULL,
  `order_type` tinyint(1) NOT NULL,
  `amount` decimal(9, 2) NOT NULL DEFAULT 0,
  `pay_method` tinyint(1) NOT NULL,
  `status` char(1) NOT NULL DEFAULT 'P',
  `create_time` datetime NOT NULL,
  `pay_time` datetime,
  `refund_time` datetime,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `trade_pay_notify`;
CREATE TABLE `trade_pay_notify` (
  `id` int(1) NOT NULL AUTO_INCREMENT,
  `trade_id` varchar(32) NOT NULL,
  `pay_method` tinyint(1) NOT NULL,
  `notify` text,
  `create_time` datetime NOT NULL,
  `update_time` datetime,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `notify`;
CREATE TABLE `notify` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sender_id` int(11) NOT NULL,
  `receiver_id` int(11) NOT NULL,
  `action` int(3) NOT NULL DEFAULT 1,
  `target_id` int(11) NOT NULL,
  `notify_type` tinyint(1) NOT NULL DEFAULT 1,
  `extra` int(11) DEFAULT NULL,
  `extra_info` varchar(255) DEFAULT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 0,
  `create_time` datetime NOT NULL,
  `read_time` datetime,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `user_payment_code`;
CREATE TABLE `user_payment_code` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `payment_code` varchar(255) NOT NULL,
  `create_time` datetime NOT NULL,
  `update_time` datetime,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `device`;
CREATE TABLE `device` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `device_token` varchar(128) NOT NULL,
  `os` tinyint(1) NOT NULL,
  `create_time` datetime NOT NULL,
  `update_time` datetime,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `room_push`;
CREATE TABLE `room_push` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `room_id` int(11) NOT NULL,
  `content_id` int(11),
  `push_time` datetime NOT NULL,
  `status` char(1) NOT NULL DEFAULT 'P',
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `presented_balance`;
CREATE TABLE `presented_balance` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `amount` decimal(9, 2) NOT NULL DEFAULT 10,
  `type` tinyint(1) NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `user_follows`;
CREATE TABLE `user_follows` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `follow_id` int(11) NOT NULL,
  `follow_type` tinyint(1) NOT NULL DEFAULT 1,
  `create_time` datetime NOT NULL,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `user_fans`;
CREATE TABLE `user_follows` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `follow_id` int(11) NOT NULL,
  `follow_type` tinyint(1) NOT NULL DEFAULT 1,
  `create_time` datetime NOT NULL,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `room_question`;
CREATE TABLE `room_question` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `room_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `room_question_option`;
CREATE TABLE `room_question_option` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `question_id` int(11) NOT NULL,
  `text` varchar(255) NOT NULL,
  `is_right_answer` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `wallet_record`;
CREATE TABLE `wallet_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `source` int(2) NOT NULL,
  `order_type` tinyint(1),
  `order_id` int(11),
  `amount` decimal(9, 2) NOT NULL DEFAULT 0,
  `create_time` datetime NOT NULL,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `star_fund_record`;
CREATE TABLE `star_fund_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `room_id` int(11) NOT NULL,
  `source` int(2) NOT NULL,
  `amount` decimal(9, 2) NOT NULL DEFAULT 0,
  `create_time` datetime NOT NULL,
  `extra` int(11),
  `extra_info` varchar(255),
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `tag_proverbs`;
CREATE TABLE `tag_proverbs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `creator_id` int(11) NOT NULL,
  `proverbs` varchar(255) NOT NULL,
  `status` char(1) NOT NULL DEFAULT 'P',
  `create_time` datetime NOT NULL,
  `check_time` datetime,
  `extra` varchar(255),
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `user_integral`;
CREATE TABLE `user_integral` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `integral` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `user_integral_record`;
CREATE TABLE `user_integral_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `source` int(2) NOT NULL,
  `amount` int(11) NOT NULL DEFAULT 0,
  `integral` int(11) NOT NULL DEFAULT 0,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `withdraw_account`;
CREATE TABLE `withdraw_account` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `account_type` tinyint(1) NOT NULL,
  `account_name` varchar(255) NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `withdraw`;
CREATE TABLE `withdraw` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `withdraw_account_id` int(11) NOT NULL,
  `amount` decimal(9, 2) NOT NULL DEFAULT 0,
  `status` char(1) NOT NULL DEFAULT 'P',
  `create_time` datetime NOT NULL,
  `withdraw_time` datetime,
  `extra` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `withdraw_batch`;
CREATE TABLE `withdraw_batch` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `batch_no` varchar(32) NOT NULL,
  `withdraw_ids` text,
  `success_details` text,
  `fail_details` text,
  `status` char(1) NOT NULL DEFAULT 'p',
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `welfare`;
CREATE TABLE `welfare` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `creator_id` int(11) NOT NULL,
  `room_id` int(11) NOT NULL,
  `price` decimal(9, 2) NOT NULL DEFAULT 0,
  `count` int(11) NOT NULL DEFAULT 0,
  `name` varchar(100) NOT NULL,
  `start_time` datetime NOT NULL,
  `deadline` datetime NOT NULL,
  `images` text,
  `status` char(1) NOT NULL DEFAULT 'P',
  `create_time` datetime NOT NULL,
  `update_time` datetime,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `welfare_order`;
CREATE TABLE `welfare_order` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `welfare_id` int(11) NOT NULL,
  `address_id` int(11) NOT NULL,
  `status` char(1) NOT NULL DEFAULT 'P',
  `create_time` datetime NOT NULL,
  `delivery_time` datetime,
  `confirm_time` datetime,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `user_integral`;
CREATE TABLE `welfare_order` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `integral` int(11) NOT NULL DEFAULT 0
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `user_integral_record`;
CREATE TABLE `user_integral_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `source` int(2) NOT NULL,
  `amount` int(11) NOT NULL DEFAULT 0,
  `integral` int(11) NOT NULL DEFAULT 0,
  `create_date` date NOT NULL,
  `create_time` datetime NOT NULL,
  `extra` int(11) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `star_fund_presented`;
CREATE TABLE `star_fund_presented` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `room_id` int(11) NOT NULL,
  `amount` decimal(9, 2) NOT NULL DEFAULT 0,
  `intro` varchar(255),
  `create_time` datetime NOT NULL,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `user_background`;
CREATE TABLE `user_background` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11),
  `short_url` varchar(255),
  `create_time` datetime NOT NULL,
  `update_time` datetime,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `user_room_background`;
CREATE TABLE `user_room_background` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11),
  `room_id` int(11),
  `short_url` varchar(255),
  `create_time` datetime NOT NULL,
  `update_time` datetime,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `rong_token`;
CREATE TABLE `rong_token` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `token` varchar(255) NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY(`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `report`;
CREATE TABLE `report` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `reporter_id` int(11) NOT NULL,
  `report_type` tinyint(1) NOT NULL DEFAULT 1,
  `report_dist` int(11) NOT NULL,
  `status` char(1) NOT NULL DEFAULT 'P',
  `reason` varchar(50),
  `create_time` datetime NOT NULL,
  `check_time` datetime,
  `extra` varchar(50),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `rong_group`;
CREATE TABLE `rong_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `creator_id` int(11) NOT NULL,
  `avatar` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `announcement` varchar(255) NOT NULL,
  `limit_user` int(11) NOT NULL DEFAULT 1,
  `create_time` datetime NOT NULL,
  `update_time` datetime,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `rong_group_user`;
CREATE TABLE `rong_group_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 2,
  `join_time` datetime NOT NULL,
  `last_voice_time` datetime,
  `disturb` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `flower_user`;
CREATE TABLE `flower_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `name` varchar(255),
  `avatar` varchar(255),
  `create_time` datetime NOT NULL,
  `update_time` datetime,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `group_message`;
CREATE TABLE `group_message` (
  `id` varchar(64) NOT NULL,
  `creator_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `object_name` varchar(20),
  `channel_type` varchar(20),
  `content` text,
  `create_time` datetime NOT NULL,
  `liked_amount` int(11) NOT NULl DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `group_message_liked`;
CREATE TABLE `group_message_liked` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `message_id` varchar(64) NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `group_voice_time`;
CREATE TABLE `group_voice_time` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `voice_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `advice`;
CREATE TABLE `advice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `creator_id` int(11),
  `reply_user_id` int(11),
  `text` varchar(255) NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `room_black_user`;
CREATE TABLE `room_black_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `room_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `tag_proverbs_liked`;
CREATE TABLE `tag_proverbs_liked` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `proverbs_id` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `group_reward`;
CREATE TABLE `group_reward` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `receiver_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `message_id` varchar(64) NOT NULL,
  `liked_amount` int(11),
  `reward_type` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `group_envelope`;
CREATE TABLE `group_envelope` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `receiver_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `message_id` varchar(64) NOT NULL,
  `liked_amount` int(11),
  `amount` int(11),
  `status` char(1) NOT NULL DEFAULT 'P',
  `create_time` datetime NOT NULL,
  `receive_time` datetime,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `group_seeds`;
CREATE TABLE `group_seeds` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `receiver_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  `message_id` varchar(64) NOT NULL,
  `liked_amount` int(11) NOT NULL,
  `amount` int(11),
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `user_seeds`;
CREATE TABLE `user_seeds` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `seeds_amount` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `user_chat_status`;
CREATE TABLE `user_chat_status` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `status` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `group_black_user`;
CREATE TABLE `group_black_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

DROP TABLE IF EXISTS `xiaoshuo`;
CREATE TABLE `xiaoshuo` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `link_uri` varchar(1000),
  `img_uri` varchar(1000),
  `article_title` varchar(255),
  `article_desc` varchar(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

DROP TABLE IF EXISTS `xiaoshuo_focuspic`;
CREATE TABLE `xiaoshuo_focuspic` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `link_uri` varchar(1000),
  `img_uri` varchar(1000),
  `focus_desc` varchar(255),
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

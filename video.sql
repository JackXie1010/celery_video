/*
Navicat MySQL Data Transfer

Source Server         : xzj
Source Server Version : 50528
Source Host           : localhost:3306
Source Database       : video

Target Server Type    : MYSQL
Target Server Version : 50528
File Encoding         : 65001

Date: 2018-10-20 16:45:57
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for playlist
-- ----------------------------
DROP TABLE IF EXISTS `playlist`;
CREATE TABLE `playlist` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `name` varchar(23) NOT NULL,
  `youtube` varchar(80) DEFAULT NULL,
  `youku` varchar(80) DEFAULT NULL,
  `iqiyi` varchar(80) DEFAULT NULL,
  `bilibili` varchar(80) DEFAULT NULL,
  `oss` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`id`,`name`),
  UNIQUE KEY `n` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of playlist
-- ----------------------------
INSERT INTO `playlist` VALUES ('1', 'abc1', 'vAivHE-13iM', null, null, null, null);
INSERT INTO `playlist` VALUES ('2', 'yt_signature4', 'PLbTSKnD3It8rHN8omVlHs2tceTRvuMdTs', null, null, null, null);

-- ----------------------------
-- Table structure for playlist_details
-- ----------------------------
DROP TABLE IF EXISTS `playlist_details`;
CREATE TABLE `playlist_details` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `pid` varchar(50) DEFAULT NULL,
  `pl_expired` int(2) NOT NULL DEFAULT '0',
  `v_expire_t` int(25) DEFAULT NULL,
  `title` varchar(80) DEFAULT NULL,
  `img` text,
  `type` varchar(30) DEFAULT NULL,
  `plays` varchar(30) DEFAULT NULL,
  `intro` text,
  PRIMARY KEY (`id`),
  UNIQUE KEY `pid` (`pid`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of playlist_details
-- ----------------------------
INSERT INTO `playlist_details` VALUES ('1', 'vAivHE-13iM', '0', '1539601987', '《了不起的孩子》餛飩小王子劉明輝日包1萬個餛飩、淚灑現場。', '1539601816201.jpg', '未知', '250万次', null);

-- ----------------------------
-- Table structure for videos
-- ----------------------------
DROP TABLE IF EXISTS `videos`;
CREATE TABLE `videos` (
  `id` int(13) NOT NULL AUTO_INCREMENT,
  `pid` varchar(80) NOT NULL,
  `vid` int(12) NOT NULL,
  `vtitle` varchar(51) NOT NULL,
  `vimg` text,
  `vpurl` text,
  `vvurl` text,
  `oss_status` varchar(5) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`,`pid`,`vid`,`vtitle`),
  UNIQUE KEY `p_t` (`pid`,`vtitle`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Records of videos
-- ----------------------------
INSERT INTO `videos` VALUES ('1', 'vAivHE-13iM', '1', '《了不起的孩子》餛飩小王子劉明輝日包1萬個餛飩、淚灑現場。', 'https://i.ytimg.com/vi/UvuRUhwra9w/hqdefault.jpg?sqp=-oaymwEZCNACELwBSFXyq4qpAwsIARUAAIhCGAFwAQ==&rs=AOn4CLAqpJXrp1kFo_h6xg4HtgPwJvgJIg', 'UvuRUhwra9w.mp4', 'https://www.youtube.com/watch?v=UvuRUhwra9w', '0');
INSERT INTO `videos` VALUES ('3', 'vAivHE-13iM', '2', '【抖音】那些笑死人不償命的動物合集2。動物們開始侵略地球啦！只有你想不到、沒有動物做不到的事。', 'https://i.ytimg.com/vi/LfatijnTXLY/hqdefault.jpg?sqp=-oaymwEZCNACELwBSFXyq4qpAwsIARUAAIhCGAFwAQ==&rs=AOn4CLBhLhQmx-0rqxaWQAxxkF4FEc05Vw', 'LfatijnTXLY.mp4', 'https://www.youtube.com/watch?v=LfatijnTXLY', '0');
INSERT INTO `videos` VALUES ('4', 'vAivHE-13iM', '3', '寵物狗狗界中的搞笑擔當，搞笑從來都是認真的！', 'https://i.ytimg.com/vi/eq6uVigeFs0/hqdefault.jpg?sqp=-oaymwEZCNACELwBSFXyq4qpAwsIARUAAIhCGAFwAQ==&rs=AOn4CLD79cdunReqQYUDxuoImhwVKEG2MA', 'eq6uVigeFs0.mp4', 'https://www.youtube.com/watch?v=eq6uVigeFs0', '0');

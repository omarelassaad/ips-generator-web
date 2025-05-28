
BEGIN TRANSACTION;

/*
* django_migrations
*/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[django_migrations]') AND type in (N'U'))
DROP TABLE [dbo].[django_migrations]
GO

CREATE TABLE "django_migrations" (
	id [int] IDENTITY(1,1) NOT NULL, 
	app varchar(255) NOT NULL, 
	name varchar(255) NOT NULL, 
	applied datetime NOT NULL,
	PRIMARY KEY (id)
);

INSERT INTO django_migrations VALUES('contenttypes','0001_initial', CONVERT(DATETIME, '2024-06-07 15:42:29'));

INSERT INTO django_migrations VALUES('auth','0001_initial',CONVERT(DATETIME, '2024-06-07 15:42:29'));
INSERT INTO django_migrations VALUES('admin','0001_initial',CONVERT(DATETIME, '2024-06-07 15:42:29'));
INSERT INTO django_migrations VALUES('admin','0002_logentry_remove_auto_add',CONVERT(DATETIME, '2024-06-07 15:42:29'));
INSERT INTO django_migrations VALUES('admin','0003_logentry_add_action_flag_choices',CONVERT(DATETIME, '2024-06-07 15:42:29'));
INSERT INTO django_migrations VALUES('contenttypes','0002_remove_content_type_name',CONVERT(DATETIME, '2024-06-07 15:42:29'));
INSERT INTO django_migrations VALUES('auth','0002_alter_permission_name_max_length',CONVERT(DATETIME, '2024-06-07 15:42:29'));
INSERT INTO django_migrations VALUES('auth','0003_alter_user_email_max_length',CONVERT(DATETIME, '2024-06-07 15:42:29'));
INSERT INTO django_migrations VALUES('auth','0004_alter_user_username_opts',CONVERT(DATETIME, '2024-06-07 15:42:29'));
INSERT INTO django_migrations VALUES('auth','0005_alter_user_last_login_null',CONVERT(DATETIME, '2024-06-07 15:42:29'));
INSERT INTO django_migrations VALUES('auth','0006_require_contenttypes_0002',CONVERT(DATETIME, '2024-06-07 15:42:29'));
INSERT INTO django_migrations VALUES('auth','0007_alter_validators_add_error_messages',CONVERT(DATETIME, '2024-06-07 15:42:29'));
INSERT INTO django_migrations VALUES('auth','0008_alter_user_username_max_length',CONVERT(DATETIME, '2024-06-07 15:42:29'));
INSERT INTO django_migrations VALUES('auth','0009_alter_user_last_name_max_length',CONVERT(DATETIME, '2024-06-07 15:42:29'));
INSERT INTO django_migrations VALUES('auth','0010_alter_group_name_max_length',CONVERT(DATETIME, '2024-06-07 15:42:29'));
INSERT INTO django_migrations VALUES('auth','0011_update_proxy_permissions',CONVERT(DATETIME, '2024-06-07 15:42:29'));
INSERT INTO django_migrations VALUES('auth','0012_alter_user_first_name_max_length',CONVERT(DATETIME, '2024-06-07 15:42:29'));
INSERT INTO django_migrations VALUES('ips','0001_initial',CONVERT(DATETIME, '2024-06-07 15:42:29'));
INSERT INTO django_migrations VALUES('sessions','0001_initial',CONVERT(DATETIME, '2024-06-07 15:42:29'));
INSERT INTO django_migrations VALUES('ips','0002_choosemyselfdata',CONVERT(DATETIME, '2024-06-18 23:02:25'));
INSERT INTO django_migrations VALUES('ips','0003_choosemyselfdata_version_number',CONVERT(DATETIME, '2024-06-25 03:27:32'));
INSERT INTO django_migrations VALUES('ips','0004_letpmchoosedata',CONVERT(DATETIME, '2024-07-02 05:08:01'));
INSERT INTO django_migrations VALUES('ips','0005_letpmchoosedata_additional_info',CONVERT(DATETIME, '2024-07-02 05:30:44'));
INSERT INTO django_migrations VALUES('ips','0006_alter_choosemyselfdata_strategy',CONVERT(DATETIME, '2024-07-02 19:38:36'));
INSERT INTO django_migrations VALUES('ips','0007_profile',CONVERT(DATETIME, '2024-07-02 22:17:06'));

/*
* django_content_type
*/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[django_content_type]') AND type in (N'U'))
DROP TABLE [dbo].[django_content_type]
GO

CREATE TABLE "django_content_type" (
	id [int] IDENTITY(1,1) NOT NULL, 
	app_label varchar(100) NOT NULL, 
	model varchar(100) NOT NULL,
	PRIMARY KEY (id)
	);
INSERT INTO django_content_type VALUES('admin','logentry');
INSERT INTO django_content_type VALUES('auth','permission');
INSERT INTO django_content_type VALUES('auth','group');
INSERT INTO django_content_type VALUES('auth','user');
INSERT INTO django_content_type VALUES('contenttypes','contenttype');
INSERT INTO django_content_type VALUES('sessions','session');
INSERT INTO django_content_type VALUES('ips','questionnaireresponse');
INSERT INTO django_content_type VALUES('ips','choosemyselfdata');
INSERT INTO django_content_type VALUES('ips','letpmchoosedata');
INSERT INTO django_content_type VALUES('ips','profile');

/*
* auth_group
*/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[auth_group]') AND type in (N'U'))
DROP TABLE [dbo].[auth_group]
GO

CREATE TABLE [dbo].[auth_group] (
	id [int] IDENTITY(1,1) NOT NULL, 
	name varchar(150) NOT NULL UNIQUE,
	PRIMARY KEY(id)
	);

/*
* auth_permission
*/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[auth_permission]') AND type in (N'U'))
DROP TABLE [dbo].[auth_permission]
GO

CREATE TABLE "auth_permission" (
	id [int] IDENTITY(1,1) NOT NULL, 
	content_type_id integer NOT NULL,-- REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, 
	codename varchar(100) NOT NULL, 
	name varchar(255) NOT NULL,
	PRIMARY KEY(id),
    CONSTRAINT FK_AuthPermission_ContentTypeId FOREIGN KEY (content_type_id)
    REFERENCES django_content_type(id)
	);
INSERT INTO auth_permission VALUES(1,'add_logentry','Can add log entry');
INSERT INTO auth_permission VALUES(1,'change_logentry','Can change log entry');
INSERT INTO auth_permission VALUES(1,'delete_logentry','Can delete log entry');
INSERT INTO auth_permission VALUES(1,'view_logentry','Can view log entry');
INSERT INTO auth_permission VALUES(2,'add_permission','Can add permission');
INSERT INTO auth_permission VALUES(2,'change_permission','Can change permission');
INSERT INTO auth_permission VALUES(2,'delete_permission','Can delete permission');
INSERT INTO auth_permission VALUES(2,'view_permission','Can view permission');
INSERT INTO auth_permission VALUES(3,'add_group','Can add group');
INSERT INTO auth_permission VALUES(3,'change_group','Can change group');
INSERT INTO auth_permission VALUES(3,'delete_group','Can delete group');
INSERT INTO auth_permission VALUES(3,'view_group','Can view group');
INSERT INTO auth_permission VALUES(4,'add_user','Can add user');
INSERT INTO auth_permission VALUES(4,'change_user','Can change user');
INSERT INTO auth_permission VALUES(4,'delete_user','Can delete user');
INSERT INTO auth_permission VALUES(4,'view_user','Can view user');
INSERT INTO auth_permission VALUES(5,'add_contenttype','Can add content type');
INSERT INTO auth_permission VALUES(5,'change_contenttype','Can change content type');
INSERT INTO auth_permission VALUES(5,'delete_contenttype','Can delete content type');
INSERT INTO auth_permission VALUES(5,'view_contenttype','Can view content type');
INSERT INTO auth_permission VALUES(6,'add_session','Can add session');
INSERT INTO auth_permission VALUES(6,'change_session','Can change session');
INSERT INTO auth_permission VALUES(6,'delete_session','Can delete session');
INSERT INTO auth_permission VALUES(6,'view_session','Can view session');
INSERT INTO auth_permission VALUES(7,'add_questionnaireresponse','Can add questionnaire response');
INSERT INTO auth_permission VALUES(7,'change_questionnaireresponse','Can change questionnaire response');
INSERT INTO auth_permission VALUES(7,'delete_questionnaireresponse','Can delete questionnaire response');
INSERT INTO auth_permission VALUES(7,'view_questionnaireresponse','Can view questionnaire response');
INSERT INTO auth_permission VALUES(8,'add_choosemyselfdata','Can add choose myself data');
INSERT INTO auth_permission VALUES(8,'change_choosemyselfdata','Can change choose myself data');
INSERT INTO auth_permission VALUES(8,'delete_choosemyselfdata','Can delete choose myself data');
INSERT INTO auth_permission VALUES(8,'view_choosemyselfdata','Can view choose myself data');
INSERT INTO auth_permission VALUES(9,'add_letpmchoosedata','Can add let pm choose data');
INSERT INTO auth_permission VALUES(9,'change_letpmchoosedata','Can change let pm choose data');
INSERT INTO auth_permission VALUES(9,'delete_letpmchoosedata','Can delete let pm choose data');
INSERT INTO auth_permission VALUES(9,'view_letpmchoosedata','Can view let pm choose data');
INSERT INTO auth_permission VALUES(10,'add_profile','Can add profile');
INSERT INTO auth_permission VALUES(10,'change_profile','Can change profile');
INSERT INTO auth_permission VALUES(10,'delete_profile','Can delete profile');
INSERT INTO auth_permission VALUES(10,'view_profile','Can view profile');

/*
* auth_group_permissions
*/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[auth_group_permissions]') AND type in (N'U'))
DROP TABLE [dbo].[auth_group_permissions]
GO

CREATE TABLE "auth_group_permissions" (
	id [int] IDENTITY(1,1) NOT NULL, 
	group_id integer NOT NULL, --REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED, 
	permission_id integer NOT NULL,-- REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY(id),
    CONSTRAINT FK_AuthGroupPermissions_AuthGroup FOREIGN KEY (group_id)
    REFERENCES auth_group(id),
    CONSTRAINT FK_AuthGroupPermissions_AuthPermission FOREIGN KEY (permission_id)
    REFERENCES auth_permission(id)
);

/*
* auth_user_groups
*/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[auth_user_groups]') AND type in (N'U'))
DROP TABLE [dbo].[auth_user_groups]
GO

CREATE TABLE "auth_user_groups" (
	id [int] IDENTITY(1,1) NOT NULL, 
	user_id integer NOT NULL, --REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, 
	group_id integer NOT NULL, --REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED
    PRIMARY KEY(id),
	CONSTRAINT FK_AuthUserGroups_AuthUser FOREIGN KEY (user_id)
    REFERENCES auth_group(id),
    CONSTRAINT FK_AuthUserGroups_AuthGroup FOREIGN KEY (group_id)
    REFERENCES auth_group(id)
	);

/*
* auth_user
*/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[auth_user]') AND type in (N'U'))
DROP TABLE [dbo].[auth_user]
GO

CREATE TABLE "auth_user" (
	"id" [int] IDENTITY(1,1) NOT NULL, 
	"password" varchar(128) NOT NULL, 
	"last_login" datetime NULL, 
	"is_superuser" bit NOT NULL, 
	"username" varchar(150) NOT NULL UNIQUE, 
	"last_name" varchar(150) NOT NULL, 
	"email" varchar(254) NOT NULL, 
	"is_staff" bit NOT NULL, 
	"is_active" bit NOT NULL, 
	"date_joined" datetime NOT NULL, 
	"first_name" varchar(150) NOT NULL,
	PRIMARY KEY(id));

-- 1
INSERT INTO auth_user VALUES('pbkdf2_sha256$600000$ZpRLqYVyfC1mIjJT7vGnoi$Z/WA8InOHi0vvXyWoA8T7kllPrKHmpkeg+rtW4CH6Jg=',CONVERT(DATETIME, '2025-02-04 22:12:20'),1,'bardi','','',1,1,CONVERT(DATETIME, '2024-06-07 15:42:38'),'');
-- 2
INSERT INTO auth_user VALUES('pbkdf2_sha256$600000$emGjzMAOd2dM4MxdiefV5k$uWgSCvZwGbgzYcM5ues1Ce+1j3geH0wFUcjWknQQl4I=',CONVERT(DATETIME, '2025-04-08 17:19:06'),1,'bardia','','',1,1,CONVERT(DATETIME, '2024-06-17 21:41:46'),'');
-- 3
INSERT INTO auth_user VALUES('pbkdf2_sha256$600000$61yEQONriCZl3PcE0lieVL$fx3BUhEDmDS1ooIr9olSR6azbOvlogJ9mO81EJdkA+c=',CONVERT(DATETIME, '2024-07-03 04:47:17'),0,'oelassaad','','oelassaad@aviso.ca',1,1,CONVERT(DATETIME, '2024-07-02 22:22:07'),'');
--4
INSERT INTO auth_user VALUES('pbkdf2_sha256$600000$djqK7tbS6kN7UwUlWrjXzw$Jj0qhvkAdXyf2pmXdx0incp9PK9QPK+KUKzzMaVJGQk=',CONVERT(DATETIME, '2025-04-16 15:43:37'),0,'bhiggins','Higgins','bhiggins@aviso.ca',0,1,CONVERT(DATETIME, '2025-04-08 17:18:28'),'Brian');

/*
* auth_user_user_permissions
*/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[auth_user_user_permissions]') AND type in (N'U'))
DROP TABLE [dbo].[auth_user_user_permissions]
GO

CREATE TABLE "auth_user_user_permissions" (
	id [int] IDENTITY(1,1) NOT NULL, 
	user_id integer NOT NULL,-- REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, 
	permission_id integer NOT NULL,-- REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY(id),
	CONSTRAINT FK_AuthUserUserPermissions_AuthUser FOREIGN KEY (user_id)
    REFERENCES auth_user(id),
    CONSTRAINT FK_AuthUserUserPermissions_AuthPermission FOREIGN KEY (permission_id)
    REFERENCES auth_permission(id)
	);

declare @userIdCount int = 1;
declare @permissionIdCount int = 1;

-- Give all four users all permissions
while @userIdCount < 5
BEGIN
	while @permissionIdCount < 41
	BEGIN
		INSERT INTO auth_user_user_permissions VALUES(@userIdCount,@permissionIdCount)
		SET @permissionIdCount = @permissionIdCount + 1
	END
	SET @userIdCount = @userIdCount + 1
	SET @permissionIdCount = 1
END

--INSERT INTO auth_user_user_permissions VALUES(21,5,21);
--INSERT INTO auth_user_user_permissions VALUES(22,5,22);
--INSERT INTO auth_user_user_permissions VALUES(23,5,23);
--INSERT INTO auth_user_user_permissions VALUES(24,5,24);
--INSERT INTO auth_user_user_permissions VALUES(25,5,25);
--INSERT INTO auth_user_user_permissions VALUES(26,5,26);
--INSERT INTO auth_user_user_permissions VALUES(27,5,27);
--INSERT INTO auth_user_user_permissions VALUES(28,5,28);
--INSERT INTO auth_user_user_permissions VALUES(29,5,29);
--INSERT INTO auth_user_user_permissions VALUES(30,5,30);
--INSERT INTO auth_user_user_permissions VALUES(31,5,31);
--INSERT INTO auth_user_user_permissions VALUES(32,5,32);
--INSERT INTO auth_user_user_permissions VALUES(33,5,33);
--INSERT INTO auth_user_user_permissions VALUES(34,5,34);
--INSERT INTO auth_user_user_permissions VALUES(35,5,35);
--INSERT INTO auth_user_user_permissions VALUES(36,5,36);
--INSERT INTO auth_user_user_permissions VALUES(37,5,37);
--INSERT INTO auth_user_user_permissions VALUES(38,5,38);
--INSERT INTO auth_user_user_permissions VALUES(39,5,39);
--INSERT INTO auth_user_user_permissions VALUES(40,5,40);
--INSERT INTO auth_user_user_permissions VALUES(41,1,1);
--INSERT INTO auth_user_user_permissions VALUES(42,1,2);
--INSERT INTO auth_user_user_permissions VALUES(43,1,3);
--INSERT INTO auth_user_user_permissions VALUES(44,1,4);
--INSERT INTO auth_user_user_permissions VALUES(45,1,5);
--INSERT INTO auth_user_user_permissions VALUES(46,1,6);
--INSERT INTO auth_user_user_permissions VALUES(47,1,7);
--INSERT INTO auth_user_user_permissions VALUES(48,1,8);
--INSERT INTO auth_user_user_permissions VALUES(49,1,9);
--INSERT INTO auth_user_user_permissions VALUES(50,1,10);
--INSERT INTO auth_user_user_permissions VALUES(51,1,11);
--INSERT INTO auth_user_user_permissions VALUES(52,1,12);
--INSERT INTO auth_user_user_permissions VALUES(53,1,13);
--INSERT INTO auth_user_user_permissions VALUES(54,1,14);
--INSERT INTO auth_user_user_permissions VALUES(55,1,15);
--INSERT INTO auth_user_user_permissions VALUES(56,1,16);
--INSERT INTO auth_user_user_permissions VALUES(57,1,17);
--INSERT INTO auth_user_user_permissions VALUES(58,1,18);
--INSERT INTO auth_user_user_permissions VALUES(59,1,19);
--INSERT INTO auth_user_user_permissions VALUES(60,1,20);
--INSERT INTO auth_user_user_permissions VALUES(61,1,21);
--INSERT INTO auth_user_user_permissions VALUES(62,1,22);
--INSERT INTO auth_user_user_permissions VALUES(63,1,23);
--INSERT INTO auth_user_user_permissions VALUES(64,1,24);
--INSERT INTO auth_user_user_permissions VALUES(65,1,25);
--INSERT INTO auth_user_user_permissions VALUES(66,1,26);
--INSERT INTO auth_user_user_permissions VALUES(67,1,27);
--INSERT INTO auth_user_user_permissions VALUES(68,1,28);
--INSERT INTO auth_user_user_permissions VALUES(69,1,29);
--INSERT INTO auth_user_user_permissions VALUES(70,1,30);
--INSERT INTO auth_user_user_permissions VALUES(71,1,31);
--INSERT INTO auth_user_user_permissions VALUES(72,1,32);
--INSERT INTO auth_user_user_permissions VALUES(73,1,33);
--INSERT INTO auth_user_user_permissions VALUES(74,1,34);
--INSERT INTO auth_user_user_permissions VALUES(75,1,35);
--INSERT INTO auth_user_user_permissions VALUES(76,1,36);
--INSERT INTO auth_user_user_permissions VALUES(77,1,37);
--INSERT INTO auth_user_user_permissions VALUES(78,1,38);
--INSERT INTO auth_user_user_permissions VALUES(79,1,39);
--INSERT INTO auth_user_user_permissions VALUES(80,1,40);

/*
* django_admin_log
*/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[django_admin_log]') AND type in (N'U'))
DROP TABLE [dbo].[django_admin_log]
GO

CREATE TABLE "django_admin_log" (
	id [int] IDENTITY(1,1) NOT NULL, 
	object_id text NULL, 
	object_repr varchar(200) NOT NULL, 
	action_flag int NOT NULL CHECK ("action_flag" >= 0), 
	change_message text NOT NULL, 
	content_type_id integer NULL,-- REFERENCES "django_content_type" ("id") DEFERRABLE INITIALLY DEFERRED, 
	user_id integer NOT NULL,-- REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, 
	action_time datetime NOT NULL,
	PRIMARY KEY(id),
	CONSTRAINT FK_DjangoAdminLog_DjangoContentTypeId FOREIGN KEY (content_type_id)
    REFERENCES django_content_type(id),
    CONSTRAINT FK_DjangoAdminLog_AuthUser FOREIGN KEY (user_id)
    REFERENCES auth_user(id));

--INSERT INTO django_admin_log VALUES(1,'2','kareem',3,'',4,1,'2024-07-02 22:21:52.724382');
--INSERT INTO django_admin_log VALUES(2,'4','oelassaad',3,'',4,1,'2024-07-02 22:21:58.235844');
--INSERT INTO django_admin_log VALUES(3,'5','oelassaad',2,'[]',4,1,'2024-07-02 22:24:32.656717');
--INSERT INTO django_admin_log VALUES(4,'5','oelassaad',2,'[{"changed": {"fields": ["Staff status"]}}]',4,1,'2024-07-02 22:24:50.597614');
--INSERT INTO django_admin_log VALUES(5,'5','oelassaad',2,'[{"changed": {"fields": ["User permissions"]}}]',4,1,'2024-07-02 22:25:14.089237');
--INSERT INTO django_admin_log VALUES(6,'2','oelassaad - Approved',2,'[{"changed": {"fields": ["Is approved"]}}]',10,1,'2024-07-02 22:26:59.126531');
--INSERT INTO django_admin_log VALUES(7,'5','oelassaad',2,'[{"changed": {"fields": ["User permissions"]}}]',4,5,'2024-07-02 22:37:53.196450');
--INSERT INTO django_admin_log VALUES(8,'3','bardi - Approved',2,'[{"changed": {"fields": ["Is approved"]}}]',10,1,'2024-07-02 22:45:48.969095');
--INSERT INTO django_admin_log VALUES(9,'1','bardi',2,'[{"changed": {"fields": ["User permissions"]}}]',4,1,'2024-07-02 22:45:58.457181');
--INSERT INTO django_admin_log VALUES(10,'4','bianca - Approved',2,'[{"changed": {"fields": ["Is approved"]}}]',10,1,'2024-07-03 02:59:54.506334');
--INSERT INTO django_admin_log VALUES(11,'6','bianca',3,'',4,1,'2024-07-03 03:00:54.221894');
--INSERT INTO django_admin_log VALUES(12,'7','biancab',3,'',4,1,'2024-07-03 03:00:54.229405');
--INSERT INTO django_admin_log VALUES(13,'42476','bardi - CMS Fee - CMS Fee',3,'',8,1,'2024-11-07 21:55:22.184097');
--INSERT INTO django_admin_log VALUES(14,'42475','bardi - Desired Rate - Desired Rate',3,'',8,1,'2024-11-07 21:55:22.191096');
--INSERT INTO django_admin_log VALUES(15,'42474','bardi - Comments - Comments',3,'',8,1,'2024-11-07 21:55:22.197100');
--INSERT INTO django_admin_log VALUES(16,'42473','bardi - Client Managed Holdings - ',3,'',8,1,'2024-11-07 21:55:22.204103');
--INSERT INTO django_admin_log VALUES(17,'42472','bardi -  - Cash',3,'',8,1,'2024-11-07 21:55:22.211103');
--INSERT INTO django_admin_log VALUES(18,'17183','oelassaad - CMS Fee - CMS Fee',3,'',8,1,'2024-11-07 21:55:22.218118');
--INSERT INTO django_admin_log VALUES(19,'17182','oelassaad - Desired Rate - Desired Rate',3,'',8,1,'2024-11-07 21:55:22.225123');
--INSERT INTO django_admin_log VALUES(20,'17181','oelassaad - Comments - Comments',3,'',8,1,'2024-11-07 21:55:22.232670');
--INSERT INTO django_admin_log VALUES(21,'17180','oelassaad - Client Managed Holdings - 234 - Cash',3,'',8,1,'2024-11-07 21:55:22.238676');
--INSERT INTO django_admin_log VALUES(22,'17179','oelassaad - 234 - Cash',3,'',8,1,'2024-11-07 21:55:22.245675');
--INSERT INTO django_admin_log VALUES(23,'5345','bardi - responsible_investing',3,'',7,1,'2024-11-07 21:55:39.069057');
--INSERT INTO django_admin_log VALUES(24,'5344','bardi - annual_withdrawal',3,'',7,1,'2024-11-07 21:55:39.076057');
--INSERT INTO django_admin_log VALUES(25,'5343','bardi - liquidity_needs',3,'',7,1,'2024-11-07 21:55:39.083057');
--INSERT INTO django_admin_log VALUES(26,'5342','bardi - time_horizon',3,'',7,1,'2024-11-07 21:55:39.090058');
--INSERT INTO django_admin_log VALUES(27,'5341','bardi - investment_knowledge',3,'',7,1,'2024-11-07 21:55:39.097061');
--INSERT INTO django_admin_log VALUES(28,'5340','bardi - volatility',3,'',7,1,'2024-11-07 21:55:39.105061');
--INSERT INTO django_admin_log VALUES(29,'5339','bardi - high_risk_opportunities',3,'',7,1,'2024-11-07 21:55:39.112568');
--INSERT INTO django_admin_log VALUES(30,'5338','bardi - reaction_to_drop',3,'',7,1,'2024-11-07 21:55:39.119569');
--INSERT INTO django_admin_log VALUES(31,'5337','bardi - recovery_period',3,'',7,1,'2024-11-07 21:55:39.126568');
--INSERT INTO django_admin_log VALUES(32,'5336','bardi - investment_loss',3,'',7,1,'2024-11-07 21:55:39.134568');
--INSERT INTO django_admin_log VALUES(33,'5335','bardi - risk_tolerance',3,'',7,1,'2024-11-07 21:55:39.141568');
--INSERT INTO django_admin_log VALUES(34,'5334','bardi - emergency_fund',3,'',7,1,'2024-11-07 21:55:39.148571');
--INSERT INTO django_admin_log VALUES(35,'5333','bardi - spending_needs',3,'',7,1,'2024-11-07 21:55:39.156573');
--INSERT INTO django_admin_log VALUES(36,'5332','bardi - income_savings',3,'',7,1,'2024-11-07 21:55:39.163079');
--INSERT INTO django_admin_log VALUES(37,'5331','bardi - annual_income',3,'',7,1,'2024-11-07 21:55:39.170579');
--INSERT INTO django_admin_log VALUES(38,'5330','bardi - investment_goals',3,'',7,1,'2024-11-07 21:55:39.177033');
--INSERT INTO django_admin_log VALUES(39,'5329','bardi - client_identifier',3,'',7,1,'2024-11-07 21:55:39.183593');
--INSERT INTO django_admin_log VALUES(40,'5328','bardi - advisor_name',3,'',7,1,'2024-11-07 21:55:39.189592');
--INSERT INTO django_admin_log VALUES(41,'4528','oelassaad - responsible_investing',3,'',7,1,'2024-11-07 21:55:39.196593');
--INSERT INTO django_admin_log VALUES(42,'4527','oelassaad - annual_withdrawal',3,'',7,1,'2024-11-07 21:55:39.202593');
--INSERT INTO django_admin_log VALUES(43,'4526','oelassaad - liquidity_needs',3,'',7,1,'2024-11-07 21:55:39.209593');
--INSERT INTO django_admin_log VALUES(44,'4525','oelassaad - time_horizon',3,'',7,1,'2024-11-07 21:55:39.216297');
--INSERT INTO django_admin_log VALUES(45,'4524','oelassaad - investment_knowledge',3,'',7,1,'2024-11-07 21:55:39.222296');
--INSERT INTO django_admin_log VALUES(46,'4523','oelassaad - volatility',3,'',7,1,'2024-11-07 21:55:39.228297');
--INSERT INTO django_admin_log VALUES(47,'4522','oelassaad - high_risk_opportunities',3,'',7,1,'2024-11-07 21:55:39.235297');
--INSERT INTO django_admin_log VALUES(48,'4521','oelassaad - reaction_to_drop',3,'',7,1,'2024-11-07 21:55:39.241300');
--INSERT INTO django_admin_log VALUES(49,'4520','oelassaad - recovery_period',3,'',7,1,'2024-11-07 21:55:39.249192');
--INSERT INTO django_admin_log VALUES(50,'4519','oelassaad - investment_loss',3,'',7,1,'2024-11-07 21:55:39.255191');
--INSERT INTO django_admin_log VALUES(51,'4518','oelassaad - risk_tolerance',3,'',7,1,'2024-11-07 21:55:39.262191');
--INSERT INTO django_admin_log VALUES(52,'4517','oelassaad - emergency_fund',3,'',7,1,'2024-11-07 21:55:39.268222');
--INSERT INTO django_admin_log VALUES(53,'4516','oelassaad - spending_needs',3,'',7,1,'2024-11-07 21:55:39.275226');
--INSERT INTO django_admin_log VALUES(54,'4515','oelassaad - income_savings',3,'',7,1,'2024-11-07 21:55:39.282225');
--INSERT INTO django_admin_log VALUES(55,'4514','oelassaad - annual_income',3,'',7,1,'2024-11-07 21:55:39.288226');
--INSERT INTO django_admin_log VALUES(56,'4513','oelassaad - investment_goals',3,'',7,1,'2024-11-07 21:55:39.295704');
--INSERT INTO django_admin_log VALUES(57,'4512','oelassaad - client_identifier',3,'',7,1,'2024-11-07 21:55:39.301704');
--INSERT INTO django_admin_log VALUES(58,'4511','oelassaad - advisor_name',3,'',7,1,'2024-11-07 21:55:39.308703');
--INSERT INTO django_admin_log VALUES('8','bhiggins',1,'[{"added": {}}]',4,3,'2025-04-08 17:18:28.298407');
--INSERT INTO django_admin_log VALUES('8','bhiggins',2,'[{"changed": {"fields": ["First name", "Last name", "Email address"]}}]',4,3,'2025-04-08 17:19:36.325253');
--INSERT INTO django_admin_log VALUES('7','bhiggins - Approved',2,'[{"changed": {"fields": ["Is approved"]}}]',10,3,'2025-04-08 17:20:28.683027');

/*
* ips_questionnaireresponse
*/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[ips_questionnaireresponse]') AND type in (N'U'))
DROP TABLE [dbo].[ips_questionnaireresponse]
GO

CREATE TABLE "ips_questionnaireresponse" (
	id [int] IDENTITY(1,1) NOT NULL, 
	question varchar(255) NOT NULL, 
	answer varchar(255) NULL, 
	score integer NOT NULL, 
	user_id integer NOT NULL,-- REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY(id),
    CONSTRAINT FK_IPSQUESTIONNAIRERESPONSE_AuthUser FOREIGN KEY (user_id)
    REFERENCES auth_user(id));


/*
* django_session
*/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[django_session]') AND type in (N'U'))
DROP TABLE [dbo].[django_session]
GO

CREATE TABLE "django_session" (
	session_key varchar(40) NOT NULL PRIMARY KEY, 
	session_data text NOT NULL, 
	expire_date datetime NOT NULL);

/*
* ips_letpmchoosedata
*/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[ips_letpmchoosedata]') AND type in (N'U'))
DROP TABLE [dbo].[ips_letpmchoosedata]
GO

CREATE TABLE "ips_letpmchoosedata" (
	id [int] IDENTITY(1,1) NOT NULL, 
	account_owner varchar(255) NOT NULL, 
	account_type varchar(255) NOT NULL, 
	amount decimal NOT NULL, 
	timestamp datetime NOT NULL, 
	user_id integer NOT NULL,-- REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, 
	additional_info varchar(255) NULL,
	PRIMARY KEY(id),
    CONSTRAINT FK_IPSLETPMCHOOSEDATA_AuthUser FOREIGN KEY (user_id)
    REFERENCES auth_user(id));


/*
* ips_choosemyselfdata
*/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[ips_choosemyselfdata]') AND type in (N'U'))
DROP TABLE [dbo].[ips_choosemyselfdata]
GO

CREATE TABLE "ips_choosemyselfdata" (
	id [int] IDENTITY(1,1) NOT NULL, 
	account_owner varchar(255) NOT NULL, 
	account_type varchar(50) NOT NULL, 
	amount decimal NOT NULL, 
	user_id integer NOT NULL,-- REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, 
	version_number varchar(50) NOT NULL, 
	strategy text NOT NULL,
	PRIMARY KEY(id),
    CONSTRAINT FK_IPSCHOOSEMYSELFDATA_AuthUser FOREIGN KEY (user_id)
    REFERENCES auth_user(id));

/*
* ips_profile
*/
IF  EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].["ips_profile"]') AND type in (N'U'))
DROP TABLE [dbo].[ips_profile]
GO

CREATE TABLE "ips_profile" (
	"id" [int] IDENTITY(1,1) NOT NULL, 
	"is_approved" bit NOT NULL, 
	"user_id" integer NOT NULL,-- UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED,
	PRIMARY KEY(id),
    CONSTRAINT FK_IPSPROFILE_AuthUser FOREIGN KEY (user_id)
    REFERENCES auth_user(id));

INSERT INTO ips_profile VALUES(1,1);
INSERT INTO ips_profile VALUES(1,1);
INSERT INTO ips_profile VALUES(0,1);
INSERT INTO ips_profile VALUES(1,1);

CREATE UNIQUE INDEX "auth_group_permissions_group_id_permission_id_0cd325b0_uniq" ON "auth_group_permissions" ("group_id", "permission_id");
CREATE INDEX "auth_group_permissions_group_id_b120cbf9" ON "auth_group_permissions" ("group_id");
CREATE INDEX "auth_group_permissions_permission_id_84c5c92e" ON "auth_group_permissions" ("permission_id");
CREATE UNIQUE INDEX "auth_user_groups_user_id_group_id_94350c0c_uniq" ON "auth_user_groups" ("user_id", "group_id");
CREATE INDEX "auth_user_groups_user_id_6a12ed8b" ON "auth_user_groups" ("user_id");
CREATE INDEX "auth_user_groups_group_id_97559544" ON "auth_user_groups" ("group_id");
CREATE UNIQUE INDEX "auth_user_user_permissions_user_id_permission_id_14a6b632_uniq" ON "auth_user_user_permissions" ("user_id", "permission_id");
CREATE INDEX "auth_user_user_permissions_user_id_a95ead1b" ON "auth_user_user_permissions" ("user_id");
CREATE INDEX "auth_user_user_permissions_permission_id_1fbb5f2c" ON "auth_user_user_permissions" ("permission_id");
CREATE INDEX "django_admin_log_content_type_id_c4bce8eb" ON "django_admin_log" ("content_type_id");
CREATE INDEX "django_admin_log_user_id_c564eba6" ON "django_admin_log" ("user_id");
CREATE UNIQUE INDEX "django_content_type_app_label_model_76bd3d3b_uniq" ON "django_content_type" ("app_label", "model");
CREATE UNIQUE INDEX "auth_permission_content_type_id_codename_01ab375a_uniq" ON "auth_permission" ("content_type_id", "codename");
CREATE INDEX "auth_permission_content_type_id_2f476e4b" ON "auth_permission" ("content_type_id");
CREATE INDEX "ips_questionnaireresponse_user_id_31871649" ON "ips_questionnaireresponse" ("user_id");
CREATE INDEX "django_session_expire_date_a5c62663" ON "django_session" ("expire_date");
CREATE INDEX "ips_letpmchoosedata_user_id_587f6224" ON "ips_letpmchoosedata" ("user_id");
CREATE INDEX "ips_choosemyselfdata_user_id_9c90e3c2" ON "ips_choosemyselfdata" ("user_id");
COMMIT;
--ROLLBACK

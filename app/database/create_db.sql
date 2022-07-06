create database Fast_api default CHARACTER SET UTF8;
show databases;
GRANT ALL PRIVILEGES ON fast_api.* TO travis;
use fast_api;
create table  users
(
    id              int auto_increment primary key,
    status          enum ('active', 'deleted', 'blocked') default 'active'          not null,
    email           varchar(255)                                                    null,
    pw              varchar(2000)                                                   null,
    name            varchar(255)                                                    null,
    phone_number    varchar(20)                                                     null,
    profile_img     varchar(1000)                                                   null,
    sns_type        enum ('FB', 'G', 'K', 'Email')                                  null,
    marketing_agree tinyint(1)                            default 0                 null,
    updated_at      datetime                              default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP,
    created_at      datetime                              default CURRENT_TIMESTAMP not null
);
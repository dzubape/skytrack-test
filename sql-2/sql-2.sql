/*
Существует таблица, в которой хранятся записи о неких событиях (например, выставки или фестивали).
CREATE TABLE events (
   id INTEGER PRIMARY KEY NOT NULL,
   name CHARACTER VARYING(255),
   begin_date TIMESTAMP(0) WITHOUT TIME ZONE,
   end_date TIMESTAMP(0) WITHOUT TIME ZONE
);
Необходимо написать код, который выводил бы на экран события, которые проходят на этой неделе.
*/


use skytrack;

drop table `events`;

create table if not exists `events`(
	`id` int auto_increment primary key not null,
	`name` varchar(255),
	`begin_date` timestamp(0),
	`end_date` timestamp(0)
	);

insert into `events`(`name`, `begin_date`, `end_date`) values("A+", "2019-02-15", "2022-02-19");
insert into `events`(`name`, `begin_date`, `end_date`) values("B+", "2019-02-15 23:58", "2019-02-17 23:59");
insert into `events`(`name`, `begin_date`, `end_date`) values("C+", "2019-02-11 00:00", "2019-02-11 00:01");
insert into `events`(`name`, `begin_date`, `end_date`) values("D+", "2019-02-17 23:59:59", "2019-02-18 00:00");
insert into `events`(`name`, `begin_date`, `end_date`) values("E+", "2019-02-15", "2019-02-15 00:01");
insert into `events`(`name`, `begin_date`, `end_date`) values("F-", "2018-02-15", "2018-02-15 00:01");

select `name` from (
	select 
		`name`,
		yearweek(`begin_date`, 7) as begin_week,
		yearweek(`end_date`, 7) as end_week,
		yearweek(current_timestamp(), 7) as now_week from `events`
) as `t`
where begin_week <= now_week and end_week >= now_week;

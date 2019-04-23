# Wings of Vaivora

## DB Module

### Description
This module is not to be used manually.

It serves as the backend of the following cogs:
- [`$boss`](./BOSS.md)
- [`$settings`](./SETTINGS.md)
- [`$offset`](./OFFSET.md)
- [`$events`](./EVENTS.md)

### Table schema
```
sqlite> .schema
CREATE TABLE contribution(mention integer, points integer);
CREATE TABLE owner(mention integer);
CREATE TABLE offset(hours integer);
CREATE TABLE guild(level integer, points integer);
CREATE TABLE roles(role text, mention integer);
CREATE TABLE channels(type text, channel integer);
CREATE TABLE boss(name text,channel integer,map text,status text,text_channel text,year integer,month integer,day integer,hour integer,minute integer);
CREATE TABLE tz(time_zone text);
CREATE TABLE events(name text,year integer,month integer,day integer,hour integer,minutes integer,enabled integer);
```

#### File last modified: 2019-04-23 15:35 (UTC-7)

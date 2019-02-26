# Wings of Vaivora

## DB Module

### Description
This module is not to be used manually.

It serves as the backend of the [`boss`](./BOSS.md) and [`settings`](./SETTINGS.md) modules.

### Table schema
```
sqlite> .schema
CREATE TABLE contribution(mention integer, points integer);
CREATE TABLE owner(mention integer);
CREATE TABLE offset(hours integer);
CREATE TABLE guild(level integer, points integer);
CREATE TABLE roles(role text, mention integer);
CREATE TABLE channels(type text, channel integer);
CREATE TABLE boss(name text,channel integer,
                    map text,status text,text_channel text,
                    year integer,month integer,day integer,
                    hour integer,minute integer);
```

#### File last modified: 2019-02-26 13:55 (UTC-8)
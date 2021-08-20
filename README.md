# no-downtime-upgrade

Upgrade Postgres without any downtime.

## Process

Dump the schema and then use it to provision the destination.

```
pg_dump -s -h localhost -p 5433 -U database database > schema.sql
psql -h localhost -p 5434 -U database database < schema.sql
```

Create the publication on the source and the subscription on the destination.

```
psql -h localhost -p 5433 -U database database < tools/publication.sql
psql -h localhost -p 5434 -U database database < tools/subscription.sql
```

Start monitoring the process by looking at the sequences. This process is
typically done using table size, but for our example sequences work better.
Note that every time you measure the sequences, you will also increase them by 1
as well.

```
watch 'psql -h localhost -p 5433 -U database database < tools/sequences.sql'
watch 'psql -h localhost -p 5434 -U database database < tools/sequences.sql'
```

Bump the sequences to a value higher than anything they'll reach before you
switch the application over.

```
psql -h localhost -p 5434 -U database database < tools/bumper.sql
```

Switch the application over:

```
curl localhost:8080
```

Check to make sure the data is being inserted into the destination and not the
source.

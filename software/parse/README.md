# How to install the Openbookscanner backend

### Postgres

The parse platform used in this project depends on Postgres with the version >=9.5.

On the Raspberry Pi, you can install the right version by calling the script `install-postgres.sh` found in the `parse` directory of the repository.

#### Create database and user

Run:
```
install-postgres-access.sh
```

### NodeJS and npm
Make sure you have [node](https://nodejs.org/en/) and [yarn](https://yarnpkg.com/en/) installed.

On the Raspberry Pi, you can install node and friends by calling the script [install-node.sh](parse/install-node.sh).

Then run:
```
yarn install
```

### Start the server

Run:
```
yarn run start
```

### Troubleshooting

#### Permissions error

If an error output contains mention of "permissions", make sure you call the install scripts with the highest possible user privileges (e.g. by using `sudo`).

#### npm crashes randomly

Especially the installation of the parse-server via npm fails very often due to an issue in npm 5.7 and 5.8 (see [npm issue 19989](https://github.com/npm/npm/issues/19989)). If recurring (around five) installation attempts fail to successfully exit, you could try downgrading npm to version 5.6 with `npm install -g npm@5.6.0`.

#### pg_hba.conf

If the script `install-postgres-access.sh` fails because the file `pg_hba.conf` could not be found, Postgres most likely has to be initialized first to use a specific database cluster location.

Run `sudo -u postgres -i` to get into the Postgres prompt as root.

Now, in the Postgres prompt, call

`initdb --locale $LANG -E UTF8 -D '/etc/postgresql/9.6/main'`

which sets the database cluster location to the expected location in the `install-postgres-access.sh` script.

If the call is not successful, try 

`initdb --locale $LANG -E UTF8 -D '/var/lib/postgres/data'`

and try adopting the `install-postgres-access.sh` script to the new location, so that in the table at the end of the file `/var/lib/postgres/data/pg_hba.conf` under `METHOD` only `trust` is written. The file can only be found and read as root.

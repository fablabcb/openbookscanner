# How to install the Openbookscanner backend

### Postgres

The parse platform used in this project depends on Postgres with the version >=9.5.

On the Raspberry Pi, you can install the right version by calling the script `install-postgres.sh` found in the `parse` directory of the repository.


### node.js and npm

If you already have these tools installed, just run `npm update -g` to make sure you're using the newest versions of all packages.

Otherwise call the `install-node.sh` script in the `parse` directory of the repository or get a hold of node.js and npm by using your OS' package manager.

### Parse Platform

Either call the `install-parse.sh` script in the `parse` directory of the repository, or call `npm install -g parse-server`.

In the end, run 

`npm list -g depth=0` 

and check if you see 

`parse-server` 

in the output. Then the installation was successful.

### Troubleshooting

If an error output contains mention of "permissions", make sure you call the install scripts with the highest possible user privileges (e.g. by using `sudo`).

Especially the installation of the parse-server via npm fails very often due to an issue in npm 5.7 and 5.8 (see [npm issue 19989](https://github.com/npm/npm/issues/19989)). If recurring (around five)installation attempts fail to successfully exit, you could try downgrading npm to version 5.6 with `npm install -g npm@5.6.0`.

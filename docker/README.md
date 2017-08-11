# PgSanity

PgSanity checks the syntax of Postgresql SQL files.

This Dockerfile is based on Alpine linux and generates images with approximately
110MB.

## Usage

This is a simple example of checking files in the current directory:

```bash
docker run --rm -it -v $PWD:/host -w /host pgsanity file1.sql file2.sql
```

More information on its [Github repository](https://github.com/markdrago/pgsanity).

# PgSanity

PgSanity checks the syntax of Postgresql SQL files.

This Dockerfile is based on Alpine Linux and generates images that are approximately 110MB in size.

## Usage

This is a simple example of checking files in the current directory:

```bash
docker run --rm -it -v $PWD:/host -w /host pgsanity file1.sql file2.sql
```

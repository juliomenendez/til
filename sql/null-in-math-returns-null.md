# NULL in math expressions always returns NULL

When using `NULL` values in a mathematical expression, the result is always going to be `NULL`. To avoid this we need to use `COALESCE`.

For example, let's say we have this table `Table1`:

| Column1 | Column2 |
| ------- | ------- |
| Text 1  | 10      |
| Text 2  | NULL    |
| Text 3  | 2.5     |

and we want to get the values of `Column2` and add 10 to it but we need all the results to be numbers. Doing it like this:

```sql
SELECT
    Column1,
    Column2 + 10 AS Column2
FROM
    Table1
```

the result will be:

| Column1 | Column2 |
| ------- | ------- |
| Text 1  | 20      |
| Text 2  | NULL    |
| Text 3  | 12.5    |

If instead we do this:

```sql
SELECT
    Column1,
    COALESCE(Column2, 0) + 10 AS Column2
FROM
    Table1
```

we get a better result:

| Column1 | Column2 |
| ------- | ------- |
| Text 1  | 20      |
| Text 2  | 10      |
| Text 3  | 12.5    |

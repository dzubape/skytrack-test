/*
Есть таблица с колонками a и b, обе колонки типа INT.
Дан запрос "select a, count(*) from t group by a".
Как изменить этот запрос, чтобы вывелись уникальные значения “a”
которые встречаются в таблице более 2х раз
*/

select a from (select a, count(*) as cnt from t group by a) as t1 where t1.cnt > 2
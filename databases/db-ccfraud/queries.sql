----------------------------------------------------------------------------------
-- anteil_datensaetze_jahr
----------------------------------------------------------------------------------
with
  base1(jahr, anz_jahr, anz_gesamt, anteil_pro_jahr) as (
    select 
      extract(year from ts), 
      count(*),
      sum(count(*)) over (),
      (cast(count(*) as float) / sum(count(*)) over ()) * 100
    from ccfraud
    group by extract(year from ts)
  )
select
  jahr as "jahr",
  anz_jahr as "anz_jahr",
  anz_gesamt as "anz_gesamt",
  anteil_pro_jahr as "anteil_pro_jahr"
from base1
order by jahr;

----------------------------------------------------------------------------------
-- anteil_datensaetze_land
----------------------------------------------------------------------------------
with
  base1(land) as (
    select 
      case when length(mstate)=2 then 'USA' else mstate end
    from ccfraud
    -- where ts >= to_date('2019-01-01', 'YYYY-MM-DD')
  ),
  base2(land, anz, anteil_land) as (
    select 
      land, 
      count(*),
      count(*) * 100 / sum(count(*)) over ()
    from base1
    group by land
    order by count(*) desc limit 20
  )
select
  land as "land",
  anz as "anz",
  anteil_land as "anteil_land"
from base2
order by anz desc;

----------------------------------------------------------------------------------
-- anteil_datensaetze_ok_betrug
----------------------------------------------------------------------------------
with
  base1(is_fraud, anz, anteil) as (
    select 
      is_fraud, 
      count(*),
      cast(count(*) as float) / sum(count(*)) over ()
    from ccfraud
    -- where ts >= to_date('2019-01-01', 'YYYY-MM-DD')
    group by is_fraud
  )
select
  is_fraud as "is_fraud",
  anz as "anz",
  anteil as "anteil"
from base1
order by is_fraud;


----------------------------------------------------------------------------------
-- anz_trx_nutzer
----------------------------------------------------------------------------------
with
  base1(nutzer, anz_trx) as (
    select 
      userid,
      count(*)
    from ccfraud
    -- where ts >= to_date('2019-01-01', 'YYYY-MM-DD')
    group by userid
    -- having count(*) > 40000 or (count(*) between 2 and 100)
  )
select
  nutzer as "nutzer",
  anz_trx as "anz_trx"
from base1
order by anz_trx;

----------------------------------------------------------------------------------
-- anz_trx_unternehmen
----------------------------------------------------------------------------------
with
  base1(unternehmen, anz_trx) as (
    select 
      mname,
      count(*)
    from ccfraud
    -- where ts >= to_date('2019-01-01', 'YYYY-MM-DD')
    group by mname
    having count(*) >= 100000
  )
select
  unternehmen as "unternehmen",
  anz_trx as "anz_trx"
from base1
order by anz_trx;

----------------------------------------------------------------------------------
-- betrugsanteil_art
----------------------------------------------------------------------------------
with
  base(art, is_fraud) as (
    select 
      use_chip,
      is_fraud
    from ccfraud
    -- where ts >= to_date('2019-01-01', 'YYYY-MM-DD')
  ),
  proportion(art, anz_trx, ant_ok, ant_fraud) as (
    select 
      art,
      count(*),
      sum(case when is_fraud='No' then 1 else 0 end),
      sum(case when is_fraud='Yes' then 1 else 0 end)
    from base
    group by art
  ),
  ratio(art, anz_trx, ant_ok, ant_fraud, quote_ok, quote_fraud) as (
    select
      art,
      anz_trx,
      ant_ok,
      ant_fraud,
      round(ant_ok*100/anz_trx::numeric, 4),
      round(ant_fraud*100/anz_trx::numeric, 4)
     from proportion where ant_fraud>0
  )
select
  art as "art",
  anz_trx as "anz_trx",
  ant_ok as "ant_ok",
  ant_fraud as "ant_fraud",
  quote_ok as "quote_ok",
  quote_fraud as "quote_fraud"
from ratio
order by quote_fraud desc;

----------------------------------------------------------------------------------
-- betrugsanteil_fehler1
----------------------------------------------------------------------------------
with
  base(fehler1, is_fraud) as (
    select
      err1,
      is_fraud
    from ccfraud
    -- where ts >= to_date('2019-01-01', 'YYYY-MM-DD')
  ),
  proportion(fehler1, anz_trx, ant_ok, ant_fraud) as (
    select
      fehler1,
      count(*),
      sum(case when is_fraud='No' then 1 else 0 end),
      sum(case when is_fraud='Yes' then 1 else 0 end)
    from base
    group by fehler1
  ),
  ratio(fehler1, anz_trx, ant_ok, ant_fraud, quote_ok, quote_fraud) as (
    select
      fehler1,
      anz_trx,
      ant_ok,
      ant_fraud,
      round(ant_ok*100/anz_trx::numeric, 4),
      round(ant_fraud*100/anz_trx::numeric, 4)
     from proportion where ant_fraud>0
  )
select
  fehler1 as "fehler1",
  anz_trx as "anz_trx",
  ant_ok as "ant_ok",
  ant_fraud as "ant_fraud",
  quote_ok as "quote_ok",
  quote_fraud as "quote_fraud"
from ratio
order by quote_fraud desc;

----------------------------------------------------------------------------------
-- betrugsanteil_jahr
----------------------------------------------------------------------------------
with
  base(jahr, is_fraud) as (
    select
      extract(year from ts),
      is_fraud
    from ccfraud
  ),
  proportion(jahr, anz_trx, ant_ok, ant_fraud) as (
    select
      jahr,
      count(*),
      sum(case when is_fraud='No' then 1 else 0 end),
      sum(case when is_fraud='Yes' then 1 else 0 end)
    from base
    group by jahr
  ),
  ratio(jahr, anz_trx, ant_ok, ant_fraud, quote_ok, quote_fraud) as (
    select
      jahr,
      anz_trx,
      ant_ok,
      ant_fraud,
      round(ant_ok*100/anz_trx::numeric, 4),
      round(ant_fraud*100/anz_trx::numeric, 4)
     from proportion
  )
select
  jahr as "jahr",
  anz_trx as "anz_trx",
  ant_ok as "ant_ok",
  ant_fraud as "ant_fraud",
  quote_ok as "quote_ok",
  quote_fraud as "quote_fraud"
from ratio
order by jahr;

----------------------------------------------------------------------------------
-- betrugsanteil_land
----------------------------------------------------------------------------------
with
  base(land, is_fraud) as (
    select
      case when length(mstate)=2 then 'USA' else mstate end,
      is_fraud
    from ccfraud
  ),
  proportion(land, anz_trx, ant_ok, ant_fraud) as (
    select
      land,
      count(*),
      sum(case when is_fraud='No' then 1 else 0 end),
      sum(case when is_fraud='Yes' then 1 else 0 end)
    from base
    group by land
  ),
  ratio(land, anz_trx, ant_ok, ant_fraud, quote_ok, quote_fraud) as (
    select
      land,
      anz_trx,
      ant_ok,
      ant_fraud,
      round(ant_ok*100/anz_trx::numeric, 4),
      round(ant_fraud*100/anz_trx::numeric, 4)
     from proportion where ant_fraud>0
  )
select
  land as "land",
  anz_trx as "anz_trx",
  ant_ok as "ant_ok",
  ant_fraud as "ant_fraud",
  quote_ok as "quote_ok",
  quote_fraud as "quote_fraud"
from ratio
order by quote_fraud desc;

----------------------------------------------------------------------------------
-- betrugsanteil_umsatz
----------------------------------------------------------------------------------
with
  base(umsatz_bis, is_fraud) as (
    select
      case
        when amount<-500 then -550
        when amount<-400 then -400
        when amount<-300 then -300
        when amount<-200 then -200
        when amount<-100 then -100
        when amount<0 then 0
        when amount<20 then 20
        when amount<40 then 40
        when amount<60 then 60
        when amount<80 then 80
        when amount<100 then 100
        when amount<1000 then 1000
        when amount<2000 then 2000
        when amount<3000 then 3000
        when amount<4000 then 4000
        when amount<5000 then 5000
        else 6820
      end,
      is_fraud
    from ccfraud
    -- where ts >= to_date('2019-01-01', 'YYYY-MM-DD')
  ),
  proportion(umsatz_bis, anz_trx, ant_ok, ant_fraud) as (
    select
      umsatz_bis,
      count(*),
      sum(case when is_fraud='No' then 1 else 0 end),
      sum(case when is_fraud='Yes' then 1 else 0 end)
    from base
    group by umsatz_bis
  ),
  ratio(umsatz_bis, anz_trx, ant_ok, ant_fraud, quote_ok, quote_fraud) as (
    select
      umsatz_bis,
      anz_trx,
      ant_ok,
      ant_fraud,
      round(ant_ok*100/anz_trx::numeric, 4),
      round(ant_fraud*100/anz_trx::numeric, 4)
     from proportion
  )
select
  umsatz_bis as "umsatz_bis",
  anz_trx as "anz_trx",
  ant_ok as "ant_ok",
  ant_fraud as "ant_fraud",
  quote_ok as "quote_ok",
  quote_fraud as "quote_fraud"
from ratio
order by umsatz_bis;

----------------------------------------------------------------------------------
-- betrugsanteil_zeit_abstand
----------------------------------------------------------------------------------
with
  base1 as (
    select
      userid,
      ts,
      lag(ts) over (partition by userid order by ts) as ts_p,
      mcity,
      lag(mcity) over (partition by userid order by ts) as mcity_p,
      is_fraud
    from ccfraud
    -- where ts >= to_date('2019-01-01', 'YYYY-MM-DD')
  ),
  base2 as (
    select
      userid,
      ts,
      ts_p,
      mcity,
      mcity_p,
      (extract(epoch from ts) - extract(epoch from ts_p)) / 60 as abstand_minuten,
      is_fraud
    from base1
    where not ts_p is null
  ),
  base as (
    select
      case
        when abstand_minuten < 5 then 'a) bis 5 min'
        else 'b) ab 5 min'
      end as abstand_minuten,
      is_fraud
    from base2
    where mcity<>mcity_p
  ),
  proportion(abstand_minuten, anz_trx, ant_ok, ant_fraud) as (
    select
      abstand_minuten,
      count(*),
      sum(case when is_fraud='No' then 1 else 0 end),
      sum(case when is_fraud='Yes' then 1 else 0 end)
    from base
    group by abstand_minuten
  ),
  ratio(abstand_minuten, anz_trx, ant_ok, ant_fraud, quote_ok, quote_fraud) as (
    select
      abstand_minuten,
      anz_trx,
      ant_ok,
      ant_fraud,
      round(ant_ok*100/anz_trx::numeric, 4),
      round(ant_fraud*100/anz_trx::numeric, 4)
     from proportion
  )
select
  abstand_minuten as "abstand_minuten",
  anz_trx as "anz_trx",
  ant_ok as "ant_ok",
  ant_fraud as "ant_fraud",
  quote_ok as "quote_ok",
  quote_fraud as "quote_fraud"
from ratio
order by abstand_minuten;

----------------------------------------------------------------------------------
-- stat_anz_trx_nutzer
----------------------------------------------------------------------------------
with
  base1(userid, anz) as (
    select
      userid,
      count(*)
    from ccfraud
    -- where ts >= to_date('2019-01-01', 'YYYY-MM-DD')
    group by userid
  ),
  base2(anz_nutzer, avg_anz_trx, min_anz_trx, max_anz_trx) as (
    select
      count(*),
      round(avg(anz)::numeric, 0),
      min(anz),
      max(anz)
    from base1
  )
select
  anz_nutzer as "anz_nutzer",
  avg_anz_trx as "avg_anz_trx",
  min_anz_trx as "min_anz_trx",
  max_anz_trx as "max_anz_trx"
from base2
order by anz_nutzer;

----------------------------------------------------------------------------------
-- stat_anz_trx_unternehmen
----------------------------------------------------------------------------------
with
  base1(mname, anz) as (
    select
      mname,
      count(*)
    from ccfraud
    -- where ts >= to_date('2019-01-01', 'YYYY-MM-DD')
    group by mname
  ),
  base2(anz_unternehmen, avg_anz_trx, min_anz_trx, max_anz_trx) as (
    select
      count(*),
      round(avg(anz)::numeric, 0),
      min(anz),
      max(anz)
    from base1
  )
select
  anz_unternehmen as "anz_unternehmen",
  avg_anz_trx as "avg_anz_trx",
  min_anz_trx as "min_anz_trx",
  max_anz_trx as "max_anz_trx"
from base2
order by anz_unternehmen;

----------------------------------------------------------------------------------
-- betrugsanteil_unternehmen
----------------------------------------------------------------------------------
with
  base(unternehmen, is_fraud) as (
    select
      mname,
      is_fraud
    from ccfraud
    -- where ts >= to_date('2019-01-01', 'YYYY-MM-DD')
  ),
  proportion(unternehmen, anz_trx, ant_ok, ant_fraud) as (
    select
      unternehmen,
      count(*),
      sum(case when is_fraud='No' then 1 else 0 end),
      sum(case when is_fraud='Yes' then 1 else 0 end)
    from base
    group by unternehmen
  ),
  ratio(unternehmen, anz_trx, ant_ok, ant_fraud, quote_ok, quote_fraud) as (
    select
      unternehmen,
      anz_trx,
      ant_ok,
      ant_fraud,
      round(ant_ok*100/anz_trx::numeric, 4),
      round(ant_fraud*100/anz_trx::numeric, 4)
     from proportion where ant_fraud>50
  )
select
  unternehmen as "unternehmen",
  anz_trx as "anz_trx",
  ant_ok as "ant_ok",
  ant_fraud as "ant_fraud",
  quote_ok as "quote_ok",
  quote_fraud as "quote_fraud"
from ratio
where quote_fraud>10
order by quote_fraud desc;

----------------------------------------------------------------------------------
-- 
----------------------------------------------------------------------------------


----------------------------------------------------------------------------------
-- 
----------------------------------------------------------------------------------


----------------------------------------------------------------------------------
-- 
----------------------------------------------------------------------------------


----------------------------------------------------------------------------------
-- 
----------------------------------------------------------------------------------


----------------------------------------------------------------------------------
-- 
----------------------------------------------------------------------------------



use metroblo_website;

SELECT  latitude, 
longitude, 
accuracy, 
address, 
city, 
zip, 
raingarden, 
scoresheet, 
score, 
eval_type, 
rating, 
comments, 
date_evaluated  
FROM gardenevals_evaluations eval
left outer join (gardenevals_gardens garden, geolocation geo) 
on (garden.garden_id = eval.garden_id AND garden.geo_id = geo.geo_id) 
where completed = 1 AND scoresheet is not null
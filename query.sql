SELECT flight_id, flight_type, scheduled_departure, scheduled_arrival,departure_airport, arrival_airport, seats_available FROM flights ORDER BY flight_id
SELECT CASE 
WHEN (SELECT COUNT(*) FROM (SELECT * FROM flights WHERE flight_id = '1001' AND seats_available = 0) AS a) > 0 THEN 't' 
WHEN (SELECT COUNT(*) FROM (SELECT * FROM flights WHERE flight_id = '1002' AND seats_available = 0) AS a) > 0 THEN 't' 
ELSE 'f' END;

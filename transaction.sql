BEGIN TRANSACTION;
INSERT INTO bookings(book_ref,book_date,total_amount) 
VALUES('BV4SBT',CURRENT_TIMESTAMP,'537.30');
INSERT INTO ticket_flights(ticket_no,flight_id,fare_conditions) 
SELECT 'T3ENS7','1001','business' 
WHERE EXISTS 
(SELECT * FROM flights WHERE flight_id = '1001' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);
INSERT INTO payment(payment_id,book_ref,discount,amount_due,currency_type,card_number,tax) 
SELECT 'SK20LSLIS7','BV4SBT','no','519.00','CAD','9999222299992222','18.30' 
WHERE EXISTS 
(SELECT * FROM flights WHERE flight_id = '1001' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);
INSERT INTO ticket(ticket_no,book_ref,passenger_id,passenger_name,email,phone) 
SELECT 'T3ENS7','BV4SBT','657841266','name4','name4@email.com','444-444-4444' 
WHERE EXISTS
(SELECT * FROM flights WHERE flight_id = '1001' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);
UPDATE flights 
SET seats_booked = seats_booked + 1, seats_available = seats_available - 1 
WHERE seats_booked < 50 AND flight_id = 1001;
INSERT INTO boarding(boarding_id,ticket_no,riding_status,gate,boarding_time) 
SELECT '34864653918','T3ENS7','Group','A2','2020-12-20 00:45:00' 
WHERE EXISTS 
(SELECT * FROM flights WHERE flight_id = '1001' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);
INSERT INTO arrival(boarding_id,arrival_time,arrival_gate,baggage_claim) 
SELECT '34864653918','2020-12-20 05:55:00','B12','4' 
WHERE EXISTS 
(SELECT * FROM flights WHERE flight_id = '1001' AND seats_booked < 50 AND CURRENT_TIMESTAMP < scheduled_departure);
COMMIT;


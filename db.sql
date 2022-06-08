drop table if exists airport cascade;
drop table if exists boarding_passes cascade;
drop table if exists aircraft cascade;
drop table if exists ticket cascade;
drop table if exists ticket_flights cascade;
drop table if exists bookings cascade;
drop table if exists flights cascade;
drop table if exists aircraft cascade;
drop table if exists arrival cascade;
drop table if exists boarding cascade;
drop table if exists connecting_flights cascade;
drop table if exists payment cascade;
drop table if exists waitlist cascade;
drop table if exists pilot cascade;
drop table if exists pilot_info cascade;
drop table if exists flight_crew cascade;
drop table if exists employee_info cascade;
drop table if exists airline cascade;
drop table if exists baggage cascade;


create table aircraft(
    aircraft_code char(3),
    model char(25),
    range integer,
    primary key (aircraft_code),
    constraint "flights_aircraft_code_fkey" foreign key (aircraft_code) references aircraft(aircraft_code),
    constraint "seats_aircraft_code_fkey" foreign key (aircraft_code) references aircraft(aircraft_code) on delete cascade
);

create table airport (
    airport_code char(3) not null,
    airport_name char(40),
    city char(20),
    timezone text,
    primary key (airport_code)
);

create table flights (
    flight_id integer not null,
    flight_no character(10) not null,
    flight_type character(8) default 'Direct',
    scheduled_departure timestamp with time zone,
    scheduled_arrival timestamp with time zone,
    departure_airport character(3),
    arrival_airport character(3),
    status character varying(20),
    aircraft_code character(3),
    seats_available integer,
    seats_booked integer,
    movie char(3) default 'no',
    meal char(3) default 'no',
    primary key (flight_id),
    constraint flights_aircraft_code_fkey foreign key (aircraft_code) references aircraft(aircraft_code),
    constraint flights_arrival_airport_fkey foreign key (arrival_airport) references airport(airport_code),
    constraint flights_departure_airport_fkey foreign key (departure_airport) references airport(airport_code),
    constraint flights_check check ((scheduled_arrival > scheduled_departure)),
    constraint movie_check check (
        (
            (movie)::text = any (
                array [('yes'::char(3))::text, ('y'::char(3))::text, ('no'::char(3))::text, ('n'::char(3))::text]
            )
        )
    ),
    constraint meal_check check (
        (
            (meal)::text = any (
                array [('yes'::char(3))::text, ('y'::char(3))::text, ('no'::char(3))::text, ('n'::char(3))::text]
            )
        )
    ),
    constraint flight_type_check check (
        (flight_type)::text = any (
            array [('Direct'::char(8))::text, ('Indirect'::char(8))::text]
        )
    ),
    constraint flights_status_check check (
        (
            (status)::text = any (
                array [('On Time'::character varying)::text, ('Delayed'::character varying)::text, ('Departed'::character varying)::text, ('Arrived'::character varying)::text, ('Scheduled'::character varying)::text, ('Cancelled'::character varying)::text]
            )
        )
    )
);

create table bookings (
    book_ref character(7) not null ,
    book_date timestamp with time zone default current_timestamp,
    total_amount numeric(25, 2),
    primary key (book_ref)
);

create table ticket(
    ticket_no char(13) not null,
    book_ref character(7) not null,
    passenger_id varchar(20),
    passenger_name text,
    email char(50),
    phone char(15),
    primary key (ticket_no)
    /*constraint "tickets_book_ref_fkey" foreign key (book_ref) references bookings(book_ref)*/
);

create table boarding (
    boarding_id character (13) not null,
    ticket_no char(13) not null,
    riding_status varchar default 'Solo',
    gate character (20) default 'A',
    boarding_time timestamp with time zone,
    primary key (boarding_id),
    /*constraint ticket_no_fkey foreign key (ticket_no) references ticket(ticket_no),*/
    constraint riding_check check (
        (
            (riding_status)::text = any (
                array [('Family'::character varying)::text, ('Couple'::character varying)::text, ('Group'::character varying)::text, ('Solo'::character varying)::text]
            )
        )
    )
);

create table arrival (
    boarding_id character(13) not null,
    arrival_time timestamp with time zone,
    arrival_gate character (20),
    baggage_claim integer default 10,
    primary key (boarding_id)
    /*constraint boarding_id_fkey foreign key (boarding_id) references boarding(boarding_id)*/
);

create table waitlist (
    waitlist_number serial primary key not null,
    book_ref character(7) not null,
    passenger_name text,
    email char(50)
    /*constraint book_ref_check foreign key (boarding_id) references bookings(book_ref)*/
);

/* Added table*/
create table payment (
    payment_id character(15) not null,
    book_ref character(7) not null,
    discount varchar(3) not null,
    amount_due numeric(25,2),
    currency_type char(4) default 'USD',
    card_number char(24) not null,
    tax numeric(4),
    primary key (payment_id),
    /*constraint book_ref_fkey foreign key (book_ref) references bookings(book_ref)*/
    constraint currency_type_check check (
        (
            (currency_type)::text = any (
                array [('USD'::character varying)::text,('CAD'::character varying)::text,('usd'::character varying)::text,('cad'::character varying)::text]
            )
        )
    ),
    constraint discount_check check (
        (
            (discount)::text = any (
                array [('yes'::character varying)::text,('no'::character varying)::text]
            )
        )
    )
);

create table ticket_flights (
    ticket_no character(13) not null,
    flight_id integer not null,
    fare_conditions character varying(10),
    primary key (ticket_no, flight_id),
    /*constraint ticket_flights_flight_id_fkey foreign key (flight_id) references flights(flight_id),
    constraint ticket_flights_ticket_no_fkey foreign key (ticket_no) references ticket(ticket_no),*/
    constraint ticket_flights_fare_conditions_check check (
        (
            (fare_conditions)::text = any (
                array [('economy'::character varying)::text,('business'::character varying)::text]
            )
        )
    )
);

create table pilot (
    pilot_id character(6),
    flight_id integer not null,
    seniority integer not null,
    primary key(pilot_id)
);

insert into pilot (pilot_id, flight_id, seniority) values ('lbm0oe', 1002, 10);
insert into pilot (pilot_id, flight_id, seniority) values ('rbx5dy', 1004, 30);
insert into pilot (pilot_id, flight_id, seniority) values ('iv4c5d', 1004, 19);
insert into pilot (pilot_id, flight_id, seniority) values ('zsj5i6', 1001, 9);
insert into pilot (pilot_id, flight_id, seniority) values ('kjod4x', 1010, 19);
insert into pilot (pilot_id, flight_id, seniority) values ('0yfgva', 1008, 24);
insert into pilot (pilot_id, flight_id, seniority) values ('ocza2b', 1008, 8);
insert into pilot (pilot_id, flight_id, seniority) values ('424m1u', 1003, 14);
insert into pilot (pilot_id, flight_id, seniority) values ('kvpg6a', 1003, 20);
insert into pilot (pilot_id, flight_id, seniority) values ('097q0f', 1003, 42);

create table pilot_info (
    license_number character (13) not null,
    pilot_id character (6) not null,
    name text not null,
    salary integer not null,
    year_of_birth integer not null,
    flown_hours integer not null,
    primary key(license_number)
);

insert into pilot_info (license_number, pilot_id, name, salary, year_of_birth, flown_hours) values ('3375606184730', 'lbm0oe', 1004, 86667, 1993, 1581);
insert into pilot_info (license_number, pilot_id, name, salary, year_of_birth, flown_hours) values ('3070008928564', 'rbx5dy', 1008, 104186, 1993, 1491);
insert into pilot_info (license_number, pilot_id, name, salary, year_of_birth, flown_hours) values ('5066013951176', 'iv4c5d', 1009, 121743, 1988, 2493);
insert into pilot_info (license_number, pilot_id, name, salary, year_of_birth, flown_hours) values ('6255951173083', 'zsj5i6', 1005, 939, 1975, 848);
insert into pilot_info (license_number, pilot_id, name, salary, year_of_birth, flown_hours) values ('9545512315523', 'kjod4x', 1009, 67058, 1990, 761);
insert into pilot_info (license_number, pilot_id, name, salary, year_of_birth, flown_hours) values ('4904512914539', '0yfgva', 1009, 72906, 2001, 1704);
insert into pilot_info (license_number, pilot_id, name, salary, year_of_birth, flown_hours) values ('7069989617591', 'ocza2b', 1010, 65644, 2001, 1348);
insert into pilot_info (license_number, pilot_id, name, salary, year_of_birth, flown_hours) values ('6765394552130', '424m1u', 1009, 55741, 1978, 656);
insert into pilot_info (license_number, pilot_id, name, salary, year_of_birth, flown_hours) values ('3741460747502', 'kvpg6a', 1009, 45004, 2000, 816);
insert into pilot_info (license_number, pilot_id, name, salary, year_of_birth, flown_hours) values ('4086172628641', '097q0f', 1000, 57940, 1987, 2330);


create table flight_crew (
    crew_id character(6),
    flight_id integer not null,
    job text not null,
    constraint job_check check (
        (
            (job)::text = any (
                array [('stewardess'::character varying)::text,('steward'::character varying)::text]
            )
        )
    ),
    primary key(crew_id)
);

insert into flight_crew (crew_id, flight_id, job) values ('8iraj7', 1002, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('bpvd41', 1002, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('5wcdr4', 1007, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('obyyrp', 1007, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('y3kwda', 1002, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('akkyle', 1008, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('vfsm0a', 1002, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('8xtfod', 1002, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('gth56n', 1009, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('qh2w6s', 1000, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('k933a6', 1000, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('bublxa', 1010, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('bsz8ez', 1010, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('wsixdk', 1010, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('asmyox', 1003, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('jbrk7k', 1006, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('w9vcbo', 1001, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('flbtjp', 1004, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('u0y0zs', 1002, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('go1ji1', 1007, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('g31pz9', 1000, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('ipzn0k', 1001, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('esp7u1', 1006, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('8k4zif', 1003, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('np68qj', 1009, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('sxfxhm', 1010, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('zg9w9q', 1004, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('ckhriv', 1005, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('9zesd1', 1008, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('ba5cfr', 1005, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('i48ht1', 1000, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('vx5137', 1003, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('ejroyu', 1002, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('t7qhmu', 1003, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('5z3q98', 1005, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('z8nqdt', 1007, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('kkua62', 1007, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('9is2vq', 1009, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('0n5c3i', 1006, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('s3bn7p', 1002, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('fhbw1k', 1007, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('d2f326', 1003, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('chlhwi', 1004, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('g59wmp', 1009, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('w4dgxe', 1005, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('x6ut30', 1003, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('gng7bx', 1000, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('fw6sou', 1008, 'steward');
insert into flight_crew (crew_id, flight_id, job) values ('bsz089', 1003, 'stewardess');
insert into flight_crew (crew_id, flight_id, job) values ('s41dvq', 1002, 'steward');


create table employee_info (
    employee_id character(13) not null,
    crew_id character(6) not null,
    year_of_birth integer not null,
    salary integer not null,
    years_experience integer not null,
    name text not null,
    primary key(employee_id)
);

insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('s6868y0uec4on', '8iraj7', 1981, 73792, 8, 'Weber Edowes');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('z35olqmj63gin', 'bpvd41', 1986, 76553, 13, 'Chery Batteson');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('0wgujtlft7eee', '5wcdr4', 1988, 69646, 2, 'Libby Empleton');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('fqxkji69498w5', 'obyyrp', 1980, 77091, 25, 'Reyna Engelmann');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('gyuqvkqd0e8xy', 'y3kwda', 2002, 93137, 7, 'Jessee Watkiss');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('1t8ywa94wiz1x', 'akkyle', 1993, 67499, 20, 'Raphael Zoephel');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('a1puvgsb818fo', 'vfsm0a', 1996, 89504, 14, 'Diane-marie Gronow');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('f86snyi962h9v', '8xtfod', 1980, 89226, 2, 'Catharine Plunkett');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('i421jhhjlk8gd', 'gth56n', 1998, 72345, 4, 'Karrah Cridlan');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('gbezw6lwu3djn', 'qh2w6s', 1990, 67461, 4, 'Nefen Carlino');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('asm0rb86ah12n', 'k933a6', 1992, 71111, 10, 'Marsha Pheazey');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('520kyw48cf78e', 'bublxa', 1987, 77426, 2, 'Milka Ferraron');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('ljwmfovrzngj2', 'bsz8ez', 1999, 83804, 7, 'Herve Gather');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('i0isbzm82f9dz', 'wsixdk', 1987, 81227, 7, 'Janna Elliot');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('fazslz8rrx9nc', 'asmyox', 1994, 71750, 10, 'Allie Shellshear');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('n4zej64003356', 'jbrk7k', 2001, 68813, 7, 'Bartholemy Rylstone');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('igccpfa7e35nr', 'w9vcbo', 1986, 95665, 3, 'Ursulina Musto');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('mxyt5w6568cdl', 'flbtjp', 2001, 71814, 11, 'Cortie Bartell');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('cmwebxa68wu2w', 'u0y0zs', 2001, 72425, 25, 'Garik Broad');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('u2daymwqn1yo6', 'go1ji1', 2002, 84163, 7, 'Frederik Stiven');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('eno9e6aluu6mt', 'g31pz9', 2001, 91870, 9, 'Garrott Hatchard');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('7guh9adoztuf1', 'ipzn0k', 1984, 68414, 7, 'Alicea Jandl');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('29x1v7b91bf98', 'esp7u1', 2000, 67600, 6, 'Leisha Bottle');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('5a9ef64p9rlkn', '8k4zif', 1986, 76737, 17, 'Toby Greenhough');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('di3cc34e826ya', 'np68qj', 2002, 91213, 22, 'Kent Mulvey');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('v2mlwq24ifpes', 'sxfxhm', 1984, 87164, 20, 'Pepillo Leate');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('sxlp4zc990vgf', 'zg9w9q', 1988, 81844, 20, 'Kaleena Schurcke');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('py7b6uvp0fg4x', 'ckhriv', 1983, 70184, 16, 'Pooh Crut');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('6ipz6fmyl3ra5', '9zesd1', 1991, 78326, 7, 'Wendell Skpsey');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('ta3zaxyb4qcev', 'ba5cfr', 2002, 80859, 22, 'Calli Danilin');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('sx7l0rtar3rll', 'i48ht1', 1980, 92205, 10, 'Delilah McLucky');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('sxhyxcdhbugwf', 'vx5137', 1985, 93360, 19, 'Fraser Conachie');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('1ypy6bv8v9z4q', 'ejroyu', 1981, 91405, 21, 'Goldi Biscomb');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('jstye5q285hi0', 't7qhmu', 1992, 73139, 11, 'Easter Figgess');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('htr2vjqyg1tns', '5z3q98', 1985, 65578, 7, 'Kaila Meuse');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('e1x1i69ptfkaz', 'z8nqdt', 1991, 64073, 4, 'Stafford Creech');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('brdjhhbbvavww', 'kkua62', 2000, 94985, 14, 'Dayle Zanetto');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('tuwq4kvrp26w1', '9is2vq', 2002, 62453, 2, 'Stacy Messenbird');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('o3zppvt2i04hh', '0n5c3i', 1981, 86144, 17, 'Mick Cluderay');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('lwhghdgy2h3kt', 's3bn7p', 2000, 65766, 11, 'Vachel Danielsky');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('8590kyrfv2hm6', 'fhbw1k', 1996, 94386, 10, 'Chloette Dauber');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('j3awwk4v82j2w', 'd2f326', 2002, 94126, 4, 'Ellissa Brecher');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('7lj8tj5wa6jl0', 'chlhwi', 1991, 80221, 25, 'Eolande Rosenfelder');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('eutv2m3qhdhnd', 'g59wmp', 1998, 69490, 9, 'Faber Storcke');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('82ygnolkeskff', 'w4dgxe', 1999, 82555, 4, 'Marybelle Dandie');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('sv6yym5yoh7my', 'x6ut30', 2001, 68232, 13, 'Wyn Defraine');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('hrclofn59ugxf', 'gng7bx', 1984, 62543, 15, 'Ag Cottesford');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('a1liw93m0dd10', 'fw6sou', 1996, 70554, 15, 'Ranice Aust');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('r4scs8f0wze85', 'bsz089', 1985, 63016, 23, 'Roger Hairesnape');
insert into employee_info (employee_id, crew_id, year_of_birth, salary, years_experience, name) values ('acmv9s4d3ntzg', 's41dvq', 1989, 71106, 17, 'Rosalia Dillaway');

create table airline (
    airline_id character(6) not null,
    airline_name text not null,
    airline_code character(3) not null,
    tag_line text not null,
    primary key(airline_id)
);

insert into airline (airline_id, airline_name, airline_code, tag_line) values ('nx0kco', 'JetBlue Airways', '321', 'Fly the friendly skies');
insert into airline (airline_id, airline_name, airline_code, tag_line) values ('m1pke2', 'JetBlue Airways', '321', 'Delta gets you there. We’re ready to fly.');
insert into airline (airline_id, airline_name, airline_code, tag_line) values ('6j3lg0', 'American Airlines', 'SU9', 'Life is a journey');
insert into airline (airline_id, airline_name, airline_code, tag_line) values ('dfgk98', 'American Airlines', '773', 'Life is a journey');
insert into airline (airline_id, airline_name, airline_code, tag_line) values ('oqtqej', 'Delta Air Lines', '321', 'Delta gets you there. We’re ready to fly.');
insert into airline (airline_id, airline_name, airline_code, tag_line) values ('ht9v85', 'JetBlue Airways', '321', 'travel it well.');
insert into airline (airline_id, airline_name, airline_code, tag_line) values ('j42fs7', 'American Airlines', '321', 'Life is a journey');
insert into airline (airline_id, airline_name, airline_code, tag_line) values ('uaielb', 'Southwest Airlines', 'SU9', 'A symbol of freedom');

create table baggage (
    baggage_id character(7) not null,
    book_ref character(7) not null,
    late character(10) not null,
    on_flight character varying(10) not null,
    primary key(baggage_id),
    constraint late_check check (
        (
            (late)::text = any (
                array [('yes'::character varying)::text,('no'::character varying)::text]
            )
        )
    ),
    constraint on_flight_check check (
        (
            (on_flight)::text = any (
                array [('yes'::character varying)::text,('no'::character varying)::text]
            )
        )
    )
);

/* airports */
insert into airport
values (
        'HOU',
        'George Bush Airport',
        'Houston',
        'CT'
    );

insert into airport
values (
        'JFK',
        'John F Kennedy Airport',
        'New York',
        'ET'
    );

insert into airport
values (
        'LAX',
        'Los Angeles Airport',
        'Los Angeles',
        'PT'
    );

insert into airport
values (
        'ORD',
        'O Hare Airport',
        'Chicago',
        'CT'

    );

insert into airport
values (
        'MIA',
        'Miami Airport',
        'Miami',
        'ET'

    );

/*aircraft*/
insert into aircraft
values ('773', 'Boeing 777-300', 11100);

insert into aircraft
values ('763', 'Boeing 767-300', 7900);

insert into aircraft
values ('SU9', 'Boeing 777-300', 5700);

insert into aircraft
values ('320', 'Boeing 777-300', 6400);

insert into aircraft
values ('321', 'Boeing 777-300', 6100);

/* Flights */
insert into flights
values (
        1001,
        'PG0010',
        'Indirect',
        '2020-12-20 09:50:00+03',
        '2020-12-20 14:55:00+03',
        'HOU',
        'JFK',
        'Scheduled',
        '763',
        50,
        0,
        'yes',
        'yes'
    );

insert into flights
values (
        1002,
        'PG0020',
        'Direct',
        '2020-12-20 15:30:00+03',
        '2020-12-20 17:55:00+03',
        'JFK',
        'LAX',
        'Scheduled',
        '763',
        50,
        0,
        'no',
        'no'
    );

insert into flights
values (
        1003,
        'PG0030',
        'Indirect',
        '2021-01-16 09:30:00+03',
        '2021-01-16 12:55:00+03',
        'LAX',
        'ORD',
        'Scheduled',
        '773',
        50,
        0,
        'yes',
        'yes'
    );

insert into flights
values (
        1004,
        'PG0040',
        'Direct',
        '2021-01-16 13:30:00+03',
        '2021-01-16 17:55:00+03',
        'ORD',
        'MIA',
        'Scheduled',
        '773',
        50,
        0,
        'yes',
        'yes'
    );

insert into flights
values (
        1005,
        'PG0050',
        'Direct',
        '2020-12-23 09:50:00+03',
        '2020-12-23 15:55:00+03',
        'LAX',
        'JFK',
        'Scheduled',
        '763',
        50,
        0,
        'yes',
        'yes'
    );

insert into flights
values (
        1006,
        'PG0060',
        'Direct',
        '2020-12-27 08:50:00+03',
        '2020-12-27 14:55:00+03',
        'ORD',
        'MIA',
        'Scheduled',
        '320',
        50,
        0,
        'yes',
        'yes'
    );

insert into flights
values (
        1007,
        'PG0070',
        'Direct',
        '2020-12-27 12:50:00+03',
        '2020-12-27 14:55:00+03',
        'HOU',
        'LAX',
        'Scheduled',
        '763',
        50,
        0,
        'yes',
        'yes'
    );

insert into flights
values (
        1008,
        'PG0080',
        'Direct',
        '2021-01-13 07:50:00+03',
        '2021-01-13 09:55:00+03',
        'JFK',
        'ORD',
        'Scheduled',
        '321',
        50,
        0,
        'no',
        'no'
    );

insert into flights
values (
        1009,
        'PG0090',
        'Direct',
        '2021-01-17 04:50:00+03',
        '2021-01-17 08:55:00+03',
        'ORD',
        'LAX',
        'Scheduled',
        '320',
        50,
        0,
        'yes',
        'yes'
    );

insert into flights
values (
        1010,
        'PG0010',
        'Direct',
        '2021-01-24 14:50:00+03',
        '2021-01-24 16:55:00+03',
        'LAX',
        'HOU',
        'Scheduled',
        '763',
        50,
        0,
        'no',
        'no'
    );

DROP TABLE IF EXISTS route_information;

CREATE TABLE smart_city.route_information AS
SELECT 
    FROM_UNIXTIME(UNIX_TIMESTAMP(v.timestamp)) AS timestamp,
    CASE
        WHEN v.location REGEXP '^\\[\\d+(\\.\\d+)?,\\s*-?\\d+(\\.\\d+)?\\]$'
        THEN CAST(SUBSTRING_INDEX(TRIM(TRAILING ']' FROM TRIM(LEADING '[' FROM v.location)), ',', 1) AS DECIMAL(10,6))
        ELSE NULL
    END AS latitude,
    CASE
        WHEN v.location REGEXP '^\\[\\d+(\\.\\d+)?,\\s*-?\\d+(\\.\\d+)?\\]$'
        THEN CAST(SUBSTRING_INDEX(TRIM(TRAILING ']' FROM TRIM(LEADING '[' FROM v.location)), ',', -1) AS DECIMAL(10,6))
        ELSE NULL
    END AS longitude,
    CASE
        WHEN v.speed REGEXP '^\\d+(\\.\\d+)?$'
        THEN CAST(v.speed AS DECIMAL(10,2))
        ELSE NULL
    END AS speed,
    v.direction AS direction,
    e.type AS incident_type,
    e.status AS incident_status,
    w.weathercondition AS weather_condition
FROM
    smart_city.vehicle_data v
LEFT JOIN
    smart_city.emergency_data e ON v.timestamp = e.timestamp AND v.location = e.location
LEFT JOIN
    smart_city.weather_data w ON v.timestamp = w.timestamp AND v.location = w.location;

SELECT * FROM smart_city.route_information ORDER BY timestamp;


CREATE TABLE smart_city.coordinates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    latitude DECIMAL(10, 6),
    longitude DECIMAL(10, 6)
);

CREATE TABLE `Flights`(
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `origin_id` INT NOT NULL,
    `destination_id` INT NOT NULL,
    `date` DATETIME NOT NULL,
    `price` DOUBLE(8, 2) NOT NULL
);
CREATE TABLE `Origins`(
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `country` INT NOT NULL,
    `city` INT NOT NULL
);
CREATE TABLE `Destinations`(
    `id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
    `country` INT NOT NULL,
    `city` INT NOT NULL
);
ALTER TABLE
    `Flights` ADD CONSTRAINT `flights_destination_id_foreign` FOREIGN KEY(`destination_id`) REFERENCES `Destinations`(`id`);
ALTER TABLE
    `Flights` ADD CONSTRAINT `flights_origin_id_foreign` FOREIGN KEY(`origin_id`) REFERENCES `Origins`(`id`);
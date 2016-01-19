CREATE TABLE `github_db`.`user_info` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_` VARCHAR(45) NULL,
  `user_name` VARCHAR(45) NULL,
  `user_email` VARCHAR(45) NULL,
  `user_location` VARCHAR(45) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC),
  UNIQUE INDEX `name_UNIQUE` (`user_` ASC));

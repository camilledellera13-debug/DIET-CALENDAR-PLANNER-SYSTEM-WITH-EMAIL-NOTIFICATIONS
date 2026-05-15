-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 27, 2026 at 05:46 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `dietcalendarplannersys`
--

-- --------------------------------------------------------

--
-- Table structure for table `activities`
--

CREATE TABLE `activities` (
  `id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `calories_per_minute` decimal(5,2) NOT NULL,
  `intensity` enum('low','medium','high') NOT NULL,
  `goal_type` enum('lose','gain','maintain','all') NOT NULL,
  `description` text DEFAULT NULL,
  `icon` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `activities`
--

INSERT INTO `activities` (`id`, `name`, `calories_per_minute`, `intensity`, `goal_type`, `description`, `icon`) VALUES
(1, 'Jogging', 11.50, 'high', 'lose', 'Great for burning calories and improving cardiovascular health', '????'),
(2, 'Running', 13.00, 'high', 'lose', 'High-intensity cardio for maximum calorie burn', '????‍♀️'),
(3, 'HIIT Training', 14.50, 'high', 'lose', 'High Intensity Interval Training for rapid fat loss', '⚡'),
(4, 'Jump Rope', 12.50, 'high', 'lose', 'Excellent full-body workout', '????'),
(5, 'Brisk Walking', 5.50, 'medium', 'maintain', 'Low-impact activity for daily health', '????'),
(6, 'Cycling', 8.00, 'medium', 'maintain', 'Great for leg strength and endurance', '????'),
(7, 'Swimming', 9.00, 'medium', 'maintain', 'Full-body low-impact workout', '????'),
(8, 'Yoga', 4.00, 'low', 'maintain', 'Improves flexibility and reduces stress', '????'),
(9, 'Light Walking', 3.50, 'low', 'gain', 'Gentle activity to maintain mobility', '????'),
(10, 'Stretching', 2.50, 'low', 'gain', 'Improves flexibility without burning excess calories', '????‍♀️'),
(11, 'Weight Training', 8.50, 'medium', 'gain', 'Build muscle mass and strength', '????'),
(12, 'Calisthenics', 9.50, 'medium', 'gain', 'Bodyweight exercises for functional strength', '????️');

-- --------------------------------------------------------

--
-- Table structure for table `dietplan`
--

CREATE TABLE `dietplan` (
  `planid` int(11) NOT NULL,
  `userid` int(11) NOT NULL,
  `planname` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `startdate` date NOT NULL,
  `enddate` date DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `dietplan`
--

INSERT INTO `dietplan` (`planid`, `userid`, `planname`, `description`, `startdate`, `enddate`, `created_at`) VALUES
(1, 1, 'Summer Cut 2026', 'High protein, low carb for fat loss', '2026-04-01', '2026-06-30', '2026-04-05 12:46:04'),
(2, 1, 'Maintenance Phase', 'Balanced diet after summer cut', '2026-07-01', '2026-09-30', '2026-04-05 12:46:04'),
(3, 2, 'Clean Bulk', 'Slow muscle gain with clean foods', '2026-04-01', '2026-07-31', '2026-04-05 12:46:04'),
(4, 2, 'Weight Maintenance', 'Keeping current weight stable', '2026-08-01', '2026-12-31', '2026-04-05 12:46:04'),
(5, 3, 'Mass Gain 3000', 'Calorie surplus for muscle gain', '2026-04-15', '2026-08-15', '2026-04-05 12:46:04'),
(6, 3, 'Lean Bulk', 'Moderate surplus, cleaner foods', '2026-08-16', '2026-12-31', '2026-04-05 12:46:04'),
(7, 5, 'My Diet Plan', 'Personalized diet plan', '2026-04-27', '2026-07-27', '2026-04-27 13:39:22');

-- --------------------------------------------------------

--
-- Table structure for table `fooditem`
--

CREATE TABLE `fooditem` (
  `foodid` int(11) NOT NULL,
  `foodname` varchar(100) NOT NULL,
  `calories` decimal(6,2) NOT NULL,
  `protein` decimal(5,2) DEFAULT 0.00,
  `carbs` decimal(5,2) DEFAULT 0.00,
  `fats` decimal(5,2) DEFAULT 0.00
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `fooditem`
--

INSERT INTO `fooditem` (`foodid`, `foodname`, `calories`, `protein`, `carbs`, `fats`) VALUES
(1, 'Chicken Breast', 95.00, 31.00, 0.00, 3.60),
(2, 'Brown Rice', 120.00, 2.60, 23.50, 0.90),
(3, 'Broccoli', 69.00, 3.70, 11.20, 0.60),
(4, 'Apple', 158.00, 0.50, 25.00, 0.30),
(5, 'Grilled Chicken Breast', 95.00, 31.00, 0.00, 3.60),
(6, 'Brown Rice (cooked)', 112.00, 2.60, 23.50, 0.90),
(7, 'Steamed Broccoli', 94.00, 3.70, 11.20, 0.60),
(8, 'Scrambled Eggs (2)', 12.00, 12.00, 1.00, 10.00),
(9, 'Oatmeal with Berries', 208.00, 5.50, 27.00, 3.20),
(10, 'Greek Yogurt', 55.00, 17.00, 6.00, 0.40),
(11, 'Salmon Fillet', 105.00, 22.00, 0.00, 13.00),
(12, 'Sweet Potato', 208.00, 2.00, 27.00, 0.10),
(13, 'Avocado', 165.00, 2.90, 12.00, 21.00),
(14, 'Protein Shake (whey)', 160.00, 24.00, 3.00, 1.50),
(15, 'Quinoa Salad', 165.00, 4.40, 21.30, 1.90),
(16, 'Banana', 100.00, 1.30, 27.00, 0.40),
(17, 'Almonds (10 pcs)', 105.00, 2.50, 2.50, 6.00),
(18, 'Whole Wheat Bread (2 slices)', 165.00, 6.00, 30.00, 2.00),
(19, 'Peanut Butter (1 tbsp)', 94.00, 4.00, 3.50, 8.00),
(20, 'Manok', 120.00, 0.00, 0.00, 0.00);

-- --------------------------------------------------------

--
-- Table structure for table `meal`
--

CREATE TABLE `meal` (
  `mealid` int(11) NOT NULL,
  `planid` int(11) NOT NULL,
  `mealtype` enum('Breakfast','Lunch','Dinner','Snack') NOT NULL,
  `mealdate` date NOT NULL,
  `totalcalories` decimal(6,2) DEFAULT 0.00,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `meal`
--

INSERT INTO `meal` (`mealid`, `planid`, `mealtype`, `mealdate`, `totalcalories`, `created_at`) VALUES
(1, 1, 'Breakfast', '2026-04-03', 277.00, '2026-04-05 12:46:19'),
(2, 1, 'Lunch', '2026-04-03', 414.50, '2026-04-05 12:46:19'),
(3, 1, 'Dinner', '2026-04-03', 520.00, '2026-04-05 12:46:19'),
(4, 1, 'Snack', '2026-04-03', 234.00, '2026-04-05 12:46:19'),
(5, 1, 'Breakfast', '2026-04-04', 340.00, '2026-04-05 12:46:19'),
(6, 1, 'Lunch', '2026-04-04', 465.00, '2026-04-05 12:46:19'),
(7, 1, 'Dinner', '2026-04-04', 510.00, '2026-04-05 12:46:19'),
(8, 1, 'Snack', '2026-04-04', 100.00, '2026-04-05 12:46:19'),
(9, 1, 'Breakfast', '2026-04-05', 340.00, '2026-04-05 12:46:19'),
(10, 1, 'Lunch', '2026-04-05', 450.00, '2026-04-05 12:46:19'),
(11, 1, 'Dinner', '2026-04-05', 520.00, '2026-04-05 12:46:19'),
(12, 1, 'Snack', '2026-04-05', 120.00, '2026-04-05 12:46:19'),
(13, 3, 'Breakfast', '2026-04-03', 294.00, '2026-04-05 12:46:27'),
(14, 3, 'Lunch', '2026-04-03', 373.00, '2026-04-05 12:46:27'),
(15, 3, 'Dinner', '2026-04-03', 195.00, '2026-04-05 12:46:27'),
(16, 3, 'Snack', '2026-04-03', 226.00, '2026-04-05 12:46:27'),
(17, 3, 'Breakfast', '2026-04-04', 420.00, '2026-04-05 12:46:27'),
(18, 3, 'Lunch', '2026-04-04', 580.00, '2026-04-05 12:46:27'),
(19, 3, 'Dinner', '2026-04-04', 620.00, '2026-04-05 12:46:27'),
(20, 3, 'Snack', '2026-04-04', 180.00, '2026-04-05 12:46:27'),
(21, 3, 'Breakfast', '2026-04-05', 420.00, '2026-04-05 12:46:27'),
(22, 3, 'Lunch', '2026-04-05', 550.00, '2026-04-05 12:46:27'),
(23, 3, 'Dinner', '2026-04-05', 600.00, '2026-04-05 12:46:27'),
(24, 3, 'Snack', '2026-04-05', 200.00, '2026-04-05 12:46:27'),
(25, 5, 'Breakfast', '2026-04-16', 461.50, '2026-04-05 12:46:34'),
(26, 5, 'Lunch', '2026-04-16', 656.00, '2026-04-05 12:46:34'),
(27, 5, 'Dinner', '2026-04-16', 412.50, '2026-04-05 12:46:34'),
(28, 5, 'Snack', '2026-04-16', 580.00, '2026-04-05 12:46:34'),
(29, 5, 'Breakfast', '2026-04-17', 650.00, '2026-04-05 12:46:34'),
(30, 5, 'Lunch', '2026-04-17', 780.00, '2026-04-05 12:46:34'),
(31, 5, 'Dinner', '2026-04-17', 820.00, '2026-04-05 12:46:34'),
(32, 5, 'Snack', '2026-04-17', 320.00, '2026-04-05 12:46:34'),
(33, 5, 'Breakfast', '2026-04-18', 650.00, '2026-04-05 12:46:34'),
(34, 5, 'Lunch', '2026-04-18', 750.00, '2026-04-05 12:46:34'),
(35, 5, 'Dinner', '2026-04-18', 800.00, '2026-04-05 12:46:34'),
(36, 5, 'Snack', '2026-04-18', 300.00, '2026-04-05 12:46:34');

-- --------------------------------------------------------

--
-- Table structure for table `mealfood`
--

CREATE TABLE `mealfood` (
  `mealid` int(11) NOT NULL,
  `foodid` int(11) NOT NULL,
  `quantity` decimal(5,2) NOT NULL DEFAULT 1.00,
  `servingsize` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `mealfood`
--

INSERT INTO `mealfood` (`mealid`, `foodid`, `quantity`, `servingsize`) VALUES
(1, 5, 1.00, '1 bowl'),
(1, 6, 1.00, '1 cup'),
(2, 1, 1.50, '150g'),
(2, 2, 1.00, '1 cup'),
(2, 3, 1.00, '1 cup'),
(4, 13, 1.00, '10 almonds'),
(13, 4, 1.00, '2 eggs'),
(13, 9, 0.50, '0.5 avocado'),
(13, 14, 1.00, '2 slices'),
(14, 1, 1.00, '100g'),
(14, 11, 1.00, '1 cup'),
(15, 7, 1.00, '150g'),
(15, 8, 1.00, '1 medium'),
(16, 6, 1.00, '1 cup'),
(16, 12, 1.00, '1 banana'),
(25, 5, 1.50, '1.5 bowls'),
(25, 10, 1.00, '1 scoop'),
(25, 12, 1.00, '1 banana'),
(26, 1, 2.00, '200g'),
(26, 2, 1.50, '1.5 cups'),
(26, 9, 1.00, '1 avocado'),
(27, 7, 1.50, '200g'),
(27, 8, 1.50, '1.5 medium'),
(27, 15, 1.00, '1 tbsp'),
(28, 6, 1.00, '1 cup'),
(28, 13, 2.00, '20 almonds');

-- --------------------------------------------------------

--
-- Table structure for table `progresslog`
--

CREATE TABLE `progresslog` (
  `logid` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `date` date NOT NULL,
  `weight` decimal(5,2) NOT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `progresslog`
--

INSERT INTO `progresslog` (`logid`, `user_id`, `date`, `weight`, `notes`, `created_at`) VALUES
(1, 1, '2026-04-01', 85.30, 'Starting weight', '2026-04-05 12:48:19'),
(2, 1, '2026-04-08', 84.50, 'Down 0.8kg, feeling good', '2026-04-05 12:48:19'),
(3, 1, '2026-04-15', 83.90, 'Steady progress', '2026-04-05 12:48:19'),
(4, 1, '2026-04-22', 83.10, 'Energy levels high', '2026-04-05 12:48:19'),
(5, 1, '2026-04-29', 82.40, 'Halfway to goal', '2026-04-05 12:48:19'),
(6, 2, '2026-04-01', 68.50, 'Starting weight', '2026-04-05 12:48:19'),
(7, 2, '2026-04-08', 68.40, 'Stable', '2026-04-05 12:48:19'),
(8, 2, '2026-04-15', 68.60, 'Slight fluctuation, normal', '2026-04-05 12:48:19'),
(9, 2, '2026-04-22', 68.30, 'Maintenance working well', '2026-04-05 12:48:19'),
(10, 2, '2026-04-29', 68.50, 'Back to start, perfect', '2026-04-05 12:48:19'),
(11, 3, '2026-04-15', 92.00, 'Starting bulk', '2026-04-05 12:48:19'),
(12, 3, '2026-04-22', 92.80, 'Up 0.8kg, good start', '2026-04-05 12:48:19'),
(13, 3, '2026-04-29', 93.50, 'Steady gain, strength up', '2026-04-05 12:48:19'),
(14, 3, '2026-05-06', 94.20, 'Hitting calorie targets', '2026-04-05 12:48:19'),
(15, 3, '2026-05-13', 95.00, '5kg gained total', '2026-04-05 12:48:19');

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `userid` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(150) NOT NULL,
  `password` varchar(255) NOT NULL,
  `age` int(11) DEFAULT NULL,
  `gender` enum('Male','Female','Other') DEFAULT NULL,
  `height` decimal(5,2) DEFAULT NULL,
  `weight` decimal(5,2) DEFAULT NULL,
  `goal` enum('lose','gain','maintain') NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `user`
--

INSERT INTO `user` (`userid`, `name`, `email`, `password`, `age`, `gender`, `height`, `weight`, `goal`, `created_at`) VALUES
(1, 'John Doe', 'john@example.com', 'hashed_pw_123', 30, 'Male', 175.50, 80.20, 'lose', '2026-04-05 12:43:35'),
(2, 'John Smith', 'john.smith@email.com', 'hashed_pw_123', 32, 'Male', 180.50, 85.30, 'lose', '2026-04-05 12:45:46'),
(3, 'Sarah Johnson', 'sarah.j@email.com', 'hashed_pw_456', 28, 'Female', 165.00, 68.50, 'maintain', '2026-04-05 12:45:46'),
(4, 'Mike Chen', 'mike.chen@email.com', 'hashed_pw_789', 35, 'Male', 175.00, 92.00, 'gain', '2026-04-05 12:45:46'),
(5, 'joshtravieza', '1231travz@gmail.com', '5994471abb01112afcc18159f6cc74b4f511b99806da59b3caf5a9c173cacfc5', 23, NULL, 158.00, 52.00, 'gain', '2026-04-27 13:39:22');

-- --------------------------------------------------------

--
-- Table structure for table `user_activities`
--

CREATE TABLE `user_activities` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `activity_id` int(11) NOT NULL,
  `duration_minutes` int(11) NOT NULL,
  `date` date NOT NULL,
  `calories_burned` int(11) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `user_preferences`
--

CREATE TABLE `user_preferences` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `preference_key` varchar(100) NOT NULL,
  `preference_value` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `waterintake`
--

CREATE TABLE `waterintake` (
  `intakeid` int(11) NOT NULL,
  `userid` int(11) NOT NULL,
  `date` date NOT NULL,
  `amountml` int(11) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `waterintake`
--

INSERT INTO `waterintake` (`intakeid`, `userid`, `date`, `amountml`, `created_at`) VALUES
(1, 1, '2026-04-03', 2500, '2026-04-05 12:48:11'),
(2, 1, '2026-04-04', 2700, '2026-04-05 12:48:11'),
(3, 1, '2026-04-05', 2600, '2026-04-05 12:48:11'),
(4, 2, '2026-04-03', 2100, '2026-04-05 12:48:11'),
(5, 2, '2026-04-04', 2300, '2026-04-05 12:48:11'),
(6, 2, '2026-04-05', 2200, '2026-04-05 12:48:11'),
(7, 3, '2026-04-16', 3000, '2026-04-05 12:48:11'),
(8, 3, '2026-04-17', 3200, '2026-04-05 12:48:11'),
(9, 3, '2026-04-18', 3100, '2026-04-05 12:48:11');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `activities`
--
ALTER TABLE `activities`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `dietplan`
--
ALTER TABLE `dietplan`
  ADD PRIMARY KEY (`planid`),
  ADD KEY `idx_dietplan_user` (`userid`);

--
-- Indexes for table `fooditem`
--
ALTER TABLE `fooditem`
  ADD PRIMARY KEY (`foodid`),
  ADD UNIQUE KEY `foodname` (`foodname`);

--
-- Indexes for table `meal`
--
ALTER TABLE `meal`
  ADD PRIMARY KEY (`mealid`),
  ADD KEY `idx_meal_plan` (`planid`),
  ADD KEY `idx_meal_date` (`mealdate`);

--
-- Indexes for table `mealfood`
--
ALTER TABLE `mealfood`
  ADD PRIMARY KEY (`mealid`,`foodid`),
  ADD KEY `foodid` (`foodid`);

--
-- Indexes for table `progresslog`
--
ALTER TABLE `progresslog`
  ADD PRIMARY KEY (`logid`),
  ADD UNIQUE KEY `unique_daily_progress` (`user_id`,`date`),
  ADD KEY `idx_progress_user_date` (`user_id`,`date`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`userid`),
  ADD UNIQUE KEY `email` (`email`),
  ADD KEY `idx_user_email` (`email`);

--
-- Indexes for table `user_activities`
--
ALTER TABLE `user_activities`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `activity_id` (`activity_id`);

--
-- Indexes for table `user_preferences`
--
ALTER TABLE `user_preferences`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_preference` (`user_id`,`preference_key`);

--
-- Indexes for table `waterintake`
--
ALTER TABLE `waterintake`
  ADD PRIMARY KEY (`intakeid`),
  ADD UNIQUE KEY `unique_daily_water` (`userid`,`date`),
  ADD KEY `idx_water_user_date` (`userid`,`date`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `activities`
--
ALTER TABLE `activities`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `dietplan`
--
ALTER TABLE `dietplan`
  MODIFY `planid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `fooditem`
--
ALTER TABLE `fooditem`
  MODIFY `foodid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `meal`
--
ALTER TABLE `meal`
  MODIFY `mealid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=274;

--
-- AUTO_INCREMENT for table `progresslog`
--
ALTER TABLE `progresslog`
  MODIFY `logid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=16;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `userid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `user_activities`
--
ALTER TABLE `user_activities`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user_preferences`
--
ALTER TABLE `user_preferences`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `waterintake`
--
ALTER TABLE `waterintake`
  MODIFY `intakeid` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `dietplan`
--
ALTER TABLE `dietplan`
  ADD CONSTRAINT `dietplan_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `user` (`userid`) ON DELETE CASCADE;

--
-- Constraints for table `meal`
--
ALTER TABLE `meal`
  ADD CONSTRAINT `meal_ibfk_1` FOREIGN KEY (`planid`) REFERENCES `dietplan` (`planid`) ON DELETE CASCADE;

--
-- Constraints for table `mealfood`
--
ALTER TABLE `mealfood`
  ADD CONSTRAINT `mealfood_ibfk_1` FOREIGN KEY (`mealid`) REFERENCES `meal` (`mealid`) ON DELETE CASCADE,
  ADD CONSTRAINT `mealfood_ibfk_2` FOREIGN KEY (`foodid`) REFERENCES `fooditem` (`foodid`) ON DELETE CASCADE;

--
-- Constraints for table `progresslog`
--
ALTER TABLE `progresslog`
  ADD CONSTRAINT `progresslog_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`userid`) ON DELETE CASCADE;

--
-- Constraints for table `user_activities`
--
ALTER TABLE `user_activities`
  ADD CONSTRAINT `user_activities_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`userid`) ON DELETE CASCADE,
  ADD CONSTRAINT `user_activities_ibfk_2` FOREIGN KEY (`activity_id`) REFERENCES `activities` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `user_preferences`
--
ALTER TABLE `user_preferences`
  ADD CONSTRAINT `user_preferences_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`userid`) ON DELETE CASCADE;

--
-- Constraints for table `waterintake`
--
ALTER TABLE `waterintake`
  ADD CONSTRAINT `waterintake_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `user` (`userid`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

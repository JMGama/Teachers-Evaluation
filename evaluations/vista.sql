CREATE ALGORITHM = UNDEFINED DEFINER = `root`@`localhost` SQL SECURITY DEFINER VIEW `1streport` AS SELECT
	`evaluations_signatures`.`name` AS `signature`,
	concat(
		`evaluations_teachers`.`name`,
		' ',
		`evaluations_teachers`.`lastName`,
		' ',
		`evaluations_teachers`.`lastName2`
	) AS `name`,
	`fnQavg` (
		1,
		`evaluations_detail_student_signature_exam`.`idSignature`,
		`evaluations_detail_student_group`.`idGroup`
	) AS `Q1`,
	`fnQavg` (
		2,
		`evaluations_detail_student_signature_exam`.`idSignature`,
		`evaluations_detail_student_group`.`idGroup`
	) AS `Q2`,
	`fnQavg` (
		3,
		`evaluations_detail_student_signature_exam`.`idSignature`,
		`evaluations_detail_student_group`.`idGroup`
	) AS `Q3`,
	`fnQavg` (
		4,
		`evaluations_detail_student_signature_exam`.`idSignature`,
		`evaluations_detail_student_group`.`idGroup`
	) AS `Q4`,
	(
		SELECT
			group_concat(`ans`.`answer` SEPARATOR ':')
		FROM
			(
				`evaluations_answers` `ans`
				JOIN `evaluations_detail_student_group` `det` ON (
					(`det`.`id` = `ans`.`idGroup`)
				)
			)
		WHERE
			(
				(`ans`.`idQuestion` = 5)
				AND (
					`det`.`idSignature` = `evaluations_detail_student_signature_exam`.`idSignature`
				)
				AND (
					`det`.`idGroup` = `evaluations_detail_student_group`.`idGroup`
				)
			)
	) AS `Q5`,
	(
		SELECT
			count(DISTINCT `ans`.`idStudent`)
		FROM
			(
				`evaluations_answers` `ans`
				JOIN `evaluations_detail_student_group` `det` ON (
					(`det`.`id` = `ans`.`idGroup`)
				)
			)
		WHERE
			(
				(`ans`.`idQuestion` = 1)
				AND (
					`det`.`idSignature` = `evaluations_detail_student_signature_exam`.`idSignature`
				)
				AND (
					`det`.`idGroup` = `evaluations_detail_student_group`.`idGroup`
				)
			)
	) AS `Ptotal`,
	`evaluations_detail_student_signature_exam`.`idTeacher` AS `idTeacher`,
	`evaluations_detail_student_signature_exam`.`idSignature` AS `idSignature`
FROM
	(
		(
			(
				`evaluations_detail_student_signature_exam`
				JOIN `evaluations_signatures` ON (
					(
						`evaluations_detail_student_signature_exam`.`idSignature` = `evaluations_signatures`.`id`
					)
				)
			)
			JOIN `evaluations_teachers` ON (
				(
					`evaluations_detail_student_signature_exam`.`idTeacher` = `evaluations_teachers`.`idPerson`
				)
			)
		)
		JOIN `evaluations_detail_student_group` ON (
			(
				`evaluations_detail_student_group`.`id` = `evaluations_detail_student_signature_exam`.`idGroup`
			)
		)
	)
GROUP BY
	`evaluations_detail_student_group`.`idSignature`,
	`evaluations_detail_student_signature_exam`.`idTeacher`

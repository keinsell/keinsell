open OUnit2;

/* Test cases for CSV parser */
let test_parse_content = _ => {
  let input = "a,b,c\n1,2,3\n4,5,6";

  /* Call the parser */
  let result = Csv.parse_content(input);

  /* Check overall structure */
  assert_equal(3, List.length(result), ~msg="Should have 3 rows");

  /* Check first row */
  switch (List.nth_opt(result, 0)) {
  | Some(row) =>
    assert_equal(
      3,
      List.length(row),
      ~msg="First row should have 3 columns",
    );
    assert_equal(
      "a",
      List.nth(row, 0),
      ~msg="First row, first column should be 'a'",
    );
    assert_equal(
      "b",
      List.nth(row, 1),
      ~msg="First row, second column should be 'b'",
    );
    assert_equal(
      "c",
      List.nth(row, 2),
      ~msg="First row, third column should be 'c'",
    );
  | None => assert_failure("First row is missing")
  };

  /* Check second row */
  switch (List.nth_opt(result, 1)) {
  | Some(row) =>
    assert_equal(
      3,
      List.length(row),
      ~msg="Second row should have 3 columns",
    );
    assert_equal(
      "1",
      List.nth(row, 0),
      ~msg="Second row, first column should be '1'",
    );
    assert_equal(
      "2",
      List.nth(row, 1),
      ~msg="Second row, second column should be '2'",
    );
    assert_equal(
      "3",
      List.nth(row, 2),
      ~msg="Second row, third column should be '3'",
    );
  | None => assert_failure("Second row is missing")
  };

  /* Check third row */
  switch (List.nth_opt(result, 2)) {
  | Some(row) =>
    assert_equal(
      3,
      List.length(row),
      ~msg="Third row should have 3 columns",
    );
    assert_equal(
      "4",
      List.nth(row, 0),
      ~msg="Third row, first column should be '4'",
    );
    assert_equal(
      "5",
      List.nth(row, 1),
      ~msg="Third row, second column should be '5'",
    );
    assert_equal(
      "6",
      List.nth(row, 2),
      ~msg="Third row, third column should be '6'",
    );
  | None => assert_failure("Third row is missing")
  };

  /* Test success! */
  print_endline("CSV parser test passed successfully!");
};

/* Test empty content */
let test_empty_content = _ => {
  let input = "";
  let result = Csv.parse_content(input);

  /* Should get a list with one empty item (empty string gets split to a single item) */
  assert_equal(
    1,
    List.length(result),
    ~msg="Empty content should produce a single row",
  );

  /* Check the row */
  switch (List.nth_opt(result, 0)) {
  | Some(row) =>
    assert_equal(
      1,
      List.length(row),
      ~msg="Empty content row should have 1 empty column",
    );
    assert_equal(
      "",
      List.nth(row, 0),
      ~msg="Empty content column should be empty string",
    );
  | None => assert_failure("Row is missing from empty content")
  };

  print_endline("Empty content test passed successfully!");
};

/* Test single line */
let test_single_line = _ => {
  let input = "a,b,c,d";
  let result = Csv.parse_content(input);

  assert_equal(
    1,
    List.length(result),
    ~msg="Single line should produce 1 row",
  );

  /* Check the row */
  switch (List.nth_opt(result, 0)) {
  | Some(row) =>
    assert_equal(
      4,
      List.length(row),
      ~msg="Single line should have 4 columns",
    );
    assert_equal("a", List.nth(row, 0), ~msg="First column should be 'a'");
    assert_equal("b", List.nth(row, 1), ~msg="Second column should be 'b'");
    assert_equal("c", List.nth(row, 2), ~msg="Third column should be 'c'");
    assert_equal("d", List.nth(row, 3), ~msg="Fourth column should be 'd'");
  | None => assert_failure("Row is missing from single line")
  };

  print_endline("Single line test passed successfully!");
};

/* Test empty fields */
let test_empty_fields = _ => {
  let input = "a,,c\n,,\nd,e,";
  let result = Csv.parse_content(input);

  assert_equal(3, List.length(result), ~msg="Should have 3 rows");

  /* Check first row with middle empty field */
  switch (List.nth_opt(result, 0)) {
  | Some(row) =>
    assert_equal(
      3,
      List.length(row),
      ~msg="First row should have 3 columns",
    );
    assert_equal(
      "a",
      List.nth(row, 0),
      ~msg="First row, first column should be 'a'",
    );
    assert_equal(
      "",
      List.nth(row, 1),
      ~msg="First row, second column should be empty",
    );
    assert_equal(
      "c",
      List.nth(row, 2),
      ~msg="First row, third column should be 'c'",
    );
  | None => assert_failure("First row is missing")
  };

  /* Check second row with all empty fields */
  switch (List.nth_opt(result, 1)) {
  | Some(row) =>
    assert_equal(
      3,
      List.length(row),
      ~msg="Second row should have 3 columns",
    );
    assert_equal(
      "",
      List.nth(row, 0),
      ~msg="Second row, first column should be empty",
    );
    assert_equal(
      "",
      List.nth(row, 1),
      ~msg="Second row, second column should be empty",
    );
    assert_equal(
      "",
      List.nth(row, 2),
      ~msg="Second row, third column should be empty",
    );
  | None => assert_failure("Second row is missing")
  };

  /* Check third row with last empty field */
  switch (List.nth_opt(result, 2)) {
  | Some(row) =>
    assert_equal(
      3,
      List.length(row),
      ~msg="Third row should have 3 columns",
    );
    assert_equal(
      "d",
      List.nth(row, 0),
      ~msg="Third row, first column should be 'd'",
    );
    assert_equal(
      "e",
      List.nth(row, 1),
      ~msg="Third row, second column should be 'e'",
    );
    assert_equal(
      "",
      List.nth(row, 2),
      ~msg="Third row, third column should be empty",
    );
  | None => assert_failure("Third row is missing")
  };

  print_endline("Empty fields test passed successfully!");
};

/* Define test suite */
let suite =
  "CSV Parser Tests"
  >::: [
    "test_parse_content" >:: test_parse_content,
    "test_empty_content" >:: test_empty_content,
    "test_single_line" >:: test_single_line,
    "test_empty_fields" >:: test_empty_fields,
  ];

/* Run the tests with verbose output */
let () = run_test_tt_main(suite);

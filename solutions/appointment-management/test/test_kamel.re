open Alcotest;

let test_create_identity_model () = {
  let identity = Kamel.Identity.Identity.create(None, "test-user", "test-pass");
  Alcotest.check(string, "username matches", "test-user", identity.username)
  // TODO: Should check if password was hashed
  // TODO: Should check if id is a uuid
};

let () = {
  Alcotest.run("Kamel", [
 ("Identity", [
  Alcotest.test_case("create identity", `Quick, test_create_identity_model)
 ])
  ]);
}

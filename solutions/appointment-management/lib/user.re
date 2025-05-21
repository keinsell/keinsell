type user_id = UserId(string);

module Email = {
  type t = Email(string);

  let create = (email: string): t => {
    Email(email);
  };
};

type email = Email.t;

module Password = {
  type t = Password(string);

  let hash = (password: string): t => {
    /// TODO: Implement hashing algorithm (argon2)
    Password(password);
  };

  let verify = (hash: t, plain: string): bool => {
    let hash_as_string = switch (hash) {
      | Password(p) => p
    };
    /// TODO: Implement verification logic
    hash_as_string == plain
  }
};

type password = Password.t;

let _generate_user_id = (): user_id => UserId(Random.int(1000000) |> string_of_int);

type user = {
  id: user_id,
  first_name: string,
  last_name: string,
  email: email,
  password: password,
  created_at: string,
  updated_at: string,
};

type user_repository = {
  insert: (user) => Result.t(user, string),
}


type create_user = {
  id: option(user_id),
  first_name: string,
  last_name: string,
  email: email,
  created_at: option(string),
  updated_at: option(string),
};

type register_user = {
  first_name: string,
  last_name: string,
  email: email,
  password: password,
};

let create_user = (
  register_user: register_user,
  user_repository: user_repository,
): Result.t(user, string) => {
  let user = {
    id: _generate_user_id(),
    first_name: register_user.first_name,
    last_name: register_user.last_name,
    email: register_user.email,
    password: register_user.password,
    created_at: "",
    updated_at: "",
  };

 let maybe_user =  user_repository.insert(user);
  switch (maybe_user) {
    | Ok(user) => {
        Ok(user)
      }
    | Error(error) => {
        Error(error)
      }
  };
};

module Password = {
    type t = string;
    let create = (password: string) => password;
    let verify = (password: string, hash: t) => password == hash;
  };

/** Password represent hash of orginally provided password which is stored in the database. */
type password = Password.t;

/** Module representing an identity with a unique ID, username, and password. */
module Identity = {
  /** Type representing a unique identifier for an identity. */
  type identity_id = IdentityId(string);

  /** Type representing an identity, containing its ID, username, and password. */
  type t = {
    id: identity_id,
    username: string,
    password: password,
  };

  /**
   * Creates a new identity.
   * If an ID is provided, it will be used; otherwise, a random ID will be generated.
   * @param id An optional string representing the identity's ID.
   * @param username The username for the identity.
   * @param password The hashed password for the identity.
   * @return The created identity record.
   */
  let create = (
    id: option(string),
    username: string,
    password: Password.t,
  ) => {
      let id = switch (id) {
        | Some(id) => IdentityId(id)
        | None => IdentityId(string_of_int(Random.int(1000000)))
      };
      {id, username, password};
  };
};

/** Type alias for `Identity.t`. Represents an identity. */
type identity = Identity.t;

/**
 * Represents a repository for storing and retrieving identities.
 * It defines an `insert` function to add new identities.
 */
type identity_repository = {
  insert: (identity) => Result.t(identity, string),
};

module Command = {
  /** Type representing a command to create an identity. */
  type create_identity = {
    id: option(string),
    username: string,
    password: Password.t,
  };

  /** Type representing a command to register an identity. */
  type register_identity = {
    username: string,
    password: Password.t,
  };
};


/**
 * Creates a new identity.
 */
let register_identity = (
  register_identity: Command.register_identity,
  identity_repository: identity_repository,
): Result.t(Identity.t, string) => {
  Identity.create(
    None,
    register_identity.username,
    register_identity.password,
  ) |> identity_repository.insert |> fun(result) => switch(result) {
  | Ok(identity_created) => {
    Logs.info @@ fun (m) => {
      m("Identity created: %s", identity_created.username);
    };
    Ok(identity_created)
  } | Error(error_during_identity_creation) => {
    Logs.err @@ fun (m) => {
      m("Error creating identity: %s", error_during_identity_creation);
    };
    Error(error_during_identity_creation)
  }
};
}

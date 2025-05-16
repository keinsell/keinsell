[@@@ocaml.format "ignore"]
[@@@ocaml.warning "-4"]
[@@@ocaml.warning "-3"]
[@@@ocaml.warning "-27"]
[@@@ocaml.warning "-26"]
[@@@ocaml.warning "-27"]
[@@@ocaml.warning "-32"]
(*
No matter how bad it actually sounds, it's my first-ever parser that I am writing out of pure curiosity and boredom of web apis and software applications. Not as much complex task, however it's probably the best environment to try a new langauge and explore what one have to offer.

.ini configuration files come with multiple dialects
- Sections are marked with `[section_name]`
- Key-value pairs formatter as key=value
- Comment lintes starting with ; or #
- Support for whitespace around delimiters
*)

(* define a very small sample which would represent ini file *)
let the_most_hated_ini_config : string =
{|hello = world
[database]
# lucky you...
host=localhost
port=1337
[logging]
; you should use INFO or ERROR
level = INFO
|}

(* Define myself types because i am de facto retarded,
to which point one must fuckup oneself to not remember
which string is which string. *)

(* Sections are marked with `[section_name]` *)
type selection = Selection of string

let get_section_name (selection: selection) =
  match selection with
  | Selection(name) -> name

(* Key-value pairs formatter as key=value *)
type property = Property of (string * string option)

let get_property_key (prop: property) =
  match prop with
  | Property(key, _) -> key

let get_property_value (prop: property) =
  match prop with
  | Property(_, value) -> value

let get_property_value_or_empty (prop: property) =
  match prop with
  | Property(_, value) -> value |> Option.value ~default:""

let create_property (key: string) (value: string option) =
  Property(key, value)

(* Comment lintes starting with ; or # *)
type comment = Comment of string

(* Empty line *)
type unknown_line = Selection | Property | Comment | Empty

(* define function with one string parameter called "ini_content" which returns list of strings, in our case we put there whole stringified ini file which is parsed into individual lines *)
let chunk_file_content (ini_content : string) : string list =
  String.split_on_char '\n' ini_content

(* function will check if given string is selection by looking out for brackets *)
let is_selection_line (line : string) : bool =
  String.length line > 0
  && line.[0] = '['
  && line.[String.length line - 1] = ']'

let parse_selection_line (line : string) : selection option =
  if is_selection_line line then
    let content = String.sub line 1 (String.length line - 2) |> String.trim in
    Some (Selection content)
  else
    None

let is_comment_line (line : string) : bool =
  String.length line > 0 && (line.[0] == ';' || line.[0] == '#')

let parse_comment_line (line : string) : comment option =
  let is_comment : bool = is_comment_line line in
  if is_comment then Some (Comment line) else None

(* TODO: To chyba nie jest poprawnie *)
let is_property_line (line : string) : bool =
  String.length line > 0 && String.contains line '='

let parse_property_line (line : string) : property option =
  let is_property : bool = is_property_line line in
  if is_property then
    let parts = String.split_on_char '=' line in
    let key = List.nth parts 0 in
    let value = List.nth_opt parts 1 in
    let trimmed_key = String.trim key in
    let trimmed_value = Option.map String.trim value in
    Some (Property (trimmed_key, trimmed_value))
  else None

(* at this point we theoretically should be able to parse all of the lines, yet there is a need to handle selections and prefix keys of actual values. *)

let match_line_kind (line : string) : unknown_line =
  let maybe_comment = parse_comment_line line in
  let maybe_property = parse_property_line line in
  let maybe_selection = parse_selection_line line in
  match (maybe_comment, maybe_property, maybe_selection) with
  | Some _, _, _ -> Comment
  | _, Some _, _ -> Property
  | _, _, Some _ -> Selection
  | _ -> Empty

let print_kind (kind : unknown_line) : string =
  match kind with
  | Comment -> "[COMMENT]"
  | Property -> "[PROPERTY]"
  | Selection -> "[SELECTION]"
  | Empty -> "[EMPTY]"

let print_line_content_and_kind (line : string) : unit =
  let kind = match_line_kind line in
  match kind with
  | Comment -> print_endline (Printf.sprintf "[COMMENT] %s" line)
  | Property -> print_endline (Printf.sprintf "[PROPERTY] %s" line)
  | Selection -> print_endline (Printf.sprintf "[SELECTION] %s" line)
  | Empty -> print_endline "Empty"

let walk_line_list (lines : string list) : unit =
  List.iter print_line_content_and_kind lines

let () =
  let selection_prefix : selection option ref = ref None in
  let parsed_properties_storage = ref [] in
  let ini_lines = (chunk_file_content the_most_hated_ini_config) in
  let seq = List.to_seq ini_lines in

  (Seq.iter (fun (line: string) ->
    let kind = match_line_kind line in
    let line_parts: string list = ["[L] "; (print_kind kind); " "; line; ] in
    let debug_line: string =  String.concat "" line_parts in
    print_endline debug_line;
    let trimmed_line = String.trim line in
    match kind with
    | Comment -> let maybe_comment = parse_comment_line trimmed_line in
      if Option.is_some maybe_comment then ()
    | Property ->
        let maybe_property = parse_property_line trimmed_line in
        (match maybe_property with
          | Some(ppp) ->
            let prefix = match !selection_prefix with
              | Some(selection) -> get_section_name selection
              | None -> ""
            in
            let key = if prefix != "" then prefix ^ "." ^ (get_property_key ppp) else (get_property_key ppp) in
            let value = get_property_value ppp in
            let kv = (create_property key value) in
            parsed_properties_storage := kv :: !parsed_properties_storage
          | None -> ())
    | Selection ->
      let maybe_selection = parse_selection_line trimmed_line in
      (
        match maybe_selection with
          | Some(selection) -> selection_prefix := Some(selection)
          | None -> ()
      )
    | Empty -> print_endline "Empty"
  ) seq);
  let parsed_values_count: int = (List.length !parsed_properties_storage) in
  print_endline (Printf.sprintf "Parsed values count: %d" parsed_values_count);

let parsed_sequence = List.to_seq !parsed_properties_storage in
print_endline "----------------------------------";
Seq.iter (fun (property: property) ->
    let key = get_property_key property in
    let value = get_property_value_or_empty property in
    print_endline (Printf.sprintf "%s=%s" key value)
  ) parsed_sequence;
print_endline "----------------------------------";

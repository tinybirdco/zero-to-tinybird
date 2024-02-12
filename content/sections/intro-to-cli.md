# An introduction to the Tinybird CLI
  
What we will do in this session:   
  * Install the CLI.
  * Exploring our Workspace with the CLI.
  * Touring available commands and preparing for managing projects under version control.

### Screencasts:

* [Getting started with the CLI](https://youtu.be/OOEe84ly7Cs)
* [Create a Workspace from the CLI](https://youtu.be/-jozbkGu31A)
* [Edit a Data Source schema with the CLI](https://youtu.be/gzpuQfk3Byg)


### Documentation:

* [Getting started guide](https://www.tinybird.co/docs/quick-start-cli.html)
* [Tinybird CLI](https://www.tinybird.co/docs/cli.html)

* [Advanced templating with the CLI](https://www.tinybird.co/docs/cli/advanced-templates.html)

* [Common use cases](https://www.tinybird.co/docs/cli/common-use-cases.html)

## Installing the CLI

Here, we are creating a `.temp-project` virtual environment, loading the environment, then installing the `tinybird-cli` with PIP. 

```bash
python3 -m venv .temp-project
source .temp-project/bin/activate

pip3 install tinybird-cli
```


## Example commands

### Getting started

* tb --help
* tb auth --help
  * --interactive
* tb init --help
  * --git
  * --cicd
  * --generate-datasources
  * --force
  * --folder

### Commands for working directly with Tinybird core objects:
* tb workspace --help
  * tb workspace [OPTIONS] COMMAND [ARGS]
  * ls / current / create / delete / use
  * tb workspace create --fork
* tb datasource --help
  *  tb datasource [OPTIONS] COMMAND [ARGS]
  * ls / generate / truncate / analyze / append / connect / copy / rm
* tb pipe --
  * tb pipe [OPTIONS] COMMAND [ARGS]
  * ls / generate / publish / unpublish / rm / stats 

* tb materialize --help  
  * tb materialize [OPTIONS] FILENAME [TARGET_DATASOURCE]

### Commands for working with version control 

* tb branch --help
  * tb branch [OPTIONS] COMMAND [ARGS]
  * ls / create / current / data / datasource / rm
* tb deploy --help
  * tb deploy [OPTIONS]
  * tb --semver <semver> deploy
  * semver <semver> format is major.minor.patch-post where major, minor, patch and post are integer numbers.

### Utilities: 
* tb fmt --help
* tb sql --help
* tb check --help
* tb pull --help
  * --auto --force
* tb push --help 
  * --auto --force 


## A tour of our project

* Install CLI if needed:
  ```bash
  python3 -m venv .temp-project
  source .temp-project/bin/activate
  pip3 install tinybird-cli
  ```
* Authenticate with Tinybird Auth Token
  * Using `admin @email` Token.

  ```bash
  tb auth
  ```

* Explore the CLI and project

  ```bash
  tb --help

  tb workspace ls

  tb datasource ls

  tb pipe ls

  tb sql "SELECT COUNT(*) FROM event_stream"
  tb sql "SELECT timestamp,symbol,price FROM event_stream WHERE symbol='ALG' LIMIT 10"

  tb branch ls
  ```

* Download resources from Tinybird

  ```bash 
  tb pull --auto
  ```

* Create a new Workspace

```bash
tb workspace create cli_temp
```






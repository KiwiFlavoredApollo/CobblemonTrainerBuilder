# README

CobblemonTrainerGenerator made for [CobblemonTrainer](https://github.com/davo899/CobblemonTrainers) by selfdot

GUI provided by the mod itself isn't bad, but it feels quite cumbersome when adding Pokemon and configuring their movesets. This script aims to mitigate that by automating moveset creation.

## Usage

```commandline
python main.py
```

### Exporting to json files

Scripts automatically create `export` directory for you

### Importing from json files

If you want to import `.json` files, create `import` directory at the root of the project (where `main.py` resides) and put `.json` files there

## Dependency

- Requests
- Inquirer
- CobblemonTrainer 0.9.12
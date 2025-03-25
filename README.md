# pocket-to-html
This script converts [Pocket's](https://getpocket.com/) .csv files and Firefox .json backups to a HTML file.

![Running version 0.3.0 in Termux](assets/demo.gif)

## Getting Started

### Prerequisites
The only thing you need is **Python 3** (version 3.8 would be enough).

### Installation

1. Download `pocket-to-html.py`
2. Run `chmod +x pocket-to-html.py` if you don't want to type `python script_name.py its_arguments` every time

## Usage
If you run the line below, data from `part_000000.csv` will be read and output will be written to `bookmarks.html`.

```shell
python pocket-to-html.py -o bookmarks.html part_000000.csv
```
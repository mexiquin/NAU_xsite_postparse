# README.md

## Usage Text

```
usage: blockparse-win.exe [-h] [-u USERNAME] [-p PASSWORD] selector

Find selector in NAU sites. You can use this to print out all marketing-2021 sites that contain a specific selector.
Or you can pipe the STDOUT to a file to save the results for later.

Data is sent to STDOUT. All progress is printed to STDERR.

Output data will be in TSV format:
page/post-url (tab) number-of-blocks-present

positional arguments:
  selector              CSS selector to find

options:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Username for NAU sites
  -p PASSWORD, --password PASSWORD
                        Password for NAU sites
```

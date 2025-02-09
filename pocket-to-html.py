#!/usr/bin/env python3
import csv
import argparse

parser = argparse.ArgumentParser(prog="pocket-to-html", description="This script converts Pocket backup to Netscape's bookmarks file")
parser.add_argument("input", help="Path of Pocket's .csv backup file")
parser.add_argument("-o", "--output", default=None, help="Path of output HTML file (default: contents are printed to console)")
args = parser.parse_args()
bookmark_str = "<!DOCTYPE NETSCAPE-Bookmark-file-1>\n<!-- This is an automatically generated file.\n     It will be read and overwritten.\n     DO NOT EDIT! -->"
bookmark_str += '\n<!-- Visit https://learn.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/aa753582(v=vs.85) to learn more -->\n<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">'
bookmark_str += '\n<META NAME="generator" CONTENT="pocket-to-html.py">\n    <Title>Bookmarks</Title>\n    <H1>Bookmarks</H1>\n    <DL>'
if args.input:
    pocket_file = args.input
if args.output != None:
    out_file = args.output
else:
    out_file = None
if pocket_file == None:
    print("Error: no `pocket_file`")
    exit()
with open(pocket_file, "r", encoding="utf-8") as pocket_csv:
    reader = csv.DictReader(pocket_csv)
    for row in reader:
        bookmark_str += f'\n    <DT><A HREF="{row["url"]}" ADD_DATE="{row["time_added"]}" LAST_VISIT="{row["time_added"]}"\n        LAST_MODIFIED="{row["time_added"]}">{row["title"]} (tags: `{row["tags"]}`)</A>'
bookmark_str += "\n    </DL>"
if out_file != None:
    with open(out_file, "w", encoding="utf-8") as real_out:
        real_out.write(bookmark_str)
else:
    print(bookmark_str)
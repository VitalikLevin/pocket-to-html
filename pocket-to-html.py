#!/usr/bin/env python3
import csv
import json
import argparse
from math import trunc
import os.path
from time import time
parser = argparse.ArgumentParser(prog="pocket-to-html", description="This script converts Pocket and Firefox bookmark backups to Netscape's bookmarks files")
parser.add_argument("input", help="Path of backup file")
parser.add_argument("-o", "-O", "--output", default=None, help="Path of output HTML file (default: contents are printed to console)", metavar="out.html")
parser.add_argument("-m", "-M", "--mode", choices=["pocket", "moz-json"], default="pocket", help="How to parse input (default: as a Pocket .csv, `moz-json` as a Firefox JSON)")
parser.add_argument("-n", "-N", action="store_true", help="Get rid of `overwrite file or not` dialogs", dest="no")
parser.add_argument("--mobile", action="store_true", help="Turn on mobile-friendly output")
args = parser.parse_args()
bookmark_str = "<!DOCTYPE NETSCAPE-Bookmark-file-1>\n<!-- This is an automatically generated file.\n     It will be read and overwritten.\n     DO NOT EDIT! -->"
bookmark_str += '\n<!-- Visit https://learn.microsoft.com/en-us/previous-versions/windows/internet-explorer/ie-developer/platform-apis/aa753582(v=vs.85) to learn more -->\n<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">'
if args.mobile == True:
    bookmark_str += '\n<META NAME="viewport" CONTENT="width=device-width, initial-scale=1">'
bookmark_str += '\n<META NAME="generator" CONTENT="pocket-to-html.py v0.2">\n<TITLE>Bookmarks</TITLE>\n<H1>Bookmarks</H1>\n<DL><p>'

def insert_bm(url, title, add_date, last_visit, last_mod, indent_lvl=1):
    return f'\n{"    " * indent_lvl}<DT><A HREF="{url}" ADD_DATE="{add_date}" LAST_VISIT="{last_visit}"\n{"    " * (indent_lvl + 1)}LAST_MODIFIED="{last_mod}">{title}</A>'

def ins_mozsubdir(moz_cont, ind_lvl=1):
    global bookmark_str
    if 'children' in moz_cont:
        temp_str = f'\n{"    " * ind_lvl}<DT><H3 FOLDED ADD_DATE="{trunc(moz_cont['dateAdded'] / 1000000)}" LAST_MODIFIED="{trunc(moz_cont['lastModified'] / 1000000)}">{moz_cont['title']}</H3>\n{"    " * ind_lvl}<DL><p>'
        for its_child in moz_cont['children']:
            if its_child["type"] == "text/x-moz-place":
                temp_str += insert_bm(its_child["uri"], its_child["title"], trunc(its_child["dateAdded"] / 1000000), trunc(its_child["lastModified"] / 1000000), trunc(its_child["lastModified"] / 1000000), ind_lvl + 1)
            else:
                ins_mozsubdir(its_child, ind_lvl + 1)
        temp_str += f"\n{"    " * ind_lvl}</DL><p>"
        bookmark_str += temp_str

def moz_parse(moz_file):
    global bookmark_str
    with open(moz_file, "r", encoding="utf-8") as moz_json:
        moz_mark = json.load(moz_json)
        for root_child in moz_mark["children"]:
            ins_mozsubdir(root_child)
    bookmark_str += "\n</DL>"

def pocket_parse(pocket_file):
    global bookmark_str
    with open(pocket_file, "r", encoding="utf-8") as pocket_csv:
        reader = csv.DictReader(pocket_csv)
        is_first_item = True
        for row in reader:
            if is_first_item == True:
                bookmark_str += f'\n    <DT><H3 FOLDED ADD_DATE="{row['time_added']}" LAST_MODIFIED="{trunc(time())}">Pocket</H3>'
                is_first_item = False
            bookmark_str += insert_bm(row["url"], f"{row['title']} (tags: `{row['tags']}`)", row["time_added"], row["time_added"], row["time_added"])
    bookmark_str += "\n</DL>"

if args.input:
    if os.path.isfile(args.input):
        in_file = args.input
    else:
        print(f"Error: File `{args.input}` does not exist.")
        exit()
if args.output != None:
    out_file = args.output
else:
    out_file = None

if args.mode == "pocket":
    pocket_parse(in_file)

if args.mode == "moz-json":
    moz_parse(in_file)

if out_file != None:
    if os.path.isfile(out_file) == True:
        print(f"Warning: file `{out_file}` exists")
        temp_choice = None
        if args.no != True:
            temp_choice = input("Do you want to overwrite it or exit (any value/[ENTER])? ")
        if temp_choice == None or args.no == True:
            exit()
    with open(out_file, "w", encoding="utf-8") as real_out:
        real_out.write(bookmark_str)
else:
    print(bookmark_str)
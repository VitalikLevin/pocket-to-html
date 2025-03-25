#!/usr/bin/env python3
import csv
import json
import html
import argparse
from math import trunc
import os.path
from time import time

prog_name = "pocket-to-html"
prog_ver = "0.4.0-beta"
indent_str = "    "

def usage_str(p_name):
    return """
{0} [--output out.html] [--mode MODE]
{2:{1}} [--mobile] [--tags] [--ie]
{2:{1}} [-n] [--interactive]
{2:{1}} input
{0} --help""".format(p_name, len(p_name), "")

parser = argparse.ArgumentParser(prog=prog_name, usage=usage_str(prog_name), description="This script converts Pocket and Firefox bookmark backups to Netscape's bookmarks files", add_help=False, allow_abbrev=False)
g_ess = parser.add_argument_group("Essential options")
g_ess.add_argument("input", help="Path of backup file")
g_ess.add_argument("-o", "-O", "--output", default=None, help="Path of output HTML file (default: contents are printed to console)", metavar="out.html")
g_ess.add_argument("-m", "-M", "--mode", choices=["pocket", "moz-json"], default="pocket", help="How to parse input (default: as a Pocket .csv, `moz-json` as a Firefox JSON)")
g_out = parser.add_argument_group("What is written in output file")
g_out.add_argument("--ie", action="store_true", help="Turn on compatibility with Internet Explorer specification")
g_out.add_argument("--mobile", action="store_true", help="Turn on mobile-friendly output")
g_out.add_argument("--tags", action="store_true", help="Write entries' tags in output if they are available")
g_misc = parser.add_argument_group("Miscellaneous options")
g_misc.add_argument("-i", "-I", "--interactive", action="store_true", help="Make the program more interactive")
g_misc.add_argument("-n", "-N", action="store_true", help="Get rid of `overwrite file or not` dialogs", dest="no")
g_misc.add_argument("-h", "-H", "--help", action="help", help="Show this help message and exit")
g_misc.add_argument("-v", "-V", "--version", action="version", version=f"%(prog)s {prog_ver}", help="Show version number and exit")
args = parser.parse_args()

bookmark_str = "<!DOCTYPE NETSCAPE-Bookmark-file-1>\n<!-- This is an automatically generated file.\n     It will be read and overwritten.\n     DO NOT EDIT! -->"
bookmark_str += "\n<META HTTP-EQUIV=\"Content-Type\" CONTENT=\"text/html; charset=UTF-8\">"
if args.mobile == True:
    bookmark_str += "\n<META NAME=\"viewport\" CONTENT=\"width=device-width, initial-scale=1\">"
bookmark_str += f"\n<META NAME=\"generator\" CONTENT=\"{prog_name}.py v{prog_ver}\">\n<TITLE>Bookmarks</TITLE>\n<H1>Bookmarks</H1>\n<DL><p>"

def insert_bm(url, title, add_date, last_visit, last_mod, tags, indent_lvl=1):
    if args.interactive == True:
        temp_title = title
        title = input(f"The current entry's title is ''{temp_title}''.\nPress [ENTER] to keep it or type the new one:\n> ")
        if title == None:
            title = temp_title
    temp_entry = f"\n{indent_str * indent_lvl}<DT><A HREF=\"{url}\" ADD_DATE=\"{add_date}\""
    if args.ie == True:
        temp_entry += f' LAST_VISIT="{last_visit}"'
    temp_entry += f"\n{indent_str * (indent_lvl + 1)}LAST_MODIFIED=\"{last_mod}\""
    if args.tags == True and tags != None and tags != "":
        temp_entry += f" TAGS=\"{tags}\""
    temp_entry += f">{html.escape(title)}</A>"
    return temp_entry

def ins_mozsubdir(moz_cont, ind_lvl=1):
    global bookmark_str
    if "children" in moz_cont:
        temp_str = f"\n{indent_str * ind_lvl}<DT><H3 "
        if args.ie == True:
            temp_str += "FOLDED "
        temp_str += f"ADD_DATE=\"{ trunc(moz_cont['dateAdded'] / 1000000) }\" LAST_MODIFIED=\"{ trunc(moz_cont['lastModified'] / 1000000) }\">{ html.escape(moz_cont['title']) }</H3>\n{ indent_str * ind_lvl }<DL><p>"
        for its_child in moz_cont['children']:
            if its_child["type"] == "text/x-moz-place":
                temp_tags = None
                if "tags" in its_child:
                    temp_tags = its_child["tags"]
                temp_str += insert_bm(its_child["uri"], its_child["title"], trunc(its_child["dateAdded"] / 1000000), trunc(its_child["lastModified"] / 1000000), trunc(its_child["lastModified"] / 1000000), temp_tags, ind_lvl + 1)
            else:
                ins_mozsubdir(its_child, ind_lvl + 1)
        temp_str += f"\n{indent_str * ind_lvl}</DL><p>"
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
                bookmark_str += "\n    <DT><H3 "
                if args.ie == True:
                    bookmark_str += "FOLDED "
                bookmark_str += f"ADD_DATE=\"{row['time_added']}\" LAST_MODIFIED=\"{trunc(time())}\">Pocket</H3>"
                is_first_item = False
            item_tags = row["tags"]
            if item_tags != None:
                item_tags = item_tags.replace("|", ",")
            bookmark_str += insert_bm(row["url"], row["title"], row["time_added"], row["time_added"], row["time_added"], item_tags)
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
        print(f"Warning: file `{out_file}` already exists")
        temp_choice = None
        if args.no != True:
            temp_choice = input("Do you want to overwrite it or exit (any value/[ENTER])? ")
        if temp_choice == None or args.no == True:
            exit()
    with open(out_file, "w", encoding="utf-8") as real_out:
        real_out.write(bookmark_str)
else:
    print(bookmark_str)
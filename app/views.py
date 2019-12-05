from app import app
from flask import render_template, request, redirect, jsonify, make_response
import os
import exiftool
import json
import pefile
import csv
import os
import sys
import json
from sklearn.externals import joblib
import pandas as pd
from pandas.io.json import json_normalize
from collections import OrderedDict
import sqlite3
from datetime import datetime, timedelta

content = []
with open('./dump/suspicious_functions.txt') as f:
    content = f.readlines()
content = [x.strip() for x in content]

name_packers = []
with open('./dump/name_packers.txt', encoding="utf8") as f:
    name_packers = f.readlines()
name_packers = [x.strip() for x in name_packers]


def c_json(name, pe, malware):

    count_suspicious_functions = 0
    number_packers = 0

    entropy = map(lambda x: x.get_entropy(), pe.sections)
    raw_sizes = map(lambda x: x.SizeOfRawData, pe.sections)
    virtual_sizes = map(lambda x: x.Misc_VirtualSize, pe.sections)
    physical_address = map(lambda x: x.Misc_PhysicalAddress, pe.sections)
    virtual_address = map(lambda x: x.VirtualAddress, pe.sections)
    pointer_raw_data = map(lambda x: x.PointerToRawData, pe.sections)
    characteristics = map(lambda x: x.Characteristics, pe.sections)

    data = {'Name': name,
            'e_magic': pe.DOS_HEADER.e_magic,
            'e_cblp': pe.DOS_HEADER.e_cblp,
            'e_cp': pe.DOS_HEADER.e_cp,
            'e_crlc': pe.DOS_HEADER.e_crlc,
            'e_cparhdr': pe.DOS_HEADER.e_cparhdr,
            'e_minalloc': pe.DOS_HEADER.e_minalloc,
            'e_maxalloc': pe.DOS_HEADER.e_maxalloc,
            'e_ss': pe.DOS_HEADER.e_ss,
            'e_sp': pe.DOS_HEADER.e_sp,
            'e_csum': pe.DOS_HEADER.e_csum,
            'e_ip': pe.DOS_HEADER.e_ip,
            'e_cs': pe.DOS_HEADER.e_cs,
            'e_lfarlc': pe.DOS_HEADER.e_lfarlc,
            'e_ovno': pe.DOS_HEADER.e_ovno,
            'e_oemid': pe.DOS_HEADER.e_oemid,
            'e_oeminfo': pe.DOS_HEADER.e_oeminfo,
            'e_lfanew': pe.DOS_HEADER.e_lfanew,
            'Machine': pe.FILE_HEADER.Machine,
            'NumberOfSections': pe.FILE_HEADER.NumberOfSections,
            'TimeDateStamp': pe.FILE_HEADER.TimeDateStamp,
            'PointerToSymbolTable': pe.FILE_HEADER.PointerToSymbolTable,
            'NumberOfSymbols': pe.FILE_HEADER.NumberOfSymbols,
            'SizeOfOptionalHeader': pe.FILE_HEADER.SizeOfOptionalHeader,
            'Characteristics': pe.FILE_HEADER.Characteristics,
            'Magic': pe.OPTIONAL_HEADER.Magic,
            'MajorLinkerVersion': pe.OPTIONAL_HEADER.MajorLinkerVersion,
            'MinorLinkerVersion': pe.OPTIONAL_HEADER.MinorLinkerVersion,
            'SizeOfCode': pe.OPTIONAL_HEADER.SizeOfCode,
            'SizeOfInitializedData': pe.OPTIONAL_HEADER.SizeOfInitializedData,
            'SizeOfUninitializedData': pe.OPTIONAL_HEADER.SizeOfUninitializedData,
            'AddressOfEntryPoint': pe.OPTIONAL_HEADER.AddressOfEntryPoint,
            'BaseOfCode': pe.OPTIONAL_HEADER.BaseOfCode,
            'ImageBase': pe.OPTIONAL_HEADER.ImageBase,
            'SectionAlignment': pe.OPTIONAL_HEADER.SectionAlignment,
            'FileAlignment': pe.OPTIONAL_HEADER.FileAlignment,
            'MajorOperatingSystemVersion': pe.OPTIONAL_HEADER.MajorOperatingSystemVersion,
            'MinorOperatingSystemVersion': pe.OPTIONAL_HEADER.MinorOperatingSystemVersion,
            'MajorImageVersion': pe.OPTIONAL_HEADER.MajorImageVersion,
            'MinorImageVersion': pe.OPTIONAL_HEADER.MinorImageVersion,
            'MajorSubsystemVersion': pe.OPTIONAL_HEADER.MajorSubsystemVersion,
            'MinorSubsystemVersion': pe.OPTIONAL_HEADER.MinorSubsystemVersion,
            'SizeOfHeaders': pe.OPTIONAL_HEADER.SizeOfHeaders,
            'CheckSum': pe.OPTIONAL_HEADER.CheckSum,
            'SizeOfImage': pe.OPTIONAL_HEADER.SizeOfImage,
            'Subsystem': pe.OPTIONAL_HEADER.Subsystem,
            'DllCharacteristics': pe.OPTIONAL_HEADER.DllCharacteristics,
            'SizeOfStackReserve': pe.OPTIONAL_HEADER.SizeOfStackReserve,
            'SizeOfStackCommit': pe.OPTIONAL_HEADER.SizeOfStackCommit,
            'SizeOfHeapReserve': pe.OPTIONAL_HEADER.SizeOfHeapReserve,
            'SizeOfHeapCommit': pe.OPTIONAL_HEADER.SizeOfHeapCommit,
            'LoaderFlags': pe.OPTIONAL_HEADER.LoaderFlags,
            'NumberOfRvaAndSizes': pe.OPTIONAL_HEADER.NumberOfRvaAndSizes
            }

    try:
        for entry in pe.DIRECTORY_ENTRY_IMPORT:
            for func in entry.imports:
                if func.name.decode('utf-8') in index().content:
                    count_suspicious_functions += 1
        data['SuspiciousImportFunctions'] = count_suspicious_functions
    except AttributeError:
        data['SuspiciousImportFunctions'] = 0

    try:
        for entry in pe.sections:
            try:
                entry.Name.decode('utf-8')
            except Exception:
                number_packers += 1
            if entry.Name in name_packers:
                number_packers += 1

        data['SuspiciousNameSection'] = number_packers
    except AttributeError as e:
        data['SuspiciousNameSection'] = 0
    try:
        data['SectionsLength'] = len(pe.sections)
    except (ValueError, TypeError):
        data['SectionsLength'] = 0
    try:
        data['SectionMinEntropy'] = min(entropy)
    except (ValueError, TypeError):
        data['SectionMinEntropy'] = 0
    try:
        data['SectionMaxEntropy'] = max(entropy)
    except (ValueError, TypeError):
        data['SectionMaxEntropy'] = 0
    try:
        data['SectionMinRawsize'] = min(raw_sizes)
    except (ValueError, TypeError):
        data['SectionMinRawsize'] = 0
    try:
        data['SectionMaxRawsize'] = max(raw_sizes)
    except (ValueError, TypeError):
        data['SectionMaxRawsize'] = 0
    try:
        data['SectionMinVirtualsize'] = min(virtual_sizes)
    except (ValueError, TypeError):
        data['SectionMinVirtualsize'] = 0
    try:
        data['SectionMaxVirtualsize'] = max(virtual_sizes)
    except (ValueError, TypeError):
        data['SectionMaxVirtualsize'] = 0
    try:
        data['SectionMaxVirtualsize'] = max(virtual_sizes)
    except (ValueError, TypeError):
        data['SectionMaxVirtualsize'] = 0

    try:
        data['SectionMaxPhysical'] = max(physical_address)
    except (ValueError, TypeError):
        data['SectionMaxPhysical'] = 0
    try:
        data['SectionMinPhysical'] = min(physical_address)
    except (ValueError, TypeError):
        data['SectionMinPhysical'] = 0

    try:
        data['SectionMaxVirtual'] = max(virtual_address)
    except (ValueError, TypeError):
        data['SectionMaxVirtual'] = 0
    try:
        data['SectionMinVirtual'] = min(virtual_address)
    except (ValueError, TypeError):
        data['SectionMinVirtual'] = 0

    try:
        data['SectionMaxPointerData'] = max(pointer_raw_data)
    except (ValueError, TypeError):
        data['SectionMaxPointerData'] = 0

    try:
        data['SectionMinPointerData'] = min(pointer_raw_data)
    except (ValueError, TypeError):
        data['SectionMinPointerData'] = 0

    try:
        data['SectionMaxChar'] = max(characteristics)
    except (ValueError, TypeError):
        data['SectionMaxChar'] = 0

    try:
        data['SectionMinChar'] = min(characteristics)
    except (ValueError, TypeError):
        data['SectionMainChar'] = 0

    try:
        data['DirectoryEntryImport'] = (len(pe.DIRECTORY_ENTRY_IMPORT))
        imports = sum([x.imports for x in pe.DIRECTORY_ENTRY_IMPORT], [])
        data['DirectoryEntryImportSize'] = (len(imports))
    except AttributeError:
        data['DirectoryEntryImport'] = 0
        data['DirectoryEntryImportSize'] = 0
    # Exports
    try:
        data['DirectoryEntryExport'] = (len(pe.DIRECTORY_ENTRY_EXPORT.symbols))
    except AttributeError:
        # No export
        data['DirectoryEntryExport'] = 0

    data['ImageDirectoryEntryExport'] = pe.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXPORT']].VirtualAddress
    data['ImageDirectoryEntryImport'] = pe.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_IMPORT']].VirtualAddress
    data['ImageDirectoryEntryResource'] = pe.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_RESOURCE']].VirtualAddress
    data['ImageDirectoryEntryException'] = pe.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_EXCEPTION']].VirtualAddress
    data['ImageDirectoryEntrySecurity'] = pe.OPTIONAL_HEADER.DATA_DIRECTORY[pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_SECURITY']].VirtualAddress

    return data


@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        file = request.files["file"]
        file.save(os.path.join("app/uploads", file.filename))
        files = "app/uploads/"+file.filename
        with exiftool.ExifTool() as et:
            metadata = et.get_metadata(files)

        keys = metadata.keys()
        values = metadata.values()
        # data = {}
        # for keys, values in metadata.items():
        #     data [keys] = values
        # output = json.dumps(data)

        p_json = c_json(files, pefile.PE(files, fast_load=True), 0)
        fieldnames = p_json.keys()
        test = pd.DataFrame([p_json], columns=fieldnames)
        X_to_push = test
        X_testing = test.drop(['Name'], axis=1)
        clf = joblib.load(
            'D:/Final_Year_Project/APP/app/MLmodels/RFC_model.pkl')
        X_testing_scaled = clf.named_steps['scale'].transform(X_testing)
        X_testing_pca = clf.named_steps['pca'].transform(X_testing_scaled)
        y_testing_pred = clf.named_steps['clf'].predict_proba(X_testing_pca)
        y_pred = y_testing_pred[0][0]*100
        if y_pred >= 40:
            pred_text = "Not Malicious"
        else:
            pred_text = "Malicious"

        return render_template("details.html", colnames=keys, records=values, predict=y_pred, predict_text=pred_text)

    return render_template("upload.html", message="Upload")


@app.route("/report")
def report():

    return render_template("details.html")


@app.route('/test', methods=['GET', 'POST'])
def test():
    # file = request.files["file"]
    # file.save(os.path.join("app/uploads", file.filename))
    filename = request.args['filename']
    print(filename)
    files = "app/uploads/"+filename
    with exiftool.ExifTool() as et:
        metadata = et.get_metadata(files)

    keys = metadata.keys()
    values = metadata.values()

    p_json = c_json(files, pefile.PE(files, fast_load=True), 0)
    fieldnames = p_json.keys()
    test = pd.DataFrame([p_json], columns=fieldnames)
    X_to_push = test
    X_testing = test.drop(['Name'], axis=1)
    clf = joblib.load(
        'D:/Final_Year_Project/APP/app/MLmodels/RFC_model.pkl')
    X_testing_scaled = clf.named_steps['scale'].transform(X_testing)
    X_testing_pca = clf.named_steps['pca'].transform(X_testing_scaled)
    y_testing_pred = clf.named_steps['clf'].predict_proba(X_testing_pca)
    y_pred = y_testing_pred[0][0]*100
    if y_pred >= 40:
        pred_text = "Not Malicious"
    else:
        pred_text = "Malicious"

    return jsonify({'prediction':pred_text,'pred_val':y_pred,'metadata':metadata})

# def Find_path():
#     User_profile = os.environ.get("USERPROFILE")
#     History_path = User_profile + r"\\AppData\Local\Google\Chrome\User Data\Default\History" #Usually this is where the chrome history file is located, change it if you need to.
#     return History_path

# @app.route('/history', methods=['GET'])
# def history():
#     data_base = Find_path()
#     connection = sqlite3.connect(data_base)
#     connection.text_factory = str
#     cur = connection.cursor()
#     output_file = open('chrome_history.csv', 'wb')
#     csv_writer = csv.writer(output_file)
#     #headers = ('URL', 'Title', 'Visit Count', 'Date (GMT)')
#     #csv_writer.writerow(headers)
#     epoch = datetime(1601, 1, 1)
#     for row in (cur.execute('select url, title, visit_count, last_visit_time from urls')):
#         row = list(row)
#         url_time = epoch + timedelta(microseconds=row[3])
#         row[3] = url_time
#         csv_writer.writerow(row)

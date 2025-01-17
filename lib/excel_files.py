import os
from stat import S_IREAD

import numpy as np
import pandas as pd


def create_excel_file(file_name: str):
    if '.xlsx' not in file_name:
        file_name = file_name + '.xlsx'
    writer = pd.ExcelWriter(file_name)
    return writer


def close_excel_file(writer):
    writer.close()
    os.chmod(writer, S_IREAD)


def get_excel_file(path):
    return pd.ExcelFile(path)


def get_data_from_excel(path):
    input_file = get_excel_file(path)
    list_of_sheets = []
    for sheet_name in input_file.sheet_names:
        df = input_file.parse(sheet_name)
        list_of_sheets.append(df)
    return list_of_sheets


def get_sheets_from_excel(path, sheet_names, input_file=None, header=0):
    if input_file is None:
        input_file = get_excel_file(path)
    list_of_sheets = []
    for sheet_name in sheet_names:
        df = input_file.parse(sheet_name, header=header)
        list_of_sheets.append(df)
    return list_of_sheets


def save_df_to_excel_sheet(writer, data_frame, sheet_name, index=True):
    data_frame.to_excel(writer, sheet_name=sheet_name, engine='xlsxwriter', index=index)
    writer.save()
    return writer


def add_data_to_existing_excel_sheet(writer, values_to_add: list, data_columns_names: list, sheet_name=0):
    file = pd.ExcelFile(writer, engine='openpyxl')
    df_in_file = file.parse(sheet_name=sheet_name)
    del df_in_file['Unnamed: 0']
    df_to_add = pd.DataFrame(np.reshape(values_to_add, (1, len(data_columns_names))), columns=data_columns_names)
    df = pd.concat([df_in_file, df_to_add])
    if sheet_name == 0:
        sheet_name = 'Sheet1'
    df.to_excel(writer, engine='xlsxwriter', sheet_name=sheet_name)
    writer.save()
    return df


def add_empty_line_to_df(df):
    empty_data = [None] * df.shape[1]
    df = pd.concat([df, pd.DataFrame([empty_data], columns=df.columns)])
    return df
import argparse
import csv
import pytest
import tempfile
import os
from main import CsvFile,StudentPerformanceReport
from rich.console import Console


@pytest.fixture
def temp_csv_data():
    data = [
        {
            'student_name':'testname',
            'subject':'testsubject',
            'teacher_name':'testteacher',
            'date':'2025-10-10',
            'grade':'1',
        },
        {
            'student_name':'testname',
            'subject':'testsubject',
            'teacher_name':'testteacher',
            'date':'2025-10-10',
            'grade':'2',
        },
        {
            'student_name':'testname2',
            'subject':'testsubject2',
            'teacher_name':'testteacher2',
            'date':'2025-10-10',
            'grade':'3',
        },
        {
            'student_name':'testname2',
            'subject':'testsubject2',
            'teacher_name':'testteacher2',
            'date':'2025-10-10',
            'grade':'4',
        },
        
    ]
    return data


@pytest.fixture
def temp_csv_file(temp_csv_data):
    with tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.csv',
        delete=False,
        encoding='utf-8',
    ) as f:
        writer = csv.DictWriter(
            f,fieldnames=[
                'student_name',
                'subject',
                'teacher_name',
                'date',
                'grade',
            ]
        )
        writer.writeheader()
        writer.writerows(temp_csv_data)
        temp_path = f.name

    yield temp_path
    os.unlink(temp_path)

class TestCsvFile:
    def test_get_file_success(self,temp_csv_file):
        csv_file = CsvFile()
        csv_file.get_file(temp_csv_file)
    
        assert len(csv_file.unpacked_data) == 4
        assert csv_file.unpacked_data[0]['student_name'] == 'testname'
        assert csv_file.unpacked_data[0]['subject'] == 'testsubject'
        assert csv_file.unpacked_data[0]['teacher_name'] == 'testteacher'
        assert csv_file.unpacked_data[0]['date'] == '2025-10-10'
        assert csv_file.unpacked_data[0]['grade'] == '1'
    
    def test_file_not_found(self):
        csv_file = CsvFile()
        csv_file.get_file('not_existing.csv')

        assert len(csv_file.unpacked_data) == 0
    
    def test_get_file_invalid_data(self):
        with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.csv', 
                delete=False, 
                encoding='utf-8'
            ) as f:
            f.write('invalid,csv,data\n1,2,3\n')
            temp_path = f.name
        
        csv_file = CsvFile()
        csv_file.get_file(temp_path)
        os.unlink(temp_path)

        assert len(csv_file.unpacked_data) == 0
    
    def test_get_file_invalid_extension(self):
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.txt', 
            delete=False,
            encoding='utf-8'
            ) as f:
            f.write('student_name,subject,teacher_name,date,grade')
            temp_path = f.name
        
        csv_file = CsvFile()
        csv_file.get_file(temp_path)
        os.unlink(temp_path)
        
        assert len(csv_file.unpacked_data) == 0


class TestStudentPerformanceReport:
    def test_aggregate_data(self,temp_csv_file):
        csv_file = CsvFile()
        csv_file.get_file(temp_csv_file)

        report = StudentPerformanceReport()
        report.get_data(csv_file)
        report.aggregate_data()

        assert len(report.aggregated_data) == 2
        assert report.aggregated_data[0]['student_name'] == 'testname' and\
                            report.aggregated_data[0]['mean_grade'] == 1.5 
        assert report.aggregated_data[1]['student_name'] == 'testname2' and\
                            report.aggregated_data[1]['mean_grade'] == 3.5
    
    def test_sort_data(self,temp_csv_file):
        csv_file = CsvFile()
        csv_file.get_file(temp_csv_file)

        report = StudentPerformanceReport()
        report.get_data(csv_file)
        report.aggregate_data()
        report.sort_data()

        assert report.aggregated_data[0]['student_name'] == 'testname2'
        assert report.aggregated_data[1]['student_name'] == 'testname'
    
    def test_create_table(self,temp_csv_file):
        csv_file = CsvFile()
        csv_file.get_file(temp_csv_file)

        report = StudentPerformanceReport()
        report.get_data(csv_file)
        report.aggregate_data()
        report.sort_data()
        report.create_table()

        console = Console(record=True)
        console.print(report.table)
        output = console.export_text()

        assert len(report.table.columns) == 3
        assert report.table.title == 'Успеваемость'
        assert 'Имя' in output
        assert 'Средняя оценка' in output
        assert 'Несуществующая колонка' not in output
    

    def test_populate_table(self,temp_csv_file):
        csv_file = CsvFile()
        csv_file.get_file(temp_csv_file)

        report = StudentPerformanceReport()
        report.get_data(csv_file)
        report.aggregate_data()
        report.sort_data()
        report.create_table()
        report.populate_table()

        console = Console(record=True)
        console.print(report.table)
        output = console.export_text()

        assert len(report.table.rows) == 2
        assert 'testname' in output
        assert 'testname2' in output
        assert 'testname3' not in output
        assert '1.5' in output
        assert '3.5' in output
        assert '6' not in output
        assert '1.' in output
        assert '2.' in output
        assert '0' not in output


class TestParser:
    def test_parser_single_file(self):
        test_args = ['--files', 'file.csv', '--report', 'student-performance']
        
        parser = argparse.ArgumentParser()
        parser.add_argument('--files', nargs='+', required=True)
        parser.add_argument('--report', required=True, choices=['student-performance'])
        
        args = parser.parse_args(test_args)
        
        assert args.files == ['file.csv']
        assert args.report == 'student-performance'

    def test_argparse_multiple_files(self):
        test_args = ['--files', 'file1.csv', 'file2.csv', '--report', 'student-performance']
        
        parser = argparse.ArgumentParser()
        parser.add_argument('--files', nargs='+', required=True)
        parser.add_argument('--report', required=True, choices=['student-performance'])
        
        args = parser.parse_args(test_args)
        
        assert args.files == ['file1.csv', 'file2.csv']
        assert args.report == 'student-performance'
import argparse
import csv
from abc import ABC,abstractmethod
from rich.console import Console
from rich.table import Table
from statistics import mean


class CsvFile:
    def __init__(self):
        self.unpacked_data = []

    def get_file(self,file):
        try:
            if not file.endswith('.csv'):
                print(f'Ошибка:{file} не является CSV файлом')
                return
            
            with open(file, 'r',encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                required_columns = ['student_name','subject','teacher_name','date','grade']
                if not all(col in reader.fieldnames for col in required_columns):
                    print(f'Ошибка: в файле {file} отсутствуют обязательные столбцы')
                    return
                
                self.unpacked_data.extend(list(reader))
            
        except FileNotFoundError:
            print(f'{file} не найден')
            return
        
        except Exception as e:
            print(e)
            return


class Report(ABC):
    @abstractmethod
    def __init__(self):
        self.data = []
        self.table = None|Table

    def get_data(self,csv:CsvFile):
        self.data = csv.unpacked_data.copy()
    
    def show_report(self):
        console = Console()
        console.print(self.table)
    
    @abstractmethod
    def create_table(self):
        pass

    @abstractmethod
    def populate_table(self):
        pass


class StudentPerformanceReport(Report):
    def __init__(self):
        super().__init__()
        self.aggregated_data = []
    
    def aggregate_data(self):
        student_by_grades = {}

        for row in self.data:
            try:
                student_name = row['student_name']
                grade = float(row['grade'])

                if student_name not in student_by_grades:
                    student_by_grades[student_name] = [grade]

                else:
                    student_by_grades[student_name].append(grade)

            except Exception as e:
                print(e)
            
        for student, grades in student_by_grades.items():
            try:
                self.aggregated_data.append(
                    {
                        'student_name':student,
                        'mean_grade': round(mean(grades),1),
                    }
                )
            except Exception as e:
                print(e)

    def sort_data(self):
        try:
            self.aggregated_data.sort(key=lambda x: (x['mean_grade']),reverse=True)

        except Exception as e:
            print(e)
    
    def create_table(self):
        self.table = Table(title='Успеваемость')
        self.table.add_column('')
        self.table.add_column('Имя')
        self.table.add_column('Средняя оценка')

    def populate_table(self):
            for index,row in enumerate(self.aggregated_data):
                self.table.add_row(str(index+1)+'.',row['student_name'],str(row['mean_grade']))
    

def main():
    parser = argparse.ArgumentParser(description='Генерация отчетов')
    parser.add_argument('--files', nargs='+', required=True, help='Название файлов c расширением csv')
    parser.add_argument('--report', required=True, choices=['student-performance'],help='Тип отчета')
    
    args = parser.parse_args()

    csv_file = CsvFile()

    for file in args.files:
        csv_file.get_file(file)
    
    if args.report == 'student-performance':
        report = StudentPerformanceReport()
        report.get_data(csv_file)
        report.aggregate_data()
        report.sort_data()
        report.create_table()
        report.populate_table()
        report.show_report()
        
if __name__ == "__main__":
    main()
"""
This script is used to analyze the sports data of a person. 
The data is stored in an Excel file and contains the following columns:
- group: the group to which the exercise belongs
- training_time: the time spent on the exercise
- date: the date of the exercise
- exercise: the type of exercise
- variation: the variation of the exercise
- weight: the weight used for the exercise
- reps: the number of repetitions
- total_time: the total time spent on the exercise
- distance: the distance covered
- speed: the speed
- slope: the slope
- notes: additional notes

The script provides three classes: DataLoader, ExerciseAnalysis, and RunAnalysis. 
DataLoader is used to load and clean the data, while ExerciseAnalysis is used to analyze the exercise data.
"""

import polars as pl
import matplotlib.pyplot as plt
import logging
import matplotlib.dates as mdates
from typing import Tuple, List, Union

logging.basicConfig(level=logging.INFO)

class DataLoader:
    def __init__(self, sheet_name: str) -> None:
        self.sheet_name = sheet_name

    def update_data(self, file_path: str, sheet_name: str) -> None:
        data = pl.read_excel(file_path, sheet_name=self.sheet_name)
        # Save the data in a specific location
        data.write_excel('data.xlsx', sheet_name=sheet_name)

    def read_data(self) -> pl.DataFrame:
        data = pl.read_excel('data.xlsx', sheet_name=self.sheet_name)
        columns = ['group', 'training_time', 'date', 'exercise',
                   'variation', 'weight', 'reps', 'total_time',
                   'distance', 'speed', 'slope', 'notes']
        data.columns = columns
        return data

    def clean_data(self, data: pl.DataFrame) -> pl.DataFrame:
        # Forward fill the 'group' and 'date' columns to handle missing values
        data = data.with_columns([
            pl.col('group').fill_null(strategy="forward"),
            # Assuming automatic datetime format inference works, if not, specify the format as a string
            pl.col('date').str.to_datetime().alias('date')
        ])

        # Fill NaN values in 'training_time' with '1:00'
        data = data.with_columns([
            pl.col('training_time').fill_null('1:00')
        ])

        # Fill NaN values in 'weight' with '80' and replace 'body' with '80'
        data = data.with_columns([
            pl.col('weight').fill_null('80').str.replace('body', '80')
        ])

        # Fill NaN values in 'reps' with '1'
        data = data.with_columns([
            pl.col('reps').fill_null('0')
        ])

        # Split 'weight' and 'reps' columns by '-' and convert to lists
        data = data.with_columns([
            pl.col('weight').str.split('-').apply(lambda x: [float(i) for i in x]),
            pl.col('reps').str.split('-').apply(lambda x: [eval(i) for i in x])
        ])

        return data

class ExerciseAnalysis:
    def __init__(self, data: pl.DataFrame) -> None:
        self.data = data

    def weight_trend_data(self, exercise: str) -> pl.DataFrame:
        exercise_data = self.data.filter(pl.col('exercise') == exercise)
        exercise_data = exercise_data.explode(['weight', 'reps']).with_columns([
            pl.col('weight').cast(pl.Float64),
            pl.col('reps').cast(pl.Float64)
        ])
        return exercise_data

    def total_weight_lifted_last_5(self) -> pl.DataFrame:
        exercises = self.data['exercise'].unique().to_list()
        total_weight_lifted = pl.DataFrame({
            'exercise': exercises,
            'total_weight_lifted': [self.weight_trend_data(exercise).tail(5).select((pl.col('weight') * pl.col('reps')).sum()).to_numpy()[0] for exercise in exercises]
        })
        return total_weight_lifted

    def total_weight_lifted_preceding_5(self) -> pl.DataFrame:
        exercises = self.data['exercise'].unique().to_list()
        total_weight_lifted = pl.DataFrame({
            'exercise': exercises,
            'total_weight_lifted': [self.weight_trend_data(exercise).tail(10).select((pl.col('weight') * pl.col('reps')).sum()).to_numpy()[0] - self.total_weight_lifted_last_5().filter(pl.col('exercise') == exercise)['total_weight_lifted'][0] for exercise in exercises]
        })
        return total_weight_lifted

    def unique_exercise_data(self) -> pl.DataFrame:
        unique_exercises = [exercise for exercise in self.data['exercise'].unique().to_list() if exercise not in ['Run', 'Walk', 'Mountain walk', 'Stretch']]
        unique_exercise_data = pl.DataFrame({'exercise': unique_exercises})

        for exercise in unique_exercises:
            count = len(self.data.filter(pl.col('exercise') == exercise))
            unique_exercise_data = unique_exercise_data.with_columns([
                pl.when(pl.col('exercise') == exercise).then(pl.lit(count)).otherwise(pl.col('exercise')).alias('count')
            ])

        for exercise in unique_exercises:
            exercise_data = self.weight_trend_data(exercise)
            max_weight = exercise_data['weight'].max()
            max_weight_reps = exercise_data.filter(pl.col('weight') == max_weight)['reps'][0]
            unique_exercise_data = unique_exercise_data.with_columns([
                pl.when(pl.col('exercise') == exercise).then(pl.lit(max_weight)).otherwise(pl.col('exercise')).alias('max_weight'),
                pl.when(pl.col('exercise') == exercise).then(pl.lit(max_weight_reps)).otherwise(pl.col('exercise')).alias('max_weight_reps')
            ])

        for exercise in unique_exercises:
            exercise_data = self.weight_trend_data(exercise)
            average_weight = exercise_data['weight'].mean()
            average_weight_last_5_runs = exercise_data.tail(5)['weight'].mean()
            unique_exercise_data = unique_exercise_data.with_columns([
                pl.when(pl.col('exercise') == exercise).then(pl.lit(average_weight)).otherwise(pl.col('exercise')).alias('average_weight'),
                pl.when(pl.col('exercise') == exercise).then(pl.lit(average_weight_last_5_runs)).otherwise(pl.col('exercise')).alias('average_weight_last_5_runs')
            ])

        total_weight_lifted_last_5 = self.total_weight_lifted_last_5()
        total_weight_lifted_preceding_5 = self.total_weight_lifted_preceding_5()
        unique_exercise_data = unique_exercise_data.with_columns([
            (pl.col('average_weight_last_5_runs') / pl.col('average_weight') * 100).alias('growth_percentage')
        ])

        unique_exercise_data = unique_exercise_data.rename({
            'exercise': 'Exercise', 'count': 'Count', 'max_weight': 'Max Weight',
            'max_weight_reps': 'Max Weight Reps', 'average_weight': 'Average Weight',
            'average_weight_last_5_runs': 'Average Weight Last 5 Runs', 'growth_percentage': 'Growth Percentage'
        })
        return unique_exercise_data

    def group_exercise_data(self) -> pl.DataFrame:
        data = self.data.with_columns([
            pl.col('group').fill_null('No group')
        ])
        unique_groups = data['group'].str.split('+').explode().str.strip().unique().to_list()
        group_exercise_data = pl.DataFrame({'group': unique_groups})

        for group in unique_groups:
            group_data = data.filter(pl.col('group') == group)
            count = len(group_data)
            average_weight = group_data['weight'].apply(lambda x: sum(x) / len(x)).mean()
            average_weight_last_5 = group_data['weight'].apply(lambda x: sum(x) / len(x)).tail(5).mean()
            growth_percentage = (average_weight_last_5 / average_weight * 100).round(2)
            group_exercise_data = group_exercise_data.with_columns([
                pl.when(pl.col('group') == group).then(pl.lit(count)).otherwise(pl.col('group')).alias('count'),
                pl.when(pl.col('group') == group).then(pl.lit(average_weight)).otherwise(pl.col('group')).alias('average_weight'),
                pl.when(pl.col('group') == group).then(pl.lit(average_weight_last_5)).otherwise(pl.col('group')).alias('average_weight_last_5'),
                pl.when(pl.col('group') == group).then(pl.lit(growth_percentage)).otherwise(pl.col('group')).alias('growth_percentage')
            ])

        group_exercise_data = group_exercise_data.rename({
            'group': 'Group', 'count': 'Count', 'average_weight': 'Average Weight',
            'average_weight_last_5': 'Average Weight Last 5', 'growth_percentage': 'Growth Percentage'
        })
        return group_exercise_data

class RunAnalysis:
    def __init__(self, data: pl.DataFrame) -> None:
        self.data = data

    def run_trend_data(self) -> pl.DataFrame:
        run_data = self.data.filter(pl.col('exercise') == 'Run').sort('date')
        run_data = run_data.with_columns([
            pl.col('distance').cast(pl.Float64),
            pl.col('total_time').apply(lambda x: int(x.split(':')[0]) * 60 + int(x.split(':')[1])).alias('total_time_in_minutes'),
            (pl.col('distance') / (pl.col('total_time_in_minutes') / 60)).alias('speed')
        ])
        return run_data

    def plot_run_trend(self, run_data: pl.DataFrame) -> None:
        plt.figure(figsize=(10, 6))
        plt.plot(run_data['date'], run_data['speed'], label='Speed')
        plt.xlabel('Date')
        plt.ylabel('Speed (km/h)')
        plt.title('Run Speed Trend Over Time')
        plt.legend()
        plt.grid(True)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.gcf().autofmt_xdate()
        plt.show()

if __name__ == '__main__':
    # Load and clean the data
    loader = DataLoader('Sports')
    data = loader.read_data()
    cleaned_data = loader.clean_data(data)

    # Perform run analysis
    running_data = RunAnalysis(cleaned_data)
    unique_running_data = running_data.run_trend_data()

    # Perform exercise analysis
    exercise_analysis = ExerciseAnalysis(cleaned_data)

    print(exercise_analysis.unique_exercise_data())
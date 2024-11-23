# QUESTION 2 PART B 
from collections import Counter
from copy import deepcopy
import pandas as pd

# Load the dataset 
df_dataset = pd.read_csv('/Users/akankshasoni/Dropbox/Econ of Ed/Pset2/school-choice-data.csv')

def deferred_acceptance(
    students_df: pd.DataFrame,
    schools_quota: dict,
    verbose: int = 0,
    max_iterations: int = 1000,
) -> dict:
    """
    The deferred acceptance algorithm implementation.
    The process would be the following:
    1. Students apply to schools based on their ranking and lottery.
    2. Schools accept students up to their capacity and reject the rest.
    3. Repeat the process until all students are matched or no more applications are possible.

    Args:
        students_df: DataFrame with columns ['student_id', 'ranking', 'school_id', 'student_lottery']
        schools_quota: Dictionary with school_id as key and capacity as value.
        verbose: If non-zero, prints the number of iterations.
        max_iterations: Safety net to stop infinite loops.

    Returns:
        Dictionary of student-school matches.
    """

    # Set up an environment for matching that identifies each unique student by their ID
    available_choices = {
        student: list(students_df.loc[students_df['student_id'] == student, 'school_id'])
        for student in students_df['student_id'].unique()
    }
    unassigned_students = set(students_df['student_id'])
    matches = {}
    itr_count = 0

    # Loop to run the DA algorithm 
    while unassigned_students and itr_count < max_iterations:
        # Students apply to their most preferred school 
        applications = {}
        for student in list(unassigned_students):
            if available_choices[student]:
                top_choice = available_choices[student][0]
                if top_choice not in applications:
                    applications[top_choice] = []
                applications[top_choice].append(student)
            else:
                # Discard all the unassigned students 
                unassigned_students.discard(student)

        # Schools take and process the applications
        progress_made = False
        for school, applicants in applications.items():
            if school in schools_quota:
                capacity = schools_quota[school]
                # Sort applicants by ranking and lottery (lower values are better)
                sorted_applicants = sorted(
                    applicants,
                    key=lambda s: (
                        students_df.loc[(students_df['student_id'] == s) & (students_df['school_id'] == school), 'ranking'].iloc[0],
                        students_df.loc[(students_df['student_id'] == s), 'student_lottery'].iloc[0],
                    )
                )
                # Use school capacity variable as a constraint 
                accepted = sorted_applicants[:capacity]
                for student in accepted:
                    matches[student] = school
                    unassigned_students.discard(student)
                    progress_made = True
                # Reject the rest
                rejected = sorted_applicants[capacity:]
                for student in rejected:
                    available_choices[student].remove(school)

        itr_count += 1
        if verbose:
            print(f"Iteration {itr_count}: {len(unassigned_students)} students remain unassigned")

        # Break if no progress is made
        if not progress_made:
            print("No progress made in this iteration. Breaking loop.")
            break

    # Check for unmatched students
    unmatched_students = unassigned_students
    if unmatched_students:
        print(f"Warning: {len(unmatched_students)} students could not be matched to any school.")

    return matches

# Prepare input data
# Ensure your dataset contains columns: 'student_id', 'ranking', 'school_id', 'student_lottery'
students_df = df_dataset[['student_id', 'ranking', 'school_id', 'student_lottery']]

# Create the schools_quota dictionary from the dataset
schools_quota = df_dataset.set_index('school_id')['school_cap'].to_dict()

# Run the DA algorithm
matches = deferred_acceptance(students_df, schools_quota, verbose=1)

# Print results
print(matches)

# Prepare a DataFrame for export
matches_df = pd.DataFrame(list(matches.items()), columns=['student_id', 'school_id'])
export_df = pd.merge(matches_df, students_df, on=['student_id', 'school_id'], how='left')

# Export the matches as a CSV
output_path = '/Users/akankshasoni/Dropbox/Econ of Ed/Pset2/Output/matches_with_details.csv'
export_df.to_csv(output_path, index=False)
print(f"Matches and additional details exported to {output_path}")

#QUESTION 2 PART C: MINORITY STUDENT GETS PRIORITY AND STUDENTS WANT SCHOOLS IN SAME ZONE
from collections import Counter
from copy import deepcopy
import pandas as pd

# Load the dataset
df_dataset = pd.read_csv('/Users/akankshasoni/Dropbox/Econ of Ed/Pset2/school-choice-data.csv')

# Create the `in_school_zone` variable: 1 if `school_zone` equals `student_zone`, else 0
df_dataset['in_school_zone'] = (df_dataset['school_zone'] == df_dataset['student_zone']).astype(int)

# Print znd verify all is well!
print(df_dataset.head())

def deferred_acceptance(
    students_df: pd.DataFrame,
    schools_quota: dict,
    verbose: int = 0,
    max_iterations: int = 1000,
) -> dict:
    """
    The deferred acceptance algorithm implementation with priority for minority students and school zones.

    Args:
        students_df: DataFrame with columns ['student_id', 'ranking', 'school_id', 'student_lottery', 'student_minority', 'in_school_zone']
        schools_quota: Dictionary with school_id as key and capacity as value.
        verbose: If non-zero, prints the number of iterations.
        max_iterations: Safety net to stop infinite loops.

    Returns:
        Dictionary of student-school matches.
    """

    # Set up an environment for matching that identifies each unique student by their ID
    available_choices = {
        student: list(students_df.loc[students_df['student_id'] == student, 'school_id'])
        for student in students_df['student_id'].unique()
    }
    unassigned_students = set(students_df['student_id'])
    matches = {}
    itr_count = 0

    # Loop to run the DA algorithm
    while unassigned_students and itr_count < max_iterations:
        # Students apply to their most preferred school
        applications = {}
        for student in list(unassigned_students):
            if available_choices[student]:
                top_choice = available_choices[student][0]
                if top_choice not in applications:
                    applications[top_choice] = []
                applications[top_choice].append(student)
            else:
                # Discard all the unassigned students
                unassigned_students.discard(student)

        # Schools take and process the applications
        progress_made = False
        for school, applicants in applications.items():
            if school in schools_quota:
                capacity = schools_quota[school]
                # Sort applicants by priority: minority status > in school zone > ranking and lottery
                sorted_applicants = sorted(
                    applicants,
                    key=lambda s: (
                        -students_df.loc[(students_df['student_id'] == s), 'student_minority'].iloc[0],  # Priority: Minority students
                        -students_df.loc[(students_df['student_id'] == s) & (students_df['school_id'] == school), 'in_school_zone'].iloc[0],  # Priority: Students in school zone
                        students_df.loc[(students_df['student_id'] == s) & (students_df['school_id'] == school), 'ranking'].iloc[0],  # Ranking
                        students_df.loc[(students_df['student_id'] == s), 'student_lottery'].iloc[0],  # Lottery
                    )
                )
                # Use school capacity as a constraint
                accepted = sorted_applicants[:capacity]
                for student in accepted:
                    matches[student] = school
                    unassigned_students.discard(student)
                    progress_made = True
                # Reject the rest
                rejected = sorted_applicants[capacity:]
                for student in rejected:
                    available_choices[student].remove(school)

        itr_count += 1
        if verbose:
            print(f"Iteration {itr_count}: {len(unassigned_students)} students remain unassigned")

        # Break if no progress is made
        if not progress_made:
            print("No progress made in this iteration. Breaking loop.")
            break

    # Check for unmatched students
    unmatched_students = unassigned_students
    if unmatched_students:
        print(f"Warning: {len(unmatched_students)} students could not be matched to any school.")

    return matches

# Prepare input data
# Ensure your dataset contains columns: 'student_id', 'ranking', 'school_id', 'student_lottery', 'student_minority', 'in_school_zone'
students_df = df_dataset[['student_id', 'ranking', 'school_id', 'student_lottery', 'student_minority', 'in_school_zone']]

# Create the schools_quota dictionary from the dataset
schools_quota = df_dataset.set_index('school_id')['school_cap'].to_dict()

# Run the DA algorithm
matches = deferred_acceptance(students_df, schools_quota, verbose=1)

# Print results
print(matches)

# Prepare a DataFrame for export
matches_df = pd.DataFrame(list(matches.items()), columns=['student_id', 'school_id'])
export_df = pd.merge(matches_df, students_df, on=['student_id', 'school_id'], how='left')

# Export the matches as a CSV
output_path = '/Users/akankshasoni/Dropbox/Econ of Ed/Pset2/Output/matches_with_zone_minority_priority.csv'
export_df.to_csv(output_path, index=False)
print(f"Matches and additional details exported to {output_path}")

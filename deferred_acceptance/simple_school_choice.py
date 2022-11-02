import itertools
import random
import numpy as np
import os
import sys
from deferred_acceptance import deferred_acceptance
from utils import create_dataframes

# class Student:
#     def __init__(self, name, permutations, minority):
#         self.name = name
#         self.alpha = 0
#         self.beta = 0
#         self.min = minority
#         self.school_pref = list(random.sample(permutations, 1)[0])
    
#     def set_alpha_beta(self, alpha_mean_maj, alpha_std, beta_std):
#         self.beta = np.random.normal(0, beta_std)

#         if self.min:
#             self.alpha = np.random.normal(0, alpha_std)
#         else:
#             self.alpha = np.random.normal(alpha_mean_maj, alpha_std)

# def create_students(num_students, schools, fraction_min, alpha_mean_maj, alpha_std, beta_std):
#     students_list = []
#     for i in range(num_students):
#         student_name = "s" + str(i + 1)
#         students_list.append(student_name)
#     min_students = random.sample(students_list, int(num_students * fraction_min))

#     students = []
#     for s in students_list:
#         is_min = (s in min_students)
#         student = Student(s, schools, is_min)
#         student.set_alpha_beta(alpha_mean_maj, alpha_std, beta_std)
#         students.append(student)
    
#     student_preferences = {}

#     for s in students:
#         student_preferences[s.name] = s.school_pref

#     return students, student_preferences

# def create_school_rankings(students, schools):
#     # scores = []
#     # indices = []
#     # aff_act_scores = []
#     # for i in range(0, len(students)):
#     #     indices.append(i + 1)
#     #     scores.append(students[i].alpha + students[i].beta)
#     #     aff_act_scores.append(students[i].beta)

#     # scores, new_indices = (list(t) for t in zip(*sorted(zip(scores, indices), reverse=True)))
#     # aff_act_scores, aff_act_indices = (list(t) for t in zip(*sorted(zip(aff_act_scores, indices), reverse=True)))

#     # school_preferences = {}
#     # for i in range(len(schools)):
#     #     if i == 0 and aff_act:
#     #         school_preferences[schools[i]] = aff_act_indices
#     #     else:
#     #         school_preferences[schools[i]] = new_indices

#     student_permutations = list(itertools.permutations(range(1, len(students) + 1)))

#     normal_school_preferences = {}
#     aff_act_school_preferences = {}
#     for i in range(len(schools)):
#         normal_prefs, aff_act_prefs = random.sample(student_permutations, 2)
#         if i == 0:
#             aff_act_school_preferences[schools[i]] = list(aff_act_prefs)
#             normal_school_preferences[schools[i]] = list(normal_prefs)
#         else:
#             aff_act_school_preferences[schools[i]] = list(normal_prefs)
#             normal_school_preferences[schools[i]] = list(normal_prefs)

#     return normal_school_preferences, aff_act_school_preferences

def create_schools_and_students(num_schools, num_students):
    schools_list = []
    schools_quota = {}
    for i in range(num_schools):
        school_name = "c" + str(i + 1)
        schools_list.append(school_name)
        schools_quota[school_name] = 1

    students_list = []
    for i in range(num_students):
        student_name = "s" + str(i + 1)
        students_list.append(student_name)
    
    return students_list, schools_list, schools_quota

def create_student_rankings(students_list, schools):
    school_permutations = list(itertools.permutations(range(1, len(schools) + 1)))

    student_preferences = {}
    for s in students_list:
        student_preferences[s] = list(random.sample(school_permutations, 1)[0])

    return student_preferences

def create_school_rankings(schools_list, students):
    student_permutations = list(itertools.permutations(range(1, len(students) + 1)))

    normal_school_preferences = {}
    aff_act_school_preferences = {}
    for i in range(len(schools_list)):
        normal_prefs, aff_act_prefs = random.sample(student_permutations, 2)
        if i == 0:
            aff_act_school_preferences[schools_list[i]] = list(aff_act_prefs)
            normal_school_preferences[schools_list[i]] = list(normal_prefs)
        else:
            aff_act_school_preferences[schools_list[i]] = list(normal_prefs)
            normal_school_preferences[schools_list[i]] = list(normal_prefs)

    return normal_school_preferences, aff_act_school_preferences

def simple_school_choice(schools_list, schools_quota, students_list, schools_preferences, students_preferences) -> None:
    """
    Here is a minimalistic example of deferred acceptance algorithm for school choice.
    """
    # Prepare the dataframes

    students_df, schools_df = create_dataframes(
        students_list=students_list,
        students_preferences=students_preferences,
        schools_list=schools_list,
        schools_preferences=schools_preferences,
    )

    matches = deferred_acceptance(
        students_df=students_df, schools_df=schools_df, schools_quota=schools_quota
    )

    return matches

def check_student_welfare(student, normal_match, aff_act_match):
    normal_ranking = -1
    aff_act_ranking = -1

    for key in normal_match:
        if student in key:
            normal_ranking = normal_match[key][0]
    for key in aff_act_match:
        if student in key:
            aff_act_ranking = aff_act_match[key][0]
    
    if normal_ranking > aff_act_ranking:
        return 1
    elif normal_ranking == aff_act_ranking:
        return 0
    else:
        return -1


if __name__ == "__main__":
    num_students = 5
    num_schools = 5

    num_same = 0
    num_diff = 0
    num_total = 0


    for i in range(5000):
        students_list, schools_list, schools_quota = create_schools_and_students(num_schools, num_students)
        students_preferences = create_student_rankings(students_list, schools_list)
        schools_preferences, aff_act_schools_preferences = create_school_rankings(schools_list, students_list)

        normal_match = simple_school_choice(schools_list, schools_quota, students_list, schools_preferences, students_preferences)
        aff_act_match = simple_school_choice(schools_list, schools_quota, students_list, aff_act_schools_preferences, students_preferences)

        normal_match_keys = list(normal_match.keys())
        aff_act_match_keys = list(aff_act_match.keys())

        if normal_match_keys == aff_act_match_keys:
            num_same += 1
        else:
            num_diff += 1
            num_min_students_worse = 0
            for student in students_list:
                improved = check_student_welfare(student, normal_match, aff_act_match)
                if improved == -1:
                    num_min_students_worse += 1
                
            if num_min_students_worse >= num_students - 1:
                print(num_min_students_worse)
                print("Student preferences: " + str(students_preferences))
                print("School preferences: " + str(schools_preferences))
                print("Affirmative Action School preferences: " + str(aff_act_schools_preferences))
                print("Normal Match: " + str(normal_match))
                print("Affirmative Action Match: " + str(aff_act_match))

    print("# Same " + str(num_same))
    print("# Diff " + str(num_diff))

    
